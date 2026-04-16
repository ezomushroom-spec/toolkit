from __future__ import annotations

import sqlite3


INITIAL_DESTINATIONS = [
    ("Pixiv", 1, 10),
    ("X", 1, 20),
    ("Instagram", 1, 30),
    ("その他", 1, 40),
]


def seed_initial_data(connection: sqlite3.Connection) -> None:
    connection.executemany(
        """
        INSERT OR IGNORE INTO destinations (name, is_active, sort_order)
        VALUES (?, ?, ?)
        """,
        INITIAL_DESTINATIONS,
    )
