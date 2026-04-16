"""QApplication初期化・アプリデータディレクトリ管理"""

import os
import sys

from PySide6.QtWidgets import QApplication

from civitai_downloader.constants import APP_NAME, APP_VERSION


def get_app_data_dir() -> str:
    """アプリデータディレクトリを取得（%LOCALAPPDATA%/CivitaiDownloader/）"""
    base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    app_dir = os.path.join(base, "CivitaiDownloader")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_temp_dir() -> str:
    """一時ダウンロード先ディレクトリ"""
    d = os.path.join(get_app_data_dir(), "Temp")
    os.makedirs(d, exist_ok=True)
    return d


def get_unsorted_dir() -> str:
    """未分類ファイル保存ディレクトリ"""
    d = os.path.join(get_app_data_dir(), "Unsorted")
    os.makedirs(d, exist_ok=True)
    return d


def create_application(argv: list[str] | None = None) -> QApplication:
    """QApplicationを生成して返す"""
    if argv is None:
        argv = sys.argv
    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    return app
