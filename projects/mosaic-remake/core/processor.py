import os
import threading
import traceback
import logging
from typing import Callable

import cv2
from PIL import Image
from ultralytics import YOLO

from core.filter_utils import ImageFilterUtils
from utils.file_io import imread_safe, imwrite_safe

logger = logging.getLogger(__name__)


class MosaicProcessor:
    def __init__(self):
        self.stop_flag = False
        self.model_lock = threading.Lock()
        self.inference_lock = threading.Lock()
        self.model = None
        self.model_path = ""
        self.class_names = {}

    def load_model(self, model_path: str):
        if not model_path or not os.path.exists(model_path):
            logger.warning("Model not found: %s", model_path)
            with self.model_lock:
                self.model = None
                self.model_path = ""
                self.class_names = {}
            return False, {}

        try:
            logger.info("Loading model: %s", model_path)
            loaded_model = YOLO(model_path)
            class_names = {
                int(idx): str(name) for idx, name in dict(loaded_model.names).items()
            }
            with self.model_lock:
                self.model = loaded_model
                self.model_path = model_path
                self.class_names = class_names
            return True, class_names
        except Exception as exc:
            logger.error("Failed to load model: %s", exc)
            with self.model_lock:
                self.model = None
                self.model_path = ""
                self.class_names = {}
            return False, {}

    def unload_model(self):
        with self.model_lock:
            self.model = None
            self.model_path = ""
            self.class_names = {}

    def has_model(self) -> bool:
        with self.model_lock:
            return self.model is not None

    def get_model_info(self) -> dict:
        with self.model_lock:
            return {
                "loaded": self.model is not None,
                "model_path": self.model_path,
                "class_names": dict(self.class_names),
            }

    def detect_candidates(self, img, imgsz: int = 640, min_conf: float = 0.01) -> list:
        with self.model_lock:
            model = self.model
            class_names = dict(self.class_names)
        if model is None:
            return []

        candidates = []
        try:
            with self.inference_lock:
                results = model.predict(img, conf=min_conf, imgsz=imgsz, verbose=False)
            result = results[0]
            if result.boxes:
                for index, box in enumerate(result.boxes):
                    mask_data = None
                    if result.masks is not None:
                        mask_data = result.masks.data[index].cpu().numpy()

                    cls_index = int(box.cls[0])
                    cls_name = class_names.get(cls_index, str(cls_index))
                    candidates.append(
                        {
                            "cls": cls_name,
                            "conf": float(box.conf[0]),
                            "xyxy": box.xyxy[0].tolist(),
                            "mask": mask_data,
                        }
                    )
        except Exception as exc:
            logger.error("Detection error: %s", exc)

        return candidates

    def filter_candidates(self, raw_candidates: list, class_settings: dict) -> list:
        filtered = []
        for candidate in raw_candidates:
            cls_id = candidate["cls"]
            settings = class_settings.get(cls_id, {})
            if not settings.get("enabled", False):
                continue

            threshold = settings.get("conf", 0.25)
            if candidate["conf"] >= threshold:
                filtered.append(candidate)

        return filtered

    def render_preview(self, img, params: dict, class_settings: dict):
        has_enabled = any(
            settings.get("enabled", False) for settings in class_settings.values()
        )
        if img is None or not has_enabled or not self.has_model():
            return img.copy() if img is not None else None, []

        active_confs = [
            settings["conf"]
            for settings in class_settings.values()
            if settings.get("enabled")
        ]
        preview_min_conf = min(active_confs) if active_confs else 0.25
        raw_candidates = self.detect_candidates(
            img,
            imgsz=params["imgsz"],
            min_conf=preview_min_conf,
        )
        valid_candidates = self.filter_candidates(raw_candidates, class_settings)

        if params["shape_type"] == "box":
            preview_image = ImageFilterUtils.apply_filter_box(
                img,
                valid_candidates,
                params["mask_type"],
                params["strength"],
                params["margin"],
            )
        else:
            preview_image = ImageFilterUtils.apply_filter_mask(
                img,
                valid_candidates,
                params["mask_type"],
                params["strength"],
                params["margin"],
            )
        return preview_image, valid_candidates

    def _save_without_metadata(self, img_bgr, output_path: str):
        try:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            clean_img = Image.new(pil_img.mode, pil_img.size)
            clean_img.putdata(list(pil_img.getdata()))

            ext = os.path.splitext(output_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                clean_img.save(output_path, "JPEG", quality=95)
            elif ext == ".png":
                clean_img.save(output_path, "PNG")
            elif ext == ".webp":
                clean_img.save(output_path, "WEBP", quality=95)
            else:
                clean_img.save(output_path)
        except Exception as exc:
            logger.error("Metadata removal save error: %s", exc)
            imwrite_safe(output_path, img_bgr)

    def process_batch(
        self,
        input_dir: str,
        output_dir: str,
        imgsz: int,
        strength: float,
        margin: float,
        mask_type: str,
        shape_type: str,
        class_settings: dict,
        reviewed_candidates_by_path: dict | None,
        progress_cb: Callable[[int, int, str], None],
        finish_cb: Callable[[int, int], None],
    ) -> dict:
        result_summary = {"total": 0, "processed": 0, "errors": 0}
        has_enabled = any(
            settings.get("enabled", False) for settings in class_settings.values()
        )

        if has_enabled and not self.has_model():
            logger.error("No model loaded.")
            finish_cb(0, 0)
            return result_summary

        self.stop_flag = False
        os.makedirs(output_dir, exist_ok=True)

        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        paths = []
        try:
            for entry in os.scandir(input_dir):
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in exts:
                    paths.append(entry.path)
        except Exception as exc:
            logger.error("Error reading directory: %s", exc)

        paths = sorted(paths)
        total = len(paths)
        result_summary["total"] = total

        if total == 0:
            finish_cb(0, 0)
            return result_summary

        processed_count = 0
        error_count = 0

        for index, path in enumerate(paths):
            if self.stop_flag:
                break

            filename = os.path.basename(path)
            try:
                img = imread_safe(path)
                if img is None:
                    error_count += 1
                    logger.error("Could not read image: %s", filename)
                    progress_cb(index + 1, total, filename)
                    continue

                if not has_enabled:
                    self._save_without_metadata(img, os.path.join(output_dir, filename))
                else:
                    reviewed_candidates = None
                    if reviewed_candidates_by_path:
                        reviewed_candidates = reviewed_candidates_by_path.get(path)

                    if reviewed_candidates is not None:
                        valid_candidates = list(reviewed_candidates)
                    else:
                        active_confs = [
                            settings["conf"]
                            for settings in class_settings.values()
                            if settings.get("enabled")
                        ]
                        batch_min_conf = min(active_confs) if active_confs else 0.25
                        raw_candidates = self.detect_candidates(
                            img, imgsz=imgsz, min_conf=batch_min_conf
                        )

                        if self.stop_flag:
                            break

                        valid_candidates = self.filter_candidates(
                            raw_candidates, class_settings
                        )

                    if shape_type == "mask":
                        result_img = ImageFilterUtils.apply_filter_mask(
                            img, valid_candidates, mask_type, strength, margin
                        )
                    else:
                        result_img = ImageFilterUtils.apply_filter_box(
                            img, valid_candidates, mask_type, strength, margin
                        )

                    self._save_without_metadata(
                        result_img, os.path.join(output_dir, filename)
                    )

                processed_count += 1
            except Exception as exc:
                error_count += 1
                logger.error("Error processing %s: %s", filename, exc)
                logger.debug(traceback.format_exc())

            progress_cb(index + 1, total, filename)

        result_summary["processed"] = processed_count
        result_summary["errors"] = error_count
        finish_cb(processed_count, error_count)
        return result_summary
