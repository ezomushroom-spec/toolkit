"""スタイル付きボタンウィジェット"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt


class PrimaryButton(QPushButton):
    """アクセントカラーのプライマリボタン"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("btn_primary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class IconButton(QPushButton):
    """ナビゲーション用の小型アイコンボタン"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("btn_icon")
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
