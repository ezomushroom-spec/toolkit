"""
テキスト/矢印/ラベル描画
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Windowsフォントパス候補
_FONT_CANDIDATES = [
    "C:/Windows/Fonts/BIZ-UDGothicR.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/YuGothR.ttc",
]


def _find_font_path() -> str | None:
    for fp in _FONT_CANDIDATES:
        if Path(fp).exists():
            return fp
    return None


_DEFAULT_FONT_PATH = _find_font_path()


@dataclass
class TextConfig:
    """テキストオーバーレイ設定"""

    # 属性ラベル（比較系の左右下部）
    label_texts: list[str] = field(default_factory=list)   # 各セルのラベル（空文字=非表示）
    label_position: str = "bottom"   # "top" | "bottom"
    label_bg_opacity: float = 0.6
    label_font_size: int = 24
    label_color: str = "#FFFFFF"

    # タイトルバー（画像全体の上部/下部）
    title_text: str = ""
    title_position: str = "top"      # "top" | "bottom"
    title_font_size: int = 32
    title_color: str = "#FFFFFF"
    title_bg_opacity: float = 0.7

    # 矢印・記号（比較系中央）
    arrow_text: str = ""             # "▶" | "→" | "VS" | "" (空=非表示)
    arrow_font_size: int = 64
    arrow_shadow: bool = True
    arrow_color: str = "#FFFFFF"


class TextOverlayRenderer:
    """PIL ImageDraw を使ったテキスト描画"""

    def __init__(self):
        self._font_cache: dict[tuple, ImageFont.FreeTypeFont] = {}

    def apply(self, canvas: Image.Image, config: TextConfig) -> Image.Image:
        """label → title → arrow の順で描画し、結果を返す"""
        result = canvas.copy()
        # ラベル帯
        if config.label_texts:
            result = self._draw_label_bands(result, config)
        # タイトルバー
        if config.title_text:
            result = self._draw_title_bar(result, config)
        # 矢印
        if config.arrow_text:
            result = self._draw_arrow(result, config)
        return result

    # ------------------------------------------------------------------
    # ラベル帯（比較系の各セル下部）
    # ------------------------------------------------------------------

    def _draw_label_bands(self, canvas: Image.Image, config: TextConfig) -> Image.Image:
        """各セルの下部/上部に半透明帯+テキストを描画"""
        if not config.label_texts:
            return canvas

        W, H = canvas.size
        n = len(config.label_texts)
        cell_w = W // n

        font = self._get_font(config.label_font_size)
        label_h = config.label_font_size + 16

        canvas_rgba = canvas.convert("RGBA")
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for i, text in enumerate(config.label_texts):
            if not text:
                continue
            x0 = i * cell_w
            x1 = x0 + cell_w if i < n - 1 else W
            if config.label_position == "bottom":
                y0 = H - label_h
                y1 = H
            else:
                y0 = 0
                y1 = label_h

            opacity = int(config.label_bg_opacity * 255)
            draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, opacity))

            # テキスト中央揃え
            text_color = _hex_to_rgba(config.label_color)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = x0 + (x1 - x0 - tw) // 2
            ty = y0 + (label_h - th) // 2
            draw.text((tx, ty), text, fill=text_color, font=font)

        composite = Image.alpha_composite(canvas_rgba, overlay)
        return composite.convert("RGB")

    # ------------------------------------------------------------------
    # タイトルバー（画像全体）
    # ------------------------------------------------------------------

    def _draw_title_bar(self, canvas: Image.Image, config: TextConfig) -> Image.Image:
        W, H = canvas.size
        font = self._get_font(config.title_font_size)
        bar_h = config.title_font_size + 20

        canvas_rgba = canvas.convert("RGBA")
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        if config.title_position == "top":
            y0, y1 = 0, bar_h
        else:
            y0, y1 = H - bar_h, H

        opacity = int(config.title_bg_opacity * 255)
        if opacity > 0:
            draw.rectangle([0, y0, W, y1], fill=(0, 0, 0, opacity))

        text_color = _hex_to_rgba(config.title_color)
        bbox = draw.textbbox((0, 0), config.title_text, font=font)
        tw = bbox[2] - bbox[0]
        tx = (W - tw) // 2
        ty = y0 + (bar_h - (bbox[3] - bbox[1])) // 2
        draw.text((tx, ty), config.title_text, fill=text_color, font=font)

        composite = Image.alpha_composite(canvas_rgba, overlay)
        return composite.convert("RGB")

    # ------------------------------------------------------------------
    # 矢印・記号
    # ------------------------------------------------------------------

    def _draw_arrow(self, canvas: Image.Image, config: TextConfig) -> Image.Image:
        W, H = canvas.size
        font = self._get_font(config.arrow_font_size)

        canvas_rgba = canvas.convert("RGBA")
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        text = config.arrow_text
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (W - tw) // 2
        ty = (H - th) // 2

        if config.arrow_shadow:
            # 影（オフセット2px, 半透明黒）
            draw.text((tx + 2, ty + 2), text, fill=(0, 0, 0, 180), font=font)
        text_color = _hex_to_rgba(config.arrow_color)
        draw.text((tx, ty), text, fill=text_color, font=font)

        composite = Image.alpha_composite(canvas_rgba, overlay)
        return composite.convert("RGB")

    # ------------------------------------------------------------------
    # フォントキャッシュ
    # ------------------------------------------------------------------

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        key = (size,)
        if key not in self._font_cache:
            if _DEFAULT_FONT_PATH:
                try:
                    self._font_cache[key] = ImageFont.truetype(_DEFAULT_FONT_PATH, size)
                    return self._font_cache[key]
                except Exception:
                    pass
            self._font_cache[key] = ImageFont.load_default()
        return self._font_cache[key]


# ------------------------------------------------------------------
# ユーティリティ
# ------------------------------------------------------------------

def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple:
    """#RRGGBB -> (R, G, B, A)"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b, alpha)


def hex_to_rgb(hex_color: str) -> tuple:
    """#RRGGBB -> (R, G, B)"""
    r, g, b, _ = _hex_to_rgba(hex_color)
    return (r, g, b)
