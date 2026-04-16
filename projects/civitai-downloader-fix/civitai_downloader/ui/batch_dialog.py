"""一括ダウンロード追加ダイアログ"""

import json
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTabWidget, QWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QLabel,
)
from PySide6.QtCore import Qt, Slot, QThreadPool
from PySide6.QtWebEngineWidgets import QWebEngineView

from civitai_downloader.constants import CIVITAI_BASE_URL
from civitai_downloader.ui.widgets import StyledTableWidget, PrimaryButton
from civitai_downloader.core.batch_search_worker import BatchSearchWorker

logger = logging.getLogger(__name__)

# モデルタイプ選択肢
_MODEL_TYPES = [
    ("全タイプ", ""),
    ("Checkpoint", "Checkpoint"),
    ("LORA", "LORA"),
    ("LoCon", "LoCon"),
    ("TextualInversion", "TextualInversion"),
    ("VAE", "VAE"),
    ("Controlnet", "Controlnet"),
    ("Upscaler", "Upscaler"),
    ("Poses", "Poses"),
    ("Wildcards", "Wildcards"),
    ("Workflows", "Workflows"),
    ("MotionModule", "MotionModule"),
]

# ページ収集用JavaScriptコード
_SCRAPE_JS = """
(function() {
    const links = document.querySelectorAll('a[href*="/models/"]');
    const models = new Map();
    links.forEach(a => {
        const m = a.href.match(/\\/models\\/(\\d+)/);
        if (m) {
            const id = m[1];
            if (!models.has(id)) {
                const card = a.closest('div[class*="card" i], div[class*="Card"]') || a.parentElement;
                let name = '';
                if (card) {
                    const h = card.querySelector('h2, h3, h4, [class*="name" i], [class*="Name"], [class*="title" i]');
                    if (h) name = h.textContent.trim();
                }
                if (!name) name = 'Model ' + id;
                models.set(id, name);
            }
        }
    });
    return JSON.stringify([...models.entries()].map(([id, name]) => ({id: parseInt(id), name: name})));
})()
"""

# テーブル列
COL_CHECK = 0
COL_NAME = 1
COL_TYPE = 2
COL_ID = 3


