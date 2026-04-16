"""
出力履歴パネル
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog,
)

from core.exporter import ExportRecord

_BTN_STYLE = """
    QPushButton {
        background: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 4px;
        padding: 0 8px;
        font-size: 12px;
    }
    QPushButton:hover { background: #45475a; }
    QPushButton:pressed { background: #585b70; }
"""


class HistoryPanel(QWidget):
    """出力履歴パネル"""

    record_selected = Signal(object)      # ExportRecord
    export_csv_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records: list[ExportRecord] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet("background: #181825;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # ヘッダ
        header = QLabel("出力履歴")
        header.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 13px;")
        layout.addWidget(header)

        # リスト
        self._list = QListWidget()
        self._list.setIconSize(QSize(64, 64))
        self._list.setStyleSheet("""
            QListWidget {
                background: #1e1e2e;
                border: 1px solid #3d3d5c;
                border-radius: 4px;
            }
            QListWidget::item { color: #cdd6f4; padding: 4px; border-radius: 3px; }
            QListWidget::item:selected { background: #313244; border: 1px solid #89b4fa; }
            QListWidget::item:hover { background: #292940; }
        """)
        self._list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list, stretch=1)

        # ボタン
        btn_layout = QHBoxLayout()
        self._btn_csv = QPushButton("CSVエクスポート")
        self._btn_open = QPushButton("フォルダを開く")
        self._btn_clear = QPushButton("履歴をクリア")

        for btn in [self._btn_csv, self._btn_open, self._btn_clear]:
            btn.setFixedHeight(28)
            btn.setStyleSheet(_BTN_STYLE)

        btn_layout.addWidget(self._btn_csv)
        btn_layout.addWidget(self._btn_open)
        layout.addLayout(btn_layout)
        layout.addWidget(self._btn_clear)

        self._btn_csv.clicked.connect(self.export_csv_requested)
        self._btn_open.clicked.connect(self._open_output_folder)
        self._btn_clear.clicked.connect(self.clear_requested)

    # ------------------------------------------------------------------
    # 公開API
    # ------------------------------------------------------------------

    def add_record(self, record: ExportRecord) -> None:
        self._records.append(record)
        item = self._create_item(record)
        self._list.insertItem(0, item)  # 最新を先頭に

    def refresh(self, records: list[ExportRecord]) -> None:
        self._records = list(records)
        self._list.clear()
        for rec in reversed(self._records):  # 最新が先頭
            self._list.addItem(self._create_item(rec))

    def get_output_dir(self) -> Path | None:
        if not self._records:
            return None
        return self._records[-1].output_path.parent

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _create_item(self, record: ExportRecord) -> QListWidgetItem:
        text = (
            f"{record.preset_name} #{record.variant:03d}\n"
            f"{record.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{record.output_size[0]}×{record.output_size[1]}px"
        )
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, record)

        # サムネイル読み込み
        if record.output_path.exists():
            try:
                pixmap = QPixmap(str(record.output_path))
                if not pixmap.isNull():
                    thumb = pixmap.scaled(
                        64, 64,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    item.setIcon(QIcon(thumb))
            except Exception:
                pass

        return item

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        record = item.data(Qt.ItemDataRole.UserRole)
        if record:
            self.record_selected.emit(record)

    def _open_output_folder(self) -> None:
        output_dir = self.get_output_dir()
        if output_dir and output_dir.exists():
            if sys.platform == "win32":
                subprocess.Popen(["explorer", str(output_dir)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(output_dir)])
            else:
                subprocess.Popen(["xdg-open", str(output_dir)])

    def clear_records(self) -> None:
        self._records.clear()
        self._list.clear()
