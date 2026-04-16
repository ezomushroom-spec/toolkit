from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class ConfirmDeleteWorkDialog(QDialog):
    def __init__(self, work_name: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("作品削除の確認")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"作品「{work_name}」を削除します。"))
        warning = QLabel("元画像ファイルは削除しません。作品内の管理情報だけを削除します。")
        warning.setWordWrap(True)
        layout.addWidget(warning)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        button_box.button(QDialogButtonBox.StandardButton.Yes).setText("削除")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("キャンセル")
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
