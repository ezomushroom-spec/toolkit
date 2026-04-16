from __future__ import annotations

import numpy as np

from app.core.engine.base_step import BaseStepExecutor
from app.core.recipe.schema import validate_step_params


class BrightnessAdjustStep(BaseStepExecutor):
    step_type = "brightness_adjust"

    def validate_params(self, params: dict) -> dict:
        return validate_step_params(self.step_type, params)

    def apply(self, image: np.ndarray, params: dict, context) -> np.ndarray:
        params = self.validate_params(params)
        adjusted = image.astype(np.float32) + float(params["strength"]) * 255.0
        return np.clip(adjusted, 0, 255).astype(np.uint8)
