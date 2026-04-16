"""スタイル付きテーブルウィジェット"""

from PySide6.QtWidgets import QTableWidget, QStyledItemDelegate


class _PaddedDelegate(QStyledItemDelegate):
    """セルの最小行高を確保するデリゲート"""

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(max(size.height(), 36))
        return size


class StyledTableWidget(QTableWidget):
    """交互色・行ホバー・行番号非表示のテーブル"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setMouseTracking(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(40)
        self.setItemDelegate(_PaddedDelegate(self))
