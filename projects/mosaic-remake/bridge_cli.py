import argparse
import json
import logging
import os
import sys

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
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def _load_request(path: str | None):
    if not path:
        return {}
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _resolve_settings(request: dict):
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


def _processor_from_settings(settings: dict):
    processor = MosaicProcessor()
    model_path = settings.get("model_path", "")
    load_ok = False
    class_names = {}
    if model_path:
        load_ok, class_names = processor.load_model(model_path)
    return processor, load_ok, class_names


def cmd_health(args):
    settings = _resolve_settings(_load_request(args.request))
    processor, load_ok, class_names = _processor_from_settings(settings)
    result = {
        "ok": True,
        "model_path": settings.get("model_path", ""),
        "model_loaded": bool(load_ok),
        "class_names": class_names,
        "class_settings": settings.get("class_settings", {}),
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_preview(args):
    request = _load_request(args.request)
    settings = _resolve_settings(request)
    image_path = args.image_path or request.get("image_path", "")
    output_preview_path = args.output_preview_path or request.get("output_preview_path", "")

    if not image_path:
        print(json.dumps({"ok": False, "error": "image_path is required"}, ensure_ascii=False))
        return 1
    if not output_preview_path:
        print(json.dumps({"ok": False, "error": "output_preview_path is required"}, ensure_ascii=False))
        return 1

    processor, load_ok, _class_names = _processor_from_settings(settings)
    if not load_ok:
        print(json.dumps({"ok": False, "error": "model load failed"}, ensure_ascii=False))
        return 1

    img = imread_safe(image_path)
    if img is None:
        print(json.dumps({"ok": False, "error": "image read failed"}, ensure_ascii=False))
        return 1

    preview_image, candidates = processor.render_preview(
        img,
        settings["params"],
        settings["class_settings"],
    )
    if preview_image is None:
        preview_image = img

    saved = imwrite_safe(output_preview_path, preview_image)
    result = {
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
    print(json.dumps(result, ensure_ascii=False))
    return 0 if saved else 1


def cmd_batch(args):
    request = _load_request(args.request)
    settings = _resolve_settings(request)
    input_dir = args.input_dir or request.get("input_dir", "")
    output_dir = args.output_dir or request.get("output_dir", "")
    reviewed_candidates_by_path = request.get("reviewed_candidates_by_path", {})

    if not input_dir:
        print(json.dumps({"ok": False, "error": "input_dir is required"}, ensure_ascii=False))
        return 1
    if not output_dir:
        print(json.dumps({"ok": False, "error": "output_dir is required"}, ensure_ascii=False))
        return 1

    processor, load_ok, _class_names = _processor_from_settings(settings)
    has_enabled = any(
        item.get("enabled", False) for item in settings["class_settings"].values()
    )
    if has_enabled and not load_ok:
        print(json.dumps({"ok": False, "error": "model load failed"}, ensure_ascii=False))
        return 1

    progress_events = []
    finished = []
    summary = processor.process_batch(
        input_dir,
        output_dir,
        settings["params"]["imgsz"],
        settings["params"]["strength"],
        settings["params"]["margin"],
        settings["params"]["mask_type"],
        settings["params"]["shape_type"],
        settings["class_settings"],
        reviewed_candidates_by_path,
        progress_cb=lambda step, total, name: progress_events.append(
            {"step": step, "total": total, "name": name}
        ),
        finish_cb=lambda processed, errors: finished.append(
            {"processed": processed, "errors": errors}
        ),
    )
    result = {
        "ok": True,
        "summary": summary,
        "finished": finished[-1] if finished else None,
        "progress_count": len(progress_events),
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Mosaic Remake bridge CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    health = subparsers.add_parser("health")
    health.add_argument("--request", help="JSON request file path")
    health.set_defaults(func=cmd_health)

    preview = subparsers.add_parser("preview")
    preview.add_argument("--request", help="JSON request file path")
    preview.add_argument("--image-path", help="Input image path")
    preview.add_argument("--output-preview-path", help="Output preview image path")
    preview.set_defaults(func=cmd_preview)

    batch = subparsers.add_parser("batch")
    batch.add_argument("--request", help="JSON request file path")
    batch.add_argument("--input-dir", help="Input folder path")
    batch.add_argument("--output-dir", help="Output folder path")
    batch.set_defaults(func=cmd_batch)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
