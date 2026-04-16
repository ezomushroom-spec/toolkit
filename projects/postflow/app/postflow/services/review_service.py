from __future__ import annotations

from postflow.db.database_manager import DatabaseManager
from postflow.repositories.work_check_repository import WorkCheckRepository
from postflow.services.status_service import StatusService
from postflow.utils.datetime_utils import now_iso


class ReviewService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager
        self.status_service = StatusService(database_manager)

    def update_review_check(
        self,
        work_id: int,
        thumbnail_checked: bool,
        order_checked: bool,
        destination_checked: bool,
    ) -> str:
        final_checked_at = now_iso() if all(
            [thumbnail_checked, order_checked, destination_checked]
        ) else None

        with self.database_manager.connect() as connection:
            work_check_repository = WorkCheckRepository(connection)
            checks = work_check_repository.get_by_work_id(work_id)
            if checks is None:
                raise ValueError(f"確認状態が見つかりません: {work_id}")

            work_check_repository.update(
                work_id=work_id,
                thumbnail_checked=int(thumbnail_checked),
                order_checked=int(order_checked),
                destination_checked=int(destination_checked),
                final_checked_at=final_checked_at,
            )
            connection.commit()

        return self.status_service.recalculate_work_status(work_id)
