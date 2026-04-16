"""画面右下トースト通知"""

from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve


class Toast(QLabel):
    """メインウィンドウの右下に一時表示されるトースト通知"""

    # 表示中のトースト一覧（スタック表示用）
    _active_toasts: list["Toast"] = []

    def __init__(self, message: str, parent=None, duration_ms: int = 3000):
        super().__init__(message, parent)
        self._duration_ms = duration_ms

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._apply_theme_style()
        self.setMaximumWidth(400)
        self.setWordWrap(True)

        # 不透明度エフェクト
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)

    def _apply_theme_style(self):
        """テーマに応じたスタイルを適用"""
        from civitai_downloader.ui.theme.theme_manager import ThemeManager
        tm = ThemeManager.instance()
        if tm:
            bg = tm.get_color("toast_bg")
            border = tm.get_color("toast_border")
            text = tm.get_color("toast_text")
        else:
            bg = "rgba(40, 40, 40, 230)"
            border = "#555"
            text = "#e0e0e0"

        self.setStyleSheet(
            f"QLabel {{"
            f"  background-color: {bg};"
            f"  color: {text};"
            f"  border: 1px solid {border};"
            f"  border-radius: 6px;"
            f"  padding: 10px 16px;"
            f"  font-size: 13px;"
            f"}}"
        )

    def show_toast(self):
        """トーストを表示してアニメーション開始"""
        Toast._active_toasts.append(self)
        self._position()
        self.show()
        self.raise_()

        # フェードイン
        self._fade_in = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_in.setDuration(200)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_in.start()

        # 表示維持タイマー
        QTimer.singleShot(self._duration_ms, self._start_fade_out)

    def _start_fade_out(self):
        """フェードアウト開始"""
        self._fade_out = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_out.setDuration(500)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self._on_fade_out_done)
        self._fade_out.start()

    def _on_fade_out_done(self):
        """フェードアウト完了→削除"""
        if self in Toast._active_toasts:
            Toast._active_toasts.remove(self)
        # 残存トーストの位置を詰める
        for t in Toast._active_toasts:
            t._position()
        self.deleteLater()

    def _position(self):
        """親ウィジェットの右下に配置（スタック対応）"""
        parent = self.parentWidget()
        if not parent:
            return

        self.adjustSize()
        margin = 16
        # このトーストがスタックの何番目か
        idx = Toast._active_toasts.index(self) if self in Toast._active_toasts else 0
        # 下からスタック
        offset_y = 0
        for i in range(idx):
            offset_y += Toast._active_toasts[i].sizeHint().height() + 8

        x = parent.width() - self.sizeHint().width() - margin
        y = parent.height() - self.sizeHint().height() - margin - offset_y
        self.move(x, y)


def show_toast(parent, message: str, duration_ms: int = 3000):
    """ヘルパー: 親ウィジェットにトーストを表示"""
    toast = Toast(message, parent=parent, duration_ms=duration_ms)
    toast.show_toast()