class BatchDialog(QDialog):
    """一括ダウンロード追加ダイアログ"""

    def __init__(self, web_view: QWebEngineView, api_key: str = "", parent=None):
        super().__init__(parent)
        self._web_view = web_view
        self._api_key = api_key
        self._current_page = 1
        self._total_pages = 1
        self._selected_models: list[dict] = []
        self._seen_model_ids: set[int] = set()
        self._last_skipped_duplicates = 0

        self.setWindowTitle("一括ダウンロード追加")
        self.resize(700, 500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # タブ
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # ページ収集タブ
        self._page_tab = QWidget()
        self._setup_page_tab()
        self._tabs.addTab(self._page_tab, "ページ収集")

        # API検索タブ
        self._api_tab = QWidget()
        self._setup_api_tab()
        self._tabs.addTab(self._api_tab, "API検索")

        # 結果テーブル（両タブ共通）
        self._table = StyledTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["☑", "モデル名", "タイプ", "ID"])
        self._table.horizontalHeader().setSectionResizeMode(
            COL_NAME, QHeaderView.ResizeMode.Stretch
        )
        self._table.setColumnWidth(COL_CHECK, 30)
        self._table.setColumnWidth(COL_TYPE, 120)
        self._table.setColumnWidth(COL_ID, 70)
        self._table.setEditTriggers(StyledTableWidget.EditTrigger.NoEditTriggers)
        self._table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._table)

        # 下部ボタン
        bottom_layout = QHBoxLayout()

        self._btn_select_all = PrimaryButton("全選択")
        self._btn_select_all.clicked.connect(self._select_all)
        bottom_layout.addWidget(self._btn_select_all)

        self._btn_deselect_all = PrimaryButton("全解除")
        self._btn_deselect_all.clicked.connect(self._deselect_all)
        bottom_layout.addWidget(self._btn_deselect_all)

        self._status_label = QLabel("0件")
        bottom_layout.addWidget(self._status_label)

        bottom_layout.addStretch()

        self._btn_next_page = PrimaryButton("次のページ")
        self._btn_next_page.clicked.connect(self._on_next_page)
        self._btn_next_page.setVisible(False)
        bottom_layout.addWidget(self._btn_next_page)

        self._btn_enqueue = PrimaryButton("キューに追加")
        self._btn_enqueue.clicked.connect(self._on_enqueue)
        bottom_layout.addWidget(self._btn_enqueue)

        layout.addLayout(bottom_layout)

    def _setup_page_tab(self):
        """ページ収集タブのUI"""
        layout = QVBoxLayout(self._page_tab)
        layout.addWidget(QLabel(
            "現在ブラウズ中のページからモデルリンクを収集します。"
        ))
        self._btn_scrape = PrimaryButton("ページからモデルを収集")
        self._btn_scrape.clicked.connect(self._on_scrape)
        layout.addWidget(self._btn_scrape)
        layout.addStretch()

    def _setup_api_tab(self):
        """API検索タブのUI"""
        layout = QVBoxLayout(self._api_tab)

        form = QFormLayout()

        self._input_username = QLineEdit()
        self._input_username.setPlaceholderText("例: Rin_x0")
        self._input_username.returnPressed.connect(self._on_search)
        form.addRow("ユーザー名:", self._input_username)

        self._input_query = QLineEdit()
        self._input_query.setPlaceholderText("例: anime illustrious")
        self._input_query.returnPressed.connect(self._on_search)
        form.addRow("クエリ:", self._input_query)

        self._input_tag = QLineEdit()
        self._input_tag.setPlaceholderText("例: anime")
        self._input_tag.returnPressed.connect(self._on_search)
        form.addRow("タグ:", self._input_tag)

        self._input_type = QComboBox()
        for label, value in _MODEL_TYPES:
            self._input_type.addItem(label, value)
        form.addRow("タイプ:", self._input_type)

        layout.addLayout(form)

        self._btn_search = PrimaryButton("検索")
        self._btn_search.clicked.connect(self._on_search)
        layout.addWidget(self._btn_search)
        layout.addStretch()

    # ──── ページ収集 ────

    @Slot()
    def _on_scrape(self):
        """WebViewにJS注入してモデルリンクを収集"""
        self._btn_scrape.setEnabled(False)
        self._btn_scrape.setText("収集中...")
        self._btn_next_page.setVisible(False)

        page = self._web_view.page()
        page.runJavaScript(_SCRAPE_JS, self._on_scrape_result)

    def _on_scrape_result(self, result):
        """JS実行結果を処理"""
        self._btn_scrape.setEnabled(True)
        self._btn_scrape.setText("ページからモデルを収集")

        if not result:
            self._status_label.setText("モデルが見つかりませんでした")
            return

        try:
            models = json.loads(result) if isinstance(result, str) else result
        except (json.JSONDecodeError, TypeError):
            self._status_label.setText("結果の解析に失敗しました")
            return

        added, skipped = self._populate_table(
            [{"model_id": m["id"], "name": m["name"], "type": "", "creator": ""}
             for m in models]
        )
        self._last_skipped_duplicates = skipped
        if added == 0 and skipped > 0:
            self._status_label.setText(
                f"新しいモデルはありません（重複{skipped}件を除外）"
            )
        else:
            self._update_status()

    # ──── API検索 ────

    @Slot()
    def _on_search(self):
        """API検索を実行"""
        self._current_page = 1
        self._run_search()

    @Slot()
    def _on_next_page(self):
        """次のページを取得"""
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._run_search(append=True)

    def _run_search(self, append: bool = False):
        """検索ワーカーを起動"""
        self._btn_search.setEnabled(False)
        self._btn_search.setText("検索中...")
        self._btn_next_page.setEnabled(False)

        if not append:
            self._table.setRowCount(0)

        worker = BatchSearchWorker(
            api_key=self._api_key,
            username=self._input_username.text().strip(),
            query=self._input_query.text().strip(),
            tag=self._input_tag.text().strip(),
            model_type=self._input_type.currentData(),
            page=self._current_page,
        )
        worker.signals.finished.connect(
            lambda items, meta: self._on_search_finished(items, meta, append)
        )
        worker.signals.error.connect(self._on_search_error)
        QThreadPool.globalInstance().start(worker)

    def _on_search_finished(self, models: list, metadata: dict, append: bool):
        """検索完了"""
        self._btn_search.setEnabled(True)
        self._btn_search.setText("検索")

        self._total_pages = metadata.get("totalPages", 1)
        total_items = metadata.get("totalItems", 0)

        has_next = self._current_page < self._total_pages
        self._btn_next_page.setVisible(has_next)
        self._btn_next_page.setEnabled(has_next)

        if append:
            _added, skipped = self._append_to_table(models)
        else:
            _added, skipped = self._populate_table(models)

        self._last_skipped_duplicates = skipped
        checked = self._count_checked()
        total = self._table.rowCount()
        duplicate_text = f" / 重複{skipped}件除外" if skipped else ""
        self._status_label.setText(
            f"{total}件表示 / 全{total_items}件（{checked}件選択）{duplicate_text}"
        )

    def _on_search_error(self, error: str):
        """検索エラー"""
        self._btn_search.setEnabled(True)
        self._btn_search.setText("検索")
        self._btn_next_page.setEnabled(True)
        self._status_label.setText(f"エラー: {error}")

    # ──── テーブル操作 ────

    def _populate_table(self, models: list[dict]) -> tuple[int, int]:
        """テーブルにモデル一覧を表示"""
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        self._table.blockSignals(False)
        self._seen_model_ids.clear()
        return self._append_to_table(models)

    def _append_to_table(self, models: list[dict]) -> tuple[int, int]:
        """テーブルにモデルを追加"""
        added = 0
        skipped = 0
        self._table.blockSignals(True)
        for m in models:
            model_id = int(m["model_id"])
            if model_id in self._seen_model_ids:
                skipped += 1
                continue
            self._seen_model_ids.add(model_id)

            row = self._table.rowCount()
            self._table.insertRow(row)

            # チェックボックス
            check = QTableWidgetItem()
            check.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            )
            check.setCheckState(Qt.CheckState.Checked)
            self._table.setItem(row, COL_CHECK, check)

            # モデル名
            self._table.setItem(row, COL_NAME, QTableWidgetItem(m["name"]))

            # タイプ
            self._table.setItem(row, COL_TYPE, QTableWidgetItem(m.get("type", "")))

            # ID
            self._table.setItem(
                row, COL_ID, QTableWidgetItem(str(model_id))
            )
            added += 1

        self._table.blockSignals(False)
        self._update_status()
        return added, skipped

    def _count_checked(self) -> int:
        """チェック済み件数を数える"""
        count = 0
        for row in range(self._table.rowCount()):
            item = self._table.item(row, COL_CHECK)
            if item and item.checkState() == Qt.CheckState.Checked:
                count += 1
        return count

    def _update_status(self):
        """ステータスラベルを更新"""
        checked = self._count_checked()
        total = self._table.rowCount()
        duplicate_text = (
            f" / 重複{self._last_skipped_duplicates}件除外"
            if self._last_skipped_duplicates
            else ""
        )
        self._status_label.setText(f"{total}件中 {checked}件選択{duplicate_text}")

    def _on_item_changed(self, item: QTableWidgetItem):
        """チェック変更に件数表示を追従させる"""
        if item.column() == COL_CHECK:
            self._update_status()

    @Slot()
    def _select_all(self):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, COL_CHECK)
            if item:
                item.setCheckState(Qt.CheckState.Checked)
        self._update_status()

    @Slot()
    def _deselect_all(self):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, COL_CHECK)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
        self._update_status()

    # ──── キュー追加 ────

    @Slot()
    def _on_enqueue(self):
        """選択されたモデルをキューに追加"""
        self._selected_models.clear()
        for row in range(self._table.rowCount()):
            check = self._table.item(row, COL_CHECK)
            if not check or check.checkState() != Qt.CheckState.Checked:
                continue

            id_item = self._table.item(row, COL_ID)
            name_item = self._table.item(row, COL_NAME)
            if id_item:
                model_id = id_item.text()
                name = name_item.text() if name_item else ""
                self._selected_models.append({
                    "model_id": int(model_id),
                    "name": name,
                    "url": f"{CIVITAI_BASE_URL}/models/{model_id}",
                })

        self.accept()

    def get_selected_models(self) -> list[dict]:
        """選択されたモデルリストを返す"""
        return self._selected_models
