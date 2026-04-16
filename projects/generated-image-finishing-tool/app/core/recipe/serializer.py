from __future__ import annotations

import json
from pathlib import Path

from app.core.recipe.models import Recipe


class RecipeSerializer:
    @staticmethod
    def save(recipe: Recipe, path: Path) -> None:
        recipe.touch()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(recipe.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
