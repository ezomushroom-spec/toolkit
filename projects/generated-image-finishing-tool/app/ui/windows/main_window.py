from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent, QDragEnterEvent, QDropEvent, QImage, QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QSpinBox,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.logging.logger import create_logger
from app.core.recipe.schema import STEP_DESCRIPTIONS, STEP_LABELS, STEP_SCHEMAS
from app.core.state.repositories import SettingsRepository
from app.ui.viewmodels.batch_viewmodel import BatchViewModel
from app.ui.viewmodels.editor_viewmodel import EditorViewModel
from app.ui.windows.batch_window import BatchWindow
from app.ui.windows.settings_window import SettingsWindow


class PreviewWorker(QObject):
    finished = Signal(object, int)
    failed = Signal(str, int)

    def __init__(self, editor_vm: EditorViewModel, image: np.ndarray, recipe, request_id: int) -> None:
        super().__init__()
        self.editor_vm = editor_vm
        self.image = image
        self.recipe = recipe
        self.request_id = request_id

    def run(self) -> None:
        try:
            preview = self.editor_vm.executor.run(
                self.image,
                self.recipe,
                self.editor_vm.preview_context(),
            )
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc), self.request_id)
            return
        self.finished.emit(preview, self.request_id)


class IntSliderEditor(QWidget):
    def __init__(self, minimum: int, maximum: int, value: int, on_change) -> None:
        super().__init__()
        self._on_change = on_change
        self._dragging = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.spin_box = QSpinBox()
        self.spin_box.setRange(minimum, maximum)
        self.spin_box.setValue(value)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        self.spin_box.valueChanged.connect(self._on_spin_changed)

        layout.addWidget(self.slider, 1)
        layout.addWidget(self.spin_box)

    def _on_slider_changed(self, value: int) -> None:
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(value)
        self.spin_box.blockSignals(False)
        if not self._dragging:
            self._on_change(value)

    def _on_spin_changed(self, value: int) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self._on_change(value)

    def _on_slider_pressed(self) -> None:
        self._dragging = True

    def _on_slider_released(self) -> None:
        self._dragging = False
        self._on_change(self.slider.value())


class FloatSliderEditor(QWidget):
    def __init__(self, minimum: float, maximum: float, value: float, on_change, *, decimals: int = 2, scale: int = 100) -> None:
        super().__init__()
        self._on_change = on_change
        self._scale = scale
        self._dragging = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(round(minimum * scale)), int(round(maximum * scale)))
        self.slider.setValue(int(round(value * scale)))
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setDecimals(decimals)
        self.spin_box.setSingleStep(1.0 / scale if maximum - minimum <= 2 else 0.05)
        self.spin_box.setRange(minimum, maximum)
        self.spin_box.setValue(value)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        self.spin_box.valueChanged.connect(self._on_spin_changed)

        layout.addWidget(self.slider, 1)
        layout.addWidget(self.spin_box)

    def _on_slider_changed(self, raw_value: int) -> None:
        value = raw_value / self._scale
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(value)
        self.spin_box.blockSignals(False)
        if not self._dragging:
            self._on_change(value)

    def _on_spin_changed(self, value: float) -> None:
        raw_value = int(round(value * self._scale))
        self.slider.blockSignals(True)
        self.slider.setValue(raw_value)
        self.slider.blockSignals(False)
        self._on_change(value)

    def _on_slider_pressed(self) -> None:
        self._dragging = True

    def _on_slider_released(self) -> None:
        self._dragging = False
        self._on_change(self.slider.value() / self._scale)


