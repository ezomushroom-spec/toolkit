"""
レイアウト生成エンジン（全13プリセット対応）
"""
from __future__ import annotations
import math
from typing import TYPE_CHECKING

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from core.text_overlay import TextConfig, TextOverlayRenderer, hex_to_rgb

if TYPE_CHECKING:
    from core.presets import PresetDef
class LayoutEngine:
    """ステートレスなレイアウト合成エンジン"""

    def __init__(self):
        self._text_renderer = TextOverlayRenderer()

        # プリセット名 → 合成メソッドのマップ
        self._composers = {
            "vsplit": self._compose_vsplit,
            "hsplit": self._compose_hsplit,
            "diagonal_wipe": self._compose_diagonal_wipe,
            "blur_border": self._compose_blur_border,
            "fade_transition": self._compose_fade_transition,
            "arrow_compare": self._compose_arrow_compare,
            "label_compare": self._compose_label_compare,
            "bg_color_split": self._compose_bg_color_split,
            "grid_2x2": self._compose_grid_2x2,
            "grid_h3": self._compose_grid_h3,
            "center_hero": self._compose_center_hero,
            "hero_top_strip": self._compose_hero_top_strip,
            "catalog": self._compose_catalog,
            "asymmetric": self._compose_asymmetric,
        }

    # ================================================================
    # 公開API
    # ================================================================

    def compose(
        self,
        preset: "PresetDef",
        images: list[Image.Image],
        params: dict,
        output_size: tuple[int, int],
        text_config: TextConfig | None = None,
        offsets: "dict[int, tuple[float, float]] | None" = None,
    ) -> Image.Image:
        """指定プリセットで画像を合成して返す"""
        composer = self._composers.get(preset.name)
        if composer is None:
            raise ValueError(f"未知のプリセット: {preset.name}")

        validated_params = preset.validate_params(params)
        _offsets: dict[int, tuple[float, float, float]] = offsets or {}
        result = composer(images, validated_params, output_size, _offsets)

        if text_config is not None:
            result = self._text_renderer.apply(result, text_config)

        return result

    # ================================================================
    # カテゴリA: 2枚比較系
    # ================================================================

    def _compose_vsplit(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """縦分割: 左右に2枚"""
        W, H = size
        ratio = params.get("split_ratio", 0.5)
        left_w = int(W * ratio)
        right_w = W - left_w

        img_l = _fit_image_with_offset(images[0], (left_w, H), *offsets.get(0, (0.0, 0.0, 1.0)))
        img_r = _fit_image_with_offset(images[1], (right_w, H), *offsets.get(1, (0.0, 0.0, 1.0)))

        canvas = Image.new("RGB", size, (0, 0, 0))
        canvas.paste(img_l, (0, 0))
        canvas.paste(img_r, (left_w, 0))

        bw = params.get("border_width", 2)
        if bw > 0:
            bc = hex_to_rgb(params.get("border_color", "#FFFFFF"))
            draw = ImageDraw.Draw(canvas)
            x = left_w - bw // 2
            draw.line([(x, 0), (x, H)], fill=bc, width=bw)

        return canvas

    def _compose_hsplit(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """横分割: 上下に2枚"""
        W, H = size
        ratio = params.get("split_ratio", 0.5)
        top_h = int(H * ratio)
        bot_h = H - top_h

        img_t = _fit_image_with_offset(images[0], (W, top_h), *offsets.get(0, (0.0, 0.0, 1.0)))
        img_b = _fit_image_with_offset(images[1], (W, bot_h), *offsets.get(1, (0.0, 0.0, 1.0)))

        canvas = Image.new("RGB", size, (0, 0, 0))
        canvas.paste(img_t, (0, 0))
        canvas.paste(img_b, (0, top_h))

        bw = params.get("border_width", 2)
        if bw > 0:
            bc = hex_to_rgb(params.get("border_color", "#FFFFFF"))
            draw = ImageDraw.Draw(canvas)
            y = top_h - bw // 2
            draw.line([(0, y), (W, y)], fill=bc, width=bw)

        return canvas

    def _compose_diagonal_wipe(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """斜めワイプ: 斜め境界線で分割"""
        W, H = size
        angle_deg = params.get("angle", 30)
        angle_rad = math.radians(angle_deg)

        # マスクサイズが必要描画領域全体をカバーする大きさで生成されるため、
        # 両画像とも (W, H) のサイズで切り出す。
        img_l = _fit_image_with_offset(images[0], size, *offsets.get(0, (0.0, 0.0, 1.0)))
        img_r = _fit_image_with_offset(images[1], size, *offsets.get(1, (0.0, 0.0, 1.0)))

        arr_l = np.array(img_l.convert("RGB"))
        arr_r = np.array(img_r.convert("RGB"))

        # 指定した比率のX座標を通る斜め分割線のオフセット計算
        ratio = params.get("split_ratio", 0.5)
        center_x = int(W * ratio)
        offset = int((H // 2) * math.tan(angle_rad))
        pts_left = np.array([
            [0, 0],
            [center_x - offset, 0],
            [center_x + offset, H],
            [0, H],
        ], dtype=np.int32)

        mask = np.zeros((H, W), dtype=np.uint8)
        cv2.fillPoly(mask, [pts_left], 255)

        result = arr_r.copy()
        result[mask > 0] = arr_l[mask > 0]

        # 境界線
        bw = params.get("border_width", 2)
        if bw > 0:
            bc_rgb = hex_to_rgb(params.get("border_color", "#FFFFFF"))
            bc_bgr = (bc_rgb[2], bc_rgb[1], bc_rgb[0])
            pt1 = (center_x - offset, 0)
            pt2 = (center_x + offset, H)
            cv2.line(result, pt1, pt2, bc_bgr, bw, lineType=cv2.LINE_AA)

        return Image.fromarray(result)

    def _compose_blur_border(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """境界ぼかし: 中央でグラデーション合成"""
        W, H = size
        fade_w = params.get("fade_width", 60)

        img_l = _fit_image_with_offset(images[0], size, *offsets.get(0, (0.0, 0.0, 1.0)))
        img_r = _fit_image_with_offset(images[1], size, *offsets.get(1, (0.0, 0.0, 1.0)))

        # グラデーションマスク生成（左］白/前景, 右］黒/背景）
        mask = _create_horizontal_gradient_mask(W, H, fade_w)
        result = Image.composite(img_l, img_r, mask)
        return result


    def _compose_fade_transition(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """フェード遷移: 幅広グラデーション合成"""
        W, H = size
        fade_w = params.get("fade_width", 120)
        # blur_borderと同じ処理、フェード幅が広い
        img_l = _fit_image_with_offset(images[0], size, *offsets.get(0, (0.0, 0.0, 1.0)))
        img_r = _fit_image_with_offset(images[1], size, *offsets.get(1, (0.0, 0.0, 1.0)))
        mask = _create_horizontal_gradient_mask(W, H, fade_w)
        return Image.composite(img_l, img_r, mask)

    def _compose_arrow_compare(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """矢印付き比較: vsplit + 中央に矢印"""
        canvas = self._compose_vsplit(images, params, size, offsets)
        arrow_style = params.get("arrow_style", "▶")
        arrow_size = params.get("arrow_size", 64)
        text_cfg = TextConfig(
            arrow_text=arrow_style,
            arrow_font_size=arrow_size,
            arrow_shadow=True,
        )
        return self._text_renderer.apply(canvas, text_cfg)

    def _compose_label_compare(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """ラベル付き比較: vsplit + 各セル下部にラベル"""
        canvas = self._compose_vsplit(images, params, size, offsets)
        label_left = params.get("label_left", "BEFORE")
        label_right = params.get("label_right", "AFTER")
        font_size = params.get("label_font_size", 24)
        bg_opacity = params.get("label_bg_opacity", 0.6)
        text_cfg = TextConfig(
            label_texts=[label_left, label_right],
            label_position="bottom",
            label_font_size=font_size,
            label_bg_opacity=bg_opacity,
        )
        return self._text_renderer.apply(canvas, text_cfg)

    def _compose_bg_color_split(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """背景色分割: 左右別背景色で対比強調"""
        W, H = size
        ratio = params.get("split_ratio", 0.5)
        left_w = int(W * ratio)
        right_w = W - left_w

        bg_l = hex_to_rgb(params.get("bg_color_left", "#1A1A2E"))
        bg_r = hex_to_rgb(params.get("bg_color_right", "#E94560"))

        canvas = Image.new("RGB", size, (0, 0, 0))
        # 左背景
        left_bg = Image.new("RGB", (left_w, H), bg_l)
        canvas.paste(left_bg, (0, 0))
        # 右背景
        right_bg = Image.new("RGB", (right_w, H), bg_r)
        canvas.paste(right_bg, (left_w, 0))

        # 画像はセルに収まるようリサイズ（透過対応: RGBAで合成）
        def _paste_fit(img, cell_w, cell_h, px, py):
            fitted = _fit_image_contain(img, (cell_w, cell_h))
            fw, fh = fitted.size
            ox = px + (cell_w - fw) // 2
            oy = py + (cell_h - fh) // 2
            if fitted.mode == "RGBA":
                canvas.paste(fitted, (ox, oy), mask=fitted.split()[3])
            else:
                canvas.paste(fitted, (ox, oy))

        _paste_fit(images[0], left_w, H, 0, 0)
        _paste_fit(images[1], right_w, H, left_w, 0)

        bw = params.get("border_width", 2)
        if bw > 0:
            bc = hex_to_rgb(params.get("border_color", "#FFFFFF"))
            draw = ImageDraw.Draw(canvas)
            x = left_w - bw // 2
            draw.line([(x, 0), (x, H)], fill=bc, width=bw)

        return canvas

    # ================================================================
    # カテゴリB: グリッド系
    # ================================================================

    def _compose_grid_2x2(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """2×2グリッド: 4枚均等配置"""
        W, H = size
        gap = params.get("gap", 4)
        bg_color = hex_to_rgb(params.get("bg_color", "#000000"))

        cell_w = (W - gap) // 2
        cell_h = (H - gap) // 2

        canvas = Image.new("RGB", size, bg_color)
        positions = [
            (0, 0),
            (cell_w + gap, 0),
            (0, cell_h + gap),
            (cell_w + gap, cell_h + gap),
        ]
        for i, (px, py) in enumerate(positions):
            if i < len(images):
                img = self._get_slot_image(images[i], (cell_w, cell_h), offsets, i)
            else:
                img = Image.new("RGB", (cell_w, cell_h), bg_color)
            canvas.paste(img, (px, py))

        return canvas

    def _compose_grid_h3(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """横3段階: 3枚横一列"""
        W, H = size
        gap = params.get("gap", 4)
        bg_color = hex_to_rgb(params.get("bg_color", "#000000"))

        cell_w = (W - gap * 2) // 3
        canvas = Image.new("RGB", size, bg_color)

        for i in range(3):
            if i < len(images):
                img = self._get_slot_image(images[i], (cell_w, H), offsets, i)
            else:
                img = Image.new("RGB", (cell_w, H), bg_color)
            px = i * (cell_w + gap)
            canvas.paste(img, (px, 0))

        return canvas

    def _compose_center_hero(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """中央主役+周囲: 中央大+周囲小"""
        W, H = size
        gap = params.get("gap", 4)
        bg_color = hex_to_rgb(params.get("bg_color", "#000000"))
        hero_ratio = params.get("hero_ratio", 0.5)

        canvas = Image.new("RGB", size, bg_color)
        n = len(images)

        if n == 3:
            # 左1 | 中央大 | 右1
            hero_w = int(W * hero_ratio)
            side_w = (W - hero_w - gap * 2) // 2
            cells = [
                (side_w, H, images[0], 0, 0, 0),
                (hero_w, H, images[1], side_w + gap, 0, 1),
                (side_w, H, images[2], side_w + gap + hero_w + gap, 0, 2),
            ]
            for cw, ch, img, px, py, slot in cells:
                if cw > 0:
                    canvas.paste(self._get_slot_image(img, (cw, ch), offsets, slot), (px, py))

        elif n == 4:
            # 左大 | 右3段
            hero_w = int(W * hero_ratio)
            right_w = W - hero_w - gap
            cell_h = (H - gap * 2) // 3
            canvas.paste(self._get_slot_image(images[0], (hero_w, H), offsets, 0), (0, 0))
            for idx in range(1, 4):
                py = (idx - 1) * (cell_h + gap)
                canvas.paste(
                    self._get_slot_image(images[idx], (right_w, cell_h), offsets, idx),
                    (hero_w + gap, py),
                )

        elif n == 5:
            # 中央大 + 四隅小
            hero_w = int(W * hero_ratio)
            hero_h = int(H * hero_ratio)
            small_w = (W - hero_w - gap) // 2
            small_h = (H - hero_h - gap) // 2

            cx = (W - hero_w) // 2
            cy = (H - hero_h) // 2
            canvas.paste(self._get_slot_image(images[0], (hero_w, hero_h), offsets, 0), (cx, cy))

            corners = [
                (0, 0, small_w, small_h),
                (W - small_w, 0, small_w, small_h),
                (0, H - small_h, small_w, small_h),
                (W - small_w, H - small_h, small_w, small_h),
            ]
            for i, (px, py, cw, ch) in enumerate(corners):
                if i + 1 < n and cw > 0 and ch > 0:
                    canvas.paste(self._get_slot_image(images[i + 1], (cw, ch), offsets, i + 1), (px, py))
        else:
            # フォールバック: カタログ型
            return self._compose_catalog(images, params, size, offsets)

        return canvas

    def _compose_hero_top_strip(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """上段主役 + 下段ストリップ: 3〜4枚"""
        W, H = size
        gap = params.get("gap", 4)
        bg_color = hex_to_rgb(params.get("bg_color", "#000000"))
        top_ratio = params.get("top_ratio", 0.66)

        canvas = Image.new("RGB", size, bg_color)
        n = len(images)
        if n < 3:
            return canvas

        top_h = int(H * top_ratio)
        bot_h = H - top_h - gap
        if bot_h <= 0:
            bot_h = max(1, H - top_h)
            gap = 0

        canvas.paste(self._get_slot_image(images[0], (W, top_h), offsets, 0), (0, 0))

        strip_count = min(3, n - 1)
        if strip_count <= 0:
            return canvas

        strip_w = (W - gap * (strip_count - 1)) // strip_count
        for idx in range(strip_count):
            slot = idx + 1
            px = idx * (strip_w + gap)
            canvas.paste(
                self._get_slot_image(images[slot], (strip_w, bot_h), offsets, slot),
                (px, top_h + gap),
            )

        return canvas

    def _compose_catalog(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """カタログ型: 2〜9枚の均等グリッド"""
        W, H = size
        gap = params.get("gap", 4)
        bg_color = hex_to_rgb(params.get("bg_color", "#000000"))
        fill_mode = params.get("fill_mode", "color")

        n = len(images)
        if n == 0:
            return Image.new("RGB", size, bg_color)

        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)

        cell_w = (W - gap * (cols - 1)) // cols
        cell_h = (H - gap * (rows - 1)) // rows

        canvas = Image.new("RGB", size, bg_color)

        for idx in range(rows * cols):
            col = idx % cols
            row = idx // cols
            px = col * (cell_w + gap)
            py = row * (cell_h + gap)

            if idx < n:
                img = self._get_slot_image(images[idx], (cell_w, cell_h), offsets, idx)
                canvas.paste(img, (px, py))
            else:
                if fill_mode in ("color", "asymmetric"):
                    fill_img = Image.new("RGB", (cell_w, cell_h), bg_color)
                    canvas.paste(fill_img, (px, py))
                # fill_mode == "text" の場合は空のまま（タイトルオーバーレイで使用）
                # "asymmetric" は旧設定互換として color と同等に扱う。

        return canvas

    def _compose_asymmetric(
        self,
        images: list[Image.Image],
        params: dict,
        size: tuple[int, int],
        offsets: dict,
    ) -> Image.Image:
        """上2下3変則: 5枚 (上段2枚 + 下段3枚)"""
        W, H = size
        gap = params.get("gap", 4)
        bg_color = hex_to_rgb(params.get("bg_color", "#000000"))
        top_ratio = params.get("top_ratio", 0.5)

        top_h = int(H * top_ratio)
        bot_h = H - top_h - gap

        top_cell_w = (W - gap) // 2
        bot_cell_w = (W - gap * 2) // 3

        canvas = Image.new("RGB", size, bg_color)

        # 上段2枚 (スロット 0, 1)
        for i in range(2):
            if i < len(images):
                img = self._get_slot_image(images[i], (top_cell_w, top_h), offsets, i)
                canvas.paste(img, (i * (top_cell_w + gap), 0))

        # 下段3枚 (スロット 2, 3, 4)
        for i in range(3):
            idx = i + 2
            if idx < len(images):
                img = self._get_slot_image(images[idx], (bot_cell_w, bot_h), offsets, idx)
                canvas.paste(img, (i * (bot_cell_w + gap), top_h + gap))

        return canvas

    # ================================================================
    # 内部ユーティリティ
    # ================================================================

    def calculate_smart_offsets(
        self,
        image: Image.Image,
        target_size: tuple[int, int],
    ) -> tuple[float, float, float]:
        """顔検出を利用して最適なオフセット (ox, oy, zoom) を計算する（顔検出機能削除に伴い中央等倍 0.0, 0.0, 1.0 を返す）"""
        return 0.0, 0.0, 1.0

    def _get_slot_image(
        self,
        image: Image.Image,
        target_size: tuple[int, int],
        offsets: dict,
        slot: int,
    ) -> Image.Image:
        """スロットのオフセットが設定されていればオフセットクロップ、なければ顔検出からオフセットを計算"""
        if slot in offsets:
            ox, oy, zoom = offsets[slot]
        else:
            ox, oy, zoom = self.calculate_smart_offsets(image, target_size)
        return _fit_image_with_offset(image, target_size, ox, oy, zoom)

    def precompute_fill_images(
        self,
        preset_name: str,
        images: list[Image.Image],
        params: dict,
        output_size: tuple[int, int],
        offsets: "dict[int, tuple[float, float, float]] | None" = None,
    ) -> "dict[int, np.ndarray]":
        """ドラッグ高速化用: 各スロットの画像をフィルサイズに事前リサイズしてキャッシュ。
        ドラッグ中はこのキャッシュへのnumpyスライスのみで済む（全方向パン対応）。
        diagonal_wipeは両スロットの画像をフルキャンバスサイズで生成する専用処理。
        ブレンド系・bg_color_split等の単純スライス不可なプリセットは空辞書を返す。"""
        W, H = output_size
        _offsets = offsets or {}

        # diagonal_wipe専用: 両スロットともフルキャンバスサイズでフィルキャッシュ生成
        if preset_name == "diagonal_wipe":
            result: dict[int, np.ndarray] = {}
            for slot in range(min(2, len(images))):
                img = images[slot].convert("RGB")
                iw, ih = img.size
                if iw == 0 or ih == 0:
                    continue
                # diagonal_wipeは常にフルキャンバスサイズで画像を準備するため、
                # target_sizeはoutput_sizeと同じ
                zoom = 1.0
                if slot in _offsets:
                    _, _, zoom = _offsets[slot]

                scale = max(W / iw, H / ih) * zoom
                new_w = max(W, int(iw * scale))
                new_h = max(H, int(ih * scale))
                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                result[slot] = np.array(img_resized, dtype=np.uint8)
            return result

        # フィルキャッシュ非対応プリセット（ブレンド・特殊合成）
        _COMPLEX_COMPOSITING_PRESETS = {
            "blur_border",     # グラデーションブレンド
            "fade_transition", # フェードブレンド
            "bg_color_split",  # 背景色分割（contain配置）
        }
        if preset_name in _COMPLEX_COMPOSITING_PRESETS:
            return {}

        bounds = self.compute_cell_bounds(preset_name, params, output_size, len(images))
        if not bounds:
            return {}

        result = {}
        for slot, (bx, by, bw, bh) in bounds.items():
            if slot >= len(images) or bw <= 0 or bh <= 0:
                continue
            # セルに収まるよりひと回り大きいサイズ（fill）にリサイズ
            img = images[slot].convert("RGB")
            iw, ih = img.size
            if iw == 0 or ih == 0:
                continue
            zoom = 1.0
            if slot in _offsets:
                _, _, zoom = _offsets[slot]

            scale = max(bw / iw, bh / ih) * zoom
            new_w = max(bw, int(iw * scale))
            new_h = max(bh, int(ih * scale))
            result[slot] = np.array(img.resize((new_w, new_h), Image.LANCZOS), dtype=np.uint8)
        return result

    def compute_diagonal_mask(
        self,
        params: dict,
        output_size: tuple[int, int],
    ) -> "np.ndarray":
        """diagonal_wipe 高速パン用 numpy バイナリマスクを生成。
        左領域が 255、右領域が 0 の (H, W) uint8 配列を返す。
        _compose_diagonal_wipe と同一ロジックなので描画結果が一致する。"""
        W, H = output_size
        angle_deg = params.get("angle", 30)
        angle_rad = math.radians(angle_deg)
        ratio = params.get("split_ratio", 0.5)
        center_x = int(W * ratio)
        offset = int((H // 2) * math.tan(angle_rad))
        pts_left = np.array([
            [0, 0],
            [center_x - offset, 0],
            [center_x + offset, H],
            [0, H],
        ], dtype=np.int32)
        mask = np.zeros((H, W), dtype=np.uint8)
        cv2.fillPoly(mask, [pts_left], 255)
        return mask


    def compute_cell_bounds(
        self,
        preset_name: str,
        params: dict,
        output_size: tuple[int, int],
        n_images: int,
    ) -> "dict[int, tuple[int, int, int, int]]":
        """各セルの矩形 (x, y, w, h) をピクセル座標で返す（ドラッグ操作用）"""
        W, H = output_size
        bounds: dict[int, tuple[int, int, int, int]] = {}

        if preset_name in ("vsplit", "arrow_compare", "label_compare"):
            ratio = params.get("split_ratio", 0.5)
            left_w = int(W * ratio)
            right_w = W - left_w
            bounds[0] = (0, 0, left_w, H)
            bounds[1] = (left_w, 0, right_w, H)

        elif preset_name == "hsplit":
            ratio = params.get("split_ratio", 0.5)
            top_h = int(H * ratio)
            bot_h = H - top_h
            bounds[0] = (0, 0, W, top_h)
            bounds[1] = (0, top_h, W, bot_h)

        elif preset_name in ("diagonal_wipe", "blur_border", "fade_transition"):
            # 全面合成のため vsplit 近似でセル境界を返す
            ratio = params.get("split_ratio", 0.5)
            left_w = int(W * ratio)
            right_w = W - left_w
            bounds[0] = (0, 0, left_w, H)
            bounds[1] = (left_w, 0, right_w, H)

        elif preset_name == "grid_2x2":
            gap = params.get("gap", 4)
            cell_w = (W - gap) // 2
            cell_h = (H - gap) // 2
            positions = [
                (0, 0), (cell_w + gap, 0),
                (0, cell_h + gap), (cell_w + gap, cell_h + gap),
            ]
            for i, (px, py) in enumerate(positions):
                bounds[i] = (px, py, cell_w, cell_h)

        elif preset_name == "grid_h3":
            gap = params.get("gap", 4)
            cell_w = (W - gap * 2) // 3
            for i in range(3):
                bounds[i] = (i * (cell_w + gap), 0, cell_w, H)

        elif preset_name == "center_hero":
            gap = params.get("gap", 4)
            hero_ratio = params.get("hero_ratio", 0.5)
            if n_images == 3:
                hero_w = int(W * hero_ratio)
                side_w = (W - hero_w - gap * 2) // 2
                bounds[0] = (0, 0, side_w, H)
                bounds[1] = (side_w + gap, 0, hero_w, H)
                bounds[2] = (side_w + gap + hero_w + gap, 0, side_w, H)
            elif n_images == 4:
                hero_w = int(W * hero_ratio)
                right_w = W - hero_w - gap
                cell_h = (H - gap * 2) // 3
                bounds[0] = (0, 0, hero_w, H)
                for idx in range(1, 4):
                    py = (idx - 1) * (cell_h + gap)
                    bounds[idx] = (hero_w + gap, py, right_w, cell_h)
            elif n_images >= 5:
                hero_w = int(W * hero_ratio)
                hero_h = int(H * hero_ratio)
                small_w = (W - hero_w - gap) // 2
                small_h = (H - hero_h - gap) // 2
                cx = (W - hero_w) // 2
                cy = (H - hero_h) // 2
                bounds[0] = (cx, cy, hero_w, hero_h)
                corners = [
                    (0, 0, small_w, small_h),
                    (W - small_w, 0, small_w, small_h),
                    (0, H - small_h, small_w, small_h),
                    (W - small_w, H - small_h, small_w, small_h),
                ]
                for i, (px, py, cw, ch) in enumerate(corners):
                    bounds[i + 1] = (px, py, cw, ch)

        elif preset_name == "hero_top_strip":
            gap = params.get("gap", 4)
            top_ratio = params.get("top_ratio", 0.66)
            top_h = int(H * top_ratio)
            bot_h = H - top_h - gap
            if bot_h <= 0:
                bot_h = max(1, H - top_h)
                gap = 0
            bounds[0] = (0, 0, W, top_h)
            strip_count = min(3, max(0, n_images - 1))
            if strip_count > 0:
                strip_w = (W - gap * (strip_count - 1)) // strip_count
                for idx in range(strip_count):
                    bounds[idx + 1] = (idx * (strip_w + gap), top_h + gap, strip_w, bot_h)

        elif preset_name == "catalog":
            n = n_images
            if n > 0:
                gap = params.get("gap", 4)
                cols = math.ceil(math.sqrt(n))
                rows = math.ceil(n / cols)
                cell_w = (W - gap * (cols - 1)) // cols
                cell_h = (H - gap * (rows - 1)) // rows
                for idx in range(n):
                    col = idx % cols
                    row = idx // cols
                    px = col * (cell_w + gap)
                    py = row * (cell_h + gap)
                    bounds[idx] = (px, py, cell_w, cell_h)

        elif preset_name == "asymmetric":
            gap = params.get("gap", 4)
            top_ratio = params.get("top_ratio", 0.5)
            top_h = int(H * top_ratio)
            bot_h = H - top_h - gap
            top_cell_w = (W - gap) // 2
            bot_cell_w = (W - gap * 2) // 3
            for i in range(2):
                bounds[i] = (i * (top_cell_w + gap), 0, top_cell_w, top_h)
            for i in range(3):
                bounds[i + 2] = (i * (bot_cell_w + gap), top_h + gap, bot_cell_w, bot_h)

        return bounds

    def compute_slot_polygons(
        self,
        preset_name: str,
        params: dict,
        output_size: tuple[int, int],
        n_images: int,
    ) -> "dict[int, list[tuple[float, float]]]":
        """各スロットの表示形状を頂点列で返す（プレビュー入力判定用）"""
        W, H = output_size

        if preset_name == "diagonal_wipe":
            angle_deg = params.get("angle", 30)
            angle_rad = math.radians(angle_deg)
            ratio = params.get("split_ratio", 0.5)
            center_x = W * ratio
            offset = (H / 2.0) * math.tan(angle_rad)
            return {
                0: [
                    (0.0, 0.0),
                    (center_x - offset, 0.0),
                    (center_x + offset, float(H)),
                    (0.0, float(H)),
                ],
                1: [
                    (center_x - offset, 0.0),
                    (float(W), 0.0),
                    (float(W), float(H)),
                    (center_x + offset, float(H)),
                ],
            }

        bounds = self.compute_cell_bounds(preset_name, params, output_size, n_images)
        polygons: dict[int, list[tuple[float, float]]] = {}
        for slot, (bx, by, bw, bh) in bounds.items():
            polygons[slot] = [
                (float(bx), float(by)),
                (float(bx + bw), float(by)),
                (float(bx + bw), float(by + bh)),
                (float(bx), float(by + bh)),
            ]
        return polygons


# ================================================================
# モジュールレベルユーティリティ
# ================================================================

def _fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """アスペクト比を保ちながら fill クロップ（中央クロップ）"""
    return ImageOps.fit(image.convert("RGB"), size, Image.LANCZOS)


def _fit_image_with_offset(
    image: Image.Image,
    size: tuple[int, int],
    ox: float = 0.0,
    oy: float = 0.0,
    zoom: float = 1.0,
) -> Image.Image:
    """アスペクト比を保ちながら fill クロップ。ox/oy: -1.0〜1.0でクロップ位置を指定（0=中央）。zoom: 拡大率（1.0=等倍）"""
    img = image.convert("RGB")
    target_w, target_h = size
    img_w, img_h = img.size
    if img_w == 0 or img_h == 0:
        return Image.new("RGB", size, (0, 0, 0))

    scale = max(target_w / img_w, target_h / img_h)
    scale *= zoom
    new_w = max(target_w, int(img_w * scale))
    new_h = max(target_h, int(img_h * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)

    extra_x = new_w - target_w
    extra_y = new_h - target_h

    # ox: -1=左端, 0=中央, 1=右端
    crop_x = int((ox + 1.0) / 2.0 * extra_x)
    crop_y = int((oy + 1.0) / 2.0 * extra_y)
    crop_x = max(0, min(crop_x, extra_x))
    crop_y = max(0, min(crop_y, extra_y))

    return img.crop((crop_x, crop_y, crop_x + target_w, crop_y + target_h))


def _fit_image_contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """アスペクト比を保ちながら contain（黒帯なしで収まるサイズ）"""
    img = image.convert("RGB")
    img.thumbnail(size, Image.LANCZOS)
    return img


def _create_horizontal_gradient_mask(
    W: int, H: int, fade_w: int
) -> Image.Image:
    """左=白(255)、右=黒(0)の水平グラデーションマスクを生成"""
    center_x = W // 2
    half_fade = fade_w // 2

    arr = np.zeros((H, W), dtype=np.uint8)
    # 左半分（フェード開始より左）: 白
    left_end = max(0, center_x - half_fade)
    arr[:, :left_end] = 255

    # グラデーション部分
    grad_start = center_x - half_fade
    grad_end = center_x + half_fade
    grad_start = max(0, grad_start)
    grad_end = min(W, grad_end)
    actual_w = grad_end - grad_start
    if actual_w > 0:
        gradient = np.linspace(255, 0, actual_w, dtype=np.uint8)
        arr[:, grad_start:grad_end] = gradient[np.newaxis, :]

    # 右半分: 0（既に0）

    return Image.fromarray(arr, mode="L")
