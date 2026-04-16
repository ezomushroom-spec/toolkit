"""設定タブ（フォルダプリセット管理）"""

import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QLabel, QComboBox,
    QGroupBox, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox,
)
from civitai_downloader.ui.widgets import StyledTableWidget, PrimaryButton
from PySide6.QtCore import Qt, Signal, Slot, QObject, QRunnable, QThreadPool

from civitai_downloader.db.connection import Database
from civitai_downloader.db import repository as repo
from civitai_downloader.app import get_app_data_dir, get_unsorted_dir

logger = logging.getLogger(__name__)

# プリセットテーブルの列定義
COL_NAME = 0
COL_PATH = 1
COL_ID = 2  # 非表示


class _ApiTestSignals(QObject):
    finished = Signal(int, str)
    error = Signal(str)


class _ApiTestWorker(QRunnable):
    """API 接続テストを UI スレッド外で実行する"""

    def __init__(self, api_key: str):
        super().__init__()
        self.signals = _ApiTestSignals()
        self._api_key = api_key
        self.setAutoDelete(True)

    def run(self):
        import httpx
        from civitai_downloader.constants import CIVITAI_API_BASE, APP_USER_AGENT

        try:
            resp = httpx.get(
                f"{CIVITAI_API_BASE}/models/4384",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "User-Agent": APP_USER_AGENT,
                },
                timeout=10.0,
                follow_redirects=True,
            )

            model_name = ""
            if resp.status_code == 200:
                try:
                    model_name = resp.json().get("name", "")
                except Exception:
                    model_name = ""

            self.signals.finished.emit(resp.status_code, model_name)
        except httpx.TimeoutException:
            self.signals.error.emit("タイムアウト\n\nサーバーに接続できません。")
        except Exception as e:
            self.signals.error.emit(f"接続エラー\n\n{e}")


