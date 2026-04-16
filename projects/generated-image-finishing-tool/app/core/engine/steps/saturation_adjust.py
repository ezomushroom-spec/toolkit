from __future__ import annotations

import cv2
import numpy as np

from app.core.engine.base_step import BaseStepExecutor
from app.core.recipe.schema import validate_step_params


class SaturationAdjustStep(BaseStepExecutor):
    step_type = "saturation_adjust"

    def validate_params(self, params: dict) -> dict:
        return validate_step_params(self.step_type, params)

    def apply(self, image: np.ndarray, params: dict, context) -> np.ndarray:
        params = self.validate_params(params)
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1.0 + float(params["strength"])), 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
