from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class CreateWorkDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新規作品")
        self.setModal(True)
        self.resize(360, 140)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("作品名"))

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("作品名を入力")
        layout.addWidget(self.name_input)

        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: #b42318;")
        layout.addWidget(self.message_label)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("作成")
        self.ok_button.setEnabled(False)
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("キャンセル")
        layout.addWidget(self.button_box)

        self.name_input.textChanged.connect(self._on_text_changed)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def work_name(self) -> str:
        return self.name_input.text().strip()

    def set_error(self, message: str) -> None:
        self.message_label.setText(message)

    def _on_text_changed(self, value: str) -> None:
        self.message_label.clear()
        self.ok_button.setEnabled(bool(value.strip()))
