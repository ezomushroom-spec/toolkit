"""
プリセット定義・レジストリ
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParameterDef:
    """プリセットパラメータ定義"""
    name: str
    type: str          # "int" | "float" | "color" | "bool" | "choice" | "str"
    default: Any
    label: str = ""
    min: Any = None
    max: Any = None
    choices: list | None = None

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "ParameterDef":
        return cls(
            name=name,
            type=data["type"],
            default=data["default"],
            label=data.get("label", name),
            min=data.get("min"),
            max=data.get("max"),
            choices=data.get("choices"),
        )

    def validate(self, value: Any) -> Any:
        """値を検証し、範囲外の場合はクランプして返す"""
        if self.type == "int":
            v = int(value)
            if self.min is not None:
                v = max(self.min, v)
            if self.max is not None:
                v = min(self.max, v)
            return v
        elif self.type == "float":
            v = float(value)
            if self.min is not None:
                v = max(float(self.min), v)
            if self.max is not None:
                v = min(float(self.max), v)
            return v
        elif self.type == "color":
            s = str(value)
            if not s.startswith("#"):
                s = "#" + s
            return s[:7].upper()
        elif self.type == "bool":
            return bool(value)
        elif self.type == "choice":
            if self.choices and value not in self.choices:
                return self.default
            return value
        elif self.type == "str":
            return str(value)
        return value


@dataclass
class PresetDef:
    """プリセット定義"""
    name: str
    display_name: str
    category: str          # "comparison" | "grid"
    min_images: int
    max_images: int
    parameters: dict[str, ParameterDef] = field(default_factory=dict)
    text_overlay_config: dict = field(default_factory=dict)

    def get_defaults(self) -> dict:
        """全パラメータのデフォルト値dictを返す"""
        return {name: param.default for name, param in self.parameters.items()}

    def validate_params(self, params: dict) -> dict:
        """パラメータを検証し、不足分をデフォルトで補完して返す"""
        defaults = self.get_defaults()
        result = {}
        for name, param_def in self.parameters.items():
            value = params.get(name, defaults[name])
            result[name] = param_def.validate(value)
        return result

    def supports_image_count(self, count: int) -> bool:
        """指定枚数に対応しているか"""
        return self.min_images <= count <= self.max_images

    @classmethod
    def from_json(cls, data: dict) -> "PresetDef":
        params = {}
        for pname, pdata in data.get("parameters", {}).items():
            params[pname] = ParameterDef.from_dict(pname, pdata)
        return cls(
            name=data["name"],
            display_name=data["display_name"],
            category=data["category"],
            min_images=data["min_images"],
            max_images=data["max_images"],
            parameters=params,
            text_overlay_config=data.get("text_overlay", {}),
        )

    def to_json(self) -> dict:
        params = {}
        for pname, pdef in self.parameters.items():
            entry: dict = {"type": pdef.type, "default": pdef.default, "label": pdef.label}
            if pdef.min is not None:
                entry["min"] = pdef.min
            if pdef.max is not None:
                entry["max"] = pdef.max
            if pdef.choices is not None:
                entry["choices"] = pdef.choices
            params[pname] = entry
        return {
            "name": self.name,
            "display_name": self.display_name,
            "category": self.category,
            "min_images": self.min_images,
            "max_images": self.max_images,
            "parameters": params,
            "text_overlay": self.text_overlay_config,
        }


class PresetRegistry:
    """プリセットの登録・検索を管理するレジストリ"""

    def __init__(self):
        self._presets: dict[str, PresetDef] = {}

    def load_builtin(self) -> None:
        """presets/ 配下の JSON をソース・オブ・トゥルースとして読み込む."""
        presets_dir = Path(__file__).resolve().parent.parent / "presets"
        if not presets_dir.is_dir():
            raise FileNotFoundError(
                f"Preset directory not found: {presets_dir}. "
                "JSON 定義が存在しないためプリセットを読み込めません。"
            )

        self.load_from_dir(presets_dir)
        if not self._presets:
            raise RuntimeError(
                f"プリセット JSON を {presets_dir} から読み込めませんでした。"
            )

    def load_from_dir(self, path: Path) -> None:
        """指定ディレクトリのJSONプリセットを読み込む"""
        if not path.is_dir():
            return
        for json_file in sorted(path.glob("*.json")):
            try:
                with json_file.open(encoding="utf-8") as f:
                    data = json.load(f)
                preset = PresetDef.from_json(data)
                self._presets[preset.name] = preset
            except Exception as e:
                print(f"プリセット読み込みエラー ({json_file.name}): {e}")

    def get(self, name: str) -> PresetDef | None:
        return self._presets.get(name)

    def get_all(self) -> list[PresetDef]:
        return list(self._presets.values())

    def get_by_category(self, category: str) -> list[PresetDef]:
        return [p for p in self._presets.values() if p.category == category]

    def get_for_image_count(self, count: int) -> list[PresetDef]:
        """画像枚数に対応したプリセット一覧を返す"""
        return [p for p in self._presets.values() if p.supports_image_count(count)]

    def save_custom(self, preset: PresetDef, save_dir: Path) -> None:
        """カスタムプリセットをJSONファイルとして保存"""
        save_dir.mkdir(parents=True, exist_ok=True)
        out_path = save_dir / f"{preset.name}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(preset.to_json(), f, ensure_ascii=False, indent=2)
        self._presets[preset.name] = preset

    def remove(self, name: str) -> None:
        self._presets.pop(name, None)

    def __len__(self) -> int:
        return len(self._presets)