class SettingsTab(QWidget):
    """設定タブ"""

    max_concurrent_changed = Signal(int)
    presets_changed = Signal()  # プリセット更新通知

    def __init__(self, db: Database, theme_manager=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._theme_manager = theme_manager
        self._thread_pool = QThreadPool.globalInstance()
        self._loading_presets = False
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # ── 一般設定 ──
        general_group = QGroupBox("一般設定")
        general_layout = QFormLayout()

        # テーマ切替
        theme_layout = QHBoxLayout()
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("ダーク", "dark")
        self._theme_combo.addItem("ライト", "light")
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(self._theme_combo)
        general_layout.addRow("テーマ:", theme_layout)

        # APIキー
        api_layout = QHBoxLayout()
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_edit.setPlaceholderText("Civitai APIキー")
        self._btn_toggle_api_key = PrimaryButton("表示")
        self._btn_toggle_api_key.setFixedWidth(60)
        self._btn_toggle_api_key.clicked.connect(self._toggle_api_key_visibility)
        self._btn_test_api = PrimaryButton("接続テスト")
        self._btn_test_api.setFixedWidth(80)
        self._btn_test_api.clicked.connect(self._test_api_connection)
        api_layout.addWidget(self._api_key_edit)
        api_layout.addWidget(self._btn_toggle_api_key)
        api_layout.addWidget(self._btn_test_api)
        general_layout.addRow("APIキー:", api_layout)

        # 同時DL数
        self._concurrent_spin = QSpinBox()
        self._concurrent_spin.setRange(1, 10)
        self._concurrent_spin.setValue(3)
        general_layout.addRow("同時DL数:", self._concurrent_spin)

        # 内部フォルダ
        folder_layout = QHBoxLayout()
        self._app_dir_label = QLabel(get_app_data_dir())
        folder_layout.addWidget(self._app_dir_label)
        general_layout.addRow("内部フォルダ:", folder_layout)

        # ログ上限
        log_layout = QHBoxLayout()
        self._log_max_spin = QSpinBox()
        self._log_max_spin.setRange(1, 100)
        self._log_max_spin.setValue(10)
        log_layout.addWidget(self._log_max_spin)
        log_layout.addWidget(QLabel("MB"))
        general_layout.addRow("ログ上限:", log_layout)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # ── 保存ボタン ──
        self._btn_save = PrimaryButton("設定を保存")
        self._btn_save.clicked.connect(self._save_settings)
        layout.addWidget(self._btn_save)

        # ── フォルダプリセット管理 ──
        preset_group = QGroupBox("フォルダプリセット管理")
        preset_layout = QVBoxLayout()

        # Unsorted表示
        unsorted_layout = QHBoxLayout()
        unsorted_layout.addWidget(QLabel("Unsorted (未分類):"))
        self._unsorted_label = QLabel(get_unsorted_dir())
        self._unsorted_label.setObjectName("unsorted_label")
        unsorted_layout.addWidget(self._unsorted_label)
        unsorted_layout.addStretch()
        preset_layout.addLayout(unsorted_layout)

        # プリセット操作ボタン
        btn_layout = QHBoxLayout()
        self._btn_new_preset = PrimaryButton("+ 新規")
        self._btn_new_preset.clicked.connect(self._create_new_preset)
        self._btn_browse_preset = PrimaryButton("参照")
        self._btn_browse_preset.clicked.connect(self._browse_selected_preset_path)
        self._btn_delete_preset = PrimaryButton("削除")
        self._btn_delete_preset.clicked.connect(self._delete_selected_preset)
        btn_layout.addWidget(self._btn_new_preset)
        btn_layout.addWidget(self._btn_browse_preset)
        btn_layout.addWidget(self._btn_delete_preset)
        btn_layout.addStretch()
        preset_layout.addLayout(btn_layout)

        hint_label = QLabel(
            "プリセットの追加・名前変更・パス変更はここで即時反映されます。一般設定は「設定を保存」で反映されます。"
        )
        hint_label.setWordWrap(True)
        preset_layout.addWidget(hint_label)

        # プリセットテーブル
        self._preset_table = StyledTableWidget()
        self._preset_table.setColumnCount(3)
        self._preset_table.setHorizontalHeaderLabels(["プリセット名", "パス", "ID"])
        self._preset_table.horizontalHeader().setSectionResizeMode(
            COL_NAME, QHeaderView.ResizeMode.Interactive
        )
        self._preset_table.horizontalHeader().setSectionResizeMode(
            COL_PATH, QHeaderView.ResizeMode.Stretch
        )
        self._preset_table.setColumnHidden(COL_ID, True)
        self._preset_table.setSelectionBehavior(StyledTableWidget.SelectionBehavior.SelectRows)
        self._preset_table.cellDoubleClicked.connect(self._on_preset_cell_double_clicked)
        self._preset_table.itemChanged.connect(self._on_preset_item_changed)
        self._preset_table.setColumnWidth(COL_NAME, 200)

        preset_layout.addWidget(self._preset_table)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

    def _load_settings(self):
        """設定をDBから読み込み"""
        self._api_key_edit.setText(repo.get_setting(self._db, "api_key", ""))
        self._concurrent_spin.setValue(
            int(repo.get_setting(self._db, "max_concurrent", "3"))
        )
        log_max = int(repo.get_setting(self._db, "log_max_bytes", "10485760"))
        self._log_max_spin.setValue(log_max // 1_048_576)

        # テーマ設定読み込み（シグナル一時切断で無駄な発火を防ぐ）
        self._theme_combo.blockSignals(True)
        current_theme = repo.get_setting(self._db, "theme", "dark")
        idx = self._theme_combo.findData(current_theme)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        self._theme_combo.blockSignals(False)

        self._load_presets()

    def _load_presets(self):
        """プリセットテーブルを更新"""
        self._loading_presets = True
        self._preset_table.setRowCount(0)
        presets = repo.get_all_presets(self._db)
        for p in presets:
            row = self._preset_table.rowCount()
            self._preset_table.insertRow(row)

            # プリセット名
            self._preset_table.setItem(row, COL_NAME, QTableWidgetItem(p["name"]))

            # パス
            self._preset_table.setItem(row, COL_PATH, QTableWidgetItem(p.get("path", "")))

            # ID（非表示列）
            self._preset_table.setItem(row, COL_ID, QTableWidgetItem(p["id"]))
        self._loading_presets = False

    def _save_settings(self):
        """設定をDBに保存"""
        repo.set_setting(self._db, "api_key", self._api_key_edit.text().strip())

        new_concurrent = self._concurrent_spin.value()
        repo.set_setting(self._db, "max_concurrent", str(new_concurrent))
        self.max_concurrent_changed.emit(new_concurrent)

        log_max_mb = self._log_max_spin.value()
        repo.set_setting(self._db, "log_max_bytes", str(log_max_mb * 1_048_576))

        # プリセットの更新を保存
        self._save_presets()

        logger.info("設定を保存しました")

    def _save_presets(self):
        """プリセットテーブルの内容をDBに保存"""
        for row in range(self._preset_table.rowCount()):
            self._sync_preset_row(row)

        self.presets_changed.emit()

    @Slot()
    def _test_api_connection(self):
        """APIキーの接続テスト"""
        api_key = self._api_key_edit.text().strip()

        if not api_key:
            QMessageBox.warning(self, "接続テスト", "APIキーが入力されていません。")
            return

        self._btn_test_api.setEnabled(False)
        self._btn_test_api.setText("テスト中...")

        worker = _ApiTestWorker(api_key)
        worker.signals.finished.connect(self._on_api_test_finished)
        worker.signals.error.connect(self._on_api_test_error)
        self._thread_pool.start(worker)

    @Slot(int, str)
    def _on_api_test_finished(self, status_code: int, model_name: str):
        self._btn_test_api.setEnabled(True)
        self._btn_test_api.setText("接続テスト")

        if status_code == 200:
            QMessageBox.information(
                self, "接続テスト",
                f"接続成功\n\n"
                f"ステータス: {status_code}\n"
                f"テストモデル: {model_name}",
            )
        elif status_code in (401, 403):
            QMessageBox.critical(
                self, "接続テスト",
                f"認証失敗 (HTTP {status_code})\n\n"
                f"APIキーが無効です。確認してください。",
            )
        else:
            QMessageBox.warning(
                self, "接続テスト",
                f"応答あり (HTTP {status_code})\n\n"
                f"サーバーに接続できましたが、予期しないステータスです。",
            )

    @Slot(str)
    def _on_api_test_error(self, message: str):
        self._btn_test_api.setEnabled(True)
        self._btn_test_api.setText("接続テスト")
        QMessageBox.critical(self, "接続テスト", message)

    @Slot()
    def _on_theme_changed(self):
        """テーマ切替"""
        theme_value = self._theme_combo.currentData()
        if self._theme_manager and theme_value:
            from civitai_downloader.constants import AppTheme
            try:
                self._theme_manager.set_theme(AppTheme(theme_value))
            except ValueError:
                pass

    @Slot()
    def _toggle_api_key_visibility(self):
        """APIキーの表示/非表示切り替え"""
        if self._api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self._btn_toggle_api_key.setText("隠す")
        else:
            self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self._btn_toggle_api_key.setText("表示")

    @Slot()
    def _create_new_preset(self):
        """新規プリセット作成"""
        pid = repo.create_preset(self._db, "新規プリセット")
        logger.info(f"プリセット作成: {pid}")
        self._load_presets()
        last_row = self._preset_table.rowCount() - 1
        if last_row >= 0:
            self._preset_table.selectRow(last_row)
        self.presets_changed.emit()

    @Slot()
    def _browse_selected_preset_path(self):
        """選択中プリセットのパスを参照ダイアログで設定"""
        row = self._preset_table.currentRow()
        if row < 0:
            QMessageBox.information(
                self, "フォルダ選択", "先にパスを設定したいプリセットを選択してください。"
            )
            return

        current_item = self._preset_table.item(row, COL_PATH)
        current_path = current_item.text() if current_item else ""
        folder = QFileDialog.getExistingDirectory(
            self,
            "フォルダを選択",
            current_path or get_app_data_dir(),
        )
        if folder:
            self._preset_table.setItem(row, COL_PATH, QTableWidgetItem(folder))

    @Slot()
    def _delete_selected_preset(self):
        """選択中のプリセットを削除"""
        row = self._preset_table.currentRow()
        if row < 0:
            return

        pid_item = self._preset_table.item(row, COL_ID)
        if not pid_item:
            return

        pid = pid_item.text()
        reply = QMessageBox.question(
            self, "確認", "このプリセットを削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            repo.delete_preset(self._db, pid)
            logger.info(f"プリセット削除: {pid}")
            self._load_presets()
            self.presets_changed.emit()

    @Slot(int, int)
    def _on_preset_cell_double_clicked(self, row: int, col: int):
        """プリセットセルダブルクリック→パス列ならフォルダ選択ダイアログ"""
        if col == COL_PATH:
            self._preset_table.selectRow(row)
            self._browse_selected_preset_path()

    @Slot(QTableWidgetItem)
    def _on_preset_item_changed(self, item: QTableWidgetItem):
        """プリセット表の編集を即時反映する"""
        if self._loading_presets:
            return
        if item.column() not in (COL_NAME, COL_PATH):
            return
        row = item.row()
        if self._sync_preset_row(row):
            self.presets_changed.emit()

    def _sync_preset_row(self, row: int) -> bool:
        """指定行のプリセットを DB へ同期する"""
        pid_item = self._preset_table.item(row, COL_ID)
        if not pid_item:
            return False

        pid = pid_item.text()
        preset = repo.get_preset(self._db, pid)
        if not preset:
            return False

        name_item = self._preset_table.item(row, COL_NAME)
        name = name_item.text().strip() if name_item else ""
        path_item = self._preset_table.item(row, COL_PATH)
        path = path_item.text().strip() if path_item else ""

        if not name:
            name = "新規プリセット"
            self._loading_presets = True
            self._preset_table.setItem(row, COL_NAME, QTableWidgetItem(name))
            self._loading_presets = False

        changed = (
            preset.get("name", "") != name
            or preset.get("path", "") != path
            or int(preset.get("sort_order", 0)) != row
        )
        if not changed:
            return False

        repo.update_preset(self._db, pid, name=name, path=path, sort_order=row)
        return True
