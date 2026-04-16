from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from postflow.dialogs.confirm_remove_image_dialog import ConfirmRemoveImageDialog
from postflow.services.image_order_service import ImageOrderService
from postflow.services.status_service import StatusService
from postflow.services.work_service import WorkService
from postflow.widgets.destination_status_panel import DestinationStatusPanel


class WorkEditorPage(QWidget):
    back_requested = Signal()
    review_requested = Signal(int)

    def __init__(
        self,
        work_service: WorkService,
        image_order_service: ImageOrderService,
        status_service: StatusService,
    ) -> None:
        super().__init__()
        self.work_service = work_service
        self.image_order_service = image_order_service
        self.status_service = status_service
        self.current_work_id: int | None = None
        self.current_images: list = []
        self._busy = False

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        header_row = QHBoxLayout()
        self.back_button = QPushButton("一覧へ戻る")
        self.title_label = QLabel("画像準備")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: 700;")
        self.status_label = QLabel("")
        header_row.addWidget(self.back_button)
        header_row.addWidget(self.title_label)
        header_row.addStretch()
        header_row.addWidget(self.status_label)
        root_layout.addLayout(header_row)

        body_row = QHBoxLayout()
        body_row.setSpacing(16)
        body_row.addWidget(self._create_image_panel(), 1)
        body_row.addWidget(self._create_preview_panel(), 2)
        body_row.addWidget(self._create_side_panel(), 1)
        root_layout.addLayout(body_row, stretch=1)

        footer_row = QHBoxLayout()
        footer_row.addStretch()
        self.review_button = QPushButton("確認へ進む")
        self.review_button.setProperty("role", "primary")
        footer_row.addWidget(self.review_button)
        root_layout.addLayout(footer_row)

        self.back_button.clicked.connect(self.back_requested.emit)
        self.review_button.clicked.connect(self._emit_review_requested)
        self.image_list.currentItemChanged.connect(self._on_image_selection_changed)
        self.add_image_button.clicked.connect(self._add_images)
        self.remove_image_button.clicked.connect(self._remove_selected_image)
        self.move_up_button.clicked.connect(self._move_selected_image_up)
        self.move_down_button.clicked.connect(self._move_selected_image_down)
        self.set_thumbnail_button.clicked.connect(self._set_selected_as_thumbnail)
        self.save_memo_button.clicked.connect(self._save_memo)
        self.destination_panel.status_changed.connect(self._update_destination_status)

    def load_work(self, work_id: int | None) -> None:
        self.current_work_id = work_id
        self._refresh()

    def _refresh(self) -> None:
        if self.current_work_id is None:
            self.title_label.setText("画像準備")
            self.status_label.clear()
            self.image_list.clear()
            self.destination_panel.set_destinations(None, [])
            self.memo_edit.clear()
            self._show_preview_message("作品が選択されていません。")
            self._update_action_states()
            return

        try:
            detail = self.work_service.get_work_detail(self.current_work_id)
        except ValueError as error:
            QMessageBox.warning(self, "読み込めません", str(error))
            self.back_requested.emit()
            return

        work = detail["work"]
        self.current_images = list(detail["images"])
        self.title_label.setText(f"画像準備 / {work['name']}")
        self.status_label.setText(f"状態: {work['status']}")
        self.memo_edit.setPlainText(str(work["memo"]))
        self.destination_panel.set_destinations(self.current_work_id, list(detail["destinations"]))

        self.image_list.clear()
        for image in self.current_images:
            file_path = str(image["file_path"])
            prefix = "★ " if int(image["is_thumbnail"]) == 1 else ""
            suffix = " [missing]" if not Path(file_path).exists() else ""
            item = QListWidgetItem(f"{prefix}{Path(file_path).name}{suffix}")
            item.setData(Qt.ItemDataRole.UserRole, int(image["id"]))
            self.image_list.addItem(item)

        if self.current_images:
            self.image_list.setCurrentRow(0)
        else:
            self._show_preview_message("画像がありません。左の「画像追加」から登録してください。")
        self._update_action_states()

    def _create_image_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("QFrame { border: 1px solid #d0d7de; border-radius: 12px; }")

        layout = QVBoxLayout(panel)
        title = QLabel("画像一覧")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        self.image_list = QListWidget(panel)
        layout.addWidget(self.image_list, stretch=1)

        button_row = QHBoxLayout()
        self.add_image_button = QPushButton("画像追加")
        self.remove_image_button = QPushButton("画像除外")
        button_row.addWidget(self.add_image_button)
        button_row.addWidget(self.remove_image_button)
        layout.addLayout(button_row)

        order_row = QHBoxLayout()
        self.move_up_button = QPushButton("上へ")
        self.move_down_button = QPushButton("下へ")
        self.set_thumbnail_button = QPushButton("先頭画像に設定")
        order_row.addWidget(self.move_up_button)
        order_row.addWidget(self.move_down_button)
        order_row.addWidget(self.set_thumbnail_button)
        layout.addLayout(order_row)
        return panel

    def _create_preview_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("QFrame { border: 1px solid #d0d7de; border-radius: 12px; }")

        layout = QVBoxLayout(panel)
        title = QLabel("プレビュー")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        self.preview_label = QLabel("画像が選択されていません。")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        self.preview_label.setMinimumHeight(360)
        self.preview_label.setStyleSheet("background: #f8fafc; border-radius: 12px; padding: 16px;")
        layout.addWidget(self.preview_label, stretch=1)

        self.preview_meta_label = QLabel("")
        self.preview_meta_label.setWordWrap(True)
        layout.addWidget(self.preview_meta_label)
        return panel

    def _create_side_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("QFrame { border: 1px solid #d0d7de; border-radius: 12px; }")

        layout = QVBoxLayout(panel)
        title = QLabel("状態とメモ")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        layout.addWidget(QLabel("作品メモ"))
        self.memo_edit = QPlainTextEdit(panel)
        self.memo_edit.setPlaceholderText("作品のメモを入力")
        layout.addWidget(self.memo_edit)

        self.save_memo_button = QPushButton("メモを保存")
        layout.addWidget(self.save_memo_button)

        layout.addWidget(QLabel("投稿先状態"))
        self.destination_panel = DestinationStatusPanel(panel)
        layout.addWidget(self.destination_panel)
        layout.addStretch()
        return panel

    def _on_image_selection_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None = None,
    ) -> None:
        _ = previous
        if current is None:
            self._show_preview_message("画像が選択されていません。")
            return

        image_id = current.data(Qt.ItemDataRole.UserRole)
        image = next((row for row in self.current_images if int(row["id"]) == int(image_id)), None)
        if image is None:
            self._show_preview_message("画像情報を読み込めません。")
            return

        file_path = Path(str(image["file_path"]))
        if not file_path.exists():
            self._show_preview_message(f"画像ファイルが見つかりません。\n{file_path}")
            return

        pixmap = QPixmap(str(file_path))
        if pixmap.isNull():
            self._show_preview_message(f"画像を読み込めません。\n{file_path}")
            return

        scaled = pixmap.scaled(
            720,
            480,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)
        self.preview_meta_label.setText(
            f"ファイル: {file_path}\n順番: {image['sort_order']} / 先頭画像: {'はい' if int(image['is_thumbnail']) == 1 else 'いいえ'}"
        )
        self._update_action_states()

    def _show_preview_message(self, message: str) -> None:
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText(message)
        self.preview_meta_label.clear()
        self._update_action_states()

    def _selected_image_id(self) -> int | None:
        item = self.image_list.currentItem()
        if item is None:
            return None
        return int(item.data(Qt.ItemDataRole.UserRole))

    def _add_images(self) -> None:
        if self.current_work_id is None:
            return
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "画像を選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp *.bmp *.gif)",
        )
        if not file_paths:
            return
        try:
            self._set_busy(True)
            self.image_order_service.add_images(self.current_work_id, file_paths)
        except ValueError as error:
            QMessageBox.warning(self, "画像を追加できません", str(error))
        finally:
            self._set_busy(False)
        self._refresh()

    def _remove_selected_image(self) -> None:
        image_id = self._selected_image_id()
        if image_id is None:
            QMessageBox.information(self, "画像未選択", "除外する画像を選択してください。")
            return
        image = next((row for row in self.current_images if int(row["id"]) == image_id), None)
        if image is None:
            return
        dialog = ConfirmRemoveImageDialog(Path(str(image["file_path"])).name, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self._set_busy(True)
            self.image_order_service.remove_image(image_id)
        except ValueError as error:
            QMessageBox.warning(self, "画像を除外できません", str(error))
        finally:
            self._set_busy(False)
        self._refresh()

    def _move_selected_image_up(self) -> None:
        image_id = self._selected_image_id()
        if image_id is None:
            return
        try:
            self._set_busy(True)
            self.image_order_service.move_image_up(image_id)
        except ValueError as error:
            QMessageBox.warning(self, "順番を変更できません", str(error))
        finally:
            self._set_busy(False)
        self._refresh()

    def _move_selected_image_down(self) -> None:
        image_id = self._selected_image_id()
        if image_id is None:
            return
        try:
            self._set_busy(True)
            self.image_order_service.move_image_down(image_id)
        except ValueError as error:
            QMessageBox.warning(self, "順番を変更できません", str(error))
        finally:
            self._set_busy(False)
        self._refresh()

    def _set_selected_as_thumbnail(self) -> None:
        image_id = self._selected_image_id()
        if image_id is None:
            return
        try:
            self._set_busy(True)
            self.image_order_service.set_thumbnail(image_id)
        except ValueError as error:
            QMessageBox.warning(self, "先頭画像を設定できません", str(error))
        finally:
            self._set_busy(False)
        self._refresh()

    def _save_memo(self) -> None:
        if self.current_work_id is None:
            return
        try:
            self._set_busy(True)
            self.work_service.update_work_memo(self.current_work_id, self.memo_edit.toPlainText())
        except ValueError as error:
            QMessageBox.warning(self, "メモを保存できません", str(error))
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

    def _emit_review_requested(self) -> None:
        self.review_requested.emit(self.current_work_id or 1)

    def _update_action_states(self) -> None:
        selected_id = self._selected_image_id()
        has_images = bool(self.current_images)
        selected_image = next(
            (row for row in self.current_images if selected_id is not None and int(row["id"]) == selected_id),
            None,
        )
        current_index = self.image_list.currentRow()
        self.remove_image_button.setEnabled(not self._busy and selected_id is not None)
        self.move_up_button.setEnabled(not self._busy and has_images and current_index > 0)
        self.move_down_button.setEnabled(
            not self._busy and has_images and 0 <= current_index < len(self.current_images) - 1
        )
        self.set_thumbnail_button.setEnabled(
            not self._busy
            and selected_image is not None
            and int(selected_image["is_thumbnail"]) != 1
        )
        self.review_button.setEnabled(not self._busy and self.current_work_id is not None)
        self.save_memo_button.setEnabled(not self._busy and self.current_work_id is not None)
        self.add_image_button.setEnabled(not self._busy and self.current_work_id is not None)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._update_action_states()
