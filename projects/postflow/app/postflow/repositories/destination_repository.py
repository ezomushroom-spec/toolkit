from __future__ import annotations

import sqlite3


class DestinationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_all(self) -> list[sqlite3.Row]:
        cursor = self.connection.execute(
            """
            SELECT *
            FROM destinations
            ORDER BY sort_order ASC, id ASC
            """
        )
        return list(cursor.fetchall())

    def list_active(self) -> list[sqlite3.Row]:
        cursor = self.connection.execute(
            """
            SELECT *
            FROM destinations
            WHERE is_active = 1
            ORDER BY sort_order ASC, id ASC
            """
        )
        return list(cursor.fetchall())
