from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QWidget


class WorksFilterBar(QWidget):
    filters_changed = Signal(str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(QLabel("検索"))
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("作品名で絞り込み")
        layout.addWidget(self.search_input, stretch=1)

        layout.addWidget(QLabel("状態"))
        self.status_combo = QComboBox(self)
        self.status_combo.addItems(
            ["すべて", "下書き", "準備中", "投稿可能", "一部投稿済み", "全投稿済み"]
        )
        layout.addWidget(self.status_combo)

        self.search_input.textChanged.connect(self._emit_filters_changed)
        self.status_combo.currentTextChanged.connect(self._emit_filters_changed)

    def _emit_filters_changed(self) -> None:
        self.filters_changed.emit(
            self.search_input.text().strip(),
            self.status_combo.currentText(),
        )
