from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class ConfirmRemoveImageDialog(QDialog):
    def __init__(self, image_name: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("画像除外の確認")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"画像「{image_name}」を作品から外します。"))
        warning = QLabel("元画像ファイルは削除しません。作品内の管理情報だけを更新します。")
        warning.setWordWrap(True)
        layout.addWidget(warning)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        button_box.button(QDialogButtonBox.StandardButton.Yes).setText("除外")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("キャンセル")
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
