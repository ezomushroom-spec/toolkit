"""テーマ管理マネージャー"""

import os
import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal

from civitai_downloader.constants import AppTheme
from civitai_downloader.db.connection import Database
from civitai_downloader.db import repository as repo
from civitai_downloader.ui.theme.colors import DARK_PALETTE, LIGHT_PALETTE

logger = logging.getLogger(__name__)

_QSS_PATH = os.path.join(os.path.dirname(__file__), "base.qss")


class ThemeManager(QObject):
    """テーマの読み込み・適用・切替を管理"""

    theme_changed = Signal(str)

    _instance: "ThemeManager | None" = None

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db = db
        self._current_theme = AppTheme.DARK
        ThemeManager._instance = self

    @classmethod
    def instance(cls) -> "ThemeManager | None":
        return cls._instance

    @property
    def current_theme(self) -> AppTheme:
        return self._current_theme

    def load_saved_theme(self):
        """DBから保存済みテーマを読み込んで適用"""
        theme_str = repo.get_setting(self._db, "theme", AppTheme.DARK.value)
        try:
            theme = AppTheme(theme_str)
        except ValueError:
            theme = AppTheme.DARK
        self.apply_theme(theme)

    def apply_theme(self, theme: AppTheme):
        """テーマをアプリケーション全体に適用"""
        self._current_theme = theme
        palette = DARK_PALETTE if theme == AppTheme.DARK else LIGHT_PALETTE

        try:
            with open(_QSS_PATH, "r", encoding="utf-8") as f:
                qss_template = f.read()
        except FileNotFoundError:
            logger.error(f"QSSファイルが見つかりません: {_QSS_PATH}")
            return

        qss = qss_template.format(**palette)

        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)

        self.theme_changed.emit(theme.value)
        logger.info(f"テーマ適用: {theme.value}")

    def set_theme(self, theme: AppTheme):
        """指定テーマに切り替えてDBに保存"""
        self.apply_theme(theme)
        repo.set_setting(self._db, "theme", theme.value)

    def get_color(self, key: str) -> str:
        """現在のテーマからカラー値を取得"""
        palette = (
            DARK_PALETTE if self._current_theme == AppTheme.DARK
            else LIGHT_PALETTE
        )
        return palette.get(key, "#ff00ff")
