from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.logging.logger import create_logger
from app.ui.viewmodels.batch_viewmodel import BatchViewModel


class BatchWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, batch_vm: BatchViewModel, input_dir: Path, output_dir: Path, recipe) -> None:
        super().__init__()
        self.batch_vm = batch_vm
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.recipe = recipe

    def run(self) -> None:
        try:
            result = self.batch_vm.run(
                self.input_dir,
                self.output_dir,
                self.recipe,
                lambda current, total, path: self.progress.emit(current, total, path.name),
            )
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)


class BatchWindow(QWidget):
    def __init__(self, batch_vm: BatchViewModel, recipe) -> None:
        super().__init__()
        self.batch_vm = batch_vm
        self.recipe = recipe
        self.input_dir: Path | None = None
        self.output_dir: Path | None = None
        self.worker_thread: QThread | None = None
        self.worker: BatchWorker | None = None
        self.logger = create_logger(Path.cwd() / "data" / "logs" / "app.log")
        self.setWindowTitle("一括適用")
        self.resize(700, 480)

        root = QVBoxLayout(self)
        form = QFormLayout()
        self.input_label = QLabel("未選択")
        self.output_label = QLabel("未選択")
        self.recipe_label = QLabel(recipe.recipe_name)

        input_row = QHBoxLayout()
        input_button = QPushButton("入力フォルダ")
        input_button.clicked.connect(self._select_input_dir)
        input_row.addWidget(input_button)
        input_row.addWidget(self.input_label, 1)

        output_row = QHBoxLayout()
        output_button = QPushButton("出力フォルダ")
        output_button.clicked.connect(self._select_output_dir)
        output_row.addWidget(output_button)
        output_row.addWidget(self.output_label, 1)

        form.addRow("入力", input_row)
        form.addRow("出力", output_row)
        form.addRow("レシピ", self.recipe_label)
        root.addLayout(form)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.current_label = QLabel("待機中")
        self.result_list = QListWidget()

        button_row = QHBoxLayout()
        self.run_button = QPushButton("実行")
        self.run_button.clicked.connect(self._run_batch)
        self.cancel_button = QPushButton("中断")
        self.cancel_button.clicked.connect(self.batch_vm.cancel)
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.cancel_button)

        root.addLayout(button_row)
        root.addWidget(self.progress)
        root.addWidget(self.current_label)
        root.addWidget(QLabel("結果"))
        root.addWidget(self.result_list, 1)

    def _select_input_dir(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "入力フォルダを選択")
        if selected:
            self.input_dir = Path(selected)
            self.input_label.setText(selected)

    def _select_output_dir(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "出力フォルダを選択")
        if selected:
            self.output_dir = Path(selected)
            self.output_label.setText(selected)

    def _on_progress(self, current: int, total: int, path_name: str) -> None:
        self.progress.setValue(int(current / max(1, total) * 100))
        self.current_label.setText(f"処理中: {path_name}")

    def _run_batch(self) -> None:
        if self.input_dir is None or self.output_dir is None:
            QMessageBox.warning(self, "入力不足", "入力フォルダと出力フォルダを選んでください。")
            return
        if self.input_dir.resolve() == self.output_dir.resolve():
            QMessageBox.warning(self, "保存先エラー", "入力フォルダと出力フォルダは分けてください。")
            return

        self.result_list.clear()
        self.progress.setValue(0)
        self.current_label.setText("開始中...")
        self.run_button.setEnabled(False)
        self.logger.info("一括適用画面から実行開始")
        self.worker_thread = QThread(self)
        self.worker = BatchWorker(self.batch_vm, self.input_dir, self.output_dir, self.recipe)
        self.worker.moveToThread(self.worker_thread)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self._cleanup_worker)
        self.worker_thread.start()

    def _on_finished(self, result) -> None:
        for item in result.successes:
            output_name = item.output_path.name if item.output_path else "(なし)"
            self.result_list.addItem(f"成功: {item.source_path.name} -> {output_name}")
        for item in result.failures:
            self.result_list.addItem(f"失敗: {item.source_path.name} / {item.message}")
            self.logger.warning("一括適用失敗: source=%s message=%s", item.source_path, item.message)
        if result.cancelled:
            self.current_label.setText("中断しました。")
        else:
            self.current_label.setText(f"完了: 成功 {len(result.successes)} 件 / 失敗 {len(result.failures)} 件")
        self.logger.info("一括適用結果表示を更新")

    def _on_failed(self, message: str) -> None:
        self.current_label.setText("失敗しました。")
        self.logger.error("一括適用全体が失敗: %s", message)
        QMessageBox.critical(self, "一括適用失敗", message)

    def _cleanup_worker(self) -> None:
        self.run_button.setEnabled(True)
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None
        if self.worker_thread is not None:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.worker_thread is not None and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "一括適用を中断",
                "一括適用を中断して閉じますか。処理中の1枚は完了後に停止します。",
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.batch_vm.cancel()
        super().closeEvent(event)
