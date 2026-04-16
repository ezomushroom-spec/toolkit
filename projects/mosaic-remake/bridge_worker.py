import json
import logging
import sys
import numpy as np

from core.config import load_settings, normalize_model_path
from core.processor import MosaicProcessor
from utils.file_io import imread_safe, imwrite_safe


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", newline="\n")


def _resolve_settings(request: dict | None):
    settings = load_settings()
    if not isinstance(request, dict):
        return settings

    if "model_path" in request:
        settings["model_path"] = normalize_model_path(str(request.get("model_path", "")))
    if "params" in request and isinstance(request["params"], dict):
        settings["params"].update(request["params"])
    if "class_settings" in request and isinstance(request["class_settings"], dict):
        for class_id, class_data in request["class_settings"].items():
            if class_id in settings["class_settings"] and isinstance(class_data, dict):
                settings["class_settings"][class_id].update(class_data)
    return settings


class WorkerState:
    def __init__(self):
        self.processor = MosaicProcessor()
        self.loaded_model_path = ""
        self.class_names = {}

    def ensure_model(self, settings: dict):
        model_path = settings.get("model_path", "")
        if not model_path:
            self.loaded_model_path = ""
            self.class_names = {}
            return False, {}

        if self.loaded_model_path == model_path:
            return True, self.class_names

        load_ok, class_names = self.processor.load_model(model_path)
        if load_ok:
            self.loaded_model_path = model_path
            self.class_names = class_names
        else:
            self.loaded_model_path = ""
            self.class_names = {}
        return load_ok, self.class_names


def handle_health(state: WorkerState, payload: dict):
    settings = _resolve_settings(payload.get("request"))
    load_ok, class_names = state.ensure_model(settings)
    return {
        "ok": True,
        "model_path": settings.get("model_path", ""),
        "model_loaded": bool(load_ok),
        "class_names": class_names,
        "class_settings": settings.get("class_settings", {}),
    }


def handle_preview(state: WorkerState, payload: dict):
    request = payload.get("request", {})
    settings = _resolve_settings(request)
    image_path = request.get("image_path", "")
    output_preview_path = request.get("output_preview_path", "")

    if not image_path:
        return {"ok": False, "error": "image_path is required"}
    if not output_preview_path:
        return {"ok": False, "error": "output_preview_path is required"}

    load_ok, _class_names = state.ensure_model(settings)
    if not load_ok:
        return {"ok": False, "error": "model load failed"}

    img = imread_safe(image_path)
    if img is None:
        return {"ok": False, "error": "image read failed"}

    preview_image, candidates = state.processor.render_preview(
        img,
        settings["params"],
        settings["class_settings"],
    )
    if preview_image is None:
        preview_image = img

    saved = imwrite_safe(output_preview_path, preview_image)
    return {
        "ok": bool(saved),
        "preview_path": output_preview_path,
        "candidate_count": len(candidates),
        "candidates": [
            {
                "cls": candidate["cls"],
                "conf": candidate["conf"],
                "xyxy": candidate["xyxy"],
            }
            for candidate in candidates
        ],
    }


def handle_detect_preview(state: WorkerState, payload: dict):
    request = payload.get("request", {})
    settings = _resolve_settings(request)
    image_path = request.get("image_path", "")

    if not image_path:
        return {"ok": False, "error": "image_path is required"}

    has_enabled = any(
        class_data.get("enabled", False)
        for class_data in settings["class_settings"].values()
    )

    img = imread_safe(image_path)
    if img is None:
        return {"ok": False, "error": "image read failed"}

    if not has_enabled:
        return {
            "ok": True,
            "candidate_count": 0,
            "image_width": int(img.shape[1]),
            "image_height": int(img.shape[0]),
            "candidates": [],
        }

    load_ok, _class_names = state.ensure_model(settings)
    if not load_ok:
        return {"ok": False, "error": "model load failed"}

    active_confs = [
        class_data["conf"]
        for class_data in settings["class_settings"].values()
        if class_data.get("enabled")
    ]
    preview_min_conf = min(active_confs) if active_confs else 0.25
    raw_candidates = state.processor.detect_candidates(
        img,
        imgsz=settings["params"]["imgsz"],
        min_conf=preview_min_conf,
    )
    candidates = state.processor.filter_candidates(raw_candidates, settings["class_settings"])

    return {
        "ok": True,
        "candidate_count": len(candidates),
        "image_width": int(img.shape[1]),
        "image_height": int(img.shape[0]),
        "candidates": [
            {
                "cls": candidate["cls"],
                "conf": candidate["conf"],
                "xyxy": candidate["xyxy"],
            }
            for candidate in candidates
        ],
    }


def handle_warmup(state: WorkerState, payload: dict):
    request = payload.get("request", {})
    settings = _resolve_settings(request)
    load_ok, _class_names = state.ensure_model(settings)
    if not load_ok:
        return {"ok": False, "error": "model load failed"}

    dummy = np.zeros((256, 256, 3), dtype=np.uint8)
    with state.processor.inference_lock:
        state.processor.model.predict(dummy, conf=0.01, imgsz=640, verbose=False)
    return {"ok": True}


def main():
    state = WorkerState()
    handlers = {
        "health": handle_health,
        "preview": handle_preview,
        "detect_preview": handle_detect_preview,
        "warmup": handle_warmup,
    }

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        try:
            payload = json.loads(line)
            command = payload.get("command")

            if command == "shutdown":
                print(json.dumps({"ok": True, "message": "shutdown"}, ensure_ascii=False), flush=True)
                return 0

            handler = handlers.get(command)
            if handler is None:
                print(json.dumps({"ok": False, "error": f"unknown command: {command}"}, ensure_ascii=False), flush=True)
                continue

            result = handler(state, payload)
            print(json.dumps(result, ensure_ascii=False), flush=True)
        except Exception as exc:
            logger.exception("bridge worker error")
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
