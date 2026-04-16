"""ダウンロードキュータブ（v3.1: 手動開始、セルウィジェット方式）"""

import logging
import os
import subprocess
import webbrowser

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QLabel,
    QHeaderView, QMenu, QComboBox, QMessageBox,
)
from civitai_downloader.ui.widgets import (
    StyledProgressBar, StyledTableWidget, PrimaryButton,
)
from PySide6.QtCore import Qt, Slot, Signal, QEvent, QPoint
from PySide6.QtGui import QAction

from civitai_downloader.constants import JobStatus, JOB_STATUS_DISPLAY, CIVITAI_BASE_URL
from civitai_downloader.db.connection import Database
from civitai_downloader.db import repository as repo
from civitai_downloader.app import get_app_data_dir, get_unsorted_dir

logger = logging.getLogger(__name__)

# 列インデックス
COL_CHECK = 0
COL_FILENAME = 1
COL_PRESET = 2
COL_PROGRESS = 3
COL_STATUS = 4

# 編集可能なステータス（保存先変更が可能）
_EDITABLE_STATUSES = frozenset({
    JobStatus.PENDING.value,
    JobStatus.PENDING_UNRESOLVED.value,
})


class DownloadTab(QWidget):
    """ダウンロードキュー一覧タブ"""

    def __init__(self, db: Database, download_manager=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._download_manager = download_manager
        self._job_rows: dict[str, int] = {}  # job_id → 行番号

        # チェック操作の状態管理
        self._last_checked_row: int = -1      # Shift+クリック用: 前回チェックした行
        self._drag_checking: bool = False      # ドラッグ中フラグ
        self._drag_check_state: Qt.CheckState | None = None  # ドラッグ中に適用するチェック状態
        self._drag_visited: set[int] = set()   # ドラッグ中に通過済みの行

        self._setup_ui()
        self._connect_signals()
        self._load_existing_jobs()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # ── 操作ボタン ──
        btn_layout = QHBoxLayout()

        self._btn_start_selected = PrimaryButton("▶ 選択を開始")
        self._btn_start_selected.clicked.connect(self._on_start_selected)
        btn_layout.addWidget(self._btn_start_selected)

        self._btn_start_all = PrimaryButton("▶▶ 全て開始")
        self._btn_start_all.clicked.connect(self._on_start_all)
        btn_layout.addWidget(self._btn_start_all)

        self._btn_change_preset = PrimaryButton("保存先を一括変更")
        self._btn_change_preset.clicked.connect(self._show_bulk_preset_menu)
        btn_layout.addWidget(self._btn_change_preset)

        self._hint_label = QLabel("保存先は開始前のジョブだけ変更できます")
        self._hint_label.setToolTip(
            "待機中またはID未確定のジョブを選ぶと保存先を変更できます。"
        )
        btn_layout.addWidget(self._hint_label)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        summary_layout = QHBoxLayout()
        self._summary_label = QLabel("開始可能 0 / 失敗 0 / 未解決 0 / 進行中 0")
        summary_layout.addWidget(self._summary_label)
        summary_layout.addStretch()
        summary_layout.addWidget(QLabel("表示:"))
        self._filter_combo = QComboBox()
        self._filter_combo.addItem("すべて", "all")
        self._filter_combo.addItem("開始前", "pending")
        self._filter_combo.addItem("ID未確定", JobStatus.PENDING_UNRESOLVED.value)
        self._filter_combo.addItem("進行中", "active")
        self._filter_combo.addItem("失敗", JobStatus.FAILED.value)
        self._filter_combo.addItem("完了/スキップ", "done")
        self._filter_combo.currentIndexChanged.connect(self._apply_filter)
        summary_layout.addWidget(self._filter_combo)
        layout.addLayout(summary_layout)

        # ── テーブル ──
        self._table = StyledTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            "☑", "ファイル名", "保存先", "進捗", "状態"
        ])
        self._table.horizontalHeader().setSectionResizeMode(
            COL_FILENAME, QHeaderView.ResizeMode.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            COL_PROGRESS, QHeaderView.ResizeMode.Stretch
        )
        self._table.setColumnWidth(COL_CHECK, 30)
        self._table.setColumnWidth(COL_PRESET, 150)
        self._table.setColumnWidth(COL_STATUS, 100)
        self._table.setSelectionBehavior(StyledTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(StyledTableWidget.SelectionMode.ExtendedSelection)

        self._table.setEditTriggers(StyledTableWidget.EditTrigger.NoEditTriggers)

        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)

        # ヘッダークリックで全選択/全解除
        self._table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)

        # ドラッグ・Shift+クリック用イベントフィルター
        self._table.viewport().installEventFilter(self)

        layout.addWidget(self._table)

    def _connect_signals(self):
        if self._download_manager:
            self._download_manager.job_added.connect(self._on_job_added)
            self._download_manager.job_updated.connect(self._on_job_updated)
            self._download_manager.job_finished.connect(self._on_job_finished)

    def _load_existing_jobs(self):
        """起動時に既存ジョブを読み込む"""
        jobs = repo.get_all_jobs(self._db)
        for job in jobs:
            self._add_job_row(job)
        self._update_summary()
        self._apply_filter()

    @Slot()
    def reload_presets(self):
        """プリセット変更を一覧へ即時反映する"""
        for row in range(self._table.rowCount()):
            job_id = self._get_job_id_for_row(row)
            if not job_id:
                continue
            job = repo.get_job(self._db, job_id)
            if not job:
                continue
            self._set_preset_cell(row, job)
        self._update_summary()

    # ──── プリセットコンボ ────

    def _create_preset_combo(self, job_id: str, current_preset_id: str | None) -> QComboBox:
        """プリセット選択用QComboBoxを生成"""
        combo = QComboBox()
        combo.addItem("（Unsorted）", None)
        presets = repo.get_all_presets(self._db)
        selected_idx = 0
        for p in presets:
            combo.addItem(p["name"], p["id"])
            if p["id"] == current_preset_id:
                selected_idx = combo.count() - 1
        combo.setCurrentIndex(selected_idx)
        combo.currentIndexChanged.connect(
            lambda _idx, jid=job_id, cb=combo: self._on_preset_changed(jid, cb)
        )
        combo.setToolTip(self._build_preset_tooltip(current_preset_id))
        return combo

    def _on_preset_changed(self, job_id: str, combo: QComboBox):
        """コンボ選択変更→DB更新"""
        preset_id = combo.currentData()
        repo.update_job(self._db, job_id, preset_id=preset_id)
        combo.setToolTip(self._build_preset_tooltip(preset_id))

    def _set_preset_cell(self, row: int, job: dict):
        """プリセット列のセル内容を設定（状態に応じてコンボorテキスト）"""
        if job["status"] in _EDITABLE_STATUSES:
            # 編集可能: コンボボックス
            combo = self._create_preset_combo(job["id"], job.get("preset_id"))
            self._table.setCellWidget(row, COL_PRESET, combo)
            # セルウィジェット使用時はアイテムのテキストは表示されないが
            # 一応データは持たせておく
            item = self._table.item(row, COL_PRESET)
            if item is None:
                item = QTableWidgetItem()
                self._table.setItem(row, COL_PRESET, item)
            item.setToolTip(self._build_preset_tooltip(job.get("preset_id")))
        else:
            # 読み取り専用: テキスト表示
            self._table.removeCellWidget(row, COL_PRESET)
            name = self._get_preset_display_name(job.get("preset_id"))
            item = self._table.item(row, COL_PRESET)
            if item is None:
                item = QTableWidgetItem(name)
                self._table.setItem(row, COL_PRESET, item)
            else:
                item.setText(name)
            item.setToolTip(self._build_preset_tooltip(job.get("preset_id")))

    # ──── 行追加・更新 ────

    def _add_job_row(self, job: dict):
        """テーブルにジョブ行を追加"""
        row = self._table.rowCount()
        self._table.insertRow(row)

        # チェックボックス
        check_item = QTableWidgetItem()
        check_item.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        )
        check_item.setCheckState(Qt.CheckState.Unchecked)
        check_item.setData(Qt.ItemDataRole.UserRole, job["id"])
        self._table.setItem(row, COL_CHECK, check_item)

        # ファイル名
        filename_item = QTableWidgetItem(job["filename"])
        self._table.setItem(row, COL_FILENAME, filename_item)

        # 保存先（状態に応じてコンボorテキスト）
        self._table.setItem(row, COL_PRESET, QTableWidgetItem())
        self._set_preset_cell(row, job)

        # 進捗バー
        progress = StyledProgressBar()
        progress.setRange(0, 100)
        total = job.get("bytes_total", 0)
        downloaded = job.get("bytes_downloaded", 0)
        if total and total > 0:
            progress.setValue(int(downloaded / total * 100))
        else:
            progress.setValue(0)
        self._table.setCellWidget(row, COL_PROGRESS, progress)

        # 状態
        status_text = JOB_STATUS_DISPLAY.get(job["status"], job["status"])
        if job["status"] == JobStatus.PENDING_UNRESOLVED.value:
            status_text = "⚠" + status_text
        status_item = QTableWidgetItem(status_text)
        if job["status"] == JobStatus.FAILED.value and job.get("error_message"):
            status_item.setToolTip(job["error_message"])
        self._table.setItem(row, COL_STATUS, status_item)
        self._sync_job_rows()
        self._update_summary()
        self._apply_filter()

    def _get_preset_display_name(self, preset_id: str | None) -> str:
        """プリセットIDから表示名を取得"""
        if not preset_id:
            return "（Unsorted）"
        preset = repo.get_preset(self._db, preset_id)
        if preset:
            return preset["name"]
        return "（Unsorted）"

    def _get_preset_path_text(self, preset_id: str | None) -> str:
        """プリセットIDから実パスを取得"""
        if not preset_id:
            return get_unsorted_dir()
        preset = repo.get_preset(self._db, preset_id)
        if preset and preset.get("path"):
            return preset["path"]
        return "パス未設定"

    def _build_preset_tooltip(self, preset_id: str | None) -> str:
        """保存先の実体を示すツールチップ"""
        return (
            f"保存先: {self._get_preset_display_name(preset_id)}\n"
            f"実パス: {self._get_preset_path_text(preset_id)}"
        )

    def _get_job_id_for_row(self, row: int) -> str | None:
        """行番号からジョブIDを取得"""
        item = self._table.item(row, COL_CHECK)
        if not item:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _get_checked_job_ids(self) -> list[str]:
        """チェックされたジョブIDリストを返す"""
        result = []
        for jid, row in self._job_rows.items():
            if self._table.isRowHidden(row):
                continue
            check_item = self._table.item(row, COL_CHECK)
            if check_item and check_item.checkState() == Qt.CheckState.Checked:
                result.append(jid)
        return result

    # ──── 操作ボタン ────

    @Slot()
    def _on_start_selected(self):
        """選択されたジョブを開始"""
        job_ids = self._get_checked_job_ids()
        if job_ids and self._download_manager:
            self._download_manager.start_selected(job_ids)

    @Slot()
    def _on_start_all(self):
        """全PENDINGジョブを開始"""
        if self._download_manager:
            self._download_manager.start_all_pending()

    @Slot()
    def _show_bulk_preset_menu(self):
        """選択ジョブ向けの保存先一括変更メニューを表示"""
        checked = self._get_checked_job_ids()
        if not checked:
            QMessageBox.information(
                self,
                "保存先変更",
                "保存先を変更したいジョブを先にチェックしてください。",
            )
            return

        menu = QMenu(self)

        unsorted_action = QAction("（Unsorted）", self)
        unsorted_action.setToolTip(get_unsorted_dir())
        unsorted_action.triggered.connect(
            lambda: self._batch_change_preset(checked, None)
        )
        menu.addAction(unsorted_action)

        for preset in repo.get_all_presets(self._db):
            action = QAction(preset["name"], self)
            action.setToolTip(preset.get("path", ""))
            action.triggered.connect(
                lambda checked_val=False, pid=preset["id"]: self._batch_change_preset(checked, pid)
            )
            menu.addAction(action)

        menu.addSeparator()
        settings_action = QAction("設定タブで保存先を追加・編集", self)
        settings_action.triggered.connect(
            lambda: QMessageBox.information(
                self,
                "保存先追加",
                "保存先の追加やパス変更は設定タブの「フォルダプリセット管理」から行えます。",
            )
        )
        menu.addAction(settings_action)

        menu.exec(
            self._btn_change_preset.mapToGlobal(
                self._btn_change_preset.rect().bottomLeft()
            )
        )

    # ──── シグナルハンドラ ────

    @Slot(str)
    def _on_job_added(self, job_id: str):
        """新規ジョブ追加"""
        job = repo.get_job(self._db, job_id)
        if job:
            self._add_job_row(job)

    @Slot(str)
    def _on_job_updated(self, job_id: str):
        """ジョブ更新（進捗・情報補完）"""
        row = self._job_rows.get(job_id)
        if row is None:
            return
        job = repo.get_job(self._db, job_id)
        if not job:
            return

        # ファイル名更新
        filename_item = self._table.item(row, COL_FILENAME)
        if filename_item:
            filename_item.setText(job["filename"])

        # 保存先更新（状態遷移でコンボ↔テキストが切り替わる）
        self._set_preset_cell(row, job)

        # 進捗更新
        progress = self._table.cellWidget(row, COL_PROGRESS)
        if isinstance(progress, StyledProgressBar):
            total = job.get("bytes_total", 0)
            downloaded = job.get("bytes_downloaded", 0)
            if total and total > 0:
                progress.setValue(int(downloaded / total * 100))

        # 状態更新
        status_item = self._table.item(row, COL_STATUS)
        if status_item:
            status_text = JOB_STATUS_DISPLAY.get(job["status"], job["status"])
            if job["status"] == JobStatus.PENDING_UNRESOLVED.value:
                status_text = "⚠" + status_text
            status_item.setText(status_text)
            status_item.setToolTip(job.get("error_message", ""))
        self._update_summary()
        self._apply_filter()

    @Slot(str, str)
    def _on_job_finished(self, job_id: str, status: str):
        """ジョブ完了/失敗"""
        row = self._job_rows.get(job_id)
        if row is None:
            return
        job = repo.get_job(self._db, job_id)
        if not job:
            return

        # 進捗100%
        progress = self._table.cellWidget(row, COL_PROGRESS)
        if isinstance(progress, StyledProgressBar) and status == JobStatus.COMPLETED.value:
            progress.setValue(100)
            progress.setCompleted(True)

        # 状態更新
        status_item = self._table.item(row, COL_STATUS)
        if status_item:
            status_text = JOB_STATUS_DISPLAY.get(status, status)
            status_item.setText(status_text)
            if status == JobStatus.FAILED.value and job.get("error_message"):
                status_item.setToolTip(job["error_message"])

        # プリセット列をテキスト表示に切り替え（コンボを除去）
        self._set_preset_cell(row, job)
        self._update_summary()
        self._apply_filter()

    # ──── 右クリックメニュー ────

    def _show_context_menu(self, pos):
        """右クリックメニュー"""
        row = self._table.rowAt(pos.y())
        if row < 0:
            return

        job_id = self._get_job_id_for_row(row)
        if not job_id:
            return

        job = repo.get_job(self._db, job_id)
        if not job:
            return

        menu = QMenu(self)

        # 全て選択 / 全て解除
        select_all_action = QAction("全てチェック", self)
        select_all_action.triggered.connect(
            lambda: self._set_all_checks(Qt.CheckState.Checked)
        )
        menu.addAction(select_all_action)

        deselect_all_action = QAction("全てチェック解除", self)
        deselect_all_action.triggered.connect(
            lambda: self._set_all_checks(Qt.CheckState.Unchecked)
        )
        menu.addAction(deselect_all_action)

        menu.addSeparator()

        # 開始（PENDINGのみ）
        if job["status"] == JobStatus.PENDING.value:
            start_action = QAction("開始", self)
            start_action.triggered.connect(
                lambda: self._start_single(job_id)
            )
            menu.addAction(start_action)

        # リトライ（FAILEDのみ）
        if job["status"] == JobStatus.FAILED.value:
            retry_action = QAction("リトライ", self)
            retry_action.triggered.connect(lambda: self._retry_job(job_id))
            menu.addAction(retry_action)
            detail_action = QAction("失敗詳細を見る", self)
            detail_action.triggered.connect(lambda: self._show_failure_detail(job))
            menu.addAction(detail_action)
            log_action = QAction("ログフォルダを開く", self)
            log_action.triggered.connect(self._open_log_folder)
            menu.addAction(log_action)

        # キャンセル（PENDING/PENDING_UNRESOLVED/QUEUED/DOWNLOADINGのみ）
        if job["status"] in (
            JobStatus.PENDING.value,
            JobStatus.PENDING_UNRESOLVED.value,
            JobStatus.QUEUED.value,
            JobStatus.DOWNLOADING.value,
        ):
            cancel_action = QAction("キャンセル", self)
            cancel_action.triggered.connect(lambda: self._cancel_job(job_id))
            menu.addAction(cancel_action)

        menu.addSeparator()

        # 保存先一括変更（チェック選択がある場合）
        checked = self._get_checked_job_ids()
        if checked:
            preset_menu = menu.addMenu("保存先を一括変更")
            presets = repo.get_all_presets(self._db)
            unsorted_action = QAction("（Unsorted）", self)
            unsorted_action.triggered.connect(
                lambda: self._batch_change_preset(checked, None)
            )
            preset_menu.addAction(unsorted_action)
            for p in presets:
                pa = QAction(p["name"], self)
                pa.triggered.connect(
                    lambda checked_val=False, pid=p["id"]: self._batch_change_preset(checked, pid)
                )
                preset_menu.addAction(pa)

        # 削除
        delete_targets = self._get_context_target_job_ids(row)
        delete_label = "選択したジョブを削除" if len(delete_targets) > 1 else "削除"
        delete_action = QAction(delete_label, self)
        delete_action.triggered.connect(lambda: self._delete_jobs(delete_targets))
        menu.addAction(delete_action)

        menu.addSeparator()

        # 保存先を開く（COMPLETEDのみ）
        if job["status"] == JobStatus.COMPLETED.value and job.get("dest_path"):
            open_action = QAction("保存先を開く", self)
            open_action.triggered.connect(
                lambda: self._open_dest_folder(job["dest_path"])
            )
            menu.addAction(open_action)

        # Civitaiページを開く
        if job.get("page_url"):
            page_action = QAction("Civitaiページを開く", self)
            page_action.triggered.connect(
                lambda: webbrowser.open(job["page_url"])
            )
            menu.addAction(page_action)
        elif job.get("model_id"):
            page_action = QAction("Civitaiページを開く", self)
            page_action.triggered.connect(
                lambda: webbrowser.open(f"{CIVITAI_BASE_URL}/models/{job['model_id']}")
            )
            menu.addAction(page_action)

        if menu.actions():
            menu.exec(self._table.viewport().mapToGlobal(pos))

    def _start_single(self, job_id: str):
        if self._download_manager:
            self._download_manager.start_selected([job_id])

    def _retry_job(self, job_id: str):
        if self._download_manager:
            self._download_manager.retry_job(job_id)

    def _cancel_job(self, job_id: str):
        if self._download_manager:
            self._download_manager.cancel_job(job_id)

    def _show_failure_detail(self, job: dict):
        """失敗理由と次の行動を表示"""
        error_message = job.get("error_message") or "失敗理由は記録されていません。"
        hint = self._build_failure_hint(error_message)
        QMessageBox.information(
            self,
            "失敗詳細",
            (
                f"ファイル: {job.get('filename', '')}\n"
                f"状態: {JOB_STATUS_DISPLAY.get(job.get('status'), job.get('status', ''))}\n\n"
                f"理由:\n{error_message}\n\n"
                f"次の行動:\n{hint}"
            ),
        )

    def _build_failure_hint(self, error_message: str) -> str:
        """エラー文言から復旧ヒントを返す"""
        message = error_message.lower()
        if "api" in message or "認証" in error_message or "401" in message or "403" in message:
            return "設定タブで API キーを確認してから、ジョブをリトライしてください。"
        if "404" in message or "見つかりません" in error_message:
            return "Civitai ページを開き、モデルやバージョンが公開中か確認してください。"
        if "保存先" in error_message or "移動" in error_message or "permission" in message:
            return "保存先プリセットのパスと書き込み権限を確認してください。"
        if "タイムアウト" in error_message or "timeout" in message or "429" in message:
            return "時間を置いてからリトライしてください。API 制限中の可能性があります。"
        if "キャンセル" in error_message:
            return "必要ならリトライしてください。削除する場合はジョブ削除を使います。"
        return "まずリトライし、再発する場合は Civitai ページとログを確認してください。"

    def _open_log_folder(self):
        """ログファイルのあるフォルダを開く"""
        log_dir = get_app_data_dir()
        if os.path.isdir(log_dir):
            subprocess.Popen(["explorer", log_dir])

    def _delete_job(self, job_id: str):
        self._delete_jobs([job_id])

    def _delete_jobs(self, job_ids: list[str]):
        """複数ジョブを確認付きで削除する"""
        job_ids = list(dict.fromkeys(job_ids))
        if not job_ids:
            return

        filenames = []
        for job_id in job_ids[:5]:
            job = repo.get_job(self._db, job_id)
            if job:
                filenames.append(job.get("filename", job_id))

        if len(job_ids) == 1:
            message = (
                "選択したジョブを削除します。\n"
                "進行中ジョブは停止を試みます。\n"
                "この操作は元に戻せません。"
            )
        else:
            shown = "\n".join(f"- {name}" for name in filenames)
            rest = f"\n...ほか {len(job_ids) - len(filenames)}件" if len(job_ids) > len(filenames) else ""
            message = (
                f"{len(job_ids)}件のジョブを削除します。\n"
                "進行中ジョブは停止を試みます。\n"
                "この操作は元に戻せません。\n\n"
                f"{shown}{rest}"
            )

        reply = QMessageBox.question(
            self,
            "ジョブ削除の確認",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        rows_to_remove = []
        for job_id in job_ids:
            if self._download_manager:
                self._download_manager.delete_job(job_id)
            row = self._job_rows.get(job_id)
            if row is not None:
                rows_to_remove.append(row)

        for row in sorted(rows_to_remove, reverse=True):
            self._table.removeRow(row)

        self._sync_job_rows()
        self._update_summary()
        self._apply_filter()

    def _get_context_target_job_ids(self, context_row: int) -> list[str]:
        """右クリック時の操作対象を決める"""
        context_job_id = self._get_job_id_for_row(context_row)
        if not context_job_id:
            return []

        checked = self._get_checked_job_ids()
        if context_job_id in checked and len(checked) > 1:
            return checked

        selected_job_ids = []
        selection_model = self._table.selectionModel()
        if selection_model:
            for index in selection_model.selectedRows():
                row = index.row()
                if self._table.isRowHidden(row):
                    continue
                job_id = self._get_job_id_for_row(row)
                if job_id:
                    selected_job_ids.append(job_id)
        if context_job_id in selected_job_ids and len(selected_job_ids) > 1:
            return selected_job_ids

        return [context_job_id]

    def _batch_change_preset(self, job_ids: list[str], preset_id: str | None):
        """保存先一括変更"""
        for jid in job_ids:
            job = repo.get_job(self._db, jid)
            if job and job["status"] in _EDITABLE_STATUSES:
                repo.update_job(self._db, jid, preset_id=preset_id)
                self._on_job_updated(jid)

    def _open_dest_folder(self, dest_path: str):
        """保存先フォルダをエクスプローラーで開く"""
        folder = os.path.dirname(dest_path)
        if os.path.isdir(folder):
            subprocess.Popen(["explorer", folder])

    def _sync_job_rows(self):
        """現在の表示順を基準にジョブID→行番号のマッピングを再構築"""
        self._job_rows.clear()
        for row in range(self._table.rowCount()):
            job_id = self._get_job_id_for_row(row)
            if job_id:
                self._job_rows[job_id] = row

    def _update_summary(self):
        """キュー全体の状態要約を更新"""
        jobs = repo.get_all_jobs(self._db)
        startable = 0
        failed = 0
        unresolved = 0
        active = 0
        for job in jobs:
            status = job["status"]
            if status == JobStatus.FAILED.value:
                failed += 1
            if status == JobStatus.PENDING_UNRESOLVED.value:
                unresolved += 1
            if status in (JobStatus.QUEUED.value, JobStatus.DOWNLOADING.value):
                active += 1
            if self._download_manager and self._download_manager.can_start(job):
                startable += 1
            elif not self._download_manager and status == JobStatus.PENDING.value:
                startable += 1
        self._summary_label.setText(
            f"開始可能 {startable} / 失敗 {failed} / 未解決 {unresolved} / 進行中 {active}"
        )

    @Slot(int)
    def _apply_filter(self, _idx: int | None = None):
        """状態フィルタをテーブルへ反映"""
        filter_value = self._filter_combo.currentData()
        for row in range(self._table.rowCount()):
            job_id = self._get_job_id_for_row(row)
            job = repo.get_job(self._db, job_id) if job_id else None
            hidden = False
            if job:
                status = job["status"]
                if filter_value == "pending":
                    hidden = status not in (
                        JobStatus.PENDING.value,
                        JobStatus.PENDING_UNRESOLVED.value,
                    )
                elif filter_value == "active":
                    hidden = status not in (
                        JobStatus.QUEUED.value,
                        JobStatus.DOWNLOADING.value,
                    )
                elif filter_value == "done":
                    hidden = status not in (
                        JobStatus.COMPLETED.value,
                        JobStatus.SKIPPED.value,
                    )
                elif filter_value != "all":
                    hidden = status != filter_value
            self._table.setRowHidden(row, hidden)

    # ──── 一括チェック操作 ────

    def _on_header_clicked(self, logical_index: int):
        """ヘッダークリック: チェック列なら全選択/全解除をトグル"""
        if logical_index != COL_CHECK:
            return
        # 現在の状態を見て全選択or全解除を判断
        visible_items = [
            self._table.item(row, COL_CHECK)
            for row in range(self._table.rowCount())
            if not self._table.isRowHidden(row) and self._table.item(row, COL_CHECK)
        ]
        all_checked = bool(visible_items) and all(
            item.checkState() == Qt.CheckState.Checked
            for item in visible_items
        )
        new_state = Qt.CheckState.Unchecked if all_checked else Qt.CheckState.Checked
        self._set_all_checks(new_state)

    def _set_all_checks(self, state: Qt.CheckState):
        """全行のチェック状態を一括設定"""
        for row in range(self._table.rowCount()):
            if self._table.isRowHidden(row):
                continue
            item = self._table.item(row, COL_CHECK)
            if item:
                item.setCheckState(state)

    def eventFilter(self, obj, event: QEvent) -> bool:
        """ビューポートのマウスイベントを処理（Shift+クリック・ドラッグ選択）"""
        if obj is not self._table.viewport():
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.MouseButtonPress:
            return self._handle_check_mouse_press(event)
        elif event.type() == QEvent.Type.MouseMove:
            return self._handle_check_mouse_move(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            return self._handle_check_mouse_release(event)

        return super().eventFilter(obj, event)

    def _handle_check_mouse_press(self, event) -> bool:
        """マウス押下: チェック列ならドラッグ開始 / Shift+クリック処理"""
        if event.button() != Qt.MouseButton.LeftButton:
            return False

        pos = event.position().toPoint()
        row = self._table.rowAt(pos.y())
        col = self._table.columnAt(pos.x())

        if col != COL_CHECK or row < 0:
            return False

        item = self._table.item(row, COL_CHECK)
        if not item:
            return False

        # Shift+クリック: 範囲選択
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            if self._last_checked_row >= 0:
                start = min(self._last_checked_row, row)
                end = max(self._last_checked_row, row)
                # 現在行の反転後の状態を範囲全体に適用
                new_state = (
                    Qt.CheckState.Unchecked
                    if item.checkState() == Qt.CheckState.Checked
                    else Qt.CheckState.Checked
                )
                for r in range(start, end + 1):
                    it = self._table.item(r, COL_CHECK)
                    if it:
                        it.setCheckState(new_state)
                self._last_checked_row = row
                return True  # イベント消費

        # 通常クリック → ドラッグ開始準備
        current = item.checkState()
        new_state = (
            Qt.CheckState.Unchecked
            if current == Qt.CheckState.Checked
            else Qt.CheckState.Checked
        )
        item.setCheckState(new_state)
        self._last_checked_row = row
        self._drag_checking = True
        self._drag_check_state = new_state
        self._drag_visited = {row}
        return True  # イベント消費（デフォルトのチェック処理を防ぐ）

    def _handle_check_mouse_move(self, event) -> bool:
        """マウス移動: ドラッグ中ならチェック状態を適用"""
        if not self._drag_checking:
            return False

        pos = event.position().toPoint()
        row = self._table.rowAt(pos.y())
        if row < 0 or row in self._drag_visited:
            return False

        item = self._table.item(row, COL_CHECK)
        if item:
            item.setCheckState(self._drag_check_state)
            self._drag_visited.add(row)
        return True

    def _handle_check_mouse_release(self, event) -> bool:
        """マウスリリース: ドラッグ終了"""
        if self._drag_checking:
            self._drag_checking = False
            self._drag_check_state = None
            self._drag_visited.clear()
            return True
        return False
