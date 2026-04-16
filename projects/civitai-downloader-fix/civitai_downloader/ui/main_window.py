"""メインウィンドウ（タブコンテナ）"""

from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PySide6.QtCore import Slot

from civitai_downloader.constants import APP_VERSION
from civitai_downloader.ui.toast import show_toast


class MainWindow(QMainWindow):
    """4タブ構成のメインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle(f"Civitai Model Downloader v{APP_VERSION}")
        self.resize(1200, 800)

        # 中央ウィジェット
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # タブウィジェット
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # 各タブ（後から実体を設定）
        self._browse_tab: QWidget | None = None
        self._download_tab: QWidget | None = None
        self._notification_tab: QWidget | None = None
        self._settings_tab: QWidget | None = None

    def setup_tabs(
        self,
        browse_tab: QWidget,
        download_tab: QWidget,
        notification_tab: QWidget,
        settings_tab: QWidget,
    ):
        """全タブを設定する"""
        self._browse_tab = browse_tab
        self._download_tab = download_tab
        self._notification_tab = notification_tab
        self._settings_tab = settings_tab

        self._tabs.addTab(self._browse_tab, "ブラウズ")
        self._tabs.addTab(self._download_tab, "ダウンロード")
        self._tabs.addTab(self._notification_tab, "通知")
        self._tabs.addTab(self._settings_tab, "設定")

    @Slot(int)
    def update_download_badge(self, count: int):
        """ダウンロードタブのバッジを更新"""
        idx = self._tabs.indexOf(self._download_tab)
        if idx >= 0:
            text = f"ダウンロード({count})" if count > 0 else "ダウンロード"
            self._tabs.setTabText(idx, text)

    @Slot(int)
    def update_notification_badge(self, count: int):
        """通知タブのバッジを更新"""
        idx = self._tabs.indexOf(self._notification_tab)
        if idx >= 0:
            text = f"通知({count})" if count > 0 else "通知"
            self._tabs.setTabText(idx, text)

    def switch_to_browse_tab(self):
        """ブラウズタブに切り替え"""
        if self._browse_tab:
            self._tabs.setCurrentWidget(self._browse_tab)

    def switch_to_download_tab(self):
        """ダウンロードタブに切り替え"""
        if self._download_tab:
            self._tabs.setCurrentWidget(self._download_tab)

    @Slot(str)
    def show_toast(self, message: str, duration_ms: int = 3000):
        """画面右下にトースト通知を表示"""
        show_toast(self, message, duration_ms)
