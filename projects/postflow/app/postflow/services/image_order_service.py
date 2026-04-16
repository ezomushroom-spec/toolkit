from __future__ import annotations

from postflow.db.database_manager import DatabaseManager
from postflow.repositories.image_repository import ImageRepository
from postflow.repositories.work_repository import WorkRepository
from postflow.services.status_service import StatusService
from postflow.utils.datetime_utils import now_iso


class ImageOrderService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager
        self.status_service = StatusService(database_manager)

    def add_images(self, work_id: int, file_paths: list[str]) -> list[int]:
        if not file_paths:
            return []

        created_ids: list[int] = []
        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            image_repository = ImageRepository(connection)
            work_repository = WorkRepository(connection)

            work = work_repository.get_by_id(work_id)
            if work is None:
                raise ValueError(f"作品が見つかりません: {work_id}")

            existing_images = image_repository.list_by_work_id(work_id)
            existing_paths = {str(row["file_path"]) for row in existing_images}
            sort_order = image_repository.get_max_sort_order(work_id)

            for file_path in file_paths:
                if file_path in existing_paths:
                    continue
                sort_order += 1
                image_id = image_repository.create(
                    work_id=work_id,
                    file_path=file_path,
                    sort_order=sort_order,
                    is_thumbnail=0,
                    created_at=timestamp,
                )
                created_ids.append(image_id)

            images = image_repository.list_by_work_id(work_id)
            if images and work["thumbnail_image_id"] is None:
                first_image_id = int(images[0]["id"])
                image_repository.clear_thumbnail_flags(work_id)
                image_repository.set_thumbnail_flag(first_image_id, 1)
                work_repository.update_thumbnail(work_id, first_image_id, timestamp)
            elif created_ids:
                work_repository.update_status(work_id, str(work["status"]), timestamp)

            connection.commit()
        self.status_service.recalculate_work_status(work_id)
        return created_ids

    def move_image_up(self, image_id: int) -> None:
        self._swap_with_neighbor(image_id=image_id, direction=-1)

    def move_image_down(self, image_id: int) -> None:
        self._swap_with_neighbor(image_id=image_id, direction=1)

    def set_thumbnail(self, image_id: int) -> None:
        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            image_repository = ImageRepository(connection)
            work_repository = WorkRepository(connection)

            image = image_repository.get_by_id(image_id)
            if image is None:
                raise ValueError(f"画像が見つかりません: {image_id}")

            work_id = int(image["work_id"])
            image_repository.clear_thumbnail_flags(work_id)
            image_repository.set_thumbnail_flag(image_id, 1)
            work_repository.update_thumbnail(work_id, image_id, timestamp)
            connection.commit()

    def remove_image(self, image_id: int) -> None:
        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            image_repository = ImageRepository(connection)
            work_repository = WorkRepository(connection)

            image = image_repository.get_by_id(image_id)
            if image is None:
                raise ValueError(f"画像が見つかりません: {image_id}")

            work_id = int(image["work_id"])
            was_thumbnail = int(image["is_thumbnail"]) == 1
            image_repository.delete(image_id)
            self._normalize_sort_order(connection, work_id)

            images = image_repository.list_by_work_id(work_id)
            replacement_id = int(images[0]["id"]) if images else None
            if was_thumbnail:
                image_repository.clear_thumbnail_flags(work_id)
                if replacement_id is not None:
                    image_repository.set_thumbnail_flag(replacement_id, 1)
            work_repository.update_thumbnail(work_id, replacement_id, timestamp)
            connection.commit()
        self.status_service.recalculate_work_status(work_id)

    def _swap_with_neighbor(self, image_id: int, direction: int) -> None:
        timestamp = now_iso()
        with self.database_manager.connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            image_repository = ImageRepository(connection)
            work_repository = WorkRepository(connection)

            image = image_repository.get_by_id(image_id)
            if image is None:
                raise ValueError(f"画像が見つかりません: {image_id}")

            work_id = int(image["work_id"])
            images = image_repository.list_by_work_id(work_id)
            target_index = next(
                (index for index, row in enumerate(images) if int(row["id"]) == image_id),
                None,
            )
            if target_index is None:
                raise ValueError(f"画像が見つかりません: {image_id}")

            neighbor_index = target_index + direction
            if neighbor_index < 0 or neighbor_index >= len(images):
                return

            current_row = images[target_index]
            neighbor_row = images[neighbor_index]
            current_order = int(current_row["sort_order"])
            neighbor_order = int(neighbor_row["sort_order"])

            image_repository.update_sort_order(int(current_row["id"]), neighbor_order)
            image_repository.update_sort_order(int(neighbor_row["id"]), current_order)
            work_repository.update_status(work_id, str(work_repository.get_by_id(work_id)["status"]), timestamp)
            connection.commit()

    def _normalize_sort_order(self, connection, work_id: int) -> None:
        image_repository = ImageRepository(connection)
        for index, image in enumerate(image_repository.list_by_work_id(work_id), start=1):
            image_repository.update_sort_order(int(image["id"]), index)
