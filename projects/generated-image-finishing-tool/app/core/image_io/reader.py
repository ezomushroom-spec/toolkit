from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from app.core.errors.codes import ErrorCode
from app.core.errors.exceptions import AppError


class ImageReader:
    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

    @classmethod
    def read(cls, path: Path) -> np.ndarray:
        if not path.exists():
            raise AppError(ErrorCode.INPUT_FILE_NOT_FOUND, "画像ファイルが見つかりません。", str(path), "ファイルの場所を確認してください。")
        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise AppError(ErrorCode.INPUT_UNSUPPORTED_FORMAT, "未対応の画像形式です。", str(path), "PNG、JPEG、WebP を選んでください。")
        try:
            image = Image.open(path).convert("RGB")
        except OSError as exc:
            raise AppError(ErrorCode.INPUT_DECODE_FAILED, "画像を読み込めませんでした。", str(path), "破損していないか確認してください。") from exc
        return np.array(image)
