from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseStepExecutor(ABC):
    step_type: str

    @abstractmethod
    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def apply(self, image: np.ndarray, params: dict[str, Any], context: Any) -> np.ndarray:
        raise NotImplementedError

    def estimate_cost(self, image_size: tuple[int, int], params: dict[str, Any]) -> dict[str, Any]:
        return {"width": image_size[0], "height": image_size[1], "step": self.step_type}

    def supports_gpu(self) -> bool:
        return False
