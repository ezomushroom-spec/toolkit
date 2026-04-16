from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .core import PromptRecord, PromptRepository, RepositorySnapshot, TagRecord, WildcardRecord
from .session_store import SessionStore, WorkSession
from .situation_store import SituationDraft, SituationStore
from .wildcard_draft_store import WildcardDraft, WildcardDraftStore


class MainWindow(QMainWindow):
    def __init__(
        self,
        repository: PromptRepository,
        session_store: SessionStore,
        situation_store: SituationStore,
        wildcard_draft_store: WildcardDraftStore,
    ):
        super().__init__()
        self.repository = repository
        self.session_store = session_store
        self.situation_store = situation_store
        self.wildcard_draft_store = wildcard_draft_store
        self.snapshot: RepositorySnapshot | None = None
        self.prompts: tuple[PromptRecord, ...] = tuple()
        self.wildcards: tuple[WildcardRecord, ...] = tuple()
        self.wildcard_drafts: dict[str, WildcardDraft] = {}
        self.tag_results: tuple[TagRecord, ...] = tuple()
        self.situations: tuple[SituationDraft, ...] = tuple()
        self.current_situation_id = ""
        self.current_tags: list[str] = []
        self.current_wildcards: list[str] = []
        self.current_random_wildcard_item = ""

        self.setWindowTitle("Image Prompt Desktop")
        self.resize(1280, 820)
        self.setMinimumSize(980, 640)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self._build_ui()
        self._load_situations()
        self._load_data()
        self._load_wildcard_drafts()
        self._restore_session()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 12)
        root_layout.setSpacing(14)

        title = QLabel("Image Prompt Desktop")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("正本 Python app の SQLite / wildcard を読み取り、プロンプト作業に使うデスクトップ版です。")
        subtitle.setObjectName("MetaLabel")
        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        self.summary_label = QLabel("読み込み待機中")
        self.summary_label.setObjectName("MetaLabel")
        root_layout.addWidget(self.summary_label)

        self.workspace_tabs = QTabWidget()
        root_layout.addWidget(self.workspace_tabs, 1)

        self.workspace_tabs.addTab(self._build_prompt_studio_panel(), "Prompt Studio")
        self.workspace_tabs.addTab(self._build_wildcard_library_panel(), "Wildcard Library")

    def _build_prompt_studio_panel(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_prompt_list_panel())
        splitter.addWidget(self._build_editor_panel())
        splitter.addWidget(self._build_tag_panel())
        splitter.setSizes([260, 560, 340])
        return splitter

    def _build_wildcard_library_panel(self) -> QWidget:
        return self._build_wildcard_panel()

    def _build_prompt_list_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        label = QLabel("Prompts")
        label.setObjectName("SectionLabel")
        layout.addWidget(label)

        self.prompt_list = QListWidget()
        self.prompt_list.currentRowChanged.connect(self._select_prompt)
        self.prompt_list.itemDoubleClicked.connect(lambda _: self._load_selected_situation())
        layout.addWidget(self.prompt_list, 1)

        self.prompt_list_empty_label = QLabel(
            "保存済み Prompt / Situation はありません。一時保存した内容は次回起動時に編集欄へ復元されます。"
        )
        self.prompt_list_empty_label.setObjectName("EmptyStateLabel")
        self.prompt_list_empty_label.setWordWrap(True)
        self.prompt_list_empty_label.hide()
        layout.addWidget(self.prompt_list_empty_label)

        self.reload_button = QPushButton("再読み込み")
        self.reload_button.clicked.connect(self._load_data)
        layout.addWidget(self.reload_button)

        self.load_situation_button = QPushButton("選択 Situation を読み込み")
        self.load_situation_button.clicked.connect(self._load_selected_situation)
        layout.addWidget(self.load_situation_button)

        return panel

    def _build_editor_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        label = QLabel("Prompt Editor")
        label.setObjectName("SectionLabel")
        layout.addWidget(label)

        prompt_label = QLabel("生成プロンプト")
        prompt_label.setObjectName("MetaLabel")
        layout.addWidget(prompt_label)
        self.situation_name_input = QLineEdit()
        self.situation_name_input.setPlaceholderText("生成シチュエーション名。例: 雨の夜の路地で振り返る人物")
        layout.addWidget(self.situation_name_input)

        self.prompt_edit = QPlainTextEdit()
        self.prompt_edit.setPlaceholderText("生成プロンプトを入力または選択します。")
        layout.addWidget(self.prompt_edit, 3)

        negative_label = QLabel("ネガティブプロンプト")
        negative_label.setObjectName("MetaLabel")
        layout.addWidget(negative_label)
        self.negative_edit = QPlainTextEdit()
        self.negative_edit.setPlaceholderText("避けたい要素や破綻しやすい要素を入力します。")
        layout.addWidget(self.negative_edit, 2)

        self.situation_meta_label = QLabel("tags: なし / wildcards: なし")
        self.situation_meta_label.setObjectName("MetaLabel")
        self.situation_meta_label.setWordWrap(True)
        layout.addWidget(self.situation_meta_label)

        self.situation_notes_edit = QPlainTextEdit()
        self.situation_notes_edit.setPlaceholderText("メモ。用途、構図、避けたい点などを短く残します。")
        self.situation_notes_edit.setMaximumHeight(80)
        layout.addWidget(self.situation_notes_edit)

        button_row = QGridLayout()
        self.copy_prompt_button = QPushButton("Prompt をコピー")
        self.copy_prompt_button.setObjectName("PrimaryButton")
        self.copy_prompt_button.clicked.connect(lambda: self._copy_text(self.prompt_edit.toPlainText(), "Prompt"))
        button_row.addWidget(self.copy_prompt_button, 0, 0)

        self.copy_negative_button = QPushButton("Negative をコピー")
        self.copy_negative_button.clicked.connect(
            lambda: self._copy_text(self.negative_edit.toPlainText(), "Negative prompt")
        )
        button_row.addWidget(self.copy_negative_button, 0, 1)

        self.clear_button = QPushButton("編集欄をクリア")
        self.clear_button.clicked.connect(self._clear_editor)
        button_row.addWidget(self.clear_button, 0, 2)

        self.save_session_button = QPushButton("一時保存")
        self.save_session_button.clicked.connect(self._save_session)
        button_row.addWidget(self.save_session_button, 1, 0)

        self.clear_session_button = QPushButton("一時保存を破棄")
        self.clear_session_button.clicked.connect(self._clear_session)
        button_row.addWidget(self.clear_session_button, 1, 1, 1, 2)

        self.save_situation_button = QPushButton("Situation として保存")
        self.save_situation_button.setObjectName("PrimaryButton")
        self.save_situation_button.clicked.connect(self._save_situation)
        button_row.addWidget(self.save_situation_button, 2, 0)

        self.clear_situation_meta_button = QPushButton("タグ情報をクリア")
        self.clear_situation_meta_button.clicked.connect(self._clear_situation_meta)
        button_row.addWidget(self.clear_situation_meta_button, 2, 1, 1, 2)

        self.new_situation_button = QPushButton("新規 Situation")
        self.new_situation_button.clicked.connect(self._start_new_situation)
        button_row.addWidget(self.new_situation_button, 3, 0, 1, 3)
        layout.addLayout(button_row)

        return panel

    def _build_wildcard_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QGridLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        label = QLabel("Wildcards")
        label.setObjectName("SectionLabel")
        layout.addWidget(label, 0, 0, 1, 2)

        self.wildcard_list = QListWidget()
        self.wildcard_list.currentRowChanged.connect(self._select_wildcard)
        layout.addWidget(self.wildcard_list, 1, 0, 1, 2)

        self.wildcard_meta_label = QLabel("未選択")
        self.wildcard_meta_label.setObjectName("MetaLabel")
        self.wildcard_meta_label.setWordWrap(True)
        layout.addWidget(self.wildcard_meta_label, 2, 0, 1, 2)

        self.wildcard_candidate_list = QListWidget()
        self.wildcard_candidate_list.setToolTip("候補をダブルクリックすると Prompt へ挿入します。")
        self.wildcard_candidate_list.itemDoubleClicked.connect(lambda _: self._insert_selected_wildcard_candidate())
        layout.addWidget(self.wildcard_candidate_list, 3, 0, 1, 2)

        draft_label = QLabel("ローカル下書き編集（正本には保存しません）")
        draft_label.setObjectName("MetaLabel")
        layout.addWidget(draft_label, 4, 0, 1, 2)

        self.wildcard_draft_edit = QPlainTextEdit()
        self.wildcard_draft_edit.setPlaceholderText("1 行 1 候補で編集します。保存先は desktop 版ローカル data/wildcard_drafts.json です。")
        layout.addWidget(self.wildcard_draft_edit, 5, 0, 1, 2)

        self.copy_wildcard_button = QPushButton("構文をコピー")
        self.copy_wildcard_button.setObjectName("PrimaryButton")
        self.copy_wildcard_button.clicked.connect(self._copy_selected_wildcard_token)
        layout.addWidget(self.copy_wildcard_button, 6, 0)

        self.insert_wildcard_button = QPushButton("Prompt へ挿入")
        self.insert_wildcard_button.clicked.connect(self._insert_selected_wildcard)
        layout.addWidget(self.insert_wildcard_button, 6, 1)

        self.random_wildcard_button = QPushButton("ランダム確認")
        self.random_wildcard_button.clicked.connect(self._preview_random_wildcard_item)
        layout.addWidget(self.random_wildcard_button, 7, 0)

        self.random_wildcard_label = QLabel("ランダム候補: 未実行")
        self.random_wildcard_label.setObjectName("MetaLabel")
        self.random_wildcard_label.setWordWrap(True)
        layout.addWidget(self.random_wildcard_label, 7, 1)

        self.copy_random_wildcard_button = QPushButton("ランダムをコピー")
        self.copy_random_wildcard_button.clicked.connect(self._copy_random_wildcard_item)
        layout.addWidget(self.copy_random_wildcard_button, 8, 0)

        self.insert_random_wildcard_button = QPushButton("ランダムを挿入")
        self.insert_random_wildcard_button.clicked.connect(self._insert_random_wildcard_item)
        layout.addWidget(self.insert_random_wildcard_button, 8, 1)

        self.save_wildcard_draft_button = QPushButton("ローカル下書きを保存")
        self.save_wildcard_draft_button.setObjectName("PrimaryButton")
        self.save_wildcard_draft_button.clicked.connect(self._save_wildcard_draft)
        layout.addWidget(self.save_wildcard_draft_button, 9, 0)

        self.reset_wildcard_draft_button = QPushButton("正本候補に戻す")
        self.reset_wildcard_draft_button.clicked.connect(self._reset_wildcard_draft_editor)
        layout.addWidget(self.reset_wildcard_draft_button, 9, 1)

        self.delete_wildcard_draft_button = QPushButton("ローカル下書きを削除")
        self.delete_wildcard_draft_button.clicked.connect(self._delete_wildcard_draft)
        layout.addWidget(self.delete_wildcard_draft_button, 10, 0, 1, 2)

        return panel

    def _build_tag_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QGridLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        label = QLabel("Tag Search")
        label.setObjectName("SectionLabel")
        layout.addWidget(label, 0, 0, 1, 3)

        self.tag_search_input = QLineEdit()
        self.tag_search_input.setPlaceholderText("例: school, smile, looking_at_viewer")
        self.tag_search_input.returnPressed.connect(self._search_tags)
        layout.addWidget(self.tag_search_input, 1, 0, 1, 2)

        self.tag_search_button = QPushButton("検索")
        self.tag_search_button.setObjectName("PrimaryButton")
        self.tag_search_button.clicked.connect(self._search_tags)
        layout.addWidget(self.tag_search_button, 1, 2)

        self.tag_category_filter = QComboBox()
        self.tag_category_filter.addItem("すべて", None)
        for category, label_text in (
            (0, "一般"),
            (1, "アーティスト"),
            (3, "作品"),
            (4, "キャラクター"),
            (5, "メタ"),
        ):
            self.tag_category_filter.addItem(label_text, category)
        layout.addWidget(self.tag_category_filter, 2, 0, 1, 3)

        self.tag_result_list = QListWidget()
        self.tag_result_list.currentRowChanged.connect(self._select_tag)
        self.tag_result_list.itemDoubleClicked.connect(lambda _: self._insert_selected_tag())
        layout.addWidget(self.tag_result_list, 3, 0, 1, 3)

        self.tag_meta_label = QLabel("検索語を入力してください。")
        self.tag_meta_label.setObjectName("MetaLabel")
        self.tag_meta_label.setWordWrap(True)
        layout.addWidget(self.tag_meta_label, 4, 0, 1, 3)

        self.insert_tag_to_prompt = QRadioButton("Prompt")
        self.insert_tag_to_prompt.setChecked(True)
        layout.addWidget(self.insert_tag_to_prompt, 5, 0)

        self.insert_tag_to_negative = QRadioButton("Negative")
        layout.addWidget(self.insert_tag_to_negative, 5, 1)

        self.insert_tag_button = QPushButton("選択タグを挿入")
        self.insert_tag_button.clicked.connect(self._insert_selected_tag)
        layout.addWidget(self.insert_tag_button, 5, 2)

        return panel

    def _load_data(self) -> None:
        try:
            self.snapshot = self.repository.load_snapshot()
        except Exception as error:
            QMessageBox.critical(self, "読み込み失敗", f"正本データの読み込みに失敗しました。\n{error}")
            self.status.showMessage("読み込み失敗")
            return

        self.prompts = self.snapshot.prompts
        self.wildcards = self.snapshot.wildcards
        self._refresh_prompt_list()

        self.wildcard_list.clear()
        for wildcard in self.wildcards:
            self.wildcard_list.addItem(f"{wildcard.token}  ({wildcard.total_items} candidates)")

        self.summary_label.setText(
            f"正本: {self.repository.paths.root} / prompts: {self.snapshot.prompt_count} / "
            f"tags: {self.snapshot.tag_count} / wildcards: {len(self.wildcards)}"
        )
        self.status.showMessage("正本データを読み込みました", 4000)

        if self.wildcards:
            self.wildcard_list.setCurrentRow(0)

    def _load_situations(self) -> None:
        self.situations = self.situation_store.load_all()
        self._refresh_prompt_list()

    def _refresh_prompt_list(self) -> None:
        if not hasattr(self, "prompt_list"):
            return

        self.prompt_list.clear()
        if self.prompts:
            for prompt in self.prompts:
                label = prompt.prompt[:60] if prompt.prompt else "(空の prompt)"
                item = QListWidgetItem(f"[Prompt] {prompt.category} / {label}")
                item.setData(Qt.ItemDataRole.UserRole, ("prompt", prompt.id))
                self.prompt_list.addItem(item)

        for situation in self.situations:
            item = QListWidgetItem(f"[Situation] {situation.name}")
            item.setData(Qt.ItemDataRole.UserRole, ("situation", situation.id))
            self.prompt_list.addItem(item)

        has_saved_items = bool(self.prompts or self.situations)
        self.prompt_list_empty_label.setVisible(not has_saved_items)

    def _load_wildcard_drafts(self) -> None:
        self.wildcard_drafts = self.wildcard_draft_store.load_all()

    def _select_prompt(self, row: int) -> None:
        if row < 0:
            return

        item = self.prompt_list.item(row)
        item_data = item.data(Qt.ItemDataRole.UserRole) if item else None
        if isinstance(item_data, tuple) and item_data[0] == "situation":
            self.status.showMessage("Situation はダブルクリックまたは読み込みボタンで開きます", 3000)
            return

        prompt_index = row
        if prompt_index < 0 or prompt_index >= len(self.prompts):
            return

        prompt = self.prompts[prompt_index]
        self.prompt_edit.setPlainText(prompt.prompt)
        self.negative_edit.setPlainText(prompt.negative_prompt)
        self.status.showMessage(f"Prompt #{prompt.id} を選択しました", 3000)

    def _load_selected_situation(self) -> None:
        row = self.prompt_list.currentRow()
        if row < 0:
            self.status.showMessage("読み込む Situation が選択されていません", 3000)
            return

        item = self.prompt_list.item(row)
        item_data = item.data(Qt.ItemDataRole.UserRole) if item else None
        if not (isinstance(item_data, tuple) and item_data[0] == "situation"):
            self.status.showMessage("選択中の項目は Situation ではありません", 3000)
            return

        situation_id = str(item_data[1])
        situation = next((draft for draft in self.situations if draft.id == situation_id), None)
        if situation is None:
            self.status.showMessage("Situation が見つかりません", 3000)
            return

        self.current_situation_id = situation.id
        self.situation_name_input.setText(situation.name)
        self.prompt_edit.setPlainText(situation.prompt)
        self.negative_edit.setPlainText(situation.negative_prompt)
        self.current_tags = list(situation.tags)
        self.current_wildcards = list(situation.wildcards)
        self.situation_notes_edit.setPlainText(situation.notes)
        self._refresh_situation_meta_label()
        self.status.showMessage(f"Situation「{situation.name}」を読み込みました", 4000)

    def _select_wildcard(self, row: int) -> None:
        if row < 0 or row >= len(self.wildcards):
            self.wildcard_meta_label.setText("未選択")
            self.wildcard_candidate_list.clear()
            return

        wildcard = self.wildcards[row]
        draft = self.wildcard_drafts.get(wildcard.name)
        items = draft.items if draft is not None else wildcard.items
        description = f"source: {wildcard.source_path.name} / preview: {len(wildcard.items)} of {wildcard.total_items}"
        if draft is not None:
            description += f" / local draft: {len(draft.items)} candidates / {draft.updated_at}"
        if wildcard.description:
            description += f" / {wildcard.description}"
        self.wildcard_meta_label.setText(description)
        self.wildcard_candidate_list.clear()
        self.wildcard_candidate_list.addItems(items)
        self.wildcard_draft_edit.setPlainText("\n".join(items))
        self.current_random_wildcard_item = ""
        self.random_wildcard_label.setText("ランダム候補: 未実行")

    def _search_tags(self) -> None:
        query = self.tag_search_input.text().strip()
        if not query:
            self.tag_result_list.clear()
            self.tag_results = tuple()
            self.tag_meta_label.setText("検索語を入力してください。")
            self.status.showMessage("タグ検索語が空です", 3000)
            return

        try:
            category = self.tag_category_filter.currentData()
            self.tag_results = self.repository.search_tags(query, limit=80, category=category)
        except Exception as error:
            QMessageBox.critical(self, "タグ検索失敗", f"タグ検索に失敗しました。\n{error}")
            self.status.showMessage("タグ検索失敗")
            return

        self.tag_result_list.clear()
        for tag in self.tag_results:
            self.tag_result_list.addItem(f"{tag.name}  [{tag.category_name}]  {tag.count}")

        if self.tag_results:
            self.tag_result_list.setCurrentRow(0)
            self.status.showMessage(f"タグを {len(self.tag_results)} 件表示しました", 3000)
        else:
            self.tag_meta_label.setText("該当タグはありません。検索語を変えてください。")
            self.status.showMessage("該当タグはありません", 3000)

    def _select_tag(self, row: int) -> None:
        if row < 0 or row >= len(self.tag_results):
            self.tag_meta_label.setText("未選択")
            return

        tag = self.tag_results[row]
        aliases = ", ".join(tag.aliases) if tag.aliases else "なし"
        self.tag_meta_label.setText(
            f"name: {tag.name} / category: {tag.category_name} / count: {tag.count} / aliases: {aliases}"
        )

    def _copy_selected_wildcard_token(self) -> None:
        row = self.wildcard_list.currentRow()
        if row < 0 or row >= len(self.wildcards):
            self.status.showMessage("コピーする wildcard が選択されていません", 3000)
            return
        self._copy_text(self.wildcards[row].token, "Wildcard token")

    def _insert_selected_wildcard(self) -> None:
        row = self.wildcard_list.currentRow()
        if row < 0 or row >= len(self.wildcards):
            self.status.showMessage("挿入する wildcard が選択されていません", 3000)
            return

        wildcard = self.wildcards[row]
        self._add_current_wildcard(wildcard.token)
        self._insert_prompt_text(wildcard.token, "Prompt へ wildcard 構文を挿入しました")

    def _insert_prompt_text(self, text: str, status_message: str) -> None:
        if not text.strip():
            self.status.showMessage("挿入するテキストが空です", 3000)
            return

        cursor = self.prompt_edit.textCursor()
        prefix = ", " if self.prompt_edit.toPlainText().strip() and not self.prompt_edit.toPlainText().rstrip().endswith(",") else ""
        cursor.insertText(f"{prefix}{text}")
        self.prompt_edit.setTextCursor(cursor)
        self.prompt_edit.setFocus()
        self.status.showMessage(status_message, 3000)

    def _preview_random_wildcard_item(self) -> None:
        row = self.wildcard_list.currentRow()
        if row < 0 or row >= len(self.wildcards):
            self.status.showMessage("ランダム確認する wildcard が選択されていません", 3000)
            return

        wildcard = self.wildcards[row]
        draft = self.wildcard_drafts.get(wildcard.name)
        item = ""
        if draft is not None and draft.items:
            item = random.choice(draft.items)
        else:
            item = self.repository.random_wildcard_item(wildcard.name)
        if not item:
            self.current_random_wildcard_item = ""
            self.random_wildcard_label.setText("ランダム候補: 空です")
            self.status.showMessage("wildcard 候補が空です", 3000)
            return

        self.current_random_wildcard_item = item
        self.random_wildcard_label.setText(f"ランダム候補: {item}")
        self.status.showMessage("wildcard 候補をランダム表示しました", 3000)

    def _copy_random_wildcard_item(self) -> None:
        self._copy_text(self.current_random_wildcard_item, "Random wildcard")

    def _insert_random_wildcard_item(self) -> None:
        row = self.wildcard_list.currentRow()
        if 0 <= row < len(self.wildcards):
            self._add_current_wildcard(self.wildcards[row].token)
        self._insert_prompt_text(self.current_random_wildcard_item, "ランダム候補を Prompt へ挿入しました")

    def _insert_selected_wildcard_candidate(self) -> None:
        item = self.wildcard_candidate_list.currentItem()
        if item is None:
            self.status.showMessage("挿入する wildcard 候補が選択されていません", 3000)
            return

        candidate = item.text().strip()
        row = self.wildcard_list.currentRow()
        if 0 <= row < len(self.wildcards):
            self._add_current_wildcard(self.wildcards[row].token)
        self._insert_prompt_text(candidate, "wildcard 候補を Prompt へ挿入しました")

    def _insert_selected_tag(self) -> None:
        row = self.tag_result_list.currentRow()
        if row < 0 or row >= len(self.tag_results):
            self.status.showMessage("挿入するタグが選択されていません", 3000)
            return

        tag_name = self.tag_results[row].name
        self._add_current_tag(tag_name)
        target = self.negative_edit if self.insert_tag_to_negative.isChecked() else self.prompt_edit
        cursor = target.textCursor()
        prefix = ", " if target.toPlainText().strip() and not target.toPlainText().rstrip().endswith(",") else ""
        cursor.insertText(f"{prefix}{tag_name}")
        target.setTextCursor(cursor)
        target.setFocus()
        self.status.showMessage("タグを挿入しました", 3000)

    def _copy_text(self, text: str, label: str) -> None:
        if not text.strip():
            self.status.showMessage(f"{label} は空です", 3000)
            return

        QGuiApplication.clipboard().setText(text)
        self.status.showMessage(f"{label} をクリップボードにコピーしました", 3000)

    def _restore_session(self) -> None:
        session = self.session_store.load()
        if session is None:
            return

        self.prompt_edit.setPlainText(session.prompt)
        self.negative_edit.setPlainText(session.negative_prompt)
        suffix = f" ({session.updated_at})" if session.updated_at else ""
        self.status.showMessage(f"一時保存した内容を復元しました{suffix}", 5000)

    def _save_session(self) -> None:
        session = WorkSession.create(
            prompt=self.prompt_edit.toPlainText(),
            negative_prompt=self.negative_edit.toPlainText(),
        )
        try:
            self.session_store.save(session)
        except OSError as error:
            QMessageBox.critical(self, "一時保存失敗", f"一時保存データを保存できませんでした。\n{error}")
            self.status.showMessage("一時保存失敗")
            return

        self.status.showMessage("一時保存しました", 4000)

    def _clear_session(self) -> None:
        try:
            self.session_store.clear()
        except OSError as error:
            QMessageBox.critical(self, "一時保存の破棄失敗", f"一時保存データを破棄できませんでした。\n{error}")
            self.status.showMessage("一時保存の破棄失敗")
            return

        self.status.showMessage("一時保存を破棄しました", 4000)

    def _clear_editor(self) -> None:
        self.prompt_edit.clear()
        self.negative_edit.clear()
        self.status.showMessage("編集欄をクリアしました", 3000)

    def _add_current_tag(self, tag_name: str) -> None:
        if tag_name and tag_name not in self.current_tags:
            self.current_tags.append(tag_name)
            self._refresh_situation_meta_label()

    def _add_current_wildcard(self, token: str) -> None:
        if token and token not in self.current_wildcards:
            self.current_wildcards.append(token)
            self._refresh_situation_meta_label()

    def _refresh_situation_meta_label(self) -> None:
        tags = ", ".join(self.current_tags) if self.current_tags else "なし"
        wildcards = ", ".join(self.current_wildcards) if self.current_wildcards else "なし"
        self.situation_meta_label.setText(f"tags: {tags} / wildcards: {wildcards}")

    def _clear_situation_meta(self) -> None:
        self.current_tags.clear()
        self.current_wildcards.clear()
        self._refresh_situation_meta_label()
        self.status.showMessage("Situation のタグ情報をクリアしました", 3000)

    def _start_new_situation(self) -> None:
        self.current_situation_id = ""
        self.situation_name_input.clear()
        self.current_tags.clear()
        self.current_wildcards.clear()
        self.situation_notes_edit.clear()
        self._refresh_situation_meta_label()
        self.status.showMessage("新規 Situation として保存できる状態にしました", 3000)

    def _save_situation(self) -> None:
        name = self.situation_name_input.text().strip()
        if not name:
            self.status.showMessage("Situation 名を入力してください", 4000)
            return

        existing = next((draft for draft in self.situations if draft.id == self.current_situation_id), None)
        draft = SituationDraft.create(
            name=name,
            prompt=self.prompt_edit.toPlainText(),
            negative_prompt=self.negative_edit.toPlainText(),
            tags=tuple(self.current_tags),
            wildcards=tuple(self.current_wildcards),
            notes=self.situation_notes_edit.toPlainText(),
        )
        if existing is not None:
            draft = SituationDraft(
                id=existing.id,
                name=draft.name,
                prompt=draft.prompt,
                negative_prompt=draft.negative_prompt,
                tags=draft.tags,
                wildcards=draft.wildcards,
                notes=draft.notes,
                updated_at=draft.updated_at,
            )

        try:
            self.situations = self.situation_store.upsert(draft)
        except OSError as error:
            QMessageBox.critical(self, "Situation 保存失敗", f"Situation として保存できませんでした。\n{error}")
            self.status.showMessage("Situation 保存失敗")
            return

        self.current_situation_id = draft.id
        self._load_data()
        self.status.showMessage(f"Situation「{draft.name}」として保存しました", 4000)

    def _selected_wildcard(self) -> WildcardRecord | None:
        row = self.wildcard_list.currentRow()
        if row < 0 or row >= len(self.wildcards):
            self.status.showMessage("対象の wildcard が選択されていません", 3000)
            return None
        return self.wildcards[row]

    def _draft_editor_items(self) -> tuple[str, ...]:
        return tuple(
            line.strip()
            for line in self.wildcard_draft_edit.toPlainText().splitlines()
            if line.strip()
        )

    def _save_wildcard_draft(self) -> None:
        wildcard = self._selected_wildcard()
        if wildcard is None:
            return

        items = self._draft_editor_items()
        if not items:
            self.status.showMessage("ローカル下書き候補が空です", 3000)
            return

        draft = WildcardDraft.create(
            name=wildcard.name,
            token=wildcard.token,
            items=items,
            source_file_name=wildcard.source_path.name,
        )
        try:
            self.wildcard_drafts = self.wildcard_draft_store.upsert(draft)
        except OSError as error:
            QMessageBox.critical(self, "Wildcard 下書き保存失敗", f"ローカル下書きを保存できませんでした。\n{error}")
            self.status.showMessage("Wildcard 下書き保存失敗")
            return

        self._select_wildcard(self.wildcard_list.currentRow())
        self.status.showMessage(f"Wildcard「{wildcard.token}」のローカル下書きを保存しました", 4000)

    def _reset_wildcard_draft_editor(self) -> None:
        wildcard = self._selected_wildcard()
        if wildcard is None:
            return

        self.wildcard_draft_edit.setPlainText("\n".join(wildcard.items))
        self.wildcard_candidate_list.clear()
        self.wildcard_candidate_list.addItems(wildcard.items)
        self.status.showMessage("正本候補を編集欄へ戻しました", 3000)

    def _delete_wildcard_draft(self) -> None:
        wildcard = self._selected_wildcard()
        if wildcard is None:
            return

        try:
            self.wildcard_drafts = self.wildcard_draft_store.delete(wildcard.name)
        except OSError as error:
            QMessageBox.critical(self, "Wildcard 下書き削除失敗", f"ローカル下書きを削除できませんでした。\n{error}")
            self.status.showMessage("Wildcard 下書き削除失敗")
            return

        self._select_wildcard(self.wildcard_list.currentRow())
        self.status.showMessage(f"Wildcard「{wildcard.token}」のローカル下書きを削除しました", 4000)
