import json
import os
import sys
from copy import deepcopy

APP_TITLE = "AutoMosaic v3.0 (Commercial Grade)"

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = APP_DIR
CONFIG_FILE = os.path.join(APP_DIR, "settings.json")
DEFAULT_MODEL_FILE = os.path.join(APP_DIR, "ntd11_anime_nsfw_segm_v5-variant1.pt")

LABEL_TRANSLATION = {
    "nipples": "乳首",
    "nipple": "乳首",
    "penis": "男性器",
    "pussy": "女性器",
    "anus": "肛門",
    "testicles": "睾丸",
    "testicle": "睾丸",
    "x-ray": "X-ray (断面図)",
    "cross-section": "断面図",
    "breast": "胸",
    "breasts": "胸",
    "genitalia": "性器",
    "face": "顔",
}

MASK_TYPES = {
    "pixel": "ピクセルモザイク",
    "blur": "ぼかし (ブラー)",
    "black": "黒塗り",
    "white": "白塗り",
}

SHAPE_TYPES = {
    "box": "矩形 (ボックス)",
    "mask": "形状に沿う (精密)",
}

INFERENCE_SIZES = [640, 960, 1280, 1600]

TARGET_CLASSES = [
    {"id": "pussy", "label_en": "pussy", "label_jp": "女性器"},
    {"id": "penis", "label_en": "penis", "label_jp": "男性器"},
    {"id": "testicles", "label_en": "testicles", "label_jp": "睾丸"},
    {"id": "anus", "label_en": "anus", "label_jp": "肛門"},
    {"id": "nipples", "label_en": "nipples", "label_jp": "乳首"},
    {"id": "breast", "label_en": "breast", "label_jp": "胸"},
]


def default_params():
    return {
        "mask_type": "pixel",
        "shape_type": "mask",
        "imgsz": 960,
        "strength": 15.0,
        "margin": 15.0,
        "show_boxes": False,
    }


def default_class_settings():
    return {
        cls["id"]: {"enabled": False, "conf": 0.3}
        for cls in TARGET_CLASSES
    }


def default_settings():
    return {
        "model_path": DEFAULT_MODEL_FILE if os.path.exists(DEFAULT_MODEL_FILE) else "",
        "input_dir": "未選択",
        "output_dir": "未選択",
        "params": default_params(),
        "class_settings": default_class_settings(),
    }


def normalize_model_path(model_path: str) -> str:
    if model_path and str(model_path).lower().endswith(".pt") and os.path.exists(model_path):
        return model_path
    if os.path.exists(DEFAULT_MODEL_FILE):
        return DEFAULT_MODEL_FILE
    return ""


def normalize_settings(data: dict | None):
    normalized = default_settings()
    if not isinstance(data, dict):
        return normalized

    normalized["model_path"] = normalize_model_path(data.get("model_path", ""))

    input_dir = data.get("input_dir")
    if isinstance(input_dir, str) and input_dir.strip():
        normalized["input_dir"] = input_dir

    output_dir = data.get("output_dir")
    if isinstance(output_dir, str) and output_dir.strip():
        normalized["output_dir"] = output_dir

    params = deepcopy(normalized["params"])
    raw_params = data.get("params", {})
    if isinstance(raw_params, dict):
        if raw_params.get("mask_type") in MASK_TYPES:
            params["mask_type"] = raw_params["mask_type"]
        if raw_params.get("shape_type") in SHAPE_TYPES:
            params["shape_type"] = raw_params["shape_type"]
        if raw_params.get("imgsz") in INFERENCE_SIZES:
            params["imgsz"] = raw_params["imgsz"]
        for key in ("strength", "margin"):
            value = raw_params.get(key)
            if isinstance(value, (int, float)):
                params[key] = float(value)
        if "show_boxes" in raw_params:
            params["show_boxes"] = bool(raw_params["show_boxes"])
    normalized["params"] = params

    class_settings = default_class_settings()
    raw_class_settings = data.get("class_settings", {})
    if isinstance(raw_class_settings, dict):
        for class_id in class_settings:
            raw = raw_class_settings.get(class_id, {})
            if not isinstance(raw, dict):
                continue
            class_settings[class_id] = {
                "enabled": bool(raw.get("enabled", False)),
                "conf": float(raw.get("conf", 0.3)),
            }
            legacy_path = raw.get("model_path", "")
            if not normalized["model_path"]:
                normalized["model_path"] = normalize_model_path(legacy_path)
    normalized["class_settings"] = class_settings

    if normalized["model_path"] == "" and os.path.exists(DEFAULT_MODEL_FILE):
        normalized["model_path"] = DEFAULT_MODEL_FILE

    return normalized


def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as handle:
                return normalize_settings(json.load(handle))
        except Exception:
            pass
    return default_settings()


def save_settings(data):
    normalized = normalize_settings(data)
    with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
        json.dump(normalized, handle, indent=4, ensure_ascii=False)
    return normalized
