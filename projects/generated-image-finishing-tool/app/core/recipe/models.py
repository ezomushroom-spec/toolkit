from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@dataclass(slots=True)
class RecipeStep:
    step_id: str
    step_type: str
    enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, step_type: str, params: dict[str, Any]) -> "RecipeStep":
        return cls(step_id=f"step-{uuid4().hex[:8]}", step_type=step_type, params=params)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Recipe:
    recipe_id: str
    recipe_name: str
    version: int = 1
    description: str = ""
    steps: list[RecipeStep] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    meta: dict[str, Any] = field(default_factory=lambda: {"app_recipe_format": 1, "notes": ""})

    @classmethod
    def create(cls, recipe_name: str = "新規レシピ") -> "Recipe":
        return cls(recipe_id=f"recipe-{uuid4().hex[:8]}", recipe_name=recipe_name)

    def touch(self) -> None:
        self.updated_at = _now_iso()

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "version": self.version,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "meta": self.meta,
        }
