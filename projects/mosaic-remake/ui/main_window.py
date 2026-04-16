import os

import cv2
from PySide6.QtCore import QThread, Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.config import (
    APP_TITLE,
    DEFAULT_MODEL_FILE,
    TARGET_CLASSES,
    load_settings,
    save_settings,
)
from core.processor import MosaicProcessor
from ui.image_list import ImageListWidget
from ui.param_panel import ParamPanel
from ui.preview_canvas import PreviewCanvas
from utils.file_io import imread_safe


class BatchWorker(QThread):
    progressUpdated = Signal(int, int, str)
    finishedProcessing = Signal(int, int)

    def __init__(self, processor, input_dir, output_dir, params, class_settings, reviewed_candidates_by_path):
        super().__init__()
        self.processor = processor
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.params = params
        self.class_settings = class_settings
        self.reviewed_candidates_by_path = reviewed_candidates_by_path

    def run(self):
        self.processor.process_batch(
            self.input_dir,
            self.output_dir,
            self.params["imgsz"],
            self.params["strength"],
            self.params["margin"],
            self.params["mask_type"],
            self.params["shape_type"],
            self.class_settings,
            self.reviewed_candidates_by_path,
            progress_cb=lambda step, total, name: self.progressUpdated.emit(
                step, total, name
            ),
            finish_cb=lambda processed, errors: self.finishedProcessing.emit(
                processed, errors
            ),
        )


