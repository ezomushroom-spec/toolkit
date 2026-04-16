from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.errors.codes import ErrorCode
from app.core.errors.exceptions import AppError


@dataclass(frozen=True, slots=True)
class ParameterSchema:
    key: str
    value_type: type
    default: Any
    minimum: float | int | None
    maximum: float | int | None
    label: str
    description: str
    warn_threshold: float | int | None = None

    def validate(self, value: Any) -> None:
        if self.value_type is bool:
            if not isinstance(value, bool):
                raise AppError(ErrorCode.RECIPE_PARAM_MISSING, f"{self.label} は真偽値で指定してください。")
            return
        if self.value_type is int:
            if not isinstance(value, int):
                raise AppError(ErrorCode.RECIPE_PARAM_MISSING, f"{self.label} は整数で指定してください。")
        elif self.value_type is float:
            if not isinstance(value, (int, float)):
                raise AppError(ErrorCode.RECIPE_PARAM_MISSING, f"{self.label} は数値で指定してください。")
        if self.minimum is not None and value < self.minimum:
            raise AppError(ErrorCode.RECIPE_PARAM_MISSING, f"{self.label} は {self.minimum} 以上で指定してください。")
        if self.maximum is not None and value > self.maximum:
            raise AppError(ErrorCode.RECIPE_PARAM_MISSING, f"{self.label} は {self.maximum} 以下で指定してください。")


STEP_SCHEMAS: dict[str, list[ParameterSchema]] = {
    "color_smoothing": [
        ParameterSchema("strength", float, 0.32, 0.0, 1.0, "補正の強さ", "色むらをどれだけ抑えるか", 0.8),
        ParameterSchema("radius", int, 9, 1, 64, "影響範囲", "どの広さのムラまで整えるか", 32),
        ParameterSchema("preserve_edges", bool, True, None, None, "輪郭を保護", "線や境界をできるだけ守る"),
        ParameterSchema("tone_protect", float, 0.68, 0.0, 1.0, "陰影保護", "自然な陰影を残す度合い", 0.9),
    ],
    "blend_softening": [
        ParameterSchema("strength", float, 0.22, 0.0, 1.0, "なじませ強度", "境界のやわらかさ", 0.7),
        ParameterSchema("radius", int, 4, 1, 32, "なじませ範囲", "ぼかしが及ぶ広さ", 16),
        ParameterSchema("preserve_edges", bool, True, None, None, "輪郭を保護", "輪郭や主線を崩れにくくする"),
    ],
    "tone_smoothing": [
        ParameterSchema("strength", float, 0.24, 0.0, 1.0, "整える強さ", "濃淡のつながり補正量", 0.75),
        ParameterSchema("blend_amount", float, 0.28, 0.0, 1.0, "なじませ量", "段差の丸め込み量", 0.8),
        ParameterSchema("contrast_protect", float, 0.72, 0.0, 1.0, "コントラスト保護", "必要な差を残す度合い", 0.9),
    ],
    "brightness_adjust": [
        ParameterSchema("strength", float, 0.04, -1.0, 1.0, "明るさ", "全体の明るさを補助的に調整する", 0.35),
    ],
    "saturation_adjust": [
        ParameterSchema("strength", float, 0.03, -1.0, 1.0, "彩度", "色の鮮やかさを調整する", 0.3),
    ],
}


STEP_LABELS = {
    "color_smoothing": "色むら補正",
    "blend_softening": "ぼかし系なじませ",
    "tone_smoothing": "濃淡なじませ",
    "brightness_adjust": "明度補正",
    "saturation_adjust": "彩度補正",
}

STEP_DESCRIPTIONS = {
    "color_smoothing": "広い面のまだらな色むらを整えます。",
    "blend_softening": "塗りの境目やザラつきをやわらげます。",
    "tone_smoothing": "不自然な濃淡の段差をなじませます。",
    "brightness_adjust": "全体の明るさを補助的に調整します。",
    "saturation_adjust": "色の鮮やかさを整えます。",
}


def build_default_params(step_type: str) -> dict[str, Any]:
    return {schema.key: schema.default for schema in STEP_SCHEMAS[step_type]}


def validate_step_params(step_type: str, params: dict[str, Any]) -> dict[str, Any]:
    if step_type not in STEP_SCHEMAS:
        raise AppError(ErrorCode.RECIPE_INVALID_TYPE, f"未対応の工程です: {step_type}")
    validated: dict[str, Any] = {}
    for schema in STEP_SCHEMAS[step_type]:
        if schema.key not in params:
            raise AppError(ErrorCode.RECIPE_PARAM_MISSING, f"{schema.label} が不足しています。")
        schema.validate(params[schema.key])
        validated[schema.key] = params[schema.key]
    return validated
