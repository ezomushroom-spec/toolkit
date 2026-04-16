from __future__ import annotations

from app.core.engine.base_step import BaseStepExecutor
from app.core.engine.steps.blend_softening import BlendSofteningStep
from app.core.engine.steps.brightness_adjust import BrightnessAdjustStep
from app.core.engine.steps.color_smoothing import ColorSmoothingStep
from app.core.engine.steps.saturation_adjust import SaturationAdjustStep
from app.core.engine.steps.tone_smoothing import ToneSmoothingStep


class StepRegistry:
    def __init__(self) -> None:
        self._steps: dict[str, BaseStepExecutor] = {
            "color_smoothing": ColorSmoothingStep(),
            "blend_softening": BlendSofteningStep(),
            "tone_smoothing": ToneSmoothingStep(),
            "brightness_adjust": BrightnessAdjustStep(),
            "saturation_adjust": SaturationAdjustStep(),
        }

    def get(self, step_type: str) -> BaseStepExecutor:
        return self._steps[step_type]
