import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.config import INFERENCE_SIZES, MASK_TYPES, SHAPE_TYPES


class DropPathLabel(QLabel):
    pathDropped = Signal(str)

    def __init__(self, placeholder: str, drop_message: str, parent=None):
        super().__init__(placeholder, parent)
        self.placeholder = placeholder
        self.drop_message = drop_message
        self.setAcceptDrops(True)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(82)
        self._set_idle_style(is_placeholder=True)

    def set_path_text(self, path: str):
        normalized = path or self.placeholder
        if normalized == self.placeholder:
            self.setText(self.drop_message)
        else:
            self.setText(normalized)
        self.setToolTip("" if normalized == self.placeholder else normalized)
        self._set_idle_style(is_placeholder=normalized == self.placeholder)

    def dragEnterEvent(self, event):
        resolved_path = self._resolve_drop_path(event)
        if resolved_path:
            self._set_drag_style()
            event.acceptProposedAction()
            return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._set_idle_style(is_placeholder=self.text() == self.placeholder)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        resolved_path = self._resolve_drop_path(event)
        self._set_idle_style(is_placeholder=self.text() == self.placeholder)
        if resolved_path:
            self.pathDropped.emit(resolved_path)
            event.acceptProposedAction()
            return
        event.ignore()

    def _resolve_drop_path(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                local_path = url.toLocalFile()
                if not local_path:
                    continue
                if os.path.isdir(local_path):
                    return os.path.abspath(local_path)
                if os.path.isfile(local_path):
                    return os.path.abspath(os.path.dirname(local_path))

        if mime.hasText():
            text = mime.text().strip().strip('"')
            if os.path.isdir(text):
                return os.path.abspath(text)
            if os.path.isfile(text):
                return os.path.abspath(os.path.dirname(text))
        return None

    def _set_idle_style(self, is_placeholder: bool):
        color = "#888" if is_placeholder else "#ddd"
        self.setStyleSheet(
            "border: 1px dashed #666; "
            "border-radius: 10px; "
            "padding: 12px; "
            f"color: {color}; "
            "background-color: #1c1f26;"
        )

    def _set_drag_style(self):
        self.setStyleSheet(
            "border: 2px solid #4da3ff; "
            "border-radius: 10px; "
            "padding: 12px; "
            "color: #ffffff; "
            "background-color: #223044;"
        )


def _link_slider_spin(slider: QSlider, spin: QDoubleSpinBox, scale: float, on_change):
    """
    スライダーとスピンボックスを双方向リンクする。
    相互伝播ループを blockSignals で防ぎ、paramChanged は1回だけ発火する。
    scale: slider整数値 → spin実数値への係数 (例: 1/100.0)
    """
    def slider_moved(int_val):
        spin.blockSignals(True)
        spin.setValue(int_val * scale)
        spin.blockSignals(False)
        on_change()

    def spin_changed(float_val):
        slider.blockSignals(True)
        slider.setValue(int(float_val / scale))
        slider.blockSignals(False)
        on_change()

    slider.valueChanged.connect(slider_moved)
    spin.valueChanged.connect(spin_changed)


class ParamPanel(QWidget):
    paramChanged = Signal()
    processRequested = Signal()
    inputFolderChanged = Signal(str)
    outputFolderChanged = Signal(str)
    modelPathChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.class_settings_ui = {}
        self.model_path = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        group_folder = QGroupBox("フォルダ設定")
        layout_folder = QVBoxLayout()
        layout_folder.setSpacing(10)

        model_header = QHBoxLayout()
        model_title = QLabel("推論モデル")
        model_title.setStyleSheet("font-weight: bold;")
        model_header.addWidget(model_title)
        model_header.addStretch(1)
        self.lbl_model_path = DropPathLabel(
            "未選択",
            "`.pt` モデルをここにドロップ\nまたは参照ボタンで選択",
        )
        self.lbl_model_path.pathDropped.connect(self.on_drop_model_path)
        btn_model = QPushButton("参照")
        btn_model.setFixedWidth(72)
        btn_model.clicked.connect(self.on_select_model)
        model_header.addWidget(btn_model)
        layout_folder.addLayout(model_header)
        layout_folder.addWidget(self.lbl_model_path)

        input_header = QHBoxLayout()
        input_title = QLabel("入力フォルダ")
        input_title.setStyleSheet("font-weight: bold;")
        input_header.addWidget(input_title)
        input_header.addStretch(1)
        self.lbl_input_dir = DropPathLabel(
            "未選択",
            "ここにドロップ\nまたは参照ボタンで選択",
        )
        self.lbl_input_dir.pathDropped.connect(self.on_drop_input_dir)
        btn_in = QPushButton("参照")
        btn_in.setFixedWidth(72)
        btn_in.clicked.connect(self.on_select_input)
        input_header.addWidget(btn_in)
        layout_folder.addLayout(input_header)
        layout_folder.addWidget(self.lbl_input_dir)

        output_header = QHBoxLayout()
        output_title = QLabel("出力フォルダ")
        output_title.setStyleSheet("font-weight: bold;")
        output_header.addWidget(output_title)
        output_header.addStretch(1)
        self.lbl_output_dir = DropPathLabel(
            "未選択",
            "ここにドロップ\nまたは参照ボタンで選択",
        )
        self.lbl_output_dir.pathDropped.connect(self.on_drop_output_dir)
        btn_out = QPushButton("参照")
        btn_out.setFixedWidth(72)
        btn_out.clicked.connect(self.on_select_output)
        output_header.addWidget(btn_out)
        layout_folder.addLayout(output_header)
        layout_folder.addWidget(self.lbl_output_dir)

        hint = QLabel("モデルは `.pt` を、入出力欄はフォルダまたは画像ファイルをドロップできます")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        hint.setWordWrap(True)
        layout_folder.addWidget(hint)

        group_folder.setLayout(layout_folder)
        layout.addWidget(group_folder)

        self.group_classes = QGroupBox("対象部位・検知感度")
        self.layout_classes = QVBoxLayout()
        self.group_classes.setLayout(self.layout_classes)
        layout.addWidget(self.group_classes)

        group_param = QGroupBox("加工パラメータ")
        layout_param = QVBoxLayout()

        row_type = QHBoxLayout()
        row_type.addWidget(QLabel("種類:"))
        self.combo_type = QComboBox()
        for key, label in MASK_TYPES.items():
            self.combo_type.addItem(label, key)
        self.combo_type.currentIndexChanged.connect(lambda _: self.paramChanged.emit())
        row_type.addWidget(self.combo_type, 1)

        row_type.addWidget(QLabel("形状:"))
        self.combo_shape = QComboBox()
        for key, label in SHAPE_TYPES.items():
            self.combo_shape.addItem(label, key)
        self.combo_shape.currentIndexChanged.connect(lambda _: self.paramChanged.emit())
        row_type.addWidget(self.combo_shape, 1)
        layout_param.addLayout(row_type)

        row_imgsz = QHBoxLayout()
        row_imgsz.addWidget(QLabel("認識解像度:"))
        self.combo_imgsz = QComboBox()
        for size in INFERENCE_SIZES:
            self.combo_imgsz.addItem(str(size), size)
        self.combo_imgsz.currentIndexChanged.connect(lambda _: self.paramChanged.emit())
        row_imgsz.addWidget(self.combo_imgsz, 1)
        layout_param.addLayout(row_imgsz)

        row_str = QHBoxLayout()
        row_str.addWidget(QLabel("フィルタ強度:"))
        self.spin_str = QDoubleSpinBox()
        self.spin_str.setRange(1.0, 100.0)
        self.spin_str.setValue(15.0)
        self.slider_str = QSlider(Qt.Horizontal)
        self.slider_str.setRange(1, 100)
        self.slider_str.setValue(15)
        _link_slider_spin(self.slider_str, self.spin_str, 1.0, self.paramChanged.emit)
        row_str.addWidget(self.slider_str, 1)
        row_str.addWidget(self.spin_str)
        layout_param.addLayout(row_str)

        row_margin = QHBoxLayout()
        row_margin.addWidget(QLabel("範囲拡張(px):"))
        self.spin_margin = QDoubleSpinBox()
        self.spin_margin.setRange(0.0, 100.0)
        self.spin_margin.setValue(15.0)
        self.slider_margin = QSlider(Qt.Horizontal)
        self.slider_margin.setRange(0, 100)
        self.slider_margin.setValue(15)
        _link_slider_spin(self.slider_margin, self.spin_margin, 1.0, self.paramChanged.emit)
        row_margin.addWidget(self.slider_margin, 1)
        row_margin.addWidget(self.spin_margin)
        layout_param.addLayout(row_margin)

        self.chk_show_boxes = QCheckBox("検出領域を表示する")
        self.chk_show_boxes.setChecked(False)
        self.chk_show_boxes.toggled.connect(lambda _: self.paramChanged.emit())
        layout_param.addWidget(self.chk_show_boxes)

        group_param.setLayout(layout_param)
        layout.addWidget(group_param)

        self.btn_run = QPushButton("一括処理開始")
        self.btn_run.setMinimumHeight(40)
        self.btn_run.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.btn_run.clicked.connect(self.processRequested.emit)
        layout.addWidget(self.btn_run)

        layout.addStretch(1)

    def build_class_settings(self, target_classes: list):
        while self.layout_classes.count():
            item = self.layout_classes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.class_settings_ui.clear()

        for cls_info in target_classes:
            cid = cls_info["id"]
            row = QHBoxLayout()
            chk = QCheckBox(cls_info["label_jp"])
            chk.toggled.connect(lambda _: self.paramChanged.emit())
            row.addWidget(chk)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(1, 100)
            slider.setSingleStep(5)
            slider.setPageStep(10)
            slider.setValue(30)
            slider.setToolTip("認識閾値スライダー")

            spin = QDoubleSpinBox()
            spin.setRange(0.01, 1.0)
            spin.setSingleStep(0.05)
            spin.setValue(0.3)
            spin.setFixedWidth(55)
            spin.setToolTip("認識閾値")

            _link_slider_spin(slider, spin, 1 / 100.0, self.paramChanged.emit)

            row.addWidget(slider, 1)
            row.addWidget(spin)
            self.layout_classes.addLayout(row)

            self.class_settings_ui[cid] = {
                "chk": chk,
                "spin": spin,
            }

    def get_input_dir(self):
        return self.lbl_input_dir.text()

    def get_output_dir(self):
        return self.lbl_output_dir.text()

    def set_input_dir(self, path: str):
        self.lbl_input_dir.set_path_text(path or "未選択")

    def set_output_dir(self, path: str):
        self.lbl_output_dir.set_path_text(path or "未選択")

    def get_model_path(self):
        return self.model_path

    def set_model_path(self, path: str):
        self.model_path = path or ""
        if self.model_path:
            self.lbl_model_path.set_path_text(self.model_path)
        else:
            self.lbl_model_path.set_path_text("")

    def get_current_params(self):
        return {
            "mask_type": self.combo_type.currentData(),
            "shape_type": self.combo_shape.currentData(),
            "imgsz": self.combo_imgsz.currentData(),
            "strength": self.spin_str.value(),
            "margin": self.spin_margin.value(),
            "show_boxes": self.chk_show_boxes.isChecked(),
        }

    def get_settings_payload(self):
        return {
            "model_path": self.get_model_path(),
            "input_dir": self.get_input_dir(),
            "output_dir": self.get_output_dir(),
            "params": self.get_current_params(),
            "class_settings": self.get_class_settings(),
        }

    def get_class_settings(self):
        settings = {}
        for cid, ui_data in self.class_settings_ui.items():
            settings[cid] = {
                "enabled": ui_data["chk"].isChecked(),
                "conf": ui_data["spin"].value(),
            }
        return settings

    def apply_settings(self, settings: dict):
        self.set_model_path(settings.get("model_path", ""))

        input_dir = settings.get("input_dir", "")
        if input_dir:
            self.set_input_dir(input_dir)

        output_dir = settings.get("output_dir", "")
        if output_dir:
            self.set_output_dir(output_dir)

        params = settings.get("params", {})
        if "mask_type" in params:
            idx = self.combo_type.findData(params["mask_type"])
            if idx >= 0:
                self.combo_type.setCurrentIndex(idx)
        if "shape_type" in params:
            idx = self.combo_shape.findData(params["shape_type"])
            if idx >= 0:
                self.combo_shape.setCurrentIndex(idx)
        if "imgsz" in params:
            idx = self.combo_imgsz.findData(params["imgsz"])
            if idx >= 0:
                self.combo_imgsz.setCurrentIndex(idx)
        if "strength" in params:
            self.spin_str.setValue(params["strength"])
        if "margin" in params:
            self.spin_margin.setValue(params["margin"])
        if "show_boxes" in params:
            self.chk_show_boxes.setChecked(params["show_boxes"])

        class_settings = settings.get("class_settings", {})
        for cid, ui_data in self.class_settings_ui.items():
            if cid in class_settings:
                class_data = class_settings[cid]
                ui_data["chk"].setChecked(class_data.get("enabled", False))
                ui_data["spin"].setValue(class_data.get("conf", 0.3))

    def on_select_input(self):
        directory = QFileDialog.getExistingDirectory(
            self, "入力フォルダを選択", self.get_input_dir()
        )
        if directory:
            self.set_input_dir(directory)
            self.inputFolderChanged.emit(directory)

    def on_select_output(self):
        directory = QFileDialog.getExistingDirectory(
            self, "出力フォルダを選択", self.get_output_dir()
        )
        if directory:
            self.set_output_dir(directory)
            self.outputFolderChanged.emit(directory)

    def on_select_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "推論モデルを選択",
            self.model_path,
            "PyTorch Model (*.pt);;All Files (*.*)",
        )
        if path:
            self.set_model_path(path)
            self.modelPathChanged.emit(path)

    def on_drop_model_path(self, path: str):
        if not str(path).lower().endswith(".pt"):
            return
        self.set_model_path(path)
        self.modelPathChanged.emit(path)

    def on_drop_input_dir(self, path: str):
        self.set_input_dir(path)
        self.inputFolderChanged.emit(path)

    def on_drop_output_dir(self, path: str):
        self.set_output_dir(path)
        self.outputFolderChanged.emit(path)