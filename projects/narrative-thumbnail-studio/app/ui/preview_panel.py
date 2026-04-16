"""
中央パネル: メインプレビュー + 縮小プレビュー（Pixivシミュレーション）
"""
from __future__ import annotations

import numpy as np
from PIL import Image
from PySide6.QtCore import Qt, Signal, QPointF, QTimer, QRectF
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QFont, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
import math


def pil_to_qpixmap(pil_image: Image.Image) -> QPixmap:
    """PIL Image -> QPixmap 変換"""
    img_rgb = pil_image.convert("RGB")
    arr = np.array(img_rgb)
    h, w, c = arr.shape
    data = arr.tobytes()
    qimg = QImage(data, w, h, w * c, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg.copy())


class ClippedPixmapItem(QGraphicsPixmapItem):
    """QGraphicsPixmapItem with local clipping path support for pan/zoom masking"""
    def __init__(self, pixmap: QPixmap = None, parent=None):
        if pixmap is not None:
            super().__init__(pixmap, parent)
        else:
            super().__init__(parent)
        self._clip_path: QPainterPath | None = None

    def set_clip_path(self, path: QPainterPath | None):
        self._clip_path = path
        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        if self._clip_path is not None:
            painter.save()
            painter.setClipPath(self._clip_path, Qt.ClipOperation.IntersectClip)
            super().paint(painter, option, widget)
            painter.restore()
        else:
            super().paint(painter, option, widget)


