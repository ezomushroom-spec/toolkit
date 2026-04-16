from __future__ import annotations

from postflow.db.database_manager import DatabaseManager
from postflow.repositories.image_repository import ImageRepository
from postflow.repositories.work_check_repository import WorkCheckRepository
from postflow.repositories.work_destination_repository import WorkDestinationRepository
from postflow.repositories.work_repository import WorkRepository
from postflow.utils.datetime_utils import now_iso


VALID_DESTINATION_STATUSES = {"未着手", "準備中", "投稿済み", "不要"}


class StatusService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def update_destination_status(self, work_id: int, destination_id: int, status: str) -> str:
        if status not in VALID_DESTINATION_STATUSES:
            raise ValueError(f"不正な投稿先状態です: {status}")

        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            work_repository = WorkRepository(connection)
            image_repository = ImageRepository(connection)
            work_destination_repository = WorkDestinationRepository(connection)
            work_check_repository = WorkCheckRepository(connection)

            work = work_repository.get_by_id(work_id)
            if work is None:
                raise ValueError(f"作品が見つかりません: {work_id}")

            destinations = work_destination_repository.list_by_work_id(work_id)
            if not any(int(row["destination_id"]) == destination_id for row in destinations):
                raise ValueError(f"投稿先が見つかりません: {destination_id}")

            current_row = next(
                row for row in destinations if int(row["destination_id"]) == destination_id
            )
            posted_at = str(current_row["posted_at"]) if current_row["posted_at"] else None
            if status == "投稿済み" and not posted_at:
                posted_at = timestamp
            elif status != "投稿済み":
                posted_at = None

            work_destination_repository.update_status(
                work_id=work_id,
                destination_id=destination_id,
                status=status,
                updated_at=timestamp,
                posted_at=posted_at,
            )

            final_status = self._calculate_work_status(
                images=image_repository.list_by_work_id(work_id),
                destinations=work_destination_repository.list_by_work_id(work_id),
                checks=work_check_repository.get_by_work_id(work_id),
            )
            work_repository.update_status(work_id, final_status, timestamp)
            connection.commit()
            return final_status

    def recalculate_work_status(self, work_id: int) -> str:
        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            work_repository = WorkRepository(connection)
            image_repository = ImageRepository(connection)
            work_destination_repository = WorkDestinationRepository(connection)
            work_check_repository = WorkCheckRepository(connection)

            work = work_repository.get_by_id(work_id)
            if work is None:
                raise ValueError(f"作品が見つかりません: {work_id}")

            final_status = self._calculate_work_status(
                images=image_repository.list_by_work_id(work_id),
                destinations=work_destination_repository.list_by_work_id(work_id),
                checks=work_check_repository.get_by_work_id(work_id),
            )
            work_repository.update_status(work_id, final_status, timestamp)
            connection.commit()
            return final_status

    def _calculate_work_status(self, images: list, destinations: list, checks) -> str:
        if not images:
            return "下書き"

        if not destinations:
            return "準備中"

        destination_statuses = [str(row["status"]) for row in destinations]
        done_statuses = {"投稿済み", "不要"}
        posted_count = sum(status == "投稿済み" for status in destination_statuses)
        all_done = all(status in done_statuses for status in destination_statuses)

        check_complete = False
        if checks is not None:
            check_complete = all(
                int(checks[key]) == 1
                for key in ("thumbnail_checked", "order_checked", "destination_checked")
            )

        if all_done:
            return "全投稿済み"
        if posted_count > 0:
            return "一部投稿済み"
        if check_complete:
            return "投稿可能"
        return "準備中"
