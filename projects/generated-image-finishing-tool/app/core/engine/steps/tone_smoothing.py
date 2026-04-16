from __future__ import annotations

import cv2
import numpy as np

from app.core.engine.base_step import BaseStepExecutor
from app.core.recipe.schema import validate_step_params


class ToneSmoothingStep(BaseStepExecutor):
    step_type = "tone_smoothing"

    def validate_params(self, params: dict) -> dict:
        return validate_step_params(self.step_type, params)

    def apply(self, image: np.ndarray, params: dict, context) -> np.ndarray:
        params = self.validate_params(params)
        alpha = float(params["strength"])
        blend_amount = float(params["blend_amount"])
        protected = float(params["contrast_protect"])

        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB).astype(np.float32)
        l_channel, a_channel, b_channel = cv2.split(lab)

        sigma = 2.5 + blend_amount * 5.5
        blurred_l = cv2.GaussianBlur(l_channel, (0, 0), sigmaX=sigma, sigmaY=sigma)

        grad_x = cv2.Sobel(l_channel, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(l_channel, cv2.CV_32F, 0, 1, ksize=3)
        gradient = cv2.magnitude(grad_x, grad_y)
        gradient_norm = gradient / max(1.0, float(gradient.max()))

        # 強い輪郭では効きを下げ、ゆるい段差では効きを上げる。
        soft_band = np.clip(1.0 - gradient_norm * (0.8 + protected * 0.2), 0.0, 1.0)
        target_mask = cv2.GaussianBlur(soft_band, (0, 0), max(0.8, sigma / 2.5))

        # 段差検出量が小さすぎる場所には過剰に効かせず、中間域だけを中心に整える。
        tonal_delta = np.abs(l_channel - blurred_l)
        tonal_norm = tonal_delta / max(1.0, float(tonal_delta.max()))
        selective = np.clip((tonal_norm - 0.05) / 0.45, 0.0, 1.0)
        selective = selective * target_mask

        smooth_strength = alpha * (0.55 + blend_amount * 0.45)
        merged_l = l_channel * (1.0 - selective * smooth_strength) + blurred_l * (selective * smooth_strength)

        # コントラスト保護が高いほど元の明度を少し戻して、影の芯を残す。
        restore_weight = 0.10 + protected * 0.30
        merged_l = merged_l * (1.0 - restore_weight * gradient_norm) + l_channel * (restore_weight * gradient_norm)

        merged = cv2.merge((np.clip(merged_l, 0, 255), a_channel, b_channel))
        return cv2.cvtColor(merged.astype(np.uint8), cv2.COLOR_LAB2RGB)
