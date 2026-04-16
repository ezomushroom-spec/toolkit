"""
メインウィンドウ: 3パネル構成 + シグナルハブ + 非同期プレビュー
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from PIL import Image
from PySide6.QtCore import Qt, Signal, QTimer, QThreadPool, QRunnable, QObject, Slot
from PySide6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QUndoStack, QUndoCommand
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStatusBar, QMenuBar, QMenu, QFileDialog,
    QMessageBox, QApplication,
)
import numpy as np
import cv2

from core.image_pool import ImagePool, ImageEntry
from core.presets import PresetRegistry
from core.layout_engine import LayoutEngine
from core.text_overlay import TextConfig, hex_to_rgb
from core.exporter import Exporter, OUTPUT_SIZE_PRESETS

from ui.image_pool_panel import ImagePoolPanel
from ui.preview_panel import PreviewPanel, pil_to_qpixmap
from ui.preset_panel import PresetPanel
from ui.history_panel import HistoryPanel

# プロジェクト設定ファイルのデフォルトパス
_DEFAULT_HISTORY_PATH = Path.home() / ".nts" / "history.json"
_DEFAULT_OUTPUT_DIR = Path.home() / "Pictures" / "NTS_Output"


# ================================================================
# PreviewWorker: バックグラウンド合成
# ================================================================

class _WorkerSignals(QObject):
    finished = Signal(int, object)   # request_id, PIL Image
    error = Signal(int, str)


class PreviewWorker(QRunnable):
    """バックグラウンドでlayout_engine.composeを実行"""

    def __init__(self, request_id, engine, preset, images, params, output_size, text_config, offsets=None):
        super().__init__()
        self.signals = _WorkerSignals()
        self._request_id = request_id
        self._engine = engine
        self._preset = preset
        self._images = images
        self._params = params
        self._output_size = output_size
        self._text_config = text_config
        self._offsets = offsets or {}

    @Slot()
    def run(self) -> None:
        try:
            result = self._engine.compose(
                self._preset, self._images, self._params,
                self._output_size, self._text_config,
                offsets=self._offsets,
            )
            self.signals.finished.emit(self._request_id, result)
        except Exception as e:
            self.signals.error.emit(self._request_id, str(e))


# ================================================================
# ParamChangeCommand: Undo/Redo用コマンド
# ================================================================

class ParamChangeCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", param_name: str, old_val: Any, new_val: Any):
        super().__init__(f"パラメータ変更: {param_name}")
        self._window = window
        self._param_name = param_name
        self._old_val = old_val
        self._new_val = new_val

    def redo(self) -> None:
        self._window._current_params[self._param_name] = self._new_val
        self._window._schedule_preview_update()

    def undo(self) -> None:
        self._window._current_params[self._param_name] = self._old_val
        self._window._schedule_preview_update()


# ================================================================
# MainWindow
# ================================================================

class MainWindow(QMainWindow):
    """Narrative Thumbnail Studio メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Narrative Thumbnail Studio")
        self.resize(1400, 900)
        self.setMinimumSize(900, 600)

        # --- コアオブジェクト ---
        self.image_pool = ImagePool()
        self.preset_registry = PresetRegistry()
        self.preset_registry.load_builtin()

        self.layout_engine = LayoutEngine()
        self.exporter = Exporter(output_dir=_DEFAULT_OUTPUT_DIR)
        self.undo_stack = QUndoStack(self)

        # --- 状態 ---
        self._current_preset = None
        self._current_params: dict = {}
        self._current_output_size: tuple[int, int] = (1200, 900)
        self._selected_images: list[ImageEntry] = []
        self._assigned_image_paths: list[str] = []
        self._current_work_id: str = ""
        self._text_config: TextConfig = TextConfig()
        # 画像ごとのクロップオフセット（永続状態）
        self._crop_offsets_by_path: dict[str, tuple[float, float, float]] = {}
        # 現在のプレビューに対するスロット別オフセット（表示用キャッシュ）
        self._crop_offsets: dict[int, tuple[float, float, float]] = {}
        self._active_entry_paths: list[str] = []
        # 最新の合成済みnumpy配列（即時パン用）
        self._composite_numpy: np.ndarray | None = None
        self._preview_request_id = 0
        self._preview_worker_running = False
        self._preview_refresh_pending = False
        self._interactive_source_payloads: dict[int, dict[int, Image.Image]] = {}
        self._last_entries: list[ImageEntry] = []
        self._drag_fill_arrays: dict = {}
        self._drag_cell_bounds: dict = {}
        self._prev_offsets_snapshot: dict = {}

        # --- debounceタイマー ---
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._do_preview_update)

        # --- UI構築 ---
        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()
        self._setup_signals()
        self._apply_dark_theme()

        # --- 履歴読み込み ---
        self.exporter.load_history(_DEFAULT_HISTORY_PATH)
        self.history_panel.refresh(self.exporter.history)

        # ステータス
        self.statusBar().showMessage("準備完了")

    # ------------------------------------------------------------------
    # UI構築
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 3パネルスプリッター
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #3d3d5c; }")

        # 左パネル（25%）
        self.pool_panel = ImagePoolPanel(self.image_pool)
        self.pool_panel.setMinimumWidth(180)

        # 中央パネル（50%）
        self.preview_panel = PreviewPanel()
        self.preview_panel.setMinimumWidth(400)

        # 右パネル（25%）: プリセット + 履歴
        right_widget = QWidget()
        right_widget.setStyleSheet("background: #181825;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.preset_panel = PresetPanel(self.preset_registry)
        self.history_panel = HistoryPanel()

        # 右パネルを上下分割
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setHandleWidth(2)
        right_splitter.setStyleSheet("QSplitter::handle { background: #3d3d5c; }")
        right_splitter.addWidget(self.preset_panel)
        right_splitter.addWidget(self.history_panel)
        right_splitter.setSizes([550, 300])

        right_layout.addWidget(right_splitter)
        right_widget.setMinimumWidth(200)

        splitter.addWidget(self.pool_panel)
        splitter.addWidget(self.preview_panel)
        splitter.addWidget(right_widget)

        total = 1400
        splitter.setSizes([int(total * 0.22), int(total * 0.53), int(total * 0.25)])

        # エクスポートボタンバー
        export_bar = self._create_export_bar()
        main_layout.addWidget(export_bar)
        main_layout.addWidget(splitter, stretch=1)

    def _create_export_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background: #1e1e2e; border-bottom: 1px solid #3d3d5c;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        title = QLabel("Narrative Thumbnail Studio")
        title.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        layout.addStretch()

        btn_style = """
            QPushButton {
                background: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 4px 16px;
                font-size: 12px;
            }
            QPushButton:hover { background: #45475a; }
            QPushButton:pressed { background: #585b70; }
        """

        self._btn_export = QPushButton("エクスポート (Ctrl+E)")
        self._btn_export.setStyleSheet(btn_style.replace("#313244", "#1e3a5f").replace("#45475a", "#2a5298"))
        self._btn_export.setStyleSheet("""
            QPushButton {
                background: #1e3a5f;
                color: #89b4fa;
                border: 1px solid #89b4fa;
                border-radius: 4px;
                padding: 4px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background: #2a5298; }
            QPushButton:pressed { background: #1565c0; }
        """)
        layout.addWidget(self._btn_export)

        self._btn_export_all = QPushButton("全プリセット出力 (Ctrl+Shift+E)")
        self._btn_export_all.setStyleSheet(btn_style)
        layout.addWidget(self._btn_export_all)

        self._btn_export.clicked.connect(self._export_single)
        self._btn_export_all.clicked.connect(self._export_all_presets)

        return bar

    def _setup_menu(self) -> None:
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar { background: #1e1e2e; color: #cdd6f4; }
            QMenuBar::item:selected { background: #313244; }
            QMenu { background: #313244; color: #cdd6f4; border: 1px solid #45475a; }
            QMenu::item:selected { background: #45475a; }
        """)

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル")
        file_menu.addAction("画像を追加...", self._open_file_dialog, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("プロジェクトを保存...", self._save_project, "Ctrl+S")
        file_menu.addAction("プロジェクトを開く...", self._load_project, "Ctrl+L")
        file_menu.addSeparator()
        file_menu.addAction("終了", self.close, "Ctrl+Q")

        # 編集メニュー
        edit_menu = menubar.addMenu("編集")
        undo_action = self.undo_stack.createUndoAction(self)
        undo_action.setShortcut("Ctrl+Z")
        redo_action = self.undo_stack.createRedoAction(self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # エクスポートメニュー
        export_menu = menubar.addMenu("エクスポート")
        export_menu.addAction("現在のプリセットをエクスポート", self._export_single, "Ctrl+E")
        export_menu.addAction("全プリセットを一括エクスポート", self._export_all_presets, "Ctrl+Shift+E")
        export_menu.addSeparator()
        export_menu.addAction("出力フォルダを開く...", self._open_output_folder)
        export_menu.addAction("CSVエクスポート...", self._export_csv)

    def _setup_shortcuts(self) -> None:
        # Space: プレビュー切替
        sc_space = QShortcut(QKeySequence("Space"), self)
        sc_space.activated.connect(self.preview_panel.toggle_view)

        # 1〜9: プリセット切替
        for i in range(1, 10):
            sc = QShortcut(QKeySequence(str(i)), self)
            sc.activated.connect(lambda n=i: self.preset_panel.select_preset_by_number(n))

        # Ctrl+E / Ctrl+Shift+E
        sc_export = QShortcut(QKeySequence("Ctrl+E"), self)
        sc_export.activated.connect(self._export_single)
        sc_export_all = QShortcut(QKeySequence("Ctrl+Shift+E"), self)
        sc_export_all.activated.connect(self._export_all_presets)

    def _setup_signals(self) -> None:
        # 画像プール
        self.pool_panel.images_dropped.connect(self._on_images_dropped)
        self.pool_panel.selection_changed.connect(self._on_image_selected)
        # プール増減時もプリセット有効/無効を再評価
        self.image_pool.images_changed.connect(self._update_preset_availability)

        # プリセット・パラメータ
        self.preset_panel.preset_changed.connect(self._on_preset_changed)
        self.preset_panel.param_changed.connect(self._on_param_changed)
        self.preset_panel.output_size_changed.connect(self._on_output_size_changed)
        self.preset_panel.text_config_changed.connect(self._on_text_config_changed)
        self.preset_panel.assignment_changed.connect(self._on_assignment_changed)

        # プレビューセル内のドラッグクロップオフセット
        self.preview_panel.crop_offset_changed.connect(self._on_crop_offset_changed)
        self.preview_panel.reorder_requested.connect(self._on_preview_reorder_requested)
        # 境界線のドラッグによる分割比率変更
        self.preview_panel.split_ratio_changed.connect(self._on_split_ratio_changed)
        # ドラッグ終了後に高品質再合成を実行
        self.preview_panel.drag_finished.connect(self._on_drag_finished)

        # 履歴
        self.history_panel.export_csv_requested.connect(self._export_csv)
        self.history_panel.record_selected.connect(self._on_history_record_selected)
        self.history_panel.clear_requested.connect(self._clear_history)

    def _apply_dark_theme(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background: #181825; }
            QStatusBar { background: #1e1e2e; color: #585b70; font-size: 11px; }
            QScrollBar:vertical {
                background: #1e1e2e; width: 8px;
                border-radius: 4px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #45475a; border-radius: 4px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar:horizontal {
                background: #1e1e2e; height: 8px; border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #45475a; border-radius: 4px; min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        """)

    # ------------------------------------------------------------------
    # シグナルハンドラ
    # ------------------------------------------------------------------

    def _on_images_dropped(self, paths: list) -> None:
        added = self.image_pool.add_images(paths)
        if added:
            self._drag_fill_arrays = {}  # 画像変更 → キャッシュ無効化
            # 新規追加分はチェック済み、既存のチェック状態を保持して再描画
            self.pool_panel.refresh_keep_checks(added)
            self.statusBar().showMessage(f"{len(added)}枚追加しました")

    def _on_image_selected(self, entries: list) -> None:
        self._selected_images = list(entries)
        self._assigned_image_paths = self._normalize_assignment_paths(self._assigned_image_paths)
        self.preset_panel.set_available_images(self._selected_images)
        self._drag_fill_arrays = {}  # 選択変更 → キャッシュ無効化
        # プリセット有効/無効はチェック済み画像数で判定
        self._update_preset_availability()
        if self._current_preset:
            self._assigned_image_paths = self._coerce_assignment_paths(
                self._current_preset,
                self._assigned_image_paths,
            )
        self.preset_panel.set_assigned_paths(self._assigned_image_paths)
        self._schedule_preview_update()

    def _update_preset_availability(self) -> None:
        """チェック済み画像数に基づいてプリセットの有効/無効を更新"""
        self.preset_panel.update_image_count(len(self._selected_images))

    def _available_paths(self) -> list[str]:
        return [str(entry.path) for entry in self._selected_images]

    def _slot_role_names(self, preset, image_count: int | None = None) -> list[str]:
        if preset is None:
            return []

        count = min(image_count if image_count is not None else len(self._selected_images), preset.max_images)
        if count < preset.min_images:
            return []

        if preset.name == "vsplit":
            return ["導入", "着地"]
        if preset.name == "grid_2x2":
            return ["左上", "右上", "左下", "右下"]
        if preset.name == "center_hero":
            if count == 3:
                return ["導入", "主役", "余韻"]
            if count == 4:
                return ["主役", "補助 上", "補助 中", "補助 下"]
            return ["主役", "導入", "補助 上", "補助 下", "余韻"][:count]
        if preset.name == "hero_top_strip":
            if count == 3:
                return ["主役", "補助 左", "補助 右"]
            return ["主役", "補助 1", "補助 2", "補助 3"][:count]
        if preset.name == "catalog":
            return [f"枠{i + 1}" for i in range(count)]
        return [f"枠{i + 1}" for i in range(count)]

    def _hero_slot_index(self, role_names: list[str]) -> int | None:
        for idx, role_name in enumerate(role_names):
            if "主役" in role_name:
                return idx
        return None

    def _default_assignment_paths(self, preset) -> list[str]:
        if preset is None:
            return self._available_paths()

        entries = list(self._selected_images)
        if preset.name == "center_hero" and len(entries) == 3:
            ordered = [entries[1], entries[0], entries[2]]
            preferred = [str(entry.path) for entry in ordered]
            remaining = [str(entry.path) for entry in entries if str(entry.path) not in preferred]
            return preferred + remaining

        return [str(entry.path) for entry in entries]

    def _normalize_assignment_paths(
        self,
        assigned_paths: list[str],
        default_paths: list[str] | None = None,
    ) -> list[str]:
        available_paths = self._available_paths()
        available_set = set(available_paths)
        normalized: list[str] = []

        for path in assigned_paths:
            if path in available_set and path not in normalized:
                normalized.append(path)

        for path in default_paths or []:
            if path in available_set and path not in normalized:
                normalized.append(path)

        for path in available_paths:
            if path not in normalized:
                normalized.append(path)

        return normalized

    def _coerce_assignment_paths(self, preset, assigned_paths: list[str]) -> list[str]:
        default_paths = self._default_assignment_paths(preset)
        return self._normalize_assignment_paths(assigned_paths, default_paths)

    def _adapt_assignment_paths_for_preset(
        self,
        preset,
        previous_paths: list[str],
        previous_role_names: list[str] | None = None,
    ) -> list[str]:
        available_paths = self._available_paths()
        current_paths = [path for path in previous_paths if path in set(available_paths)]
        if not current_paths:
            return self._coerce_assignment_paths(preset, [])

        next_roles = self._slot_role_names(preset, len(self._selected_images))
        if not next_roles:
            return self._coerce_assignment_paths(preset, current_paths)

        current_roles = list(previous_role_names or [])
        next_assigned = [""] * len(next_roles)
        remaining_paths = list(dict.fromkeys(current_paths))

        current_hero = self._hero_slot_index(current_roles)
        next_hero = self._hero_slot_index(next_roles)
        if (
            current_hero is not None
            and next_hero is not None
            and current_hero < len(current_paths)
        ):
            hero_path = current_paths[current_hero]
            if hero_path in available_paths:
                next_assigned[next_hero] = hero_path
                if hero_path in remaining_paths:
                    remaining_paths.remove(hero_path)

        default_paths = self._default_assignment_paths(preset)
        for path in default_paths:
            if path not in remaining_paths and path not in next_assigned and path in available_paths:
                remaining_paths.append(path)

        for idx in range(len(next_assigned)):
            if next_assigned[idx]:
                continue
            if not remaining_paths:
                break
            next_assigned[idx] = remaining_paths.pop(0)

        front = [path for path in next_assigned if path]
        tail = [path for path in remaining_paths if path not in front]
        return self._normalize_assignment_paths(front + tail, default_paths)

    def _slot_offsets_for_entries(
        self,
        entries: list[ImageEntry],
    ) -> dict[int, tuple[float, float, float]]:
        offsets: dict[int, tuple[float, float, float]] = {}
        for slot, entry in enumerate(entries):
            path = str(entry.path)
            if path in self._crop_offsets_by_path:
                offsets[slot] = self._crop_offsets_by_path[path]
        return offsets

    def _entries_in_assigned_order(self) -> list[ImageEntry]:
        selected_by_path = {str(entry.path): entry for entry in self._selected_images}
        ordered_paths = self._normalize_assignment_paths(self._assigned_image_paths)
        return [
            selected_by_path[path]
            for path in ordered_paths
            if path in selected_by_path
        ]

    def _resolve_images_for_preset(self, preset) -> list | None:
        """プリセットに渡す画像リストを決定する。
        チェック済み画像だけを対象にし、足りない場合は None を返す。"""
        min_n = preset.min_images
        max_n = preset.max_images
        if len(self._selected_images) < min_n:
            return None

        selected_by_path = {str(entry.path): entry for entry in self._selected_images}
        assigned_paths = self._coerce_assignment_paths(preset, self._assigned_image_paths)
        self._assigned_image_paths = list(assigned_paths)
        selected = [
            selected_by_path[path]
            for path in assigned_paths
            if path in selected_by_path
        ]

        # 選択が多すぎる場合はプリセット上限でトリム
        if len(selected) > max_n:
            selected = selected[:max_n]

        # 補完後もまだ足りない場合
        if len(selected) < min_n:
            return None

        # max_n を超えないようにトリム
        return selected[:max_n]

    def _on_preset_changed(self, preset_name: str) -> None:
        preset = self.preset_registry.get(preset_name)
        if preset:
            previous_paths = list(self._assigned_image_paths)
            previous_roles = self._slot_role_names(self._current_preset, len(self._selected_images))
            self._current_preset = preset
            self._current_params = preset.get_defaults()
            self._assigned_image_paths = self._adapt_assignment_paths_for_preset(
                preset,
                previous_paths,
                previous_roles,
            )
            self.preset_panel.set_assigned_paths(self._assigned_image_paths)
            # プリセット変更時はドラッグ状態をリセットする
            self._crop_offsets = {}
            self._active_entry_paths = []
            self._drag_fill_arrays = {}
            self._drag_cell_bounds = {}
            self._prev_offsets_snapshot = {}
            self.preview_panel.reset_offsets()
            self.preview_panel.update_offsets({})
            self._schedule_preview_update()
            self.statusBar().showMessage(f"プリセット: {preset.display_name}")

    def _on_param_changed(self, param_name: str, value) -> None:
        old_val = self._current_params.get(param_name)
        if old_val != value:
            cmd = ParamChangeCommand(self, param_name, old_val, value)
            self.undo_stack.push(cmd)

    def _on_output_size_changed(self, size: tuple) -> None:
        self._current_output_size = size
        self._schedule_preview_update()

    def _on_text_config_changed(self, config: TextConfig) -> None:
        self._text_config = config
        self._schedule_preview_update()

    def _on_assignment_changed(self, assigned_paths: list[str]) -> None:
        self._assigned_image_paths = self._coerce_assignment_paths(
            self._current_preset,
            list(assigned_paths),
        )
        self._drag_fill_arrays = {}
        self._last_entries = []
        self._composite_numpy = None
        self._active_entry_paths = []
        self._crop_offsets = {}
        self.preview_panel.update_offsets({})
        self._schedule_preview_update(0)

    def _on_preview_reorder_requested(self, source_slot: int, target_slot: int) -> None:
        if not self._current_preset:
            return

        entries = self._resolve_images_for_preset(self._current_preset)
        if not entries:
            return

        active_paths = [str(entry.path) for entry in entries]
        if (
            source_slot < 0
            or target_slot < 0
            or source_slot >= len(active_paths)
            or target_slot >= len(active_paths)
            or source_slot == target_slot
        ):
            return

        source_path = active_paths[source_slot]
        target_path = active_paths[target_slot]
        ordered_paths = self._coerce_assignment_paths(
            self._current_preset,
            self._assigned_image_paths,
        )
        try:
            source_index = ordered_paths.index(source_path)
            target_index = ordered_paths.index(target_path)
        except ValueError:
            return

        ordered_paths[source_index], ordered_paths[target_index] = (
            ordered_paths[target_index],
            ordered_paths[source_index],
        )
        self._assigned_image_paths = ordered_paths
        self.preset_panel.set_assigned_paths(self._assigned_image_paths)

        # path 基準でクロップを保持しているので、表示キャッシュだけ更新し直せばよい
        self._active_entry_paths = []
        self._crop_offsets = {}
        self._drag_fill_arrays = {}
        self._last_entries = []
        self._composite_numpy = None
        self.preview_panel.update_offsets({})
        self._schedule_preview_update(0)

    def _on_history_record_selected(self, record) -> None:
        if record.output_path.exists():
            pixmap = QPixmap(str(record.output_path))
            if not pixmap.isNull():
                self.preview_panel.set_pixmap(pixmap)

    def _clear_history(self) -> None:
        if QMessageBox.question(
            self,
            "履歴をクリア",
            "出力履歴を削除します。再起動後も復元されません。続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        self.exporter.history.clear()
        self.history_panel.clear_records()
        self.exporter.save_history(_DEFAULT_HISTORY_PATH)
        self.statusBar().showMessage("出力履歴をクリアしました")

    # ------------------------------------------------------------------
    # プレビュー更新（debounce）
    # ------------------------------------------------------------------

    def _schedule_preview_update(self, delay: int = 200, throttle: bool = False) -> None:
        self._preview_refresh_pending = True
        if throttle:
            if not self._preview_timer.isActive():
                self._preview_timer.start(delay)
        else:
            self._preview_timer.start(delay)

    def _do_preview_update(self) -> None:
        self._preview_refresh_pending = False
        if not self._current_preset:
            return

        if self._preview_worker_running:
            self._preview_refresh_pending = True
            return

        # 合成に使う画像リストを決定
        # 選択枚数がプリセット要件を満たしていない場合はプールから自動補完/トリム
        entries = self._resolve_images_for_preset(self._current_preset)
        self._last_entries = entries or []  # フィルキャッシュ再計算のために保存
        if entries is None:
            self._active_entry_paths = []
            self._crop_offsets = {}
            self.preview_panel.clear()
            self.statusBar().showMessage(
                f"このプリセットは{self._current_preset.min_images}〜"
                f"{self._current_preset.max_images}枚が必要です"
                f"（選択中 {len(self._selected_images)}枚）"
            )
            return

        try:
            images = [e.load_full() for e in entries]
        except Exception as e:
            self.statusBar().showMessage(f"画像読み込みエラー: {e}")
            return

        # テキスト設定をプリセットパネルから最新取得
        text_config = self.preset_panel.get_text_config()
        params = self.preset_panel.get_current_params() or self._current_params
        self._active_entry_paths = [str(entry.path) for entry in entries]
        self._crop_offsets = self._slot_offsets_for_entries(entries)

        # 新規スロットの初期オフセットを顔検出から計算（ドラッグ時のスムーズな移行のため）
        bounds = self.layout_engine.compute_cell_bounds(
            self._current_preset.name, params, self._current_output_size, len(images)
        )
        if bounds:
            for slot, (bx, by, bw, bh) in bounds.items():
                if slot < len(images):
                    path = self._active_entry_paths[slot]
                    if path in self._crop_offsets_by_path:
                        self._crop_offsets[slot] = self._crop_offsets_by_path[path]
                        continue
                    if bw > 0 and bh > 0:
                        ox, oy, zoom = self.layout_engine.calculate_smart_offsets(
                            images[slot], (bw, bh)
                        )
                        self._crop_offsets_by_path[path] = (ox, oy, zoom)
                        self._crop_offsets[slot] = (ox, oy, zoom)
        
        self.preview_panel.update_offsets(self._crop_offsets)

        self._preview_request_id += 1
        request_id = self._preview_request_id
        self._preview_worker_running = True
        self._interactive_source_payloads[request_id] = self._build_interactive_sources(images)

        worker = PreviewWorker(
            request_id,
            self.layout_engine,
            self._current_preset,
            images,
            params,
            self._current_output_size,
            text_config,
            offsets=self._crop_offsets,
        )
        worker.signals.finished.connect(self._on_preview_ready)
        worker.signals.error.connect(self._on_preview_error)
        QThreadPool.globalInstance().start(worker)

    def _on_preview_ready(self, request_id: int, pil_image: Image.Image) -> None:
        self._preview_worker_running = False
        if request_id != self._preview_request_id:
            self._interactive_source_payloads.pop(request_id, None)
            if self._preview_refresh_pending:
                self._schedule_preview_update(0)
            return

        # 最新の合成済みnumpy配列を保存（即時パン用）
        self._composite_numpy = np.array(pil_image.convert("RGB"))
        self.preview_panel.set_pil_image(pil_image)

        # セルバウンズを更新（ドラッグオフセット操作のため）
        self._update_cell_bounds()
        
        # ドラッグ操作（インタラクティブ）用に背景パーツをQGraphicsSceneへ供給
        # (この時点で重い処理なく瞬時にインタラクティブビューへ切り替わる準備が整う)
        self._update_interactive_sources(request_id)

        # 警告チェック（顔検出廃止につきスキップ）
        warnings: list[str] = []
        self.preview_panel.show_warnings(warnings)

        self.statusBar().showMessage(
            f"プレビュー更新 | {pil_image.width}×{pil_image.height}px"
        )
        if self._preview_refresh_pending:
            self._schedule_preview_update(0)

    def _on_preview_error(self, request_id: int, error_msg: str) -> None:
        self._preview_worker_running = False
        self._interactive_source_payloads.pop(request_id, None)
        if request_id != self._preview_request_id:
            if self._preview_refresh_pending:
                self._schedule_preview_update(0)
            return
        self.statusBar().showMessage(f"プレビューエラー: {error_msg}")
        if self._preview_refresh_pending:
            self._schedule_preview_update(0)

    # 高速パスを適用するプリセット（セルが単純な矩形貼り合わせで構成される）
    _FAST_PREVIEW_PRESETS = frozenset({
        "vsplit", "hsplit", "arrow_compare", "label_compare",
        "grid_2x2", "grid_h3", "center_hero", "hero_top_strip", "catalog", "asymmetric",
    })

    def _on_crop_offset_changed(self, slot: int, ox: float, oy: float, zoom: float) -> None:
        """プレビュー内のドラッグ/スクロールでクロップ位置/ズームが変更された"""
        if 0 <= slot < len(self._active_entry_paths):
            self._crop_offsets_by_path[self._active_entry_paths[slot]] = (ox, oy, zoom)
        self._crop_offsets[slot] = (ox, oy, zoom)
        self.preview_panel.update_offsets(self._crop_offsets)
        # ※ 重い _schedule_preview_update は呼ばない。
        # 代わりに mouseRelease などの drag_finished シグナル経由で一度だけ呼ぶ。

    def _on_split_ratio_changed(self, ratio: float) -> None:
        """境界線のドラッグ操作が行われた"""
        if "split_ratio" in self._current_params:
            self._current_params["split_ratio"] = ratio
            # 右パネルのスライダーも同期
            self.preset_panel.set_param_value("split_ratio", ratio)
            
            # 境界領域を再計算
            self._update_cell_bounds()
            
            # 再合成
            # 画像のスケール変更や境界線の描画を正確に行うためにフル描画をスロットルで回す
            # 30msごとに1回の更新を許可（約33fps）し、リアルタイムでドラッグに追従させる
            self._schedule_preview_update(30, throttle=True)

    def _build_interactive_sources(self, images: list[Image.Image]) -> dict[int, Image.Image]:
        """interactive 表示用の軽量画像を生成する"""
        source_images: dict[int, Image.Image] = {}
        for i, img in enumerate(images):
            preview_img = img.copy()
            preview_img.thumbnail((2000, 2000), Image.LANCZOS)
            source_images[i] = preview_img
        return source_images

    def _update_interactive_sources(self, request_id: int | None = None) -> None:
        """QGraphicsScene に対し、ドラッグ用のベース画像を渡す"""
        if request_id is None:
            request_id = self._preview_request_id
        source_images = self._interactive_source_payloads.pop(request_id, None)
        if source_images is None:
            return
        self.preview_panel._preview_label.set_source_images(source_images)

    def _on_drag_finished(self) -> None:
        """ドラッグ終了後に高品質な再合成を実行して最終結果を確定する"""
        self._schedule_preview_update()

    def _update_cell_bounds(self) -> None:
        """プレビューラベルのセル境界情報を更新（ドラッグ操作の座標基準）"""
        if not self._current_preset:
            return
        entries = self._resolve_images_for_preset(self._current_preset)
        if entries is None:
            return
        params = self.preset_panel.get_current_params() or self._current_params
        bounds = self.layout_engine.compute_cell_bounds(
            self._current_preset.name,
            params,
            self._current_output_size,
            len(entries),
        )
        slot_polygons = self.layout_engine.compute_slot_polygons(
            self._current_preset.name,
            params,
            self._current_output_size,
            len(entries),
        )
        preset_name = self._current_preset.name
        self._drag_cell_bounds = bounds  # 高速パス用に保存
        self.preview_panel.set_cell_bounds(
            bounds,
            self._current_output_size,
            preset_name,
            slot_polygons=slot_polygons,
        )
        
        # 境界線ドラッグ用の情報を更新
        if "split_ratio" in params:
            preset_name = self._current_preset.name
            split_mode = None
            if preset_name in ("vsplit", "arrow_compare", "label_compare"):
                split_mode = "v"
            elif preset_name == "hsplit":
                split_mode = "h"
            elif preset_name == "diagonal_wipe":
                split_mode = "diagonal"
            elif preset_name == "bg_color_split":
                split_mode = "bg_color_v"

            self.preview_panel.set_split_info(
                mode=split_mode,
                ratio=params["split_ratio"],
                angle=params.get("angle", 30.0)
            )
        else:
            self.preview_panel.set_split_info(None, 0.5)

    # ------------------------------------------------------------------
    # エクスポート
    # ------------------------------------------------------------------

    def _resolve_export_params(self, preset, current_preset_name: str | None, current_params: dict) -> dict:
        if preset.name == current_preset_name:
            return dict(current_params)
        return preset.get_defaults()

    def _export_preset_record(
        self,
        preset,
        work_id: str,
        text_config: TextConfig,
        current_preset_name: str | None,
        current_params: dict,
        selected_tags: list[str] | None = None,
    ):
        entries = self._resolve_images_for_preset(preset)
        if not entries:
            return None

        params = self._resolve_export_params(preset, current_preset_name, current_params)
        images = [entry.load_full() for entry in entries]
        offsets = self._slot_offsets_for_entries(entries)
        result = self.layout_engine.compose(
            preset,
            images,
            params,
            self._current_output_size,
            text_config,
            offsets=offsets,
        )

        source_paths = [entry.path for entry in entries]
        tags = (
            list(selected_tags)
            if selected_tags is not None
            else sorted({tag for entry in entries for tag in entry.tags})
        )
        return self.exporter.export_single(
            result,
            preset.name,
            work_id,
            source_paths,
            tags,
            params,
        )

    def _export_single(self) -> None:
        if not self._current_preset:
            QMessageBox.warning(self, "エクスポート", "プリセットを選択してください。")
            return

        if not self._resolve_images_for_preset(self._current_preset):
            QMessageBox.warning(self, "エクスポート",
                f"このプリセットは{self._current_preset.min_images}枚以上必要です。")
            return

        work_id = self._current_work_id or self.exporter.generate_work_id()
        self._current_work_id = work_id

        text_config = self.preset_panel.get_text_config()
        current_params = self.preset_panel.get_current_params() or self._current_params

        try:
            record = self._export_preset_record(
                self._current_preset,
                work_id,
                text_config,
                self._current_preset.name,
                current_params,
            )
            if record is None:
                QMessageBox.warning(self, "エクスポート", "出力対象の画像を解決できませんでした。")
                return
            self.history_panel.add_record(record)
            self.exporter.save_history(_DEFAULT_HISTORY_PATH)
            self.statusBar().showMessage(f"エクスポート完了: {record.output_path.name}")
        except Exception as e:
            QMessageBox.critical(self, "エクスポートエラー", str(e))

    def _export_all_presets(self) -> None:
        if not self._selected_images:
            QMessageBox.warning(self, "エクスポート", "画像を選択してください。")
            return

        work_id = self._current_work_id or self.exporter.generate_work_id()
        self._current_work_id = work_id
        compatible_presets = [
            preset
            for preset in self.preset_registry.get_all()
            if len(self._selected_images) >= preset.min_images
        ]
        if not compatible_presets:
            QMessageBox.warning(self, "エクスポート", "対応するプリセットがありません。")
            return

        text_config = self.preset_panel.get_text_config()
        selected_tags = sorted({tag for entry in self._selected_images for tag in entry.tags})
        current_preset_name = self._current_preset.name if self._current_preset else None
        current_params = self.preset_panel.get_current_params() or self._current_params

        try:
            records = []
            for preset in compatible_presets:
                record = self._export_preset_record(
                    preset,
                    work_id,
                    text_config,
                    current_preset_name,
                    current_params,
                    selected_tags=selected_tags,
                )
                if record is not None:
                    records.append(record)

            for rec in records:
                self.history_panel.add_record(rec)
            self.exporter.save_history(_DEFAULT_HISTORY_PATH)
            self.statusBar().showMessage(f"{len(records)}件エクスポート完了")
        except Exception as e:
            QMessageBox.critical(self, "エクスポートエラー", str(e))

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "CSVエクスポート", str(Path.home() / "nts_history.csv"),
            "CSVファイル (*.csv)"
        )
        if path:
            try:
                self.exporter.export_csv(Path(path))
                self.statusBar().showMessage(f"CSV出力: {path}")
            except Exception as e:
                QMessageBox.critical(self, "CSVエクスポートエラー", str(e))

    def _open_output_folder(self) -> None:
        self.history_panel._open_output_folder()

    # ------------------------------------------------------------------
    # プロジェクト保存・読み込み
    # ------------------------------------------------------------------

    def _serialize_project_state(self) -> dict:
        text_config = self.preset_panel.get_text_config()
        return {
            "work_id": self._current_work_id,
            "current_preset": self._current_preset.name if self._current_preset else None,
            "current_params": self.preset_panel.get_current_params() or self._current_params,
            "output_size": list(self._current_output_size),
            "image_pool": self.image_pool.to_json(),
            "text_config": {
                "label_texts": list(text_config.label_texts),
                "title_text": text_config.title_text,
                "arrow_text": text_config.arrow_text,
            },
            "crop_offsets_by_path": {
                path: [ox, oy, zoom]
                for path, (ox, oy, zoom) in self._crop_offsets_by_path.items()
            },
            # 旧版互換
            "crop_offsets": {
                str(slot): [ox, oy, zoom]
                for slot, (ox, oy, zoom) in self._crop_offsets.items()
            },
            "selected_image_paths": [str(e.path) for e in self._selected_images],
            "assigned_image_paths": list(self._assigned_image_paths),
        }

    def _reset_preview_runtime_state(self) -> None:
        self._active_entry_paths = []
        self._crop_offsets = {}
        self._composite_numpy = None
        self._preview_refresh_pending = False
        self._interactive_source_payloads.clear()
        self.preview_panel.reset_offsets()
        self.preview_panel.update_offsets({})

    def _restore_crop_offsets_by_path(self, data: dict) -> None:
        stored_offsets_by_path = {
            str(path): tuple(values)
            for path, values in data.get("crop_offsets_by_path", {}).items()
            if isinstance(values, list) and len(values) == 3
        }
        if stored_offsets_by_path:
            self._crop_offsets_by_path = stored_offsets_by_path
            return

        legacy_offsets = {
            int(slot): tuple(values)
            for slot, values in data.get("crop_offsets", {}).items()
            if isinstance(values, list) and len(values) == 3
        }
        self._crop_offsets_by_path = {}
        for slot, offset in legacy_offsets.items():
            if 0 <= slot < len(self._assigned_image_paths):
                self._crop_offsets_by_path[self._assigned_image_paths[slot]] = offset

    def _restore_project_state(self, data: dict) -> None:
        self._current_work_id = data.get("work_id", "")
        self.image_pool.from_json(data.get("image_pool", {}))
        self.pool_panel.refresh()

        size = data.get("output_size")
        if size:
            self._current_output_size = tuple(size)
            self.preset_panel.set_current_size(self._current_output_size)

        selected_paths = data.get("selected_image_paths", [])
        self.pool_panel.set_checked_paths(selected_paths)

        preset_name = data.get("current_preset")
        current_params = data.get("current_params", {})
        preset = self.preset_registry.get(preset_name) if preset_name else None
        if preset is not None:
            validated_params = preset.validate_params(current_params)
            self.preset_panel.select_preset(preset_name, validated_params)
            for name, value in validated_params.items():
                self.preset_panel.set_param_value(name, value)
            self._current_preset = preset
            self._current_params = dict(validated_params)
        else:
            self._current_preset = None
            self._current_params = dict(current_params)

        assigned_paths = data.get("assigned_image_paths", [])
        if assigned_paths:
            self._assigned_image_paths = self._coerce_assignment_paths(
                self._current_preset,
                list(assigned_paths),
            )
        else:
            self._assigned_image_paths = self._coerce_assignment_paths(
                self._current_preset,
                self.preset_panel.get_assigned_paths(),
            )
        self.preset_panel.set_available_images(self._selected_images)
        self.preset_panel.set_assigned_paths(self._assigned_image_paths)

        text_config_data = data.get("text_config", {})
        restored_text_config = TextConfig(
            label_texts=list(text_config_data.get("label_texts", [])),
            title_text=text_config_data.get("title_text", ""),
            arrow_text=text_config_data.get("arrow_text", ""),
        )
        self._text_config = restored_text_config
        self.preset_panel.set_text_config(restored_text_config)

        self._restore_crop_offsets_by_path(data)
        self._reset_preview_runtime_state()

    def _save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "プロジェクトを保存", "", "NTSプロジェクト (*.nts.json)"
        )
        if not path:
            return
        data = self._serialize_project_state()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.statusBar().showMessage(f"保存完了: {path}")
        except Exception as e:
            QMessageBox.critical(self, "保存エラー", str(e))

    def _load_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "プロジェクトを開く", "", "NTSプロジェクト (*.nts.json)"
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._restore_project_state(data)
            self._schedule_preview_update(0)
            self.statusBar().showMessage(f"読み込み完了: {path}")
        except Exception as e:
            QMessageBox.critical(self, "読み込みエラー", str(e))

    # ------------------------------------------------------------------
    # ファイルダイアログ
    # ------------------------------------------------------------------

    def _open_file_dialog(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "画像を追加", "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if paths:
            from pathlib import Path as _P
            self._on_images_dropped([_P(p) for p in paths])

    # ------------------------------------------------------------------
    # 終了時
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        self.exporter.save_history(_DEFAULT_HISTORY_PATH)
        super().closeEvent(event)
