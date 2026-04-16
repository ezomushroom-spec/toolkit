"""
左パネル: 画像プール（チェックボックス選定 + D&D + タグフィルタ）
"""
from __future__ import annotations
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QFileDialog,
    QMessageBox,
)

from core.image_pool import ImagePool, ImageEntry, SUPPORTED_EXTENSIONS

_BTN_STYLE = """
    QPushButton {
        background: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 4px;
        padding: 0 6px;
        font-size: 11px;
    }
    QPushButton:hover { background: #45475a; }
    QPushButton:pressed { background: #585b70; }
"""


class DraggableImageList(QListWidget):
    """チェックボックス付きサムネイル一覧（内部並び替え + 外部D&D対応）"""

    external_files_dropped = Signal(list)   # list[Path]
    check_state_changed = Signal()          # チェック状態が変わった
    order_changed = Signal(list)            # list[ImageEntry] 新しい順序

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QSize(88, 88))
        self.setSpacing(4)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setWordWrap(True)
        self.setUniformItemSizes(True)
        self.setStyleSheet("""
            QListWidget {
                background: #1e1e2e;
                border: 1px solid #3d3d5c;
                border-radius: 4px;
            }
            QListWidget::item {
                color: #cdd6f4;
                border-radius: 4px;
                padding: 2px;
            }
            QListWidget::item:selected {
                background: #313244;
                border: 1px solid #585b70;
            }
            QListWidget::item:hover {
                background: #292940;
            }
        """)
        self.itemChanged.connect(self._on_item_changed)

    # ------------------------------------------------------------------
    # D&D
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                local = url.toLocalFile()
                if local:
                    p = Path(local)
                    if p.suffix.lower() in SUPPORTED_EXTENSIONS:
                        paths.append(p)
                    elif p.is_dir():
                        for ext in SUPPORTED_EXTENSIONS:
                            paths.extend(sorted(p.rglob(f"*{ext}")))
            if paths:
                self.external_files_dropped.emit(paths)
        else:
            # 内部並び替え: Qt に処理させた後で新順序をシグナル発信
            super().dropEvent(event)
            new_order = [
                self.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.count())
            ]
            self.order_changed.emit(new_order)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self._parent_panel().remove_click_selected()
        else:
            super().keyPressEvent(event)

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        self.check_state_changed.emit()

    def _parent_panel(self) -> "ImagePoolPanel":
        w = self.parent()
        while w is not None:
            if isinstance(w, ImagePoolPanel):
                return w
            w = w.parent()
        raise RuntimeError("ImagePoolPanel not found")


