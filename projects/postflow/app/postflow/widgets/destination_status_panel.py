from __future__ import annotations

import sqlite3

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget


class DestinationStatusPanel(QWidget):
    status_changed = Signal(int, int, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._work_id: int | None = None
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setHorizontalSpacing(12)
        self._layout.setVerticalSpacing(8)

    def set_destinations(self, work_id: int | None, destinations: list[sqlite3.Row]) -> None:
        self._work_id = work_id
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if work_id is None or not destinations:
            self._layout.addWidget(QLabel("投稿先がありません。"), 0, 0)
            return

        for row_index, destination in enumerate(destinations):
            name = QLabel(str(destination["destination_name"]))
            name.setProperty("destinationChip", str(destination["status"]))
            combo = QComboBox(self)
            combo.addItems(["未着手", "準備中", "投稿済み", "不要"])
            combo.setCurrentText(str(destination["status"]))
            destination_id = int(destination["destination_id"])
            combo.currentTextChanged.connect(
                lambda value, did=destination_id: self.status_changed.emit(work_id, did, value)
            )
            self._layout.addWidget(name, row_index, 0)
            self._layout.addWidget(combo, row_index, 1)
