from __future__ import annotations

from dataclasses import asdict, dataclass

from app.core.engine.context import ExecutionMode


@dataclass(slots=True)
class AppSettings:
    recent_input_dir: str = ""
    recent_output_dir: str = ""
    recent_recipe_path: str = ""
    preview_scale: float = 1.0
    compare_mode: str = "after"
    execution_mode: str = ExecutionMode.CPU_ONLY.value

    def to_dict(self) -> dict:
        return asdict(self)