class MainWindow(QMainWindow):
    def __init__(self, workspace_root: Path) -> None:
        super().__init__()
        self.workspace_root = workspace_root
        self.data_dir = workspace_root / "data"
        self.logger = create_logger(self.data_dir / "logs" / "app.log")
        self.settings_repo = SettingsRepository(self.data_dir / "settings" / "app_settings.json")
        self.editor_vm = EditorViewModel(self.logger)
        self.batch_vm = BatchViewModel(self.logger)
        self.batch_window: BatchWindow | None = None
        self.settings_window: SettingsWindow | None = None
        self.current_step_index = -1
        self.param_widgets: dict[str, QWidget] = {}
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._start_preview_render)
        self.preview_thread: QThread | None = None
        self.preview_worker: PreviewWorker | None = None
        self.preview_request_id = 0
        self.preview_pending = False
        self.temporary_original_preview = False

        self.setWindowTitle("生成画像向け仕上げレシピ適用ツール")
        self.resize(1400, 900)
        self.setAcceptDrops(True)
        self._build_menu()
        self._build_ui()
        self._refresh_recipe_view()
        self._update_window_title()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("ファイル")
        for title, callback in [
            ("画像を開く", self.open_image),
            ("レシピ保存", self.save_recipe),
            ("レシピ読込", self.open_recipe),
            ("書き出し", self.export_image),
            ("一括適用", self.open_batch_window),
            ("設定", self.open_settings),
        ]:
            action = QAction(title, self)
            action.triggered.connect(callback)
            file_menu.addAction(action)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)

        toolbar = QHBoxLayout()
        self.recipe_name_edit = QLineEdit(self.editor_vm.recipe.recipe_name)
        self.recipe_name_edit.editingFinished.connect(self._on_recipe_name_changed)
        toolbar.addWidget(QLabel("レシピ名"))
        toolbar.addWidget(self.recipe_name_edit, 1)

        self.compare_mode_combo = QComboBox()
        self.compare_mode_combo.addItems(["補正後", "補正前", "左右比較"])
        self.compare_mode_combo.currentTextChanged.connect(lambda _: self._schedule_preview(immediate=True))
        toolbar.addWidget(QLabel("表示"))
        toolbar.addWidget(self.compare_mode_combo)

        self.hold_original_button = QPushButton("押している間だけ元画像")
        self.hold_original_button.setCheckable(True)
        self.hold_original_button.pressed.connect(self._show_original_temporarily)
        self.hold_original_button.released.connect(self._restore_processed_preview)
        toolbar.addWidget(self.hold_original_button)
        root_layout.addLayout(toolbar)

        splitter = QSplitter()
        root_layout.addWidget(splitter, 1)

        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        self.preview_label = QLabel("画像を開いてください。")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(640, 640)
        preview_layout.addWidget(self.preview_label, 1)

        step_panel = QWidget()
        step_layout = QVBoxLayout(step_panel)
        step_layout.addWidget(QLabel("工程一覧"))
        self.step_list = QListWidget()
        self.step_list.currentRowChanged.connect(self._on_step_selected)
        step_layout.addWidget(self.step_list, 1)

        step_button_row = QHBoxLayout()
        self.step_type_combo = QComboBox()
        for step_type, label in STEP_LABELS.items():
            self.step_type_combo.addItem(label, step_type)
        step_button_row.addWidget(self.step_type_combo, 1)

        add_step_button = QPushButton("工程追加")
        add_step_button.clicked.connect(self.add_step)
        remove_step_button = QPushButton("削除")
        remove_step_button.clicked.connect(self.remove_step)
        up_button = QPushButton("上へ")
        up_button.clicked.connect(lambda: self.move_step(-1))
        down_button = QPushButton("下へ")
        down_button.clicked.connect(lambda: self.move_step(1))
        for button in [add_step_button, remove_step_button, up_button, down_button]:
            step_button_row.addWidget(button)
        step_layout.addLayout(step_button_row)

        self.detail_panel = QWidget()
        self.detail_form = QFormLayout(self.detail_panel)
        self.step_enabled_checkbox = QCheckBox("有効")
        self.step_enabled_checkbox.stateChanged.connect(self._on_step_enabled_changed)
        self.detail_form.addRow("有効 / 無効", self.step_enabled_checkbox)
        self.step_description = QTextEdit()
        self.step_description.setReadOnly(True)
        self.step_description.setFixedHeight(80)
        self.detail_form.addRow("説明", self.step_description)
        step_layout.addWidget(self.detail_panel)

        splitter.addWidget(preview_panel)
        splitter.addWidget(step_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def open_image(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "画像を開く", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not selected:
            return
        self._open_image_path(Path(selected))

    def _open_image_path(self, path: Path) -> None:
        try:
            self.editor_vm.open_image(path)
            self.status.showMessage(f"画像を読み込みました: {path}", 5000)
            self._schedule_preview(immediate=True)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("画像読込失敗: %s", path)
            QMessageBox.critical(self, "読込失敗", str(exc))

    def add_step(self) -> None:
        self.editor_vm.add_step(self.step_type_combo.currentData())
        self._refresh_recipe_view()
        self.step_list.setCurrentRow(len(self.editor_vm.recipe.steps) - 1)
        self._update_window_title()
        self._schedule_preview()

    def remove_step(self) -> None:
        self.editor_vm.remove_step(self.step_list.currentRow())
        self._refresh_recipe_view()
        self._update_window_title()
        self._schedule_preview()

    def move_step(self, offset: int) -> None:
        new_index = self.editor_vm.move_step(self.step_list.currentRow(), offset)
        self._refresh_recipe_view()
        self.step_list.setCurrentRow(new_index)
        self._update_window_title()
        self._schedule_preview()

    def save_recipe(self) -> None:
        selected, _ = QFileDialog.getSaveFileName(self, "レシピ保存", str(self.data_dir / "recipes" / f"{self.editor_vm.recipe.recipe_name}.json"), "JSON (*.json)")
        if not selected:
            return
        try:
            self._on_recipe_name_changed()
            self.editor_vm.save_recipe(Path(selected))
            self.status.showMessage("レシピを保存しました。", 5000)
            self._update_window_title()
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("レシピ保存失敗: %s", selected)
            QMessageBox.critical(self, "保存失敗", str(exc))

    def open_recipe(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "レシピ読込", str(self.data_dir / "recipes"), "JSON (*.json)")
        if not selected:
            return
        try:
            self.editor_vm.load_recipe(Path(selected))
            self.recipe_name_edit.setText(self.editor_vm.recipe.recipe_name)
            self._refresh_recipe_view()
            self._schedule_preview(immediate=True)
            self.status.showMessage("レシピを読み込みました。", 5000)
            self._update_window_title()
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("レシピ読込失敗: %s", selected)
            QMessageBox.critical(self, "読込失敗", str(exc))

    def export_image(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "書き出し先を選択", str(self.data_dir / "exports"))
        if not selected:
            return
        try:
            self._on_recipe_name_changed()
            output_path = self.editor_vm.export_image(Path(selected))
            self.status.showMessage(f"書き出しました: {output_path}", 7000)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("画像書き出し失敗: %s", selected)
            QMessageBox.critical(self, "書き出し失敗", str(exc))

    def open_batch_window(self) -> None:
        self.batch_window = BatchWindow(self.batch_vm, self.editor_vm.recipe)
        self.batch_window.show()

    def open_settings(self) -> None:
        self.settings_window = SettingsWindow(self.settings_repo)
        self.settings_window.show()

    def _on_recipe_name_changed(self) -> None:
        new_name = self.recipe_name_edit.text().strip() or "新規レシピ"
        if self.editor_vm.recipe.recipe_name != new_name:
            self.editor_vm.recipe.recipe_name = new_name
            self.editor_vm.dirty = True
            self._update_window_title()

    def _clear_param_rows(self) -> None:
        while self.detail_form.rowCount() > 2:
            self.detail_form.removeRow(2)
        self.param_widgets.clear()

    def _on_step_selected(self, index: int) -> None:
        self.current_step_index = index
        self._clear_param_rows()
        if not (0 <= index < len(self.editor_vm.recipe.steps)):
            self.step_description.clear()
            self.step_enabled_checkbox.setChecked(False)
            return

        step = self.editor_vm.recipe.steps[index]
        self.step_enabled_checkbox.blockSignals(True)
        self.step_enabled_checkbox.setChecked(step.enabled)
        self.step_enabled_checkbox.blockSignals(False)
        self.step_description.setText(STEP_DESCRIPTIONS.get(step.step_type, ""))

        for schema in STEP_SCHEMAS[step.step_type]:
            if schema.value_type is bool:
                widget = QCheckBox()
                widget.setChecked(bool(step.params[schema.key]))
                widget.stateChanged.connect(lambda _state, key=schema.key, w=widget: self._update_step_param(key, w.isChecked()))
            elif schema.value_type is int:
                minimum = int(schema.minimum) if schema.minimum is not None else 0
                maximum = int(schema.maximum) if schema.maximum is not None else 999
                widget = IntSliderEditor(
                    minimum,
                    maximum,
                    int(step.params[schema.key]),
                    lambda value, key=schema.key: self._update_step_param(key, int(value)),
                )
            else:
                value = float(step.params[schema.key])
                minimum = float(schema.minimum) if schema.minimum is not None else -999.0
                maximum = float(schema.maximum) if schema.maximum is not None else 999.0
                scale = 100 if maximum - minimum <= 2 else 20
                widget = FloatSliderEditor(
                    minimum,
                    maximum,
                    value,
                    lambda new_value, key=schema.key: self._update_step_param(key, float(new_value)),
                    scale=scale,
                )
            widget.setToolTip(schema.description)
            self.detail_form.addRow(schema.label, widget)
            self.param_widgets[schema.key] = widget

    def _on_step_enabled_changed(self) -> None:
        if 0 <= self.current_step_index < len(self.editor_vm.recipe.steps):
            self.editor_vm.recipe.steps[self.current_step_index].enabled = self.step_enabled_checkbox.isChecked()
            self.editor_vm.dirty = True
            self._refresh_recipe_view()
            self._update_window_title()
            self._schedule_preview()

    def _update_step_param(self, key: str, value) -> None:
        if 0 <= self.current_step_index < len(self.editor_vm.recipe.steps):
            self.editor_vm.recipe.steps[self.current_step_index].params[key] = value
            self.editor_vm.dirty = True
            self._update_window_title()
            self._schedule_preview()

    def _refresh_recipe_view(self) -> None:
        self.step_list.clear()
        for step in self.editor_vm.recipe.steps:
            prefix = "ON" if step.enabled else "OFF"
            self.step_list.addItem(QListWidgetItem(f"[{prefix}] {self.editor_vm.step_label(step.step_type)}"))

    def _schedule_preview(self, *, immediate: bool = False) -> None:
        if self.editor_vm.current_image is None:
            return
        self.preview_pending = True
        self.preview_timer.start(0 if immediate else 120)
        if not immediate:
            self.status.showMessage("プレビュー更新待機中...", 1000)

    def _start_preview_render(self) -> None:
        if self.editor_vm.current_image is None:
            return
        if self.preview_thread is not None and self.preview_thread.isRunning():
            return

        self.preview_pending = False
        self.preview_request_id += 1
        request_id = self.preview_request_id
        image = self.editor_vm.current_image.copy()
        recipe = copy.deepcopy(self.editor_vm.recipe)

        self.preview_thread = QThread(self)
        self.preview_worker = PreviewWorker(self.editor_vm, image, recipe, request_id)
        self.preview_worker.moveToThread(self.preview_thread)
        self.preview_thread.started.connect(self.preview_worker.run)
        self.preview_worker.finished.connect(self._on_preview_finished)
        self.preview_worker.failed.connect(self._on_preview_failed)
        self.preview_worker.finished.connect(self.preview_thread.quit)
        self.preview_worker.failed.connect(self.preview_thread.quit)
        self.preview_thread.finished.connect(self._cleanup_preview_worker)
        self.preview_thread.start()
        self.status.showMessage("プレビュー更新中...", 1200)

    def _on_preview_finished(self, preview: np.ndarray, request_id: int) -> None:
        if request_id != self.preview_request_id:
            return
        try:
            self.editor_vm.preview_image = preview
            self._apply_current_preview_mode()
            self.status.showMessage("プレビュー更新完了", 1200)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("プレビュー反映失敗")
            QMessageBox.critical(self, "プレビュー失敗", str(exc))

    def _on_preview_failed(self, message: str, request_id: int) -> None:
        if request_id != self.preview_request_id:
            return
        self.logger.error("プレビュー更新失敗: %s", message)
        QMessageBox.critical(self, "プレビュー失敗", message)

    def _cleanup_preview_worker(self) -> None:
        if self.preview_worker is not None:
            self.preview_worker.deleteLater()
            self.preview_worker = None
        if self.preview_thread is not None:
            self.preview_thread.deleteLater()
            self.preview_thread = None
        if self.preview_pending:
            self.preview_timer.start(0)

    def _apply_current_preview_mode(self) -> None:
        if self.editor_vm.current_image is None:
            return
        display = self.editor_vm.preview_image if self.editor_vm.preview_image is not None else self.editor_vm.current_image
        if self.temporary_original_preview:
            display = self.editor_vm.current_image
        else:
            mode = self.compare_mode_combo.currentText()
            if mode == "補正前":
                display = self.editor_vm.current_image
            elif mode == "左右比較" and self.editor_vm.preview_image is not None:
                before = self.editor_vm.current_image
                after = self.editor_vm.preview_image
                min_height = min(before.shape[0], after.shape[0])
                display = np.concatenate([before[:min_height], after[:min_height]], axis=1)
        self.preview_label.setPixmap(self._array_to_pixmap(display))

    def _show_original_temporarily(self) -> None:
        if self.editor_vm.current_image is None:
            return
        self.temporary_original_preview = True
        self._apply_current_preview_mode()
        self.status.showMessage("元画像を表示中", 1000)

    def _restore_processed_preview(self) -> None:
        self.temporary_original_preview = False
        self.hold_original_button.setChecked(False)
        self._apply_current_preview_mode()
        self.status.showMessage("補正後表示に戻りました", 1000)

    def _update_window_title(self) -> None:
        suffix = " *" if self.editor_vm.dirty else ""
        self.setWindowTitle(f"生成画像向け仕上げレシピ適用ツール - {self.editor_vm.recipe.recipe_name}{suffix}")

    def closeEvent(self, event: QCloseEvent) -> None:
        self.preview_timer.stop()
        if self.preview_thread is not None and self.preview_thread.isRunning():
            self.preview_thread.quit()
            self.preview_thread.wait(2000)
        if self.editor_vm.dirty:
            reply = QMessageBox.question(
                self,
                "未保存の変更があります",
                "レシピに未保存の変更があります。保存せずに閉じますか。",
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._show_original_temporarily()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._restore_processed_preview()
            event.accept()
            return
        super().keyReleaseEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        path = self._extract_dropped_image_path(event)
        if path is not None:
            event.acceptProposedAction()
            self.status.showMessage(f"ドロップ受付: {path.name}", 2000)
            return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        path = self._extract_dropped_image_path(event)
        if path is None:
            self.status.showMessage("画像ファイルのドロップだけを受け付けます。", 4000)
            event.ignore()
            return
        self._open_image_path(path)
        event.acceptProposedAction()

    def _extract_dropped_image_path(self, event: QDragEnterEvent | QDropEvent) -> Path | None:
        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            return None

        for url in mime_data.urls():
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
                return path.resolve()
        return None

    @staticmethod
    def _array_to_pixmap(image: np.ndarray) -> QPixmap:
        height, width, channels = image.shape
        q_image = QImage(image.data, width, height, channels * width, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image.copy())
        return pixmap.scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
