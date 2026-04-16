"""カスタム描画プログレスバー"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QLinearGradient


class StyledProgressBar(QWidget):
    """角丸・グラデーション・パーセント表示のカスタムプログレスバー"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._min = 0
        self._max = 100
        self._completed = False
        self.setMinimumHeight(22)
        self.setMaximumHeight(26)

        # テーマ変更時に再描画
        from civitai_downloader.ui.theme.theme_manager import ThemeManager
        tm = ThemeManager.instance()
        if tm:
            tm.theme_changed.connect(lambda _: self.update())

    def setValue(self, value: int):
        self._value = max(self._min, min(value, self._max))
        if self._value >= self._max:
            self._completed = True
        self.update()

    def setRange(self, minimum: int, maximum: int):
        self._min = minimum
        self._max = maximum

    def value(self) -> int:
        return self._value

    def setCompleted(self, completed: bool):
        self._completed = completed
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        from civitai_downloader.ui.theme.theme_manager import ThemeManager
        tm = ThemeManager.instance()

        radius = 6.0
        rect = QRectF(0, 0, self.width(), self.height())

        # 背景
        bg_color = QColor(tm.get_color("progress_bg") if tm else "#2a2a3c")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, radius, radius)

        # 進捗部分
        if self._value > self._min and self._max > self._min:
            ratio = (self._value - self._min) / (self._max - self._min)
            fill_width = rect.width() * ratio
            fill_rect = QRectF(0, 0, fill_width, rect.height())

            if self._completed:
                fill_color = QColor(
                    tm.get_color("progress_complete") if tm else "#4caf7c"
                )
                painter.setBrush(fill_color)
            else:
                gradient = QLinearGradient(0, 0, fill_width, 0)
                base_color = QColor(
                    tm.get_color("progress_fill") if tm else "#7c6ff7"
                )
                gradient.setColorAt(0.0, base_color.lighter(110))
                gradient.setColorAt(1.0, base_color)
                painter.setBrush(gradient)

            painter.drawRoundedRect(fill_rect, radius, radius)

        # パーセンテージテキスト
        text_color = QColor(
            tm.get_color("progress_text") if tm else "#ffffff"
        )
        painter.setPen(text_color)
        font = QFont("Segoe UI", 9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self._value}%")

        painter.end()
