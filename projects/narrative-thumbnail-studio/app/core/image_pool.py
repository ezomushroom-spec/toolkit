"""
画像プール管理
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from PIL import Image, ExifTags, ImageOps
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

# 画像フルサイズのLRUキャッシュ (最大10枚)
_IMAGE_CACHE: dict[str, Image.Image] = {}
_IMAGE_CACHE_ORDER: list[str] = []
_CACHE_MAX = 10


def _cache_put(key: str, img: Image.Image) -> None:
    if key in _IMAGE_CACHE:
        _IMAGE_CACHE_ORDER.remove(key)
    elif len(_IMAGE_CACHE) >= _CACHE_MAX:
        oldest = _IMAGE_CACHE_ORDER.pop(0)
        del _IMAGE_CACHE[oldest]
    _IMAGE_CACHE[key] = img
    _IMAGE_CACHE_ORDER.append(key)


def _cache_get(key: str) -> Image.Image | None:
    return _IMAGE_CACHE.get(key)


class ImageEntry:
    """画像プール内の1枚の画像エントリ"""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.tags: list[str] = []
        self.exif_data: dict = {}
        self._thumbnail_pixmap: QPixmap | None = None
        self._thumbnail_size: int = 0

    # ------------------------------------------------------------------
    # サムネイル
    # ------------------------------------------------------------------

    def load_thumbnail(self, size: int = 184) -> QPixmap:
        """サムネイルQPixmapを返す（キャッシュ付き）"""
        if self._thumbnail_pixmap is not None and self._thumbnail_size == size:
            return self._thumbnail_pixmap
        try:
            with Image.open(self.path) as opened:
                img = ImageOps.exif_transpose(opened)
                img.thumbnail((size, size), Image.LANCZOS)
                img = img.convert("RGB")
            arr = img.tobytes()
            w, h = img.size
            qimg = QImage(arr, w, h, w * 3, QImage.Format.Format_RGB888)
            self._thumbnail_pixmap = QPixmap.fromImage(qimg.copy())
            self._thumbnail_size = size
        except Exception:
            self._thumbnail_pixmap = QPixmap(size, size)
            self._thumbnail_pixmap.fill()
        return self._thumbnail_pixmap

    # ------------------------------------------------------------------
    # フル解像度ロード
    # ------------------------------------------------------------------

    def load_full(self) -> Image.Image:
        """フル解像度PIL Imageを返す（LRUキャッシュ付き）"""
        key = str(self.path)
        cached = _cache_get(key)
        if cached is not None:
            return cached
        with Image.open(self.path) as opened:
            img = ImageOps.exif_transpose(opened).copy()
        _cache_put(key, img)
        return img

    # ------------------------------------------------------------------
    # タグ
    # ------------------------------------------------------------------

    def add_tag(self, tag: str) -> None:
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)

    # ------------------------------------------------------------------
    # EXIF
    # ------------------------------------------------------------------

    def load_exif(self) -> dict:
        """EXIFメタデータを読み込み、self.exif_dataにセット"""
        try:
            img = Image.open(self.path)
            exif_raw = img._getexif()  # type: ignore[attr-defined]
            if exif_raw:
                tag_map = {v: k for k, v in ExifTags.TAGS.items()}
                for tag_name in ["DateTimeOriginal", "Model", "Make"]:
                    tag_id = tag_map.get(tag_name)
                    if tag_id and tag_id in exif_raw:
                        self.exif_data[tag_name] = str(exif_raw[tag_id])
        except Exception:
            pass
        return self.exif_data

    def get_exif_summary(self) -> str:
        """EXIF概要文字列（UI表示用）"""
        parts = []
        if "Model" in self.exif_data:
            parts.append(self.exif_data["Model"])
        if "DateTimeOriginal" in self.exif_data:
            parts.append(self.exif_data["DateTimeOriginal"])
        return " | ".join(parts) if parts else ""

    # ------------------------------------------------------------------
    # シリアライズ
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "tags": self.tags,
            "exif_data": self.exif_data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ImageEntry":
        entry = cls(Path(data["path"]))
        entry.tags = data.get("tags", [])
        entry.exif_data = data.get("exif_data", {})
        return entry

    def __repr__(self) -> str:
        return f"ImageEntry({self.path.name}, tags={self.tags})"


class ImagePool(QObject):
    """画像プールの状態管理"""

    images_changed = Signal()
    image_added = Signal(int)     # インデックス
    image_removed = Signal(int)   # インデックス

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries: list[ImageEntry] = []

    # ------------------------------------------------------------------
    # 追加・削除
    # ------------------------------------------------------------------

    def add_images(self, paths: list[Path]) -> list[ImageEntry]:
        """画像を一括追加し、追加されたエントリを返す"""
        added: list[ImageEntry] = []
        existing = {str(e.path) for e in self.entries}
        for p in paths:
            p = Path(p)
            if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if not p.exists():
                continue
            if str(p) in existing:
                continue
            entry = ImageEntry(p)
            self.entries.append(entry)
            idx = len(self.entries) - 1
            added.append(entry)
            self.image_added.emit(idx)
        if added:
            self.images_changed.emit()
        return added

    def remove_image(self, index: int) -> None:
        if 0 <= index < len(self.entries):
            del self.entries[index]
            self.image_removed.emit(index)
            self.images_changed.emit()

    def remove_images(self, indices: list[int]) -> None:
        for idx in sorted(set(indices), reverse=True):
            if 0 <= idx < len(self.entries):
                del self.entries[idx]
                self.image_removed.emit(idx)
        self.images_changed.emit()

    def clear(self) -> None:
        self.entries.clear()
        self.images_changed.emit()

    # ------------------------------------------------------------------
    # 並び替え
    # ------------------------------------------------------------------

    def move_image(self, from_idx: int, to_idx: int) -> None:
        """画像の順序を変更する"""
        n = len(self.entries)
        if from_idx == to_idx or not (0 <= from_idx < n) or not (0 <= to_idx < n):
            return
        entry = self.entries.pop(from_idx)
        self.entries.insert(to_idx, entry)
        self.images_changed.emit()

    def reorder(self, new_order: list[int]) -> None:
        """インデックスリストで順序を指定して並び替える"""
        if sorted(new_order) != list(range(len(self.entries))):
            return
        self.entries = [self.entries[i] for i in new_order]
        self.images_changed.emit()

    # ------------------------------------------------------------------
    # 取得
    # ------------------------------------------------------------------

    def get_by_index(self, idx: int) -> ImageEntry | None:
        if 0 <= idx < len(self.entries):
            return self.entries[idx]
        return None

    def get_filtered(self, tags: set[str] | None = None) -> list[ImageEntry]:
        """タグフィルタリング。Noneまたは空setの場合は全件返す"""
        if not tags:
            return list(self.entries)
        return [e for e in self.entries if set(e.tags) & tags]

    def get_all_tags(self) -> list[str]:
        """プール内の全ユニークタグを返す"""
        tags: set[str] = set()
        for e in self.entries:
            tags.update(e.tags)
        return sorted(tags)

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)

    # ------------------------------------------------------------------
    # プロジェクト保存・読み込み
    # ------------------------------------------------------------------

    def to_json(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    def from_json(self, data: dict) -> None:
        self.entries.clear()
        for d in data.get("entries", []):
            try:
                entry = ImageEntry.from_dict(d)
                if entry.path.exists():
                    self.entries.append(entry)
            except Exception:
                pass
        self.images_changed.emit()
