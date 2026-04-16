"""SQLite接続管理（Databaseクラス — UIスレッド専用）"""

import os
import sqlite3
import threading

from civitai_downloader.app import get_app_data_dir


def get_db_path() -> str:
    """DBファイルパスを返す"""
    return os.path.join(get_app_data_dir(), "civitai_downloader.db")


class Database:
    """UIスレッド専用のSQLiteデータベース接続管理クラス"""

    def __init__(self):
        self._connection: sqlite3.Connection | None = None
        self._owner_thread: int | None = None

    def connect(self, db_path: str | None = None):
        """データベースに接続する（UIスレッドから呼び出すこと）"""
        if self._connection is not None:
            return

        if db_path is None:
            db_path = get_db_path()

        self._owner_thread = threading.get_ident()
        self._connection = sqlite3.connect(db_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")

    def get_connection(self) -> sqlite3.Connection:
        """接続を取得する（オーナースレッドからのみ呼び出し可能）"""
        if self._connection is None:
            raise RuntimeError("データベース未接続です。connect()を先に呼び出してください。")
        current = threading.get_ident()
        if current != self._owner_thread:
            raise RuntimeError(
                f"別スレッドからのDB操作は禁止です。"
                f"(owner={self._owner_thread}, caller={current})"
            )
        return self._connection

    def close(self):
        """接続を閉じる"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._owner_thread = None
