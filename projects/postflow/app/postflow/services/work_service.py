from __future__ import annotations

from postflow.db.database_manager import DatabaseManager
from postflow.repositories.destination_repository import DestinationRepository
from postflow.repositories.image_repository import ImageRepository
from postflow.repositories.work_check_repository import WorkCheckRepository
from postflow.repositories.work_destination_repository import WorkDestinationRepository
from postflow.repositories.work_repository import WorkRepository
from postflow.utils.datetime_utils import now_iso


class WorkService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def create_work(self, name: str) -> int:
        work_name = name.strip()
        if not work_name:
            raise ValueError("作品名を入力してください。")

        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            work_repository = WorkRepository(connection)
            destination_repository = DestinationRepository(connection)
            work_destination_repository = WorkDestinationRepository(connection)
            work_check_repository = WorkCheckRepository(connection)

            work_id = work_repository.create(
                name=work_name,
                created_at=timestamp,
                updated_at=timestamp,
            )

            for destination in destination_repository.list_active():
                work_destination_repository.create_initial(
                    work_id=work_id,
                    destination_id=int(destination["id"]),
                    updated_at=timestamp,
                )

            work_check_repository.create_initial(work_id)
            connection.commit()
            return work_id

    def get_work_detail(self, work_id: int) -> dict[str, object]:
        with self.database_manager.connect() as connection:
            work_repository = WorkRepository(connection)
            image_repository = ImageRepository(connection)
            work_destination_repository = WorkDestinationRepository(connection)
            work_check_repository = WorkCheckRepository(connection)

            work = work_repository.get_by_id(work_id)
            if work is None:
                raise ValueError(f"作品が見つかりません: {work_id}")

            return {
                "work": work,
                "images": image_repository.list_by_work_id(work_id),
                "destinations": work_destination_repository.list_by_work_id(work_id),
                "checks": work_check_repository.get_by_work_id(work_id),
            }

    def list_works(self) -> list:
        with self.database_manager.connect() as connection:
            work_repository = WorkRepository(connection)
            return work_repository.list_all()

    def list_work_summaries(self) -> list[dict[str, object]]:
        with self.database_manager.connect() as connection:
            work_repository = WorkRepository(connection)
            image_repository = ImageRepository(connection)
            work_destination_repository = WorkDestinationRepository(connection)

            summaries: list[dict[str, object]] = []
            for work in work_repository.list_all():
                work_id = int(work["id"])
                images = image_repository.list_by_work_id(work_id)
                destinations = work_destination_repository.list_by_work_id(work_id)
                thumbnail = next((row for row in images if int(row["is_thumbnail"]) == 1), None)
                summaries.append(
                    {
                        "work": work,
                        "image_count": len(images),
                        "thumbnail_path": str(thumbnail["file_path"]) if thumbnail else None,
                        "destination_summary": [
                            {
                                "name": str(row["destination_name"]),
                                "status": str(row["status"]),
                            }
                            for row in destinations
                        ],
                    }
                )
            return summaries

    def delete_work(self, work_id: int) -> None:
        with self.database_manager.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            work_repository = WorkRepository(connection)
            if work_repository.get_by_id(work_id) is None:
                raise ValueError(f"作品が見つかりません: {work_id}")
            work_repository.delete(work_id)
            connection.commit()

    def update_work_memo(self, work_id: int, memo: str) -> None:
        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            work_repository = WorkRepository(connection)
            if work_repository.get_by_id(work_id) is None:
                raise ValueError(f"作品が見つかりません: {work_id}")
            work_repository.update_memo(work_id, memo, timestamp)
            connection.commit()
