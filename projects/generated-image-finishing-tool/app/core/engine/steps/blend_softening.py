from __future__ import annotations

import cv2
import numpy as np

from app.core.engine.base_step import BaseStepExecutor
from app.core.recipe.schema import validate_step_params


def _edge_protection_mask(image: np.ndarray, radius: int) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(grad_x, grad_y)
    mask = cv2.GaussianBlur(magnitude, (0, 0), max(0.8, radius / 3.5))
    mask = mask / max(1.0, float(mask.max()))
    return np.repeat(mask[:, :, None], 3, axis=2)


class BlendSofteningStep(BaseStepExecutor):
    step_type = "blend_softening"

    def validate_params(self, params: dict) -> dict:
        return validate_step_params(self.step_type, params)

    def apply(self, image: np.ndarray, params: dict, context) -> np.ndarray:
        params = self.validate_params(params)
        radius = max(1, round(int(params["radius"]) * getattr(context, "preview_scale", 1.0)))
        alpha = float(params["strength"])

        image_f = image.astype(np.float32)
        low_freq = cv2.GaussianBlur(image_f, (0, 0), sigmaX=max(0.8, radius / 2.2), sigmaY=max(0.8, radius / 2.2))
        bilateral = cv2.bilateralFilter(image, d=max(3, radius * 2 + 1), sigmaColor=20 + radius * 3, sigmaSpace=18 + radius * 3).astype(np.float32)

        # 低周波となじませ用の平滑化を混ぜて、塗り境界のザラつきだけを和らげる。
        softened = cv2.addWeighted(low_freq, 0.55, bilateral, 0.45, 0.0)
        mixed = cv2.addWeighted(image_f, 1.0 - alpha, softened, alpha, 0.0)

        if params["preserve_edges"]:
            edge_mask = _edge_protection_mask(image, radius)
            protect = np.clip(edge_mask * 0.55, 0.0, 1.0)
            mixed = mixed * (1.0 - protect) + image_f * protect

        # 微細テクスチャを少し戻して、眠い塗りになりすぎるのを防ぐ。
        detail = image_f - low_freq
        detail_return = np.clip((1.0 - alpha) * 0.35, 0.08, 0.35)
        mixed = mixed + detail * detail_return
        return np.clip(mixed, 0, 255).astype(np.uint8)
