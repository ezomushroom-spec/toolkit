"""通知タブ"""

import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QLabel,
    QHeaderView, QMessageBox,
)
from civitai_downloader.ui.widgets import StyledTableWidget, PrimaryButton
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QColor

from civitai_downloader.db.connection import Database
from civitai_downloader.db import repository as repo

logger = logging.getLogger(__name__)


class NotificationTab(QWidget):
    """通知一覧タブ"""

    navigate_requested = Signal(str)  # URL
    notification_read = Signal()

    def __init__(self, db: Database, update_checker=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._update_checker = update_checker
        self._notification_ids: dict[int, str] = {}  # row → notification_id
        self._checking = False
        self._detected_during_check = 0

        self._setup_ui()
        self._load_notifications()

        if self._update_checker:
            self._update_checker.check_progress.connect(self._on_check_progress)
            self._update_checker.new_version_found.connect(self._on_new_version_found)
            self._update_checker.check_finished.connect(self._on_check_finished)

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 操作ボタン
        btn_layout = QHBoxLayout()
        self._btn_check = PrimaryButton("手動チェック実行")
        self._btn_check.clicked.connect(self._on_manual_check)
        self._btn_mark_all = PrimaryButton("すべて既読にする")
        self._btn_mark_all.clicked.connect(self._mark_all_read)
        self._btn_delete_all = PrimaryButton("すべて削除")
        self._btn_delete_all.clicked.connect(self._delete_all_notifications)
        btn_layout.addWidget(self._btn_check)
        btn_layout.addWidget(self._btn_mark_all)
        btn_layout.addWidget(self._btn_delete_all)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._status_label = QLabel("前回チェック: 未実行")
        layout.addWidget(self._status_label)

        # 通知テーブル
        self._table = StyledTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels([
            "●", "モデル名", "新バージョン", "検知日"
        ])
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.setSelectionBehavior(StyledTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(StyledTableWidget.EditTrigger.NoEditTriggers)
        self._table.cellClicked.connect(self._on_cell_clicked)

        layout.addWidget(self._table)

    @Slot()
    def _load_notifications(self):
        """通知一覧を読み込み"""
        repo.prune_notifications(self._db)
        self._table.setRowCount(0)
        self._notification_ids.clear()

        notifications = repo.get_all_notifications(self._db)
        for notif in notifications:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._notification_ids[row] = notif["id"]

            # 未読/既読マーク
            is_read = notif["is_read"]
            mark = "⚪" if is_read else "🔴"
            mark_item = QTableWidgetItem(mark)
            mark_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, mark_item)

            # モデル名
            name_item = QTableWidgetItem(notif.get("model_name", ""))
            if not is_read:
                from civitai_downloader.ui.theme.theme_manager import ThemeManager
                tm = ThemeManager.instance()
                accent = tm.get_color("accent") if tm else "#7c6ff7"
                name_item.setForeground(QColor(accent))
            self._table.setItem(row, 1, name_item)

            # 新バージョン
            ver_item = QTableWidgetItem(notif.get("new_version_name", ""))
            self._table.setItem(row, 2, ver_item)

            # 検知日
            detected = notif.get("detected_at", "")
            try:
                dt = datetime.fromisoformat(detected)
                date_str = dt.strftime("%m/%d %H:%M")
            except (ValueError, TypeError):
                date_str = detected
            self._table.setItem(row, 3, QTableWidgetItem(date_str))

            # URL情報をデータとして保持
            name_item.setData(Qt.ItemDataRole.UserRole, notif.get("model_url", ""))

    @Slot(int, int)
    def _on_cell_clicked(self, row: int, col: int):
        """行クリック→ブラウズタブでモデルページを開く"""
        name_item = self._table.item(row, 1)
        if not name_item:
            return

        url = name_item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.navigate_requested.emit(url)

        # 既読にする
        notif_id = self._notification_ids.get(row)
        if notif_id:
            repo.mark_notification_read(self._db, notif_id)
            mark_item = self._table.item(row, 0)
            if mark_item:
                mark_item.setText("⚪")
            self.notification_read.emit()

    @Slot()
    def _on_manual_check(self):
        """手動更新チェック"""
        if not self._update_checker:
            self._status_label.setText("更新チェック機能が初期化されていません")
            return
        if self._checking:
            self._status_label.setText("更新チェック中です")
            return

        tracked = repo.get_all_tracked_models(self._db)
        if not tracked:
            self._status_label.setText("追跡中モデルがありません")
            return

        api_key = repo.get_setting(self._db, "api_key", "")
        started = self._update_checker.start_check(tracked, api_key)
        if not started:
            self._status_label.setText("更新チェックは既に実行中です")
            return

        self._checking = True
        self._detected_during_check = 0
        self._btn_check.setEnabled(False)
        self._btn_check.setText("チェック中...")
        self._status_label.setText(f"更新チェック中: 0 / {len(tracked)}")

    @Slot(int, int)
    def _on_check_progress(self, current: int, total: int):
        """更新チェック進捗を表示"""
        self._status_label.setText(
            f"更新チェック中: {current} / {total}（検出 {self._detected_during_check}件）"
        )

    @Slot(object, str, object, str, str)
    def _on_new_version_found(
        self,
        model_id,
        model_name: str,
        version_id,
        version_name: str,
        model_url: str,
    ):
        """手動チェック中の検出件数を数える"""
        if self._checking:
            self._detected_during_check += 1

    @Slot()
    def _on_check_finished(self):
        """更新チェック完了後の表示更新"""
        self._load_notifications()
        self._btn_check.setEnabled(True)
        self._btn_check.setText("手動チェック実行")

        now = datetime.now().strftime("%m/%d %H:%M")
        if self._checking:
            self._status_label.setText(
                f"前回チェック: {now}（検出 {self._detected_during_check}件）"
            )
        else:
            self._status_label.setText(f"前回チェック: {now}")
        self._checking = False

    @Slot()
    def _mark_all_read(self):
        """全通知を既読にする"""
        repo.mark_all_notifications_read(self._db)
        self._load_notifications()
        self.notification_read.emit()

    @Slot()
    def _delete_all_notifications(self):
        """全通知履歴を削除する"""
        reply = QMessageBox.question(
            self,
            "通知履歴削除の確認",
            "通知履歴をすべて削除します。\nこの操作は元に戻せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        repo.delete_all_notifications(self._db)
        self._load_notifications()
        self.notification_read.emit()
