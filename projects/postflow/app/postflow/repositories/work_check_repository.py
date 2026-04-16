from __future__ import annotations

import sqlite3


class WorkCheckRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_initial(self, work_id: int) -> None:
        self.connection.execute(
            """
            INSERT INTO work_checks (work_id)
            VALUES (?)
            """,
            (work_id,),
        )

    def get_by_work_id(self, work_id: int) -> sqlite3.Row | None:
        cursor = self.connection.execute(
            "SELECT * FROM work_checks WHERE work_id = ?",
            (work_id,),
        )
        return cursor.fetchone()

    def update(
        self,
        work_id: int,
        thumbnail_checked: int,
        order_checked: int,
        destination_checked: int,
        final_checked_at: str | None,
    ) -> None:
        self.connection.execute(
            """
            UPDATE work_checks
            SET thumbnail_checked = ?,
                order_checked = ?,
                destination_checked = ?,
                final_checked_at = ?
            WHERE work_id = ?
            """,
            (
                thumbnail_checked,
                order_checked,
                destination_checked,
                final_checked_at,
                work_id,
            ),
        )
