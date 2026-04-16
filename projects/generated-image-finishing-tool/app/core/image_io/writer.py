from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from app.core.errors.codes import ErrorCode
from app.core.errors.exceptions import AppError


class ImageWriter:
    @staticmethod
    def write(image: np.ndarray, path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(image).save(path)
        except PermissionError as exc:
            raise AppError(ErrorCode.SAVE_PERMISSION_DENIED, "画像を保存する権限がありません。", str(path), "別の保存先を選んでください。") from exc
        except OSError as exc:
            raise AppError(ErrorCode.SAVE_PATH_INVALID, "画像を保存できませんでした。", str(path), "保存先と空き容量を確認してください。") from exc
