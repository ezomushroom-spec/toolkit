import os
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QWheelEvent, QMouseEvent

class PreviewCanvas(QGraphicsView):
    # シグナル
    folderDropped = Signal(str)
    boxSelectionChanged = Signal()
    boxRemoved = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag) # カスタムパンのためデフォルト無効
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("border: none; background-color: #222222;")
        
        # ズーム・パン状態
        self._zoom = 1.0
        self._pixmap_item = None
        self._boxes = [] # オーバーレイ矩形
        
        self._is_panning = False
        self._pan_start_pos = QPointF()
        
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        
    def set_image(self, pixmap: QPixmap):
        self.scene.clear()
        self._boxes.clear()
        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self._pixmap_item)
        self.scene.setSceneRect(self._pixmap_item.boundingRect())
        
        self.fit_to_view()
        
    def fit_to_view(self):
        if self._pixmap_item:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            self._zoom = 1.0

    def set_boxes(self, candidates: list):
        """AI推論結果のボックスを描画する"""
        for box in self._boxes:
            self.scene.removeItem(box)
        self._boxes.clear()
        
        if not self._pixmap_item:
            return
            
        for item in candidates:
            x1, y1, x2, y2 = item['xyxy']
            w, h = x2 - x1, y2 - y1
            
            rect = QGraphicsRectItem(x1, y1, w, h)
            pen = QPen(QColor(255, 60, 60, 200))
            pen.setWidth(2)
            # ズームに依存しないペン太さにする場合は setCosmetic(True)
            pen.setCosmetic(True) 
            rect.setPen(pen)
            
            rect.setBrush(QColor(255, 60, 60, 40))
            
            # 手動削除等用に選択・クリック可能にする
            rect.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
            rect.setZValue(10) # 画像より上に表示
            
            self.scene.addItem(rect)
            self._boxes.append(rect)
            
    def get_remaining_boxes(self):
        """ユーザーの手動修正を経た後、残っているBoxのリストを返す"""
        results = []
        for box in self._boxes:
            if box.scene() == self.scene: # まだシーンに存在する場合
                rect = box.rect()
                x1, y1, w, h = rect.x(), rect.y(), rect.width(), rect.height()
                results.append([x1, y1, x1+w, y1+h])
        return results

    # ==========================
    # マウス・ズーム・パンイベント
    # ==========================
    def wheelEvent(self, event: QWheelEvent):
        """数理的カーソル中心ズーム"""
        if not self._pixmap_item:
            return
            
        # pyside6-interactive-canvas の Pattern 2 に準拠
        delta = event.angleDelta().y()
        if delta == 0:
            return
            
        old_zoom = self._zoom
        zoom_factor = 1.15
        
        if delta > 0:
            self._zoom = min(10.0, self._zoom * zoom_factor)
        else:
            self._zoom = max(0.1, self._zoom / zoom_factor)
            
        if old_zoom == self._zoom:
            return
            
        # ズームの適用
        # scene()上でのマウス位置を記録（ズーム前の位置）
        scene_pos = self.mapToScene(event.position().toPoint())
        
        # 拡縮
        scale_factor = self._zoom / old_zoom
        self.scale(scale_factor, scale_factor)
        
        # ズーム後のマウス位置を再度マップし、ズーム前の位置との差分をスクロールバーの移動で補正する
        new_scene_pos = self.mapToScene(event.position().toPoint())
        diff = scene_pos - new_scene_pos
        
        # QGraphicsView特有のスクロール調整による精密パン
        self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() + diff.x() * self.transform().m11()))
        self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() + diff.y() * self.transform().m22()))
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            # 右クリックでパンドラッグ開始
            self._is_panning = True
            self._pan_start_pos = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if isinstance(item, QGraphicsRectItem) and item in self._boxes:
                self.scene.removeItem(item)
                self._boxes.remove(item)
                self.boxSelectionChanged.emit()
                self.boxRemoved.emit()
                event.accept()
                return
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            # ドラッグによる1:1ピクセルパン
            delta = event.position().toPoint() - self._pan_start_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._pan_start_pos = event.position().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def keyPressEvent(self, event):
        """Deleteキー等による手動マスク消去"""
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            items = self.scene.selectedItems()
            for item in items:
                if isinstance(item, QGraphicsRectItem):
                    self.scene.removeItem(item)
                    if item in self._boxes:
                        self._boxes.remove(item)
            self.boxSelectionChanged.emit()
            self.boxRemoved.emit()
        else:
            super().keyPressEvent(event)

    # ==========================
    # D&Dイベント (フォルダのドロップ対応)
    # ==========================
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.folderDropped.emit(path)
            elif os.path.isfile(path):
                # ファイルがドロップされたらディレクトリに変換
                self.folderDropped.emit(os.path.dirname(path))
        event.acceptProposedAction()
