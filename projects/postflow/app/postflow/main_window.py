from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from postflow.db.database_manager import DatabaseManager
from postflow.pages.work_editor_page import WorkEditorPage
from postflow.pages.work_review_page import WorkReviewPage
from postflow.pages.works_list_page import WorksListPage
from postflow.services.image_order_service import ImageOrderService
from postflow.services.review_service import ReviewService
from postflow.services.status_service import StatusService
from postflow.services.work_service import WorkService


class MainWindow(QMainWindow):
    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()
        self.database_manager = database_manager
        self.work_service = WorkService(database_manager)
        self.image_order_service = ImageOrderService(database_manager)
        self.status_service = StatusService(database_manager)
        self.review_service = ReviewService(database_manager)
        self.current_work_id: int | None = None

        self.setWindowTitle("PostFlow")
        self.resize(1280, 800)

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.works_list_page = WorksListPage(work_service=self.work_service)
        self.work_editor_page = WorkEditorPage(
            work_service=self.work_service,
            image_order_service=self.image_order_service,
            status_service=self.status_service,
        )
        self.work_review_page = WorkReviewPage(
            work_service=self.work_service,
            status_service=self.status_service,
            review_service=self.review_service,
        )

        self.stack.addWidget(self.works_list_page)
        self.stack.addWidget(self.work_editor_page)
        self.stack.addWidget(self.work_review_page)

        self.works_list_page.open_editor_requested.connect(self.open_work_editor)
        self.works_list_page.open_review_requested.connect(self.open_work_review)
        self.work_editor_page.back_requested.connect(self.open_works_list)
        self.work_editor_page.review_requested.connect(self.open_work_review)
        self.work_review_page.back_to_list_requested.connect(self.open_works_list)
        self.work_review_page.back_to_editor_requested.connect(self.open_work_editor)

        self.open_works_list()

    def open_works_list(self) -> None:
        self.works_list_page.reload()
        self.stack.setCurrentWidget(self.works_list_page)

    def open_work_editor(self, work_id: int | None = None) -> None:
        self.current_work_id = work_id
        self.work_editor_page.load_work(work_id)
        self.stack.setCurrentWidget(self.work_editor_page)

    def open_work_review(self, work_id: int | None = None) -> None:
        self.current_work_id = work_id
        self.work_review_page.load_work(work_id)
        self.stack.setCurrentWidget(self.work_review_page)