class InteractivePreview(QGraphicsView):
    """
    QGraphicsViewベースのプレビュー領域。
    描画やレイアウトの複雑なクリッピングはBackground層(QGraphicsScene::drawBackground)と
    Foreground層(QGraphicsScene::drawForeground)で行い、マウスドラッグによるオフセット調整
    (パン・ズーム) やスプリット位置調整の信号を発行する。
    画像そのものは再合成せず、QGraphicsPixmapItem の transform を変更してGPUベースで高速描画する。
    """
    split_ratio_changed = Signal(float)
    crop_offset_changed = Signal(int, float, float, float)
    drag_finished = Signal()
    reorder_requested = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        
        # UI設定
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background: #181825; border: 1px solid #3d3d5c; border-radius: 4px;")
        self.setMouseTracking(True)
        self.setMinimumSize(200, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 内部状態
        self._output_size = (1200, 900)  # 例
        self._cell_bounds: dict[int, tuple[int, int, int, int]] = {}
        self._slot_polygons: dict[int, list[tuple[float, float]]] = {}
        self._offsets: dict[int, tuple[float, float, float]] = {}
        
        # ハイクオリティな合成結果のキャッシュ (Noneの場合はインタラクティブモードで描画構築)
        self._hq_pixmap: QPixmap | None = None
        self._hq_item = self.scene_obj.addPixmap(QPixmap())
        self._hq_item.setZValue(100)
        self._hq_item.hide()
        
        # 描画元画像のキャッシュ (スロット単位)
        self._source_images: dict[int, QPixmap] = {}
        self._image_items: dict[int, ClippedPixmapItem] = {}
        
        # 操作状態
        self._drag_slot: int | None = None
        self._drag_start_pos: QPointF | None = None
        self._drag_start_offset: tuple[float, float, float] = (0.0, 0.0, 1.0)
        self._reorder_slot: int | None = None
        self._reorder_target_slot: int | None = None
        
        # 境界線ドラッグ
        self._split_mode: str | None = None
        self._split_ratio: float = 0.5
        self._split_angle: float = 30.0
        self._is_dragging_split = False

        self._wheel_timer = QTimer(self)
        self._wheel_timer.setSingleShot(True)
        self._wheel_timer.timeout.connect(self._on_wheel_stopped)
        
        # リサイズ対応
        self.scene_obj.setSceneRect(0, 0, self._output_size[0], self._output_size[1])

    def _render_rect_for_slot(self, slot: int) -> tuple[float, float, float, float]:
        bx, by, bw, bh = self._cell_bounds[slot]
        if getattr(self, "_preset_name", "") in ("diagonal_wipe", "blur_border", "fade_transition"):
            return 0.0, 0.0, float(self._output_size[0]), float(self._output_size[1])
        return float(bx), float(by), float(bw), float(bh)

    def _can_reorder(self) -> bool:
        return len(self._cell_bounds) >= 2

    def _view_scale(self) -> float:
        return max(0.001, self.transform().m11())

    def _handle_rect_for_slot(self, slot: int) -> QRectF:
        bx, by, bw, bh = self._cell_bounds[slot]
        scale = self._view_scale()
        size = min(24.0 / scale, bw * 0.35, bh * 0.35)
        size = max(size, min(bw, bh) * 0.18)
        margin = max(4.0 / scale, min(size * 0.25, 8.0 / scale))
        if self._preset_name == "diagonal_wipe" and slot in (0, 1):
            anchor_x, anchor_y = self._diagonal_handle_anchor(slot, size, margin)
            return QRectF(anchor_x, anchor_y, size, size)
        return QRectF(
            bx + bw - size - margin,
            by + margin,
            size,
            size,
        )

    def _diagonal_handle_anchor(self, slot: int, size: float, margin: float) -> tuple[float, float]:
        W, H = self._output_size
        cx = W * self._split_ratio
        angle_rad = math.radians(self._split_angle)
        offset = (H / 2.0) * math.tan(angle_rad)
        if slot == 0:
            x = cx - offset - size - margin
        else:
            x = W - size - margin
        x = max(margin, min(x, W - size - margin))
        y = margin
        return x, y

    def _slot_scene_path(self, slot: int) -> QPainterPath:
        path = QPainterPath()
        if slot in self._slot_polygons:
            polygon = self._slot_polygons[slot]
            if polygon:
                first_x, first_y = polygon[0]
                path.moveTo(first_x, first_y)
                for x, y in polygon[1:]:
                    path.lineTo(x, y)
                path.closeSubpath()
                return path

        if slot not in self._cell_bounds:
            return path

        bx, by, bw, bh = self._cell_bounds[slot]
        path.addRect(QRectF(bx, by, bw, bh))
        return path

    def _find_handle_slot(self, ix: float, iy: float) -> int | None:
        if not self._can_reorder():
            return None
        point = QPointF(ix, iy)
        for slot in self._cell_bounds:
            if self._handle_rect_for_slot(slot).contains(point):
                return slot
        return None

    def _on_wheel_stopped(self) -> None:
        self.drag_finished.emit()

    def set_cell_bounds(
        self,
        bounds: dict[int, tuple[int, int, int, int]],
        output_size: tuple[int, int],
        preset_name: str = "",
        slot_polygons: dict[int, list[tuple[float, float]]] | None = None,
    ) -> None:
        self._cell_bounds = bounds
        self._slot_polygons = slot_polygons or {}
        self._output_size = output_size
        self._preset_name = preset_name
        self.scene_obj.setSceneRect(0, 0, output_size[0], output_size[1])
        self._update_scene_transform()
        # セル境界変更は当たり判定だけでなく描画位置にも影響する。
        self._update_item_transforms()

    def update_offsets(self, offsets: dict[int, tuple[float, float, float]]) -> None:
        self._offsets = offsets
        self._update_item_transforms()

    def reset_offsets(self) -> None:
        self._offsets = {}
        self._drag_slot = None
        self._is_dragging_split = False
        self._update_item_transforms()

    def set_split_info(self, mode: str | None, ratio: float, angle: float = 30.0) -> None:
        self._split_mode = mode
        self._split_ratio = ratio
        self._split_angle = angle
        # スプリット情報の変更はクリッピングと配置の両方に影響する。
        self._update_item_transforms()
        self.viewport().update()

    def set_source_images(self, images: dict[int, Image.Image]) -> None:
        """背景操作用にオリジナル画像を登録する"""
        self._source_images.clear()
        
        # 既存のアイテムを削除
        for item in self._image_items.values():
            self.scene_obj.removeItem(item)
        self._image_items.clear()
        
        for slot, img in images.items():
            pixmap = pil_to_qpixmap(img)
            self._source_images[slot] = pixmap
            item = ClippedPixmapItem(pixmap)
            self.scene_obj.addItem(item)
            item.setZValue(slot)  # 描画順を制御
            self._image_items[slot] = item
            
        self._update_item_clipping()
        self._update_item_transforms()
        # HQモードの強制作動（False）は行わない。 MainWindow が判断する。
        
    def set_source_pixmap(self, pixmap: QPixmap, fast: bool = False) -> None:
        """完成済みの高画質結合画像をセットする（ドラッグ非実施中の通常表示）"""
        self._hq_pixmap = pixmap
        self._hq_item.setPixmap(pixmap)
        self.set_hq_mode(True)
        self._update_scene_transform()

    def set_pixmap(self, pixmap: QPixmap, fast: bool = False) -> None:
        self.set_source_pixmap(pixmap, fast)

    def clear_image(self) -> None:
        self._source_images.clear()
        for item in self._image_items.values():
            self.scene_obj.removeItem(item)
        self._image_items.clear()
        self._hq_pixmap = None
        self._hq_item.setPixmap(QPixmap())
        self._cell_bounds.clear()
        self._slot_polygons.clear()
        self._reorder_slot = None
        self._reorder_target_slot = None
        self.reset_offsets()

    def set_hq_mode(self, enabled: bool):
        """高品質の一枚絵表示(True)か、個別のインタラクティブパーツ表示(False)かを切り替える"""
        if enabled and self._hq_pixmap:
            self._hq_item.show()
            for item in self._image_items.values():
                item.hide()
        else:
            self._hq_item.hide()
            for item in self._image_items.values():
                item.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scene_transform()

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawForeground(painter, rect)

        if not self._can_reorder():
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for slot in self._cell_bounds:
            handle_rect = self._handle_rect_for_slot(slot)
            if self._reorder_slot == slot:
                fill = QColor(137, 180, 250, 230)
                stroke = QColor("#89b4fa")
            else:
                fill = QColor(24, 24, 37, 210)
                stroke = QColor("#585b70")

            painter.setPen(QPen(stroke, max(1.0, 1.0 / self._view_scale())))
            painter.setBrush(fill)
            painter.drawRoundedRect(handle_rect, 4, 4)

            grip_pen = QPen(QColor("#cdd6f4"), max(1.2, 1.2 / self._view_scale()))
            painter.setPen(grip_pen)
            left = handle_rect.left() + handle_rect.width() * 0.28
            right = handle_rect.right() - handle_rect.width() * 0.28
            for ratio in (0.35, 0.5, 0.65):
                y = handle_rect.top() + handle_rect.height() * ratio
                painter.drawLine(QPointF(left, y), QPointF(right, y))

        if self._reorder_slot is not None:
            source_path = self._slot_scene_path(self._reorder_slot)
            source_pen = QPen(QColor("#89b4fa"), max(2.0, 2.0 / self._view_scale()))
            painter.setPen(source_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(source_path)

        if self._reorder_target_slot is not None and self._reorder_target_slot in self._cell_bounds:
            target_path = self._slot_scene_path(self._reorder_target_slot)
            target_pen = QPen(QColor("#f9e2af"), max(2.0, 2.0 / self._view_scale()))
            target_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(target_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(target_path)

        painter.restore()

    def _update_scene_transform(self):
        """ビューのサイズに合わせてシーン全体をスケーリングする"""
        if self._output_size[0] == 0 or self._output_size[1] == 0:
            return
            
        view_w = self.viewport().width()
        view_h = self.viewport().height()
        
        scale = min(view_w / self._output_size[0], view_h / self._output_size[1])
        self.resetTransform()
        self.scale(scale, scale)

    def _update_item_clipping(self):
        self._update_item_transforms()

    def _update_item_transforms(self):
        # 各アイテムの拡大率と配置位置を計算
        for slot, item in self._image_items.items():
            if slot not in self._cell_bounds or slot not in self._source_images:
                item.hide()
                continue
                
            bx, by, bw, bh = self._cell_bounds[slot]
            pixmap = self._source_images[slot]
            pw, ph = pixmap.width(), pixmap.height()
            
            if pw == 0 or ph == 0 or bw == 0 or bh == 0:
                item.hide()
                continue
                
            item.show()
            
            render_bx, render_by, render_bw, render_bh = self._render_rect_for_slot(slot)

            # 1. Base Scale to fit bounds
            base_scale = max(render_bw / pw, render_bh / ph)
            
            # 2. Apply Custom Zoom
            ox, oy, zoom = self._offsets.get(slot, (0.0, 0.0, 1.0))
            final_scale = base_scale * zoom
            final_w = pw * final_scale
            final_h = ph * final_scale
            
            # 3. Calculate Pan
            extra_w = max(0, final_w - render_bw)
            extra_h = max(0, final_h - render_bh)
            
            crop_x = ((ox + 1.0) / 2.0) * extra_w
            crop_y = ((oy + 1.0) / 2.0) * extra_h
            
            # Scene coords
            render_x = render_bx - crop_x
            render_y = render_by - crop_y
            
            item.setPos(render_x, render_y)
            item.setScale(final_scale)
            
            # 4. Clipping
            path_scene = self._slot_scene_path(slot)

            # Transform path from scene coords to item local coords
            scene_to_item, invertible = item.sceneTransform().inverted()
            path_item = scene_to_item.map(path_scene) if invertible else None
            
            item.set_clip_path(path_item)

    def _scene_to_image_coords(self, scene_pos: QPointF) -> tuple[float, float]:
        """Scene Pos は Output Size ベース（0..W, 0..H）"""
        return scene_pos.x(), scene_pos.y()

    def _find_slot(self, ix: float, iy: float) -> int | None:
        point = QPointF(ix, iy)
        for slot in self._cell_bounds:
            if self._slot_scene_path(slot).contains(point):
                return slot
        return None

    def _get_distance_to_split(self, ix: float, iy: float) -> tuple[float, str | None]:
        if not self._split_mode:
            return float('inf'), None
            
        W, H = self._output_size
        
        if self._split_mode in ("v", "bg_color_v"):
            cx = W * self._split_ratio
            return abs(ix - cx), "SplitVCursor"
        elif self._split_mode == "h":
            cy = H * self._split_ratio
            return abs(iy - cy), "SplitHCursor"
        elif self._split_mode == "diagonal":
            cx = W * self._split_ratio
            angle_rad = math.radians(self._split_angle)
            offset = (H / 2.0) * math.tan(angle_rad)
            x1, y1 = cx - offset, 0
            x2, y2 = cx + offset, H
            
            num = abs((x2 - x1) * (y1 - iy) - (x1 - ix) * (y2 - y1))
            den = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            dist = num / den if den > 0 else float('inf')
            return dist, "SplitHCursor"
            
        return float('inf'), None

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        ix, iy = self._scene_to_image_coords(scene_pos)
        
        if event.button() == Qt.MouseButton.LeftButton:
            handle_slot = self._find_handle_slot(ix, iy)
            if handle_slot is not None:
                self._reorder_slot = handle_slot
                self._reorder_target_slot = handle_slot
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                self.viewport().update()
                event.accept()
                return

            # ドラッグ開始時にインタラクティブ表示へ切替
            self.set_hq_mode(False)
            
            dist, _ = self._get_distance_to_split(ix, iy)
            # Widgetに映った時のピクセル距離に直して当たり判定
            view_scale = min(self.viewport().width() / self._output_size[0], self.viewport().height() / self._output_size[1])
            dist_widget = dist * view_scale
            
            if dist_widget <= 8.0:
                self._is_dragging_split = True
                event.accept()
                return

            slot = self._find_slot(ix, iy)
            if slot is not None:
                self._drag_slot = slot
                self._drag_start_pos = scene_pos
                self._drag_start_offset = self._offsets.get(slot, (0.0, 0.0, 1.0))
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        ix, iy = self._scene_to_image_coords(scene_pos)
        W, H = self._output_size
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._reorder_slot is not None:
                self._reorder_target_slot = self._find_slot(ix, iy)
                self.viewport().update()
                event.accept()
                return

            if self._is_dragging_split:
                new_ratio = self._split_ratio
                if self._split_mode in ("v", "bg_color_v"):
                    new_ratio = ix / W
                elif self._split_mode == "h":
                    new_ratio = iy / H
                elif self._split_mode == "diagonal":
                    angle_rad = math.radians(self._split_angle)
                    new_ratio = (ix + (H / 2.0 - iy) * math.tan(angle_rad)) / W
                    
                new_ratio = max(0.05, min(0.95, new_ratio))
                if abs(new_ratio - self._split_ratio) > 0.001:
                    self._split_ratio = new_ratio
                    self.split_ratio_changed.emit(new_ratio)
                event.accept()
                return

            if self._drag_slot is not None and self._drag_start_pos is not None:
                dx = scene_pos.x() - self._drag_start_pos.x()
                dy = scene_pos.y() - self._drag_start_pos.y()
                
                start_ox, start_oy, start_zoom = self._drag_start_offset
                
                _, _, render_bw, render_bh = self._render_rect_for_slot(self._drag_slot)
                    
                pixmap = self._source_images[self._drag_slot]
                pw, ph = pixmap.width(), pixmap.height()
                base_scale = max(render_bw / pw, render_bh / ph)
                final_scale = base_scale * start_zoom
                
                extra_w = max(0.001, pw * final_scale - render_bw)
                extra_h = max(0.001, ph * final_scale - render_bh)
                
                delta_ox = -dx * 2.0 / extra_w
                delta_oy = -dy * 2.0 / extra_h
                
                new_ox = max(-1.0, min(1.0, start_ox + delta_ox))
                new_oy = max(-1.0, min(1.0, start_oy + delta_oy))
                
                # 自分自身の表示用だけを高速更新
                self._offsets[self._drag_slot] = (new_ox, new_oy, start_zoom)
                self._update_item_transforms()
                
                # MainWindow に伝達はするが、MainWindow側はもう重い処理は行わない前提
                self.crop_offset_changed.emit(self._drag_slot, new_ox, new_oy, start_zoom)
                event.accept()
                return

        # Hover
        if not event.buttons():
            handle_slot = self._find_handle_slot(ix, iy)
            if handle_slot is not None:
                self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
                return

            view_scale = min(self.viewport().width() / self._output_size[0], self.viewport().height() / self._output_size[1])
            dist_px, cursor_name = self._get_distance_to_split(ix, iy)
            if dist_px * view_scale <= 8.0 and cursor_name:
                if cursor_name == "SplitVCursor":
                    self.viewport().setCursor(Qt.CursorShape.SplitVCursor)
                else:
                    self.viewport().setCursor(Qt.CursorShape.SplitHCursor)
                return
                
            if self._find_slot(ix, iy) is not None:
                self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
                return

        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._reorder_slot is not None:
                source_slot = self._reorder_slot
                target_slot = self._reorder_target_slot
                self._reorder_slot = None
                self._reorder_target_slot = None
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                self.viewport().update()
                if (
                    target_slot is not None
                    and target_slot in self._cell_bounds
                    and target_slot != source_slot
                ):
                    self.reorder_requested.emit(source_slot, target_slot)
                event.accept()
                return

            was_dragging = False
            if self._is_dragging_split:
                self._is_dragging_split = False
                was_dragging = True
            if self._drag_slot is not None:
                self._drag_slot = None
                self._drag_start_pos = None
                was_dragging = True
                
            if was_dragging:
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                self.drag_finished.emit()
                # 高クオリティ表示への切り替えはMainWindowの合成終了を待ってから行われる
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if not self._cell_bounds:
            super().wheelEvent(event)
            return

        if self._reorder_slot is not None:
            event.accept()
            return

        scene_pos = self.mapToScene(event.position().toPoint())
        ix, iy = self._scene_to_image_coords(scene_pos)
        
        slot = self._find_slot(ix, iy)
        if slot is not None:
            delta = event.angleDelta().y() or event.angleDelta().x()
            if delta != 0:
                self.set_hq_mode(False) # ズーム開始時に低解像度モードへ
                ox, oy, zoom = self._offsets.get(slot, (0.0, 0.0, 1.0))
                
                render_bx, render_by, render_bw, render_bh = self._render_rect_for_slot(slot)
                    
                pixmap = self._source_images[slot]
                pw, ph = pixmap.width(), pixmap.height()
                base_scale = max(render_bw / pw, render_bh / ph)
                
                old_zoom = zoom
                zoom_step = 0.05
                if delta > 0:
                    new_zoom = min(3.0, zoom + zoom_step)
                else:
                    new_zoom = max(1.0, zoom - zoom_step)
                    
                if new_zoom == old_zoom:
                    return
                    
                z_ratio = new_zoom / old_zoom
                
                old_fw = pw * base_scale * old_zoom
                old_fh = ph * base_scale * old_zoom
                old_extra_w = max(0.0, old_fw - render_bw)
                old_extra_h = max(0.0, old_fh - render_bh)
                
                old_crop_x = ((ox + 1.0) / 2.0) * old_extra_w
                old_crop_y = ((oy + 1.0) / 2.0) * old_extra_h
                
                cx = ix - render_bx
                cy = iy - render_by
                
                new_crop_x = old_crop_x * z_ratio + cx * (z_ratio - 1.0)
                new_crop_y = old_crop_y * z_ratio + cy * (z_ratio - 1.0)
                
                new_fw = pw * base_scale * new_zoom
                new_fh = ph * base_scale * new_zoom
                new_extra_w = max(0.001, new_fw - render_bw)
                new_extra_h = max(0.001, new_fh - render_bh)
                
                new_ox = (new_crop_x / new_extra_w) * 2.0 - 1.0
                new_oy = (new_crop_y / new_extra_h) * 2.0 - 1.0
                
                new_ox = max(-1.0, min(1.0, new_ox))
                new_oy = max(-1.0, min(1.0, new_oy))
                
                self._offsets[slot] = (new_ox, new_oy, new_zoom)
                self._update_item_transforms()
                self.crop_offset_changed.emit(slot, new_ox, new_oy, new_zoom)
                self._wheel_timer.start(200)
            event.accept()
            return
            
        super().wheelEvent(event)


class ThumbnailPreviewWidget(QWidget):
    """184×184縮小プレビュー（Pixiv一覧シミュレーション）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thumb_pixmap: QPixmap | None = None
        self._show_mock = False
        self.setFixedSize(400, 220)
        self.setStyleSheet("background: #1e1e2e; border-radius: 4px;")

    def set_thumbnail(self, pil_image: Image.Image) -> None:
        thumb = pil_image.copy()
        thumb.thumbnail((184, 184), Image.LANCZOS)
        self._thumb_pixmap = pil_to_qpixmap(thumb)
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 背景（Pixiv風の暗いグレー）
        painter.fillRect(self.rect(), QColor("#1e1e2e"))

        # モック（ダミー）サムネイル（灰色の矩形）
        dummy_color = QColor("#313244")
        cell_size = 184
        margin = 6
        positions = [
            (margin, 18),
            (margin + cell_size + margin, 18),
        ]
        for mx, my in positions:
            painter.fillRect(mx, my, cell_size, cell_size, dummy_color)

        # 自分のサムネイル（中央）
        if self._thumb_pixmap:
            cx = margin + (cell_size - self._thumb_pixmap.width()) // 2
            cy = 18 + (cell_size - self._thumb_pixmap.height()) // 2
            painter.drawPixmap(cx, cy, self._thumb_pixmap)
        else:
            # プレースホルダー
            pen = QPen(QColor("#45475a"))
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(margin, 18, cell_size, cell_size)

        # ラベル
        painter.setPen(QColor("#585b70"))
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(margin, 14, "← ダミー | 自作 → | ダミー →")

        painter.end()


class WarningPanel(QWidget):
    """警告メッセージ表示"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self._label = QLabel()
        self._label.setWordWrap(True)
        self._label.setStyleSheet("""
            QLabel {
                color: #fab387;
                background: #312a1e;
                border: 1px solid #fab387;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self._label)
        self.hide()

    def show_warnings(self, messages: list[str]) -> None:
        if messages:
            self._label.setText("\n".join(f"⚠ {m}" for m in messages))
            self.show()
        else:
            self.hide()


class PreviewPanel(QWidget):
    """中央パネル: メインプレビュー + 縮小プレビュー"""

    # PreviewLabel からのシグナルをそのまま転送
    crop_offset_changed = Signal(int, float, float, float)
    drag_finished = Signal()
    split_ratio_changed = Signal(float)
    reorder_requested = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._showing_main = True
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet("background: #181825;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # ヘッダ
        header_layout = QHBoxLayout()
        title = QLabel("プレビュー")
        title.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 13px;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        space_hint = QLabel("[Space] 切替")
        space_hint.setStyleSheet("color: #585b70; font-size: 11px;")
        header_layout.addWidget(space_hint)
        layout.addLayout(header_layout)

        # タブボタン
        tab_layout = QHBoxLayout()
        self._btn_main = QPushButton("メインプレビュー")
        self._btn_thumb = QPushButton("縮小プレビュー (Pixiv)")
        for btn in [self._btn_main, self._btn_thumb]:
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setStyleSheet("""
                QPushButton {
                    background: #313244;
                    color: #a6adc8;
                    border: 1px solid #45475a;
                    border-radius: 4px;
                    padding: 0 12px;
                    font-size: 12px;
                }
                QPushButton:checked {
                    background: #45475a;
                    color: #cdd6f4;
                    border-color: #89b4fa;
                }
                QPushButton:hover { background: #45475a; }
            """)
        self._btn_main.setChecked(True)
        tab_layout.addWidget(self._btn_main)
        tab_layout.addWidget(self._btn_thumb)
        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        # メインプレビュー領域 (InteractivePreviewに置換)
        self._preview_label = InteractivePreview()
        layout.addWidget(self._preview_label, stretch=1)

        # 縮小プレビュー（Pixivシミュレーション）
        self._thumb_container = QWidget()
        thumb_layout = QVBoxLayout(self._thumb_container)
        thumb_layout.setContentsMargins(0, 0, 0, 0)
        thumb_layout.setSpacing(4)

        thumb_title = QLabel("縮小プレビュー（Pixiv一覧 184×184px）")
        thumb_title.setStyleSheet("color: #a6adc8; font-size: 11px;")
        thumb_layout.addWidget(thumb_title)

        self._thumb_preview = ThumbnailPreviewWidget()
        thumb_layout.addWidget(self._thumb_preview)
        self._thumb_container.hide()
        layout.addWidget(self._thumb_container)

        # 警告パネル
        self._warning_panel = WarningPanel()
        layout.addWidget(self._warning_panel)

        # PC/モバイル切替（Phase 3）
        view_layout = QHBoxLayout()
        self._btn_pc = QPushButton("PC表示")
        self._btn_mobile = QPushButton("モバイル表示")
        for btn in [self._btn_pc, self._btn_mobile]:
            btn.setCheckable(True)
            btn.setFixedHeight(24)
            btn.setStyleSheet("""
                QPushButton {
                    background: #1e1e2e;
                    color: #585b70;
                    border: 1px solid #3d3d5c;
                    border-radius: 3px;
                    padding: 0 8px;
                    font-size: 11px;
                }
                QPushButton:checked {
                    color: #89b4fa;
                    border-color: #89b4fa;
                }
            """)
        self._btn_pc.setChecked(True)
        view_layout.addStretch()
        view_layout.addWidget(self._btn_pc)
        view_layout.addWidget(self._btn_mobile)
        layout.addLayout(view_layout)

        # シグナル接続
        self._btn_main.clicked.connect(lambda: self._switch_view(True))
        self._btn_thumb.clicked.connect(lambda: self._switch_view(False))
        # PreviewLabel のドラッグシグナルをパネルレベルに転送
        self._preview_label.crop_offset_changed.connect(self.crop_offset_changed)
        self._preview_label.drag_finished.connect(self.drag_finished)
        self._preview_label.split_ratio_changed.connect(self.split_ratio_changed)
        self._preview_label.reorder_requested.connect(self.reorder_requested)

    # ------------------------------------------------------------------
    # 公開API
    # ------------------------------------------------------------------

    def set_cell_bounds(
        self,
        bounds: "dict[int, tuple[int, int, int, int]]",
        output_size: "tuple[int, int]",
        preset_name: str = "",
        slot_polygons: "dict[int, list[tuple[float, float]]] | None" = None,
    ) -> None:
        """セル境界をPreviewLabelに渡す（ドラッグオフセット計算用）"""
        self._preview_label.set_cell_bounds(bounds, output_size, preset_name, slot_polygons)

    def update_offsets(self, offsets: "dict[int, tuple[float, float]]") -> None:
        """現在のオフセット状態をPreviewLabelに通知"""
        self._preview_label.update_offsets(offsets)

    def set_split_info(self, mode: str | None, ratio: float, angle: float = 30.0) -> None:
        self._preview_label.set_split_info(mode, ratio, angle)

    def reset_offsets(self) -> None:
        """オフセットをリセット（プリセット変更時など）"""
        self._preview_label.reset_offsets()


    def set_pixmap(self, pixmap: QPixmap, fast: bool = False) -> None:
        """メインプレビュー画像をセット"""
        self._preview_label.set_source_pixmap(pixmap, fast=fast)

    def set_pil_image(self, pil_image: Image.Image) -> None:
        """PIL Imageからメイン+縮小両方を更新"""
        pixmap = pil_to_qpixmap(pil_image)
        self._preview_label.set_source_pixmap(pixmap)
        self._thumb_preview.set_thumbnail(pil_image)

    def set_thumbnail(self, pil_image: Image.Image) -> None:
        """縮小プレビューのみ更新"""
        self._thumb_preview.set_thumbnail(pil_image)

    def clear(self) -> None:
        self._preview_label.clear_image()

    def toggle_view(self) -> None:
        """Space キーで切替"""
        self._switch_view(not self._showing_main)

    def show_warnings(self, messages: list[str]) -> None:
        self._warning_panel.show_warnings(messages)

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _switch_view(self, show_main: bool) -> None:
        self._showing_main = show_main
        self._btn_main.setChecked(show_main)
        self._btn_thumb.setChecked(not show_main)
        self._preview_label.setVisible(show_main)
        self._thumb_container.setVisible(not show_main)
