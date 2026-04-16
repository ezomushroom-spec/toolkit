"""URL解析・モデル判定"""

import re
from urllib.parse import urlparse, parse_qs

# CivitaiダウンロードURLのパターン
DOWNLOAD_URL_PATTERN = re.compile(
    r"civitai\.com/api/download/models/(\d+)"
)

# ページURLからバージョンIDを抽出 (例: /models/12345?modelVersionId=67890)
_PAGE_VERSION_PATTERN = re.compile(
    r"civitai\.com/models/\d+.*[?&]modelVersionId=(\d+)"
)

# ページURLからモデルIDを抽出 (例: /models/12345)
_PAGE_MODEL_PATTERN = re.compile(
    r"civitai\.com/models/(\d+)"
)

# モデルファイルの拡張子
_MODEL_EXTENSIONS = frozenset({
    ".safetensors", ".ckpt", ".pt", ".pth", ".bin",
    ".onnx", ".engine",
})

# 非モデルファイルの拡張子
_NON_MODEL_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
    ".mp4", ".webm", ".avi", ".mov",
    ".txt", ".json", ".yaml", ".yml", ".toml",
    ".zip", ".7z", ".rar", ".tar", ".gz",
    ".html", ".css", ".js",
})


def parse_download_url(url: str) -> dict | None:
    """
    ダウンロードURLからモデルバージョンIDを抽出する。

    Returns:
        dict: {"model_version_id": int, "type_hint": str|None, "format": str|None}
        None: マッチしない場合
    """
    m = DOWNLOAD_URL_PATTERN.search(url)
    if not m:
        return None
    version_id = int(m.group(1))
    params = parse_qs(urlparse(url).query)
    return {
        "model_version_id": version_id,
        "type_hint": params.get("type", [None])[0],
        "format": params.get("format", [None])[0],
    }


def is_model_download_url(url: str) -> bool:
    """URLがCivitaiのモデルダウンロードURLかどうか判定"""
    return DOWNLOAD_URL_PATTERN.search(url) is not None


def extract_version_id(url: str) -> int | None:
    """ダウンロードURLからversion_idを抽出"""
    m = DOWNLOAD_URL_PATTERN.search(url)
    return int(m.group(1)) if m else None


def extract_version_id_from_page_url(page_url: str) -> int | None:
    """ページURLのクエリパラメータからmodelVersionIdを抽出"""
    m = _PAGE_VERSION_PATTERN.search(page_url)
    return int(m.group(1)) if m else None


def extract_model_id_from_page_url(page_url: str) -> int | None:
    """ページURLからモデルIDを抽出"""
    m = _PAGE_MODEL_PATTERN.search(page_url)
    return int(m.group(1)) if m else None


def is_model_extension(filename: str) -> bool:
    """ファイル名がモデルファイルの拡張子を持つか判定"""
    if not filename:
        return False
    lower = filename.lower()
    for ext in _MODEL_EXTENSIONS:
        if lower.endswith(ext):
            return True
    return False


def is_non_model_extension(filename: str) -> bool:
    """ファイル名が明らかに非モデルファイルの拡張子を持つか判定"""
    if not filename:
        return False
    lower = filename.lower()
    for ext in _NON_MODEL_EXTENSIONS:
        if lower.endswith(ext):
            return True
    return False
