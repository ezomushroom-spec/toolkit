from __future__ import annotations

import cv2
import numpy as np

from app.core.engine.context import ExecutionContext
from app.core.engine.registry import StepRegistry
from app.core.recipe.models import Recipe


class RecipeExecutor:
    def __init__(self, registry: StepRegistry | None = None) -> None:
        self.registry = registry or StepRegistry()

    def run(self, image: np.ndarray, recipe: Recipe, context: ExecutionContext) -> np.ndarray:
        working = image.copy()
        if context.is_preview:
            working, scale = self._prepare_preview_image(working, context.preview_max_size)
            context.preview_scale = scale
        for step in recipe.steps:
            if not step.enabled:
                continue
            working = self.registry.get(step.step_type).apply(working, step.params, context)
        return working

    @staticmethod
    def _prepare_preview_image(image: np.ndarray, max_size: int) -> tuple[np.ndarray, float]:
        height, width = image.shape[:2]
        longest = max(width, height)
        if longest <= max_size:
            return image, 1.0
        scale = max_size / float(longest)
        resized = cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
        return resized, scale
