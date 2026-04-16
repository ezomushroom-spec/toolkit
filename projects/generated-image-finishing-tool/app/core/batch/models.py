from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class BatchItemResult:
    source_path: Path
    output_path: Path | None
    success: bool
    message: str


@dataclass(slots=True)
class BatchResult:
    processed: int = 0
    successes: list[BatchItemResult] = field(default_factory=list)
    failures: list[BatchItemResult] = field(default_factory=list)
    cancelled: bool = False
