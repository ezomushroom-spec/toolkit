from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


def sanitize_recipe_name(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    return cleaned or "recipe"


class OutputPathResolver:
    @staticmethod
    def build_output_path(source: Path, output_dir: Path, recipe_name: str, reserved_names: Iterable[str] | None = None) -> Path:
        base = f"{source.stem}_{sanitize_recipe_name(recipe_name)}"
        extension = source.suffix or ".png"
        reserved = set(reserved_names or [])
        candidate = output_dir / f"{base}{extension}"
        index = 1
        while candidate.exists() or candidate.name in reserved:
            candidate = output_dir / f"{base}_{index}{extension}"
            index += 1
        return candidate
