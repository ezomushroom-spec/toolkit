import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Qt, Signal

class ImageListWidget(QWidget):
    fileSelected = Signal(str)      # 選択されたファイルの絶対パスを通知
    folderDropped = Signal(str)     # フォルダがD&Dされたことを通知
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_list = []
        self.init_ui()
        self.setAcceptDrops(True)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_info = QLabel("画像リスト (0 / 0)")
        self.lbl_info.setStyleSheet("padding: 2px; color: #aaa;")
        layout.addWidget(self.lbl_info)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.currentItemChanged.connect(self.on_item_selected)
        layout.addWidget(self.list_widget)
        
    def set_files(self, file_paths: list):
        """ファイルリストを更新する"""
        self.list_widget.clear()
        self.file_list = []
        
        for path in file_paths:
            self.file_list.append(path)
            name = os.path.basename(path)
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)
            
        self.update_info(0)
        
    def update_info(self, index: int):
        total = len(self.file_list)
        idx = index + 1 if total > 0 else 0
        self.lbl_info.setText(f"画像リスト ({idx} / {total})")
        
    def on_item_selected(self, current, previous):
        if current is not None:
            path = current.data(Qt.UserRole)
            index = self.list_widget.row(current)
            self.update_info(index)
            self.fileSelected.emit(path)

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
                self.folderDropped.emit(os.path.dirname(path))
        event.acceptProposedAction()
