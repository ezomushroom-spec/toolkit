from __future__ import annotations

import json
from pathlib import Path

from app.core.errors.codes import ErrorCode
from app.core.errors.exceptions import AppError
from app.core.recipe.models import Recipe, RecipeStep
from app.core.recipe.schema import validate_step_params


class RecipeLoader:
    @staticmethod
    def load(path: Path) -> Recipe:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise AppError(ErrorCode.INPUT_FILE_NOT_FOUND, "レシピファイルを開けませんでした。", str(path)) from exc
        except json.JSONDecodeError as exc:
            raise AppError(ErrorCode.RECIPE_VERSION_UNSUPPORTED, "レシピファイルの形式が不正です。", str(path)) from exc

        if not isinstance(payload, dict):
            raise AppError(ErrorCode.RECIPE_VERSION_UNSUPPORTED, "レシピファイルの形式が不正です。", str(path))

        version = payload.get("version", 0)
        if version != 1:
            raise AppError(ErrorCode.RECIPE_VERSION_UNSUPPORTED, "未対応のレシピ形式です。", str(path))

        steps: list[RecipeStep] = []
        for item in payload.get("steps", []):
            if not isinstance(item, dict):
                raise AppError(ErrorCode.RECIPE_INVALID_TYPE, "工程定義の形式が不正です。", str(path))
            step_type = item.get("step_type")
            step_id = item.get("step_id")
            if not step_type or not step_id:
                raise AppError(ErrorCode.RECIPE_PARAM_MISSING, "工程に必要な情報が不足しています。", str(path))
            steps.append(
                RecipeStep(
                    step_id=step_id,
                    step_type=step_type,
                    enabled=bool(item.get("enabled", True)),
                    params=validate_step_params(step_type, item.get("params", {})),
                )
            )

        recipe_id = payload.get("recipe_id")
        recipe_name = payload.get("recipe_name")
        if not recipe_id or not recipe_name:
            raise AppError(ErrorCode.RECIPE_PARAM_MISSING, "レシピに必要な情報が不足しています。", str(path))

        return Recipe(
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            version=version,
            description=payload.get("description", ""),
            steps=steps,
            created_at=payload.get("created_at", ""),
            updated_at=payload.get("updated_at", ""),
            meta=payload.get("meta", {"app_recipe_format": 1, "notes": ""}),
        )
