from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionMode(str, Enum):
    CPU_ONLY = "cpu_only"
    GPU_PREFERRED = "gpu_preferred"
    GPU_REQUIRED = "gpu_required"


@dataclass(slots=True)
class ExecutionContext:
    mode: ExecutionMode = ExecutionMode.CPU_ONLY
    is_preview: bool = False
    preview_max_size: int = 1400
    preview_scale: float = 1.0
