from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, Signal
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget


class ReviewChecklistWidget(QWidget):
    checks_changed = Signal(bool, bool, bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.thumbnail_checkbox = QCheckBox("先頭画像を確認した", self)
        self.order_checkbox = QCheckBox("画像順を確認した", self)
        self.destination_checkbox = QCheckBox("投稿先を確認した", self)
        layout.addWidget(self.thumbnail_checkbox)
        layout.addWidget(self.order_checkbox)
        layout.addWidget(self.destination_checkbox)

        self.thumbnail_checkbox.toggled.connect(self._emit_changed)
        self.order_checkbox.toggled.connect(self._emit_changed)
        self.destination_checkbox.toggled.connect(self._emit_changed)

    def set_values(
        self,
        thumbnail_checked: bool,
        order_checked: bool,
        destination_checked: bool,
    ) -> None:
        for checkbox, value in (
            (self.thumbnail_checkbox, thumbnail_checked),
            (self.order_checkbox, order_checked),
            (self.destination_checkbox, destination_checked),
        ):
            with QSignalBlocker(checkbox):
                checkbox.setChecked(value)

    def _emit_changed(self) -> None:
        self.checks_changed.emit(
            self.thumbnail_checkbox.isChecked(),
            self.order_checkbox.isChecked(),
            self.destination_checkbox.isChecked(),
        )
