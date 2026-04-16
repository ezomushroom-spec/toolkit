"""
出力・命名管理・CSV・履歴
"""
from __future__ import annotations
import csv
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image, ImageFilter

if TYPE_CHECKING:
    from core.presets import PresetDef
    from core.layout_engine import LayoutEngine
    from core.text_overlay import TextConfig

# 出力サイズプリセット
OUTPUT_SIZE_PRESETS: dict[str, tuple[int, int]] = {
    "Pixiv標準 (1200×900)": (1200, 900),
    "Pixiv縦型 (900×1200)": (900, 1200),
    "Pixiv正方形 (1200×1200)": (1200, 1200),
    "Twitter/X (1200×675)": (1200, 675),
}


@dataclass
class ExportRecord:
    """エクスポート履歴の1レコード"""
    record_id: str
    work_id: str
    preset_name: str
    variant: int
    output_path: Path
    created_at: datetime
    source_image_paths: list[Path]
    tags: list[str] = field(default_factory=list)
    output_size: tuple[int, int] = (1200, 900)
    parameters: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "work_id": self.work_id,
            "preset_name": self.preset_name,
            "variant": self.variant,
            "output_path": str(self.output_path),
            "created_at": self.created_at.isoformat(),
            "source_image_paths": [str(p) for p in self.source_image_paths],
            "tags": self.tags,
            "output_size": list(self.output_size),
            "parameters": self.parameters,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExportRecord":
        return cls(
            record_id=data["record_id"],
            work_id=data["work_id"],
            preset_name=data["preset_name"],
            variant=data["variant"],
            output_path=Path(data["output_path"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            source_image_paths=[Path(p) for p in data.get("source_image_paths", [])],
            tags=data.get("tags", []),
            output_size=tuple(data.get("output_size", [1200, 900])),
            parameters=data.get("parameters", {}),
        )


class Exporter:
    """エクスポート処理・履歴管理"""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path.home() / "Pictures" / "NTS_Output"
        self.history: list[ExportRecord] = []
        self._variant_counters: dict[str, int] = {}  # work_id+preset -> variant番号
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # エクスポート
    # ------------------------------------------------------------------

    def export_single(
        self,
        image: Image.Image,
        preset_name: str,
        work_id: str,
        source_paths: list[Path],
        tags: list[str] | None = None,
        params: dict | None = None,
        quality: int = 92,
        output_dir: Path | None = None,
    ) -> ExportRecord:
        """1枚エクスポート"""
        save_dir = output_dir or self.output_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        variant = self._next_variant(work_id, preset_name)
        filename = f"{work_id}_{preset_name}_{variant:03d}.jpg"
        output_path = save_dir / filename

        img_rgb = image.convert("RGB")
        img_rgb.save(str(output_path), "JPEG", quality=quality, optimize=True)

        record = ExportRecord(
            record_id=str(uuid.uuid4()),
            work_id=work_id,
            preset_name=preset_name,
            variant=variant,
            output_path=output_path,
            created_at=datetime.now(),
            source_image_paths=source_paths or [],
            tags=tags or [],
            output_size=(image.width, image.height),
            parameters=params or {},
        )
        self.history.append(record)
        return record

    def export_all_presets(
        self,
        images: list[Image.Image],
        engine: "LayoutEngine",
        presets: list["PresetDef"],
        work_id: str,
        output_size: tuple[int, int],
        text_config: "TextConfig | None" = None,
        source_paths: list[Path] | None = None,
        tags: list[str] | None = None,
        params_per_preset: dict[str, dict] | None = None,
        output_dir: Path | None = None,
    ) -> list[ExportRecord]:
        """対応するプリセット全種を一括エクスポート"""
        records: list[ExportRecord] = []
        for preset in presets:
            if not preset.supports_image_count(len(images)):
                continue
            try:
                p = (params_per_preset or {}).get(preset.name, preset.get_defaults())
                result = engine.compose(preset, images, p, output_size, text_config)
                record = self.export_single(
                    result, preset.name, work_id,
                    source_paths or [], tags,
                    p, output_dir=output_dir,
                )
                records.append(record)
            except Exception as e:
                print(f"エクスポートエラー ({preset.name}): {e}")
        return records

    # ------------------------------------------------------------------
    # CSV出力
    # ------------------------------------------------------------------

    def export_csv(self, output_path: Path) -> None:
        """履歴をCSVファイルに書き出す"""
        columns = [
            "work_id", "preset", "variant", "output_file",
            "created_at", "source_images", "tags",
            "output_width", "output_height",
        ]
        with output_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for rec in self.history:
                writer.writerow({
                    "work_id": rec.work_id,
                    "preset": rec.preset_name,
                    "variant": rec.variant,
                    "output_file": str(rec.output_path),
                    "created_at": rec.created_at.isoformat(),
                    "source_images": "|".join(str(p) for p in rec.source_image_paths),
                    "tags": "|".join(rec.tags),
                    "output_width": rec.output_size[0],
                    "output_height": rec.output_size[1],
                })

    # ------------------------------------------------------------------
    # 履歴保存・読み込み
    # ------------------------------------------------------------------

    def save_history(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(
                {"history": [r.to_dict() for r in self.history]},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def load_history(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            self.history = [ExportRecord.from_dict(d) for d in data.get("history", [])]
        except Exception as e:
            print(f"履歴読み込みエラー: {e}")

    # ------------------------------------------------------------------
    # work_id生成・バリアント管理
    # ------------------------------------------------------------------

    def generate_work_id(self) -> str:
        now = datetime.now()
        return f"nts_{now.strftime('%Y%m%d_%H%M%S')}"

    def _next_variant(self, work_id: str, preset_name: str) -> int:
        key = f"{work_id}_{preset_name}"
        self._variant_counters[key] = self._variant_counters.get(key, 0) + 1
        return self._variant_counters[key]

    # ------------------------------------------------------------------
    # Phase 3: コントラスト警告
    # ------------------------------------------------------------------

    def check_contrast_warning(
        self,
        image: Image.Image,
        preview_size: int = 184,
    ) -> list[tuple[int, int, int, int]]:
        """縮小後にコントラストが低下する領域を返す [(x,y,w,h), ...]"""
        W, H = image.size
        scale = preview_size / max(W, H)

        small = image.copy()
        small.thumbnail((preview_size, preview_size), Image.LANCZOS)
        sw, sh = small.size

        # ラプラシアンフィルタでエッジ検出
        gray_small = small.convert("L")
        arr = np.array(gray_small, dtype=np.float32)
        lap = cv2_laplacian(arr)

        # 低コントラスト領域（エッジが少ない）をブロック単位で検出
        block_size = max(1, preview_size // 8)
        low_contrast_regions: list[tuple[int, int, int, int]] = []

        for by in range(0, sh, block_size):
            for bx in range(0, sw, block_size):
                block = lap[by:by + block_size, bx:bx + block_size]
                if block.size > 0 and float(block.std()) < 5.0:
                    # 元画像座標に変換
                    x0 = int(bx / scale)
                    y0 = int(by / scale)
                    bw = int(block_size / scale)
                    bh = int(block_size / scale)
                    low_contrast_regions.append((x0, y0, bw, bh))

        return low_contrast_regions


def cv2_laplacian(arr: np.ndarray) -> np.ndarray:
    """cv2 ラプラシアン（cv2が使用可能な場合のみ）"""
    try:
        import cv2
        return cv2.Laplacian(arr, cv2.CV_32F)
    except Exception:
        return arr