class ImagePoolPanel(QWidget):
    """左パネル: 画像プール管理"""

    images_dropped = Signal(list)      # list[Path]
    selection_changed = Signal(list)   # list[ImageEntry]（チェック済み）

    def __init__(self, pool: ImagePool, parent=None):
        super().__init__(parent)
        self._pool = pool
        self._checked_paths: set[str] = set()
        self._setup_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    # UI構築
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        self.setStyleSheet("background: #181825;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # ヘッダ
        header = QLabel("画像プール")
        header.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 13px;")
        layout.addWidget(header)

        # ドロップヒント
        hint = QLabel("ここに画像をドラッグ&ドロップ")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("""
            color: #585b70; font-size: 11px;
            border: 1px dashed #45475a;
            border-radius: 4px; padding: 5px;
        """)
        layout.addWidget(hint)

        # サムネイル一覧（チェックボックス付き）
        self._list = DraggableImageList()
        layout.addWidget(self._list, stretch=1)

        # チェック操作ボタン行
        check_layout = QHBoxLayout()
        check_layout.setSpacing(4)
        self._btn_check_all = QPushButton("全選択")
        self._btn_uncheck_all = QPushButton("全解除")
        for btn in [self._btn_check_all, self._btn_uncheck_all]:
            btn.setFixedHeight(24)
            btn.setStyleSheet(_BTN_STYLE)
        check_layout.addWidget(self._btn_check_all)
        check_layout.addWidget(self._btn_uncheck_all)
        layout.addLayout(check_layout)

        # 操作ボタン行
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        self._btn_add = QPushButton("追加")
        self._btn_remove = QPushButton("削除")
        self._btn_clear = QPushButton("クリア")
        for btn in [self._btn_add, self._btn_remove, self._btn_clear]:
            btn.setFixedHeight(26)
            btn.setStyleSheet(_BTN_STYLE)
        btn_layout.addWidget(self._btn_add)
        btn_layout.addWidget(self._btn_remove)
        btn_layout.addWidget(self._btn_clear)
        layout.addLayout(btn_layout)

        # カウント表示
        self._count_label = QLabel("0枚チェック / 0枚")
        self._count_label.setStyleSheet("color: #585b70; font-size: 11px;")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._count_label)

    def _connect_signals(self) -> None:
        self._list.external_files_dropped.connect(self.images_dropped)
        self._list.check_state_changed.connect(self._on_check_state_changed)
        self._list.order_changed.connect(self._on_order_changed)
        self._btn_add.clicked.connect(self._open_file_dialog)
        self._btn_remove.clicked.connect(self.remove_click_selected)
        self._btn_clear.clicked.connect(self._clear_pool)
        self._btn_check_all.clicked.connect(self._check_all)
        self._btn_uncheck_all.clicked.connect(self._uncheck_all)
        self._pool.images_changed.connect(self.refresh)

    # ------------------------------------------------------------------
    # 公開API
    # ------------------------------------------------------------------

    def set_pool(self, pool: ImagePool) -> None:
        self._pool = pool
        self._pool.images_changed.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        """プール変更時に表示を更新（チェック状態を保持）"""
        checked_paths = set(self._checked_paths)

        self._list.blockSignals(True)
        self._list.clear()

        entries = list(self._pool.entries)
        for entry in entries:
            item = self._make_item(entry)
            state = Qt.CheckState.Checked if str(entry.path) in checked_paths else Qt.CheckState.Unchecked
            item.setCheckState(state)
            self._list.addItem(item)

        self._list.blockSignals(False)
        self._update_count_label()
        self._emit_checked()

    def refresh_keep_checks(self, new_entries: list[ImageEntry]) -> None:
        """新規追加時: 既存のチェック状態を維持しつつ新しい画像はチェック済みで追加"""
        checked_paths = set(self._checked_paths)

        self._list.blockSignals(True)
        self._list.clear()

        entries = list(self._pool.entries)
        for entry in entries:
            item = self._make_item(entry)
            is_new = entry in new_entries
            was_checked = str(entry.path) in checked_paths
            # 新規は常にチェック、既存は以前の状態を復元
            is_checked = is_new or was_checked
            item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            self._list.addItem(item)
            if is_checked:
                self._checked_paths.add(str(entry.path))

        self._list.blockSignals(False)
        self._update_count_label()
        self._emit_checked()

    def get_checked_entries(self) -> list[ImageEntry]:
        """チェック済みのエントリを返す（レイアウト用）"""
        return [entry for entry in self._pool.entries if str(entry.path) in self._checked_paths]

    def set_checked_paths(self, paths: list[str]) -> None:
        """指定パスの項目をチェック状態に反映する"""
        wanted = {str(Path(p)) for p in paths}
        self._checked_paths = set(wanted)
        self._list.blockSignals(True)
        for i in range(self._list.count()):
            item = self._list.item(i)
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                state = (
                    Qt.CheckState.Checked
                    if str(entry.path) in wanted
                    else Qt.CheckState.Unchecked
                )
                item.setCheckState(state)
        self._list.blockSignals(False)
        self._update_count_label()
        self._emit_checked()

    def get_click_selected_entries(self) -> list[ImageEntry]:
        """クリック選択されたエントリを返す（削除用）"""
        result = []
        for item in self._list.selectedItems():
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                result.append(entry)
        return result

    def remove_click_selected(self) -> None:
        """クリック選択された画像をプールから削除"""
        entries_to_remove = self.get_click_selected_entries()
        if not entries_to_remove:
            return
        indices = [i for i, e in enumerate(self._pool.entries) if e in entries_to_remove]
        self._pool.remove_images(indices)

    # ------------------------------------------------------------------
    # チェック操作
    # ------------------------------------------------------------------

    def _check_all(self) -> None:
        self._set_all_checks(Qt.CheckState.Checked)

    def _uncheck_all(self) -> None:
        self._set_all_checks(Qt.CheckState.Unchecked)

    def _set_all_checks(self, state: Qt.CheckState) -> None:
        self._list.blockSignals(True)
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(state)
        self._list.blockSignals(False)
        self._sync_checked_paths_from_list()
        self._update_count_label()
        self._emit_checked()

    # ------------------------------------------------------------------
    # スロット
    # ------------------------------------------------------------------

    def _on_check_state_changed(self) -> None:
        self._sync_checked_paths_from_list()
        self._update_count_label()
        self._emit_checked()

    def _on_order_changed(self, new_entries: list) -> None:
        """ドラッグ並び替え後にプールの順序を同期"""
        path_to_entry = {e.path: e for e in self._pool.entries}
        self._pool.entries = [
            path_to_entry[e.path]
            for e in new_entries
            if e.path in path_to_entry
        ]
        # images_changed は発火させず、順序のみ更新（再描画不要）
        self._update_count_label()
        self._emit_checked()

    def _open_file_dialog(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "画像を追加", "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if paths:
            self.images_dropped.emit([Path(p) for p in paths])

    def _clear_pool(self) -> None:
        if QMessageBox.question(
            self, "確認", "画像プールをクリアしますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            self._checked_paths.clear()
            self._pool.clear()

    # ------------------------------------------------------------------
    # 内部ユーティリティ
    # ------------------------------------------------------------------

    def _make_item(self, entry: ImageEntry) -> QListWidgetItem:
        """ImageEntry からリストアイテムを生成"""
        pixmap = entry.load_thumbnail(88)
        item = QListWidgetItem(QIcon(pixmap), entry.path.name)
        item.setData(Qt.ItemDataRole.UserRole, entry)
        item.setToolTip(f"{entry.path}\nタグ: {', '.join(entry.tags) or 'なし'}")
        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
        )
        return item

    def _sync_checked_paths_from_list(self) -> None:
        for i in range(self._list.count()):
            item = self._list.item(i)
            entry = item.data(Qt.ItemDataRole.UserRole)
            if not entry:
                continue
            path_str = str(entry.path)
            if item.checkState() == Qt.CheckState.Checked:
                self._checked_paths.add(path_str)
            else:
                self._checked_paths.discard(path_str)

        pool_paths = {str(entry.path) for entry in self._pool.entries}
        self._checked_paths.intersection_update(pool_paths)

    def _emit_checked(self) -> None:
        self.selection_changed.emit(self.get_checked_entries())

    def _update_count_label(self) -> None:
        checked = len(self._checked_paths)
        total = len(self._pool)
        self._count_label.setText(f"✓ {checked}枚 / 計{total}枚")
