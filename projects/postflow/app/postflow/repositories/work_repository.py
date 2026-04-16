from __future__ import annotations

import sqlite3


class WorkRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create(self, name: str, created_at: str, updated_at: str) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO works (name, created_at, updated_at)
            VALUES (?, ?, ?)
            """,
            (name, created_at, updated_at),
        )
        return int(cursor.lastrowid)

    def list_all(self) -> list[sqlite3.Row]:
        cursor = self.connection.execute(
            """
            SELECT *
            FROM works
            ORDER BY updated_at DESC, id DESC
            """
        )
        return list(cursor.fetchall())

    def get_by_id(self, work_id: int) -> sqlite3.Row | None:
        cursor = self.connection.execute(
            "SELECT * FROM works WHERE id = ?",
            (work_id,),
        )
        return cursor.fetchone()

    def update_memo(self, work_id: int, memo: str, updated_at: str) -> None:
        self.connection.execute(
            """
            UPDATE works
            SET memo = ?, updated_at = ?
            WHERE id = ?
            """,
            (memo, updated_at, work_id),
        )

    def update_status(self, work_id: int, status: str, updated_at: str) -> None:
        self.connection.execute(
            """
            UPDATE works
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, updated_at, work_id),
        )

    def update_thumbnail(self, work_id: int, image_id: int | None, updated_at: str) -> None:
        self.connection.execute(
            """
            UPDATE works
            SET thumbnail_image_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (image_id, updated_at, work_id),
        )

    def delete(self, work_id: int) -> None:
        self.connection.execute("DELETE FROM works WHERE id = ?", (work_id,))
