from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from postflow.dialogs.confirm_delete_work_dialog import ConfirmDeleteWorkDialog
from postflow.dialogs.create_work_dialog import CreateWorkDialog
from postflow.services.work_service import WorkService
from postflow.widgets.work_card_widget import WorkCardWidget
from postflow.widgets.works_filter_bar import WorksFilterBar


class WorksListPage(QWidget):
    open_editor_requested = Signal(int)
    open_review_requested = Signal(int)

    def __init__(self, work_service: WorkService) -> None:
        super().__init__()
        self.work_service = work_service
        self._works: list[dict[str, object]] = []
        self._search_text = ""
        self._status_filter = "すべて"

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        title = QLabel("作品一覧")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        root_layout.addWidget(title)

        description = QLabel(
            "投稿準備の進み具合を一覧し、作品の編集と確認へすぐ移れます。"
        )
        description.setWordWrap(True)
        root_layout.addWidget(description)

        self.filter_bar = WorksFilterBar(self)
        root_layout.addWidget(self.filter_bar)

        button_row = QVBoxLayout()
        self.new_work_button = QPushButton("新規追加")
        self.new_work_button.setProperty("role", "primary")
        button_row.addWidget(self.new_work_button)
        root_layout.addLayout(button_row)

        self.placeholder = QLabel("作品はまだありません。右上の「新規追加」から始めてください。")
        self.placeholder.setStyleSheet(
            "border: 1px solid #d0d7de; border-radius: 12px; padding: 32px;"
        )
        self.placeholder.setMinimumHeight(240)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(self.placeholder)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget(self.scroll_area)
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_widget)
        root_layout.addWidget(self.scroll_area, stretch=1)

        self.new_work_button.clicked.connect(self._create_work)
        self.filter_bar.filters_changed.connect(self._apply_filters)

        self.reload()

    def reload(self) -> None:
        self._works = self.work_service.list_work_summaries()
        self._render_cards()

    def _apply_filters(self, search_text: str, status_filter: str) -> None:
        self._search_text = search_text
        self._status_filter = status_filter
        self._render_cards()

    def _render_cards(self) -> None:
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        filtered_works = []
        for work in self._works:
            work_row = work["work"]
            if self._search_text and self._search_text.lower() not in str(work_row["name"]).lower():
                continue
            if self._status_filter != "すべて" and str(work_row["status"]) != self._status_filter:
                continue
            filtered_works.append(work)

        if not self._works:
            self.placeholder.setText("作品はまだありません。右上の「新規追加」から始めてください。")
        elif not filtered_works:
            self.placeholder.setText("条件に一致する作品がありません。検索語や状態を見直してください。")
        self.placeholder.setVisible(not filtered_works)
        self.scroll_area.setVisible(bool(filtered_works))

        for work in filtered_works:
            card = WorkCardWidget(work, self)
            card.open_requested.connect(self.open_editor_requested.emit)
            card.review_requested.connect(self.open_review_requested.emit)
            card.delete_requested.connect(self._confirm_delete_work)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def _create_work(self) -> None:
        dialog = CreateWorkDialog(self)
        while dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                work_id = self.work_service.create_work(dialog.work_name())
            except ValueError as error:
                dialog.set_error(str(error))
                continue
            self.reload()
            self.open_editor_requested.emit(work_id)
            return

    def _confirm_delete_work(self, work_id: int) -> None:
        summary = next((row for row in self._works if int(row["work"]["id"]) == work_id), None)
        if summary is None:
            QMessageBox.warning(self, "削除できません", "対象の作品が見つかりません。")
            self.reload()
            return

        dialog = ConfirmDeleteWorkDialog(str(summary["work"]["name"]), self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            self.work_service.delete_work(work_id)
        except ValueError as error:
            QMessageBox.warning(self, "削除できません", str(error))
            return
        self.reload()
