from __future__ import annotations

import sqlite3


class ImageRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create(
        self,
        work_id: int,
        file_path: str,
        sort_order: int,
        is_thumbnail: int,
        created_at: str,
    ) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO images (work_id, file_path, sort_order, is_thumbnail, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (work_id, file_path, sort_order, is_thumbnail, created_at),
        )
        return int(cursor.lastrowid)

    def list_by_work_id(self, work_id: int) -> list[sqlite3.Row]:
        cursor = self.connection.execute(
            """
            SELECT *
            FROM images
            WHERE work_id = ?
            ORDER BY sort_order ASC, id ASC
            """,
            (work_id,),
        )
        return list(cursor.fetchall())

    def get_by_id(self, image_id: int) -> sqlite3.Row | None:
        cursor = self.connection.execute(
            "SELECT * FROM images WHERE id = ?",
            (image_id,),
        )
        return cursor.fetchone()

    def get_max_sort_order(self, work_id: int) -> int:
        cursor = self.connection.execute(
            "SELECT COALESCE(MAX(sort_order), 0) FROM images WHERE work_id = ?",
            (work_id,),
        )
        row = cursor.fetchone()
        return int(row[0]) if row is not None else 0

    def update_sort_order(self, image_id: int, sort_order: int) -> None:
        self.connection.execute(
            "UPDATE images SET sort_order = ? WHERE id = ?",
            (sort_order, image_id),
        )

    def clear_thumbnail_flags(self, work_id: int) -> None:
        self.connection.execute(
            "UPDATE images SET is_thumbnail = 0 WHERE work_id = ?",
            (work_id,),
        )

    def set_thumbnail_flag(self, image_id: int, is_thumbnail: int) -> None:
        self.connection.execute(
            "UPDATE images SET is_thumbnail = ? WHERE id = ?",
            (is_thumbnail, image_id),
        )

    def delete(self, image_id: int) -> None:
        self.connection.execute("DELETE FROM images WHERE id = ?", (image_id,))
