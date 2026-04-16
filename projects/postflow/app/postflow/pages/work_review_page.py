from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from postflow.services.review_service import ReviewService
from postflow.services.status_service import StatusService
from postflow.services.work_service import WorkService
from postflow.widgets.destination_status_panel import DestinationStatusPanel
from postflow.widgets.review_checklist_widget import ReviewChecklistWidget


class WorkReviewPage(QWidget):
    back_to_editor_requested = Signal(int)
    back_to_list_requested = Signal()

    def __init__(
        self,
        work_service: WorkService,
        status_service: StatusService,
        review_service: ReviewService,
    ) -> None:
        super().__init__()
        self.work_service = work_service
        self.status_service = status_service
        self.review_service = review_service
        self.current_work_id: int | None = None
        self.current_images: list = []
        self._busy = False

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        header_row = QHBoxLayout()
        self.back_to_list_button = QPushButton("一覧へ戻る")
        self.title_label = QLabel("投稿確認")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: 700;")
        self.status_label = QLabel("")
        header_row.addWidget(self.back_to_list_button)
        header_row.addWidget(self.title_label)
        header_row.addStretch()
        header_row.addWidget(self.status_label)
        root_layout.addLayout(header_row)

        body_row = QHBoxLayout()
        body_row.setSpacing(16)
        body_row.addWidget(self._create_preview_panel(), 2)
        body_row.addWidget(self._create_side_panel(), 1)
        root_layout.addLayout(body_row, stretch=1)

        footer_row = QHBoxLayout()
        self.back_to_editor_button = QPushButton("編集に戻る")
        self.update_status_button = QPushButton("投稿後に状態更新")
        self.update_status_button.setProperty("role", "primary")
        footer_row.addStretch()
        footer_row.addWidget(self.back_to_editor_button)
        footer_row.addWidget(self.update_status_button)
        root_layout.addLayout(footer_row)

        self.back_to_list_button.clicked.connect(self.back_to_list_requested.emit)
        self.back_to_editor_button.clicked.connect(self._emit_back_to_editor_requested)
        self.checklist_widget.checks_changed.connect(self._update_checks)
        self.destination_panel.status_changed.connect(self._update_destination_status)
        self.update_status_button.clicked.connect(self._refresh)

    def load_work(self, work_id: int | None) -> None:
        self.current_work_id = work_id
        self._refresh()

    def _refresh(self) -> None:
        if self.current_work_id is None:
            self.title_label.setText("投稿確認")
            self.status_label.clear()
            self._show_preview_message("作品が選択されていません。")
            self.order_list.clear()
            self.destination_panel.set_destinations(None, [])
            self.checklist_widget.set_values(False, False, False)
            self._update_action_states()
            return

        try:
            detail = self.work_service.get_work_detail(self.current_work_id)
        except ValueError as error:
            QMessageBox.warning(self, "読み込めません", str(error))
            self.back_to_list_requested.emit()
            return

        work = detail["work"]
        self.current_images = list(detail["images"])
        self.title_label.setText(f"投稿確認 / {work['name']}")
        self.status_label.setText(f"状態: {work['status']}")
        self.destination_panel.set_destinations(self.current_work_id, list(detail["destinations"]))

        checks = detail["checks"]
        self.checklist_widget.set_values(
            bool(checks and int(checks["thumbnail_checked"]) == 1),
            bool(checks and int(checks["order_checked"]) == 1),
            bool(checks and int(checks["destination_checked"]) == 1),
        )

        self.order_list.clear()
        for image in self.current_images:
            prefix = "★ " if int(image["is_thumbnail"]) == 1 else ""
            suffix = " [missing]" if not Path(str(image["file_path"])).exists() else ""
            item = QListWidgetItem(
                f"{image['sort_order']}. {prefix}{Path(str(image['file_path'])).name}{suffix}"
            )
            self.order_list.addItem(item)

        thumbnail = next((row for row in self.current_images if int(row["is_thumbnail"]) == 1), None)
        if thumbnail is None:
            self._show_preview_message("先頭画像が未設定です。")
            self._update_action_states()
            return

        file_path = Path(str(thumbnail["file_path"]))
        if not file_path.exists():
            self._show_preview_message(f"先頭画像ファイルが見つかりません。\n{file_path}")
            self._update_action_states()
            return

        pixmap = QPixmap(str(file_path))
        if pixmap.isNull():
            self._show_preview_message(f"先頭画像を読み込めません。\n{file_path}")
            self._update_action_states()
            return

        self.preview_label.setPixmap(
            pixmap.scaled(
                720,
                420,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.preview_meta_label.setText(f"先頭画像: {file_path.name}\nパス: {file_path}")
        self._update_action_states()

    def _create_preview_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("QFrame { border: 1px solid #d0d7de; border-radius: 12px; }")

        layout = QVBoxLayout(panel)
        title = QLabel("先頭画像と投稿順")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        self.preview_label = QLabel("確認対象がありません。")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        self.preview_label.setMinimumHeight(320)
        self.preview_label.setStyleSheet("background: #f8fafc; border-radius: 12px; padding: 16px;")
        layout.addWidget(self.preview_label)

        self.preview_meta_label = QLabel("")
        self.preview_meta_label.setWordWrap(True)
        layout.addWidget(self.preview_meta_label)

        self.order_list = QListWidget(panel)
        layout.addWidget(self.order_list, stretch=1)
        return panel

    def _create_side_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("QFrame { border: 1px solid #d0d7de; border-radius: 12px; }")

        layout = QVBoxLayout(panel)
        title = QLabel("投稿先状態と確認")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        layout.addWidget(QLabel("投稿先状態"))
        self.destination_panel = DestinationStatusPanel(panel)
        layout.addWidget(self.destination_panel)

        layout.addWidget(QLabel("確認チェック"))
        self.checklist_widget = ReviewChecklistWidget(panel)
        layout.addWidget(self.checklist_widget)
        layout.addStretch()
        return panel

    def _show_preview_message(self, message: str) -> None:
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText(message)
        self.preview_meta_label.clear()
        self._update_action_states()

    def _update_checks(
        self,
        thumbnail_checked: bool,
        order_checked: bool,
        destination_checked: bool,
    ) -> None:
        if self.current_work_id is None:
            return
        try:
            self._set_busy(True)
            self.review_service.update_review_check(
                self.current_work_id,
                thumbnail_checked,
                order_checked,
                destination_checked,
            )
        except ValueError as error:
            QMessageBox.warning(self, "確認状態を更新できません", str(error))
        finally:
            self._set_busy(False)
        self._refresh()

    def _update_destination_status(self, work_id: int, destination_id: int, status: str) -> None:
        try:
            self._set_busy(True)
            self.status_service.update_destination_status(work_id, destination_id, status)
        except ValueError as error:
            QMessageBox.warning(self, "状態を更新できません", str(error))
        finally:
            self._set_busy(False)
        self._refresh()

    def _emit_back_to_editor_requested(self) -> None:
        self.back_to_editor_requested.emit(self.current_work_id or 1)

    def _update_action_states(self) -> None:
        enabled = not self._busy and self.current_work_id is not None
        self.back_to_editor_button.setEnabled(enabled)
        self.update_status_button.setEnabled(enabled)
        self.checklist_widget.setEnabled(enabled)
        self.destination_panel.setEnabled(enabled)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._update_action_states()
