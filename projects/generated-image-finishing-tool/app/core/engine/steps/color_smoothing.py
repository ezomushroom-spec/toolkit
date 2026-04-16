from __future__ import annotations

import cv2
import numpy as np

from app.core.engine.base_step import BaseStepExecutor
from app.core.recipe.schema import validate_step_params


def _normalized_edge_mask(image: np.ndarray, sigma: float) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(grad_x, grad_y)
    blurred = cv2.GaussianBlur(magnitude, (0, 0), max(0.8, sigma / 3.0))
    normalized = blurred / max(1.0, float(blurred.max()))
    return np.repeat(normalized[:, :, None], 3, axis=2)


class ColorSmoothingStep(BaseStepExecutor):
    step_type = "color_smoothing"

    def validate_params(self, params: dict) -> dict:
        return validate_step_params(self.step_type, params)

    def apply(self, image: np.ndarray, params: dict, context) -> np.ndarray:
        params = self.validate_params(params)
        scaled_radius = max(1, round(int(params["radius"]) * getattr(context, "preview_scale", 1.0)))
        sigma = max(1.2, scaled_radius / 2.5)
        alpha = float(params["strength"])
        tone_protect = float(params["tone_protect"])

        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB).astype(np.float32)
        l_channel, a_channel, b_channel = cv2.split(lab)

        # 色むら補正は色成分を主に整え、明度は必要最小限に留める。
        smoothed_a = cv2.bilateralFilter(a_channel, d=max(3, scaled_radius * 2 + 1), sigmaColor=18 + scaled_radius * 2, sigmaSpace=12 + scaled_radius * 2)
        smoothed_b = cv2.bilateralFilter(b_channel, d=max(3, scaled_radius * 2 + 1), sigmaColor=18 + scaled_radius * 2, sigmaSpace=12 + scaled_radius * 2)
        smoothed_l = cv2.GaussianBlur(l_channel, (0, 0), sigmaX=sigma, sigmaY=sigma)

        merged_a = cv2.addWeighted(a_channel, 1.0 - alpha, smoothed_a, alpha, 0.0)
        merged_b = cv2.addWeighted(b_channel, 1.0 - alpha, smoothed_b, alpha, 0.0)
        merged_l = cv2.addWeighted(l_channel, 1.0 - alpha * 0.35, smoothed_l, alpha * 0.35, 0.0)

        merged = cv2.merge((merged_l, merged_a, merged_b))
        smoothed = cv2.cvtColor(np.clip(merged, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
        image_f = image.astype(np.float32)

        if params["preserve_edges"]:
            edge_mask = _normalized_edge_mask(image, sigma)
            protect = np.clip(edge_mask * (0.45 + tone_protect * 0.5), 0.0, 1.0)
            smoothed = smoothed * (1.0 - protect) + image_f * protect

        # 局所コントラストが高い場所では効きを弱めて、のっぺり化を抑える。
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32)
        local_mean = cv2.GaussianBlur(gray, (0, 0), max(1.0, sigma))
        local_var = cv2.GaussianBlur((gray - local_mean) ** 2, (0, 0), max(1.0, sigma))
        variance_mask = np.clip(local_var / max(1.0, float(local_var.max())), 0.0, 1.0)
        variance_mask = np.repeat(variance_mask[:, :, None], 3, axis=2)
        adaptive = np.clip(1.0 - variance_mask * (0.35 + tone_protect * 0.25), 0.2, 1.0)
        mixed = smoothed * adaptive + image_f * (1.0 - adaptive)
        return np.clip(mixed, 0, 255).astype(np.uint8)
