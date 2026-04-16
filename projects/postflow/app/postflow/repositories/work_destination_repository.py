from __future__ import annotations

import sqlite3


class WorkDestinationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_initial(self, work_id: int, destination_id: int, updated_at: str) -> None:
        self.connection.execute(
            """
            INSERT INTO work_destinations (work_id, destination_id, updated_at)
            VALUES (?, ?, ?)
            """,
            (work_id, destination_id, updated_at),
        )

    def list_by_work_id(self, work_id: int) -> list[sqlite3.Row]:
        cursor = self.connection.execute(
            """
            SELECT wd.*, d.name AS destination_name, d.sort_order AS destination_sort_order
            FROM work_destinations wd
            JOIN destinations d ON d.id = wd.destination_id
            WHERE wd.work_id = ?
            ORDER BY d.sort_order ASC, d.id ASC
            """,
            (work_id,),
        )
        return list(cursor.fetchall())

    def update_status(
        self,
        work_id: int,
        destination_id: int,
        status: str,
        updated_at: str,
        posted_at: str | None,
    ) -> None:
        self.connection.execute(
            """
            UPDATE work_destinations
            SET status = ?, updated_at = ?, posted_at = ?
            WHERE work_id = ? AND destination_id = ?
            """,
            (status, updated_at, posted_at, work_id, destination_id),
        )