class PreviewWorker(QThread):
    previewReady = Signal(int, object, object)

    def __init__(self, processor, request_id, image, params, class_settings):
        super().__init__()
        self.processor = processor
        self.request_id = request_id
        self.image = None if image is None else image.copy()
        self.params = dict(params)
        self.class_settings = {
            key: dict(value) for key, value in class_settings.items()
        }

    def run(self):
        preview_image, valid_candidates = self.processor.render_preview(
            self.image,
            self.params,
            self.class_settings,
        )
        self.previewReady.emit(self.request_id, preview_image, valid_candidates)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1150, 900)
        self.setMinimumSize(900, 700)

        self.processor = MosaicProcessor()
        self.current_preview_image = None
        self.current_preview_path = ""
        self.current_preview_candidates = []
        self.current_preview_request_id = 0
        self.latest_applied_preview_id = 0
        self.preview_worker = None
        self.preview_workers = []
        self.preview_manual_boxes = []
        self.reviewed_candidates_by_path = {}
        self.worker = None
        self.progress_dialog = None
        self.preview_refresh_timer = QTimer(self)
        self.preview_refresh_timer.setSingleShot(True)
        self.preview_refresh_timer.timeout.connect(self._start_preview_refresh)

        self.init_ui()
        self.setup_connections()
        self.restore_settings()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        splitter_main = QSplitter(Qt.Horizontal)

        self.param_panel = ParamPanel()
        self.param_panel.build_class_settings(TARGET_CLASSES)
        splitter_main.addWidget(self.param_panel)

        right_panel = QSplitter(Qt.Horizontal)
        self.image_list = ImageListWidget()
        self.preview_canvas = PreviewCanvas()
        right_panel.addWidget(self.image_list)
        right_panel.addWidget(self.preview_canvas)
        right_panel.setSizes([150, 650])

        splitter_main.addWidget(right_panel)
        splitter_main.setSizes([350, 800])
        main_layout.addWidget(splitter_main)

    def setup_connections(self):
        self.image_list.folderDropped.connect(self.on_folder_set)
        self.preview_canvas.folderDropped.connect(self.on_folder_set)
        self.image_list.fileSelected.connect(self.on_file_selected)
        self.preview_canvas.boxSelectionChanged.connect(self.on_preview_boxes_changed)
        self.param_panel.inputFolderChanged.connect(self.on_folder_set)
        self.param_panel.modelPathChanged.connect(self.on_model_selected)
        self.param_panel.paramChanged.connect(self.schedule_preview_refresh)
        self.param_panel.processRequested.connect(self.start_batch_processing)

    def restore_settings(self):
        settings = load_settings()
        self.param_panel.apply_settings(settings)
        input_dir = settings.get("input_dir", "")
        if input_dir and input_dir != "未選択":
            self.on_folder_set(input_dir)

        model_path = settings.get("model_path", "")
        if model_path:
            self.load_model(model_path)
        elif os.path.exists(DEFAULT_MODEL_FILE):
            self.load_model(DEFAULT_MODEL_FILE)

    def closeEvent(self, event):
        if self.preview_worker and self.preview_worker.isRunning():
            self.preview_worker.wait(1000)
        for worker in list(self.preview_workers):
            if worker.isRunning():
                worker.wait(1000)
        if self.worker and self.worker.isRunning():
            self.processor.stop_flag = True
            self.worker.wait(2000)
        save_settings(self.param_panel.get_settings_payload())
        super().closeEvent(event)

    def load_model(self, model_path: str) -> bool:
        success, _class_names = self.processor.load_model(model_path)
        if success:
            self.param_panel.set_model_path(model_path)
            return True
        return False

    def on_model_selected(self, model_path: str):
        if not self.load_model(model_path):
            QMessageBox.warning(self, "エラー", "モデルの読み込みに失敗しました。")
            return
        self.schedule_preview_refresh(immediate=True)

    def on_folder_set(self, dir_path: str):
        self.param_panel.set_input_dir(dir_path)
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        paths = []
        try:
            for entry in os.scandir(dir_path):
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in exts:
                    paths.append(entry.path)
        except Exception:
            paths = []

        paths = sorted(paths)
        self.image_list.set_files(paths)

    def on_file_selected(self, file_path: str):
        img_bgr = imread_safe(file_path)
        if img_bgr is None:
            return

        self.current_preview_image = img_bgr
        self.current_preview_path = file_path
        self.preview_manual_boxes = []
        self.schedule_preview_refresh(immediate=True)

    def _normalize_box(self, xyxy):
        return tuple(int(round(value)) for value in xyxy)

    def schedule_preview_refresh(self, immediate: bool = False):
        if immediate:
            self.preview_refresh_timer.stop()
            self._start_preview_refresh()
            return
        self.preview_refresh_timer.start(90)

    def _start_preview_refresh(self):
        if self.current_preview_image is None:
            return

        params = self.param_panel.get_current_params()
        class_settings = self.param_panel.get_class_settings()
        has_enabled = any(data["enabled"] for data in class_settings.values())

        if not has_enabled or not self.processor.has_model():
            self.current_preview_candidates = []
            self.preview_manual_boxes = []
            self._set_bgr_to_canvas(self.current_preview_image)
            self.preview_canvas.set_boxes([])
            return

        self.current_preview_request_id += 1
        request_id = self.current_preview_request_id

        self.preview_worker = PreviewWorker(
            self.processor,
            request_id,
            self.current_preview_image,
            params,
            class_settings,
        )
        self.preview_workers.append(self.preview_worker)
        self.preview_worker.previewReady.connect(self.on_preview_ready)
        self.preview_worker.finished.connect(
            lambda worker=self.preview_worker: self.on_preview_worker_finished(worker)
        )
        self.preview_worker.start()

    def on_preview_ready(self, request_id: int, preview_image, valid_candidates):
        if request_id < self.current_preview_request_id:
            return

        self.latest_applied_preview_id = request_id
        self.current_preview_candidates = list(valid_candidates or [])
        self.preview_manual_boxes = [
            candidate["xyxy"] for candidate in self.current_preview_candidates
        ]
        if self.current_preview_path:
            self.reviewed_candidates_by_path[self.current_preview_path] = list(
                self.current_preview_candidates
            )

        if preview_image is None:
            preview_image = self.current_preview_image

        self._set_bgr_to_canvas(preview_image)
        if self.param_panel.get_current_params().get("show_boxes", True):
            self.preview_canvas.set_boxes(self.current_preview_candidates)
        else:
            self.preview_canvas.set_boxes([])

    def on_preview_worker_finished(self, worker):
        if worker in self.preview_workers:
            self.preview_workers.remove(worker)
        if self.preview_worker is worker and not worker.isRunning():
            self.preview_worker = None

    def on_preview_boxes_changed(self):
        self.preview_manual_boxes = self.preview_canvas.get_remaining_boxes()
        if not self.current_preview_path:
            return

        remaining_boxes = {
            self._normalize_box(box) for box in self.preview_manual_boxes
        }
        reviewed_candidates = [
            candidate
            for candidate in self.current_preview_candidates
            if self._normalize_box(candidate["xyxy"]) in remaining_boxes
        ]
        self.reviewed_candidates_by_path[self.current_preview_path] = reviewed_candidates

    def _set_bgr_to_canvas(self, img_bgr):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        height, width, channels = img_rgb.shape
        bytes_per_line = channels * width
        qimg = QImage(
            img_rgb.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888,
        )
        self.preview_canvas.set_image(QPixmap.fromImage(qimg))

    def start_batch_processing(self):
        input_dir = self.param_panel.get_input_dir()
        output_dir = self.param_panel.get_output_dir()
        params = self.param_panel.get_current_params()
        class_settings = self.param_panel.get_class_settings()

        if not input_dir or input_dir == "未選択" or not os.path.exists(input_dir):
            QMessageBox.warning(self, "エラー", "入力フォルダを正しく設定してください。")
            return
        if not output_dir or output_dir == "未選択":
            QMessageBox.warning(self, "エラー", "出力フォルダを設定してください。")
            return

        has_enabled = any(data["enabled"] for data in class_settings.values())
        if has_enabled and not self.processor.has_model():
            QMessageBox.warning(self, "エラー", "`.pt` モデルを読み込んでください。")
            return

        self.param_panel.btn_run.setEnabled(False)
        self.progress_dialog = QProgressDialog("処理中...", "キャンセル", 0, 100, self)
        self.progress_dialog.setWindowTitle("一括処理")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.canceled.connect(self.cancel_batch_processing)
        self.progress_dialog.show()

        self.worker = BatchWorker(
            self.processor,
            input_dir,
            output_dir,
            params,
            class_settings,
            dict(self.reviewed_candidates_by_path),
        )
        self.worker.progressUpdated.connect(self.on_batch_progress)
        self.worker.finishedProcessing.connect(self.on_batch_finished)
        self.worker.start()

    def cancel_batch_processing(self):
        self.processor.stop_flag = True
        if self.progress_dialog:
            self.progress_dialog.setLabelText("キャンセル中...")

    def on_batch_progress(self, step: int, total: int, name: str):
        if not self.progress_dialog:
            return
        self.progress_dialog.setMaximum(total)
        self.progress_dialog.setValue(step)
        self.progress_dialog.setLabelText(f"処理中... {name}")

    def on_batch_finished(self, processed_count: int, error_count: int):
        was_cancelled = self.processor.stop_flag
        self.processor.stop_flag = False

        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        self.param_panel.btn_run.setEnabled(True)

        if was_cancelled:
            QMessageBox.information(
                self,
                "キャンセル",
                f"処理を中断しました。\n成功: {processed_count} 件\nエラー: {error_count} 件",
            )
            return

        message = f"処理完了\n成功: {processed_count} 件\nエラー: {error_count} 件"
        if error_count > 0:
            QMessageBox.warning(self, "完了 (エラーあり)", message)
        else:
            QMessageBox.information(self, "完了", message)
