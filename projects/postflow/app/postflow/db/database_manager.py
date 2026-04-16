from __future__ import annotations

import sqlite3
from pathlib import Path

from postflow.config import APP_DATA_DIR, DB_PATH
from postflow.db.seed import seed_initial_data


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(self._load_schema())
            seed_initial_data(connection)
            connection.commit()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _load_schema(self) -> str:
        schema_path = Path(__file__).with_name("schema.sql")
        return schema_path.read_text(encoding="utf-8")
