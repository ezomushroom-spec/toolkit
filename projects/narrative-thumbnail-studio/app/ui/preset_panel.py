"""
右パネル: プリセット選択 + パラメータ調整 + 出力設定 + テキスト設定
"""
from __future__ import annotations
from typing import Any

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QLineEdit,
    QScrollArea, QFormLayout, QColorDialog, QFrame, QAbstractItemView,
    QTabWidget, QSizePolicy,
)

from core.presets import PresetDef, PresetRegistry
from core.exporter import OUTPUT_SIZE_PRESETS
from core.text_overlay import TextConfig


_PANEL_STYLE = """
    QGroupBox {
        color: #a6adc8;
        font-size: 12px;
        border: 1px solid #3d3d5c;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 4px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 8px;
        color: #89b4fa;
    }
    QLabel { color: #cdd6f4; font-size: 12px; }
    QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
        background: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 3px;
        padding: 2px 4px;
        font-size: 12px;
    }
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
        border-color: #89b4fa;
    }
    QCheckBox { color: #cdd6f4; font-size: 12px; }
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
        border: 1px solid #45475a;
        border-radius: 2px;
        background: #313244;
    }
    QCheckBox::indicator:checked {
        background: #89b4fa;
        border-color: #89b4fa;
    }
"""

_PRESET_TABS = [
    ("two", "2枚", ["vsplit", "hsplit", "diagonal_wipe"]),
    ("three", "3枚", ["center_hero", "hero_top_strip", "grid_h3"]),
    ("four_plus", "4枚以上", ["grid_2x2", "catalog", "asymmetric"]),
]

_CURATED_PRESET_LABELS = {
    "vsplit": "縦分割  2枚",
    "hsplit": "横分割  2枚",
    "diagonal_wipe": "斜めワイプ  2枚",
    "center_hero": "中央主役+周囲  3-5枚",
    "hero_top_strip": "上主役+下段  3-4枚",
    "grid_h3": "横3列  3枚",
    "grid_2x2": "2x2グリッド  4枚",
    "catalog": "カタログ型  補助",
    "asymmetric": "上2下3  5枚",
}

_PRESET_PREVIEWS = {
    "vsplit": "左右比較向け",
    "hsplit": "上下比較向け",
    "diagonal_wipe": "境界線を斜めに切り分ける",
    "center_hero": "中央主役を強調",
    "hero_top_strip": "上を主役、下に補助を並べる",
    "grid_h3": "3枚を横並び",
    "grid_2x2": "4枚を均等配置",
    "catalog": "一覧をすっきり整理",
    "asymmetric": "上2下3の変則配置",
}


class PresetListItemWidget(QWidget):
    """プリセット一覧の1行表示。"""

    def __init__(self, title: str, subtitle: str, badge: str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 4)
        outer.setSpacing(0)

        self._card = QFrame()
        self._card.setObjectName("presetCard")
        self._card.setStyleSheet(self._card_style("normal"))
        card_layout = QHBoxLayout(self._card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(10)

        self._badge = QLabel(badge)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setFixedWidth(52)
        self._badge.setStyleSheet(self._badge_style("normal"))
        card_layout.addWidget(self._badge)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(3)

        self._title = QLabel(title)
        self._title.setStyleSheet("font-size: 12px; font-weight: 600; color: #cdd6f4; letter-spacing: 0.4px;")
        self._title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._subtitle = QLabel(subtitle)
        self._subtitle.setWordWrap(True)
        self._subtitle.setStyleSheet("font-size: 11px; color: #a6adc8; letter-spacing: 0.2px;")
        self._subtitle.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        text_col.addWidget(self._title)
        text_col.addWidget(self._subtitle)

        text_box = QWidget()
        text_box.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        text_box.setLayout(text_col)
        card_layout.addWidget(text_box, stretch=1)

        outer.addWidget(self._card)

        self._apply_minimum_heights(card_layout)
        self._is_enabled = True
        self._is_recommended = False
        self._is_selected = False
        self._apply_styles()

    def sizeHint(self):
        card_hint = self._card.sizeHint()
        # 余白ぶんのゆとりを追加して文字切れを防ぐ
        return card_hint + QSize(0, 8)

    def _apply_minimum_heights(self, card_layout: QHBoxLayout) -> None:
        """計測したフォント情報から必要最小限の高さを確保する"""
        title_h = self._title.fontMetrics().height()
        subtitle_h = self._subtitle.fontMetrics().height()
        # タイトル + サブタイトル + 余白(上下マージン + テキスト間隔 + 上下バッファ)
        base = title_h + subtitle_h
        spacing = card_layout.spacing()
        margins = card_layout.contentsMargins()
        min_card_height = base + spacing + margins.top() + margins.bottom() + 12
        min_card_height = max(68, min_card_height)
        self._card.setMinimumHeight(min_card_height)
        self.setMinimumHeight(min_card_height + 4)

    def set_state(self, enabled: bool, recommended: bool) -> None:
        self._is_enabled = enabled
        self._is_recommended = recommended
        self._apply_styles()

    def set_selected(self, selected: bool) -> None:
        self._is_selected = selected
        self._apply_styles()

    def _apply_styles(self) -> None:
        enabled = self._is_enabled
        recommended = self._is_recommended
        selected = self._is_selected and enabled

        if not enabled:
            title_color = "#6c7086"
            subtitle_color = "#585b70"
            badge_mode = "disabled"
            card_mode = "disabled"
        elif recommended and selected:
            title_color = "#b4cdff"
            subtitle_color = "#c5d7ff"
            badge_mode = "recommended_active"
            card_mode = "recommended_active"
        elif recommended:
            title_color = "#8fb2ff"
            subtitle_color = "#bac2de"
            badge_mode = "recommended_hint"
            card_mode = "recommended_hint"
        elif selected:
            title_color = "#d5e3ff"
            subtitle_color = "#c3d1ff"
            badge_mode = "active"
            card_mode = "active"
        else:
            title_color = "#cdd6f4"
            subtitle_color = "#a6adc8"
            badge_mode = "normal"
            card_mode = "normal"

        self._title.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {title_color};"
        )
        self._subtitle.setStyleSheet(f"font-size: 11px; color: {subtitle_color};")
        self._badge.setStyleSheet(self._badge_style(badge_mode))
        self._card.setStyleSheet(self._card_style(card_mode))

    @staticmethod
    def _badge_style(mode: str = "normal") -> str:
        if mode == "disabled":
            bg = "#202333"
            fg = "#55596c"
            border = "#2e3144"
        elif mode == "active":
            bg = "#1f2b44"
            fg = "#b8c9f1"
            border = "#3f5d8e"
        elif mode == "recommended_active":
            bg = "#1e2f54"
            fg = "#b7d0ff"
            border = "#5d89d8"
        elif mode == "recommended_hint":
            bg = "#1e2438"
            fg = "#91aee8"
            border = "#3c4a74"
        else:
            bg = "#2a2f45"
            fg = "#cdd6f4"
            border = "#3d425b"
        return (
            "QLabel {"
            f"background: {bg}; color: {fg}; border: 1px solid {border}; "
            "border-radius: 5px; font-size: 11px; font-weight: 600; padding: 3px 6px;"
            "}"
        )

    @staticmethod
    def _card_style(mode: str) -> str:
        if mode == "disabled":
            bg = "#1b1c2b"
            border = "#2e3144"
        elif mode == "active":
            bg = "#24304f"
            border = "#5d89d8"
        elif mode == "recommended_active":
            bg = "#2a3656"
            border = "#6b9aff"
        elif mode == "recommended_hint":
            bg = "#1f2438"
            border = "#3b4260"
        else:
            bg = "#1f2335"
            border = "#2b2f42"
        return (
            "QFrame#presetCard {"
            f"background: {bg}; border: 1px solid {border}; border-radius: 8px;"
            "}"
        )


class ColorButton(QPushButton):
    """カラーピッカー付きボタン"""

    color_changed = Signal(str)  # #RRGGBB

    def __init__(self, color: str = "#FFFFFF", parent=None):
        super().__init__(parent)
        self._color = color
        self._update_style()
        self.setFixedSize(60, 24)
        self.clicked.connect(self._pick_color)

    def get_color(self) -> str:
        return self._color

    def set_color(self, color: str) -> None:
        self._color = color
        self._update_style()

    def _pick_color(self) -> None:
        r, g, b = _hex_to_rgb(self._color)
        initial = QColor(r, g, b)
        color = QColorDialog.getColor(initial, self, "色を選択")
        if color.isValid():
            self._color = color.name().upper()
            self._update_style()
            self.color_changed.emit(self._color)

    def _update_style(self) -> None:
        r, g, b = _hex_to_rgb(self._color)
        luminance = (r * 0.299 + g * 0.587 + b * 0.114) / 255
        text_color = "#000000" if luminance > 0.5 else "#FFFFFF"
        self.setStyleSheet(
            f"QPushButton {{ background: {self._color}; color: {text_color}; "
            f"border: 1px solid #45475a; border-radius: 3px; font-size: 11px; }}"
        )
        self.setText(self._color)


class ParamWidget(QWidget):
    """プリセットパラメータの動的UIウィジェット"""

    param_changed = Signal(str, object)  # (param_name, value)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._widgets: dict[str, QWidget] = {}
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self._form = layout

    def set_preset(self, preset: PresetDef | None, current_params: dict | None = None) -> None:
        """プリセット変更時にウィジェットを再構築"""
        # 既存ウィジェットを削除
        while self._form.rowCount() > 0:
            self._form.removeRow(0)
        self._widgets.clear()

        if preset is None:
            return

        defaults = preset.get_defaults()
        for pname, pdef in preset.parameters.items():
            value = (current_params or {}).get(pname, defaults[pname])
            widget = self._create_widget(pname, pdef, value)
            if widget:
                label = QLabel(pdef.label or pname)
                label.setStyleSheet("color: #a6adc8; font-size: 11px;")
                self._form.addRow(label, widget)
                self._widgets[pname] = widget

    def get_values(self) -> dict:
        """現在のパラメータ値dictを返す"""
        result = {}
        for name, widget in self._widgets.items():
            result[name] = self._get_value(widget)
        return result

    def set_value(self, param_name: str, value: Any) -> None:
        """プログラムからパラメータ値を更新し、ウィジェットに反映する（シグナル発火なし）"""
        if param_name in self._widgets:
            widget = self._widgets[param_name]
            widget.blockSignals(True)
            try:
                if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                    widget.setValue(value)
                elif isinstance(widget, ColorButton):
                    widget.set_color(str(value))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(value))
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(str(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(str(value))
            finally:
                widget.blockSignals(False)

    def _create_widget(self, pname: str, pdef, value: Any) -> QWidget | None:
        if pdef.type == "int":
            w = QSpinBox()
            if pdef.min is not None:
                w.setMinimum(int(pdef.min))
            if pdef.max is not None:
                w.setMaximum(int(pdef.max))
            w.setValue(int(value))
            w.valueChanged.connect(lambda v, n=pname: self.param_changed.emit(n, v))
            return w

        elif pdef.type == "float":
            w = QDoubleSpinBox()
            if pdef.min is not None:
                w.setMinimum(float(pdef.min))
            if pdef.max is not None:
                w.setMaximum(float(pdef.max))
            w.setSingleStep(0.05)
            w.setDecimals(2)
            w.setValue(float(value))
            w.valueChanged.connect(lambda v, n=pname: self.param_changed.emit(n, v))
            return w

        elif pdef.type == "color":
            w = ColorButton(str(value))
            w.color_changed.connect(lambda v, n=pname: self.param_changed.emit(n, v))
            return w

        elif pdef.type == "bool":
            w = QCheckBox()
            w.setChecked(bool(value))
            w.toggled.connect(lambda v, n=pname: self.param_changed.emit(n, v))
            return w

        elif pdef.type == "choice":
            w = QComboBox()
            if pdef.choices:
                for choice in pdef.choices:
                    w.addItem(str(choice))
                idx = pdef.choices.index(value) if value in pdef.choices else 0
                w.setCurrentIndex(idx)
            w.currentTextChanged.connect(lambda v, n=pname: self.param_changed.emit(n, v))
            return w

        elif pdef.type == "str":
            w = QLineEdit(str(value))
            w.editingFinished.connect(lambda n=pname, ww=w: self.param_changed.emit(n, ww.text()))
            return w

        return None

    def _get_value(self, widget: QWidget) -> Any:
        if isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QDoubleSpinBox):
            return widget.value()
        elif isinstance(widget, ColorButton):
            return widget.get_color()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()
        return None


class TextConfigWidget(QWidget):
    """テキストオーバーレイ設定UI"""

    config_changed = Signal(object)  # TextConfig

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 左ラベル
        self._label_left = QLineEdit()
        self._label_left.setPlaceholderText("左ラベル (空=非表示)")
        layout.addRow(QLabel("左ラベル"), self._label_left)

        # 右ラベル
        self._label_right = QLineEdit()
        self._label_right.setPlaceholderText("右ラベル (空=非表示)")
        layout.addRow(QLabel("右ラベル"), self._label_right)

        # タイトル
        self._title = QLineEdit()
        self._title.setPlaceholderText("タイトル (空=非表示)")
        layout.addRow(QLabel("タイトル"), self._title)

        # 矢印
        self._arrow = QComboBox()
        self._arrow.addItems(["", "▶", "→", "VS", "▷", "↓"])
        layout.addRow(QLabel("矢印"), self._arrow)

        for widget in [self._label_left, self._label_right, self._title]:
            widget.editingFinished.connect(self._emit_config)
        self._arrow.currentTextChanged.connect(lambda _: self._emit_config())

    def get_config(self) -> TextConfig:
        labels = []
        if self._label_left.text() or self._label_right.text():
            labels = [self._label_left.text(), self._label_right.text()]
        return TextConfig(
            label_texts=labels,
            title_text=self._title.text(),
            arrow_text=self._arrow.currentText(),
        )

    def set_config(self, config: TextConfig) -> None:
        self._label_left.setText(config.label_texts[0] if len(config.label_texts) > 0 else "")
        self._label_right.setText(config.label_texts[1] if len(config.label_texts) > 1 else "")
        self._title.setText(config.title_text)
        self._arrow.setCurrentText(config.arrow_text)

    def _emit_config(self) -> None:
        self.config_changed.emit(self.get_config())


class OutputSizeWidget(QWidget):
    """出力サイズ選択UI"""

    size_changed = Signal(tuple)  # (width, height)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._combo = QComboBox()
        for name in OUTPUT_SIZE_PRESETS:
            self._combo.addItem(name)
        self._combo.addItem("カスタム")
        layout.addWidget(self._combo, stretch=1)

        self._custom_w = QSpinBox()
        self._custom_w.setRange(100, 8000)
        self._custom_w.setValue(1200)
        self._custom_w.setVisible(False)
        layout.addWidget(self._custom_w)

        sep = QLabel("×")
        sep.setVisible(False)
        self._sep = sep
        layout.addWidget(sep)

        self._custom_h = QSpinBox()
        self._custom_h.setRange(100, 8000)
        self._custom_h.setValue(900)
        self._custom_h.setVisible(False)
        layout.addWidget(self._custom_h)

        self._combo.currentTextChanged.connect(self._on_combo_changed)
        self._custom_w.valueChanged.connect(self._emit_custom)
        self._custom_h.valueChanged.connect(self._emit_custom)

    def get_size(self) -> tuple[int, int]:
        name = self._combo.currentText()
        if name in OUTPUT_SIZE_PRESETS:
            return OUTPUT_SIZE_PRESETS[name]
        return (self._custom_w.value(), self._custom_h.value())

    def set_size(self, size: tuple[int, int]) -> None:
        for name, preset_size in OUTPUT_SIZE_PRESETS.items():
            if preset_size == size:
                self._combo.setCurrentText(name)
                return

        self._combo.setCurrentText("カスタム")
        self._custom_w.setValue(size[0])
        self._custom_h.setValue(size[1])

    def _on_combo_changed(self, name: str) -> None:
        is_custom = name == "カスタム"
        self._custom_w.setVisible(is_custom)
        self._sep.setVisible(is_custom)
        self._custom_h.setVisible(is_custom)
        if not is_custom:
            self.size_changed.emit(OUTPUT_SIZE_PRESETS[name])

    def _emit_custom(self) -> None:
        self.size_changed.emit((self._custom_w.value(), self._custom_h.value()))


class AssignmentOrderList(QListWidget):
    """割り当て済み画像の順序をドラッグで並び替えるリスト"""

    order_changed = Signal(list)  # list[str]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setStyleSheet("""
            QListWidget {
                background: #1e1e2e;
                border: 1px solid #3d3d5c;
                border-radius: 4px;
            }
            QListWidget::item {
                color: #cdd6f4;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background: #313244;
                color: #89b4fa;
            }
        """)

    def set_paths(self, labels_and_paths: list[tuple[str, str]]) -> None:
        self.clear()
        for label, path in labels_and_paths:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsDragEnabled
            )
            self.addItem(item)

    def dropEvent(self, event) -> None:
        super().dropEvent(event)
        self.order_changed.emit(self.get_paths())

    def get_paths(self) -> list[str]:
        return [
            self.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.count())
            if self.item(i).data(Qt.ItemDataRole.UserRole)
        ]


class SlotAssignmentWidget(QWidget):
    """現在のプリセットで使う画像の割り当てを編集するUI"""

    assignment_changed = Signal(list)  # list[str]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: list[Any] = []
        self._role_names: list[str] = []
        self._assigned_paths: list[str] = []
        self._updating = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        self._order_hint = QLabel("左の位置に合わせて右をドラッグ")
        self._order_hint.setStyleSheet("color: #a6adc8; font-size: 11px;")
        outer.addWidget(self._order_hint)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        outer.addLayout(row)

        self._slot_column = QWidget()
        self._slot_column.setFixedWidth(86)
        self._slot_column.setStyleSheet("background: transparent;")
        self._slot_column_layout = QVBoxLayout(self._slot_column)
        self._slot_column_layout.setContentsMargins(0, 1, 0, 1)
        self._slot_column_layout.setSpacing(2)
        row.addWidget(self._slot_column)

        self._order_list = AssignmentOrderList()
        self._order_list.setMaximumHeight(160)
        self._order_list.order_changed.connect(self._on_order_list_changed)
        row.addWidget(self._order_list, stretch=1)

    def set_context(
        self,
        entries: list[Any],
        role_names: list[str],
        assigned_paths: list[str] | None = None,
    ) -> None:
        self._entries = list(entries)
        self._role_names = list(role_names)
        self._assigned_paths = list(assigned_paths or [])
        self._rebuild()

    def get_assigned_paths(self) -> list[str]:
        return [path for path in self._assigned_paths if path]

    def _rebuild(self) -> None:
        self._order_list.blockSignals(True)
        self._order_list.clear()
        self._order_list.blockSignals(False)

        if not self._entries or not self._role_names:
            self._rebuild_slot_column()
            self._slot_column.hide()
            self._order_hint.hide()
            self._order_list.hide()
            return

        self._rebuild_slot_column()
        self._slot_column.show()
        self._order_hint.show()
        self._order_list.show()
        available_paths = [str(entry.path) for entry in self._entries]
        ordered_paths = [path for path in self._assigned_paths if path in available_paths]
        for path in available_paths:
            if path not in ordered_paths:
                ordered_paths.append(path)
        self._assigned_paths = ordered_paths
        self._sync_order_list()

    def _emit_assignment(self) -> None:
        self._assigned_paths = self._order_list.get_paths()
        self._refresh_order_list_labels()
        self.assignment_changed.emit(list(self._assigned_paths))

    def _sync_order_list(self) -> None:
        path_to_name = {str(entry.path): entry.path.name for entry in self._entries}
        labels_and_paths = []
        for path in self._assigned_paths:
            if not path:
                continue
            labels_and_paths.append((path_to_name.get(path, path), path))
        self._order_list.blockSignals(True)
        self._order_list.set_paths(labels_and_paths)
        self._order_list.blockSignals(False)

    def _refresh_order_list_labels(self) -> None:
        path_to_name = {str(entry.path): entry.path.name for entry in self._entries}
        for slot in range(self._order_list.count()):
            item = self._order_list.item(slot)
            path = item.data(Qt.ItemDataRole.UserRole)
            item.setText(path_to_name.get(path, path))

    def _on_order_list_changed(self, ordered_paths: list[str]) -> None:
        self._assigned_paths = list(ordered_paths)
        self._emit_assignment()

    def _rebuild_slot_column(self) -> None:
        while self._slot_column_layout.count():
            item = self._slot_column_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self._role_names:
            return

        for idx, role_name in enumerate(self._role_names):
            label = QLabel(f"{idx + 1}. {role_name}")
            label.setFixedHeight(26)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet(
                "color: #a6adc8; font-size: 11px; "
                "background: #232336; border: 1px solid #3d3d5c; "
                "border-radius: 4px; padding: 0 6px;"
            )
            self._slot_column_layout.addWidget(label)
        self._slot_column_layout.addStretch()


class PresetPanel(QWidget):
    """右パネル: プリセット選択 + パラメータ + 出力設定"""

    preset_changed = Signal(str)          # プリセット名
    param_changed = Signal(str, object)   # (param名, 値)
    output_size_changed = Signal(tuple)   # (width, height)
    text_config_changed = Signal(object)  # TextConfig
    image_count_needed = Signal(int)      # 現在の選択画像数（外部から設定）
    assignment_changed = Signal(list)     # list[str]

    def __init__(self, registry: PresetRegistry, parent=None):
        super().__init__(parent)
        self._registry = registry
        self._current_preset: PresetDef | None = None
        self._current_image_count: int = 0
        self._last_recommended_preset: str | None = None
        self._current_tab_key: str = _PRESET_TABS[0][0]
        self._available_entries: list[Any] = []
        self._assigned_paths: list[str] = []
        self._current_role_names: list[str] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet("background: #181825;" + _PANEL_STYLE)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self._recommendation_label = QLabel(
            "2枚: 縦分割 / 3枚: 中央主役 / 4枚: 2x2"
        )
        self._recommendation_label.setWordWrap(True)
        self._recommendation_label.setStyleSheet(
            "color: #a6adc8; font-size: 11px; background: #1e1e2e; "
            "border: 1px solid #3d3d5c; border-radius: 4px; padding: 4px 6px;"
        )
        layout.addWidget(self._recommendation_label)

        # === プリセット選択 ===
        preset_group = QGroupBox("レイアウト")
        preset_layout = QVBoxLayout(preset_group)
        preset_layout.setContentsMargins(6, 8, 6, 6)
        preset_layout.setSpacing(4)
        self._preset_tabs = QTabWidget()
        self._preset_tabs.setDocumentMode(True)
        self._preset_tabs.tabBar().setExpanding(True)
        self._preset_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3d3d5c;
                border-radius: 4px;
                top: -1px;
                background: #1e1e2e;
            }
            QTabBar::tab {
                background: #232336;
                color: #a6adc8;
                border: 1px solid #3d3d5c;
                padding: 6px 10px;
            }
            QTabBar::tab:selected {
                background: #313244;
                color: #89b4fa;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        self._preset_lists: dict[str, QListWidget] = {}
        list_style = """
            QListWidget {
                background: #1e1e2e;
                border: none;
                border-radius: 0;
            }
            QListWidget::item {
                margin: 0;
                padding: 0;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QListWidget::item:hover {
                background: transparent;
            }
            QListWidget::item:disabled {
                color: #45475a;
                background: transparent;
            }
        """
        for tab_key, tab_label, _ in _PRESET_TABS:
            tab_page = QWidget()
            tab_page_layout = QVBoxLayout(tab_page)
            tab_page_layout.setContentsMargins(4, 4, 4, 4)
            tab_page_layout.setSpacing(6)
            preset_list = QListWidget()
            preset_list.setStyleSheet(list_style)
            preset_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            preset_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            preset_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            preset_list.setSpacing(4)
            tab_page_layout.addWidget(preset_list)
            self._preset_tabs.addTab(tab_page, tab_label)
            self._preset_lists[tab_key] = preset_list
        preset_layout.addWidget(self._preset_tabs)
        layout.addWidget(preset_group)

        # === パラメータ ===
        param_group = QGroupBox("パラメータ")
        param_layout = QVBoxLayout(param_group)
        param_layout.setContentsMargins(6, 8, 6, 6)
        param_layout.setSpacing(4)
        self._param_widget = ParamWidget()
        self._param_widget.setStyleSheet(_PANEL_STYLE)
        param_layout.addWidget(self._param_widget)
        layout.addWidget(param_group)

        assign_group = QGroupBox("画像配置")
        assign_layout = QVBoxLayout(assign_group)
        assign_layout.setContentsMargins(6, 8, 6, 6)
        assign_layout.setSpacing(4)
        self._assignment_hint = QLabel("位置変更は中央プレビューの持ち手をドラッグ")
        self._assignment_hint.setStyleSheet("color: #a6adc8; font-size: 11px;")
        assign_layout.addWidget(self._assignment_hint)
        self._assignment_roles = QLabel("")
        self._assignment_roles.setWordWrap(True)
        self._assignment_roles.setStyleSheet("color: #cdd6f4; font-size: 11px;")
        assign_layout.addWidget(self._assignment_roles)
        self._assignment_widget = SlotAssignmentWidget()
        self._assignment_widget.hide()
        layout.addWidget(assign_group)

        # === テキストオーバーレイ ===
        text_group = QGroupBox("文字")
        text_layout = QVBoxLayout(text_group)
        text_layout.setContentsMargins(6, 8, 6, 6)
        text_layout.setSpacing(4)
        self._text_widget = TextConfigWidget()
        self._text_widget.setStyleSheet(_PANEL_STYLE)
        text_layout.addWidget(self._text_widget)
        layout.addWidget(text_group)

        # === 出力サイズ ===
        size_group = QGroupBox("出力サイズ")
        size_layout = QVBoxLayout(size_group)
        size_layout.setContentsMargins(6, 8, 6, 6)
        size_layout.setSpacing(4)
        self._size_widget = OutputSizeWidget()
        self._size_widget.setStyleSheet(_PANEL_STYLE)
        size_layout.addWidget(self._size_widget)
        layout.addWidget(size_group)

        layout.addStretch()

        # 初期ロード
        self._populate_preset_lists()

        # シグナル接続
        self._preset_tabs.currentChanged.connect(self._on_preset_tab_changed)
        for preset_list in self._preset_lists.values():
            preset_list.itemClicked.connect(self._on_preset_clicked)
            preset_list.currentItemChanged.connect(self._on_preset_selection_changed)
        self._param_widget.param_changed.connect(self.param_changed)
        self._assignment_widget.assignment_changed.connect(self._on_assignment_changed)
        self._text_widget.config_changed.connect(self.text_config_changed)
        self._size_widget.size_changed.connect(self.output_size_changed)
        self._refresh_recommendation_label()

    def _populate_preset_lists(self) -> None:
        """枚数別タブにプリセット一覧を表示する"""
        for tab_key, _, preset_names in _PRESET_TABS:
            preset_list = self._preset_lists[tab_key]
            preset_list.clear()
            for preset_name in preset_names:
                preset = self._registry.get(preset_name)
                if preset is None:
                    continue
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, preset.name)
                item.setData(Qt.ItemDataRole.UserRole + 1, preset.display_name)
                item.setData(
                    Qt.ItemDataRole.UserRole + 2,
                    _PRESET_PREVIEWS.get(preset.name, "使いやすい定番プリセット"),
                )
                item.setData(
                    Qt.ItemDataRole.UserRole + 3,
                    self._preset_count_badge(preset),
                )
                preset_list.addItem(item)
                row = self._make_preset_item_widget(preset)
                item.setSizeHint(row.sizeHint())
                preset_list.setItemWidget(item, row)

        self._refresh_preset_item_states(self._current_image_count, self._last_recommended_preset)

    def _all_preset_lists(self) -> list[QListWidget]:
        return list(self._preset_lists.values())

    def _find_preset_item(self, preset_name: str) -> tuple[QListWidget, QListWidgetItem] | None:
        for preset_list in self._all_preset_lists():
            for i in range(preset_list.count()):
                item = preset_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == preset_name:
                    return preset_list, item
        return None

    def _current_preset_list(self) -> QListWidget:
        current_index = self._preset_tabs.currentIndex()
        tab_key, _, _ = _PRESET_TABS[current_index]
        self._current_tab_key = tab_key
        return self._preset_lists[tab_key]

    def _activate_tab_for_count(self, count: int) -> None:
        target_index = 0
        if count == 3:
            target_index = 1
        elif count >= 4:
            target_index = 2
        self._preset_tabs.setCurrentIndex(target_index)

    def _on_preset_tab_changed(self, index: int) -> None:
        if 0 <= index < len(_PRESET_TABS):
            self._current_tab_key = _PRESET_TABS[index][0]
        self._refresh_recommendation_label()
        self._refresh_selection_styles()

    def _on_preset_selection_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        self._refresh_selection_styles()

    def update_image_count(self, count: int) -> None:
        """画像選択枚数に応じてプリセットの有効/無効を更新"""
        self._current_image_count = count
        recommended = self._recommended_preset_name(count)
        self._last_recommended_preset = recommended
        self._activate_tab_for_count(count)
        self._refresh_preset_item_states(count, recommended)
        self._refresh_recommendation_label()

        current_list = self._current_preset_list()
        current_item = current_list.currentItem()
        if current_item is None or not (current_item.flags() & Qt.ItemFlag.ItemIsEnabled):
            self._auto_select_best_enabled()
        else:
            self._refresh_assignment_ui()

    def select_preset_by_number(self, n: int) -> None:
        """キー1〜9でプリセット切替"""
        idx = n - 1
        current_list = self._current_preset_list()
        if 0 <= idx < current_list.count():
            item = current_list.item(idx)
            if item.flags() & Qt.ItemFlag.ItemIsEnabled:
                current_list.setCurrentItem(item)
                self._on_preset_clicked(item)

    def get_current_params(self) -> dict:
        return self._param_widget.get_values()

    def set_param_value(self, param_name: str, value: Any) -> None:
        """UIコンポーネントの値をプログラムから更新する"""
        self._param_widget.set_value(param_name, value)

    def set_current_size(self, size: tuple[int, int]) -> None:
        self._size_widget.set_size(size)

    def set_text_config(self, config: TextConfig) -> None:
        self._text_widget.set_config(config)

    def set_available_images(self, entries: list[Any]) -> None:
        self._available_entries = list(entries)
        available_paths = {str(entry.path) for entry in self._available_entries}
        self._assigned_paths = [path for path in self._assigned_paths if path in available_paths]
        self._refresh_assignment_ui()

    def get_current_size(self) -> tuple[int, int]:
        return self._size_widget.get_size()

    def get_text_config(self) -> TextConfig:
        return self._text_widget.get_config()

    def get_assigned_paths(self) -> list[str]:
        return list(self._assigned_paths)

    def set_assigned_paths(self, assigned_paths: list[str]) -> None:
        self._assigned_paths = list(assigned_paths)
        self._refresh_assignment_ui()

    def get_slot_labels(self) -> list[str]:
        return list(self._current_role_names)

    def select_preset(self, preset_name: str, current_params: dict | None = None) -> bool:
        preset = self._registry.get(preset_name)
        if preset is None:
            return False

        item_info = self._find_preset_item(preset_name)
        if item_info:
            preset_list, item = item_info
            self._current_preset = preset
            self._param_widget.set_preset(preset, current_params)
            self._preset_tabs.setCurrentWidget(preset_list.parentWidget())
            preset_list.setCurrentItem(item)
            self._assigned_paths = self._coerce_assignment_paths(self._assigned_paths)
            self._refresh_assignment_ui()
            return True
        return False

    def _auto_select_best_enabled(self) -> None:
        recommended = self._last_recommended_preset
        if recommended:
            item_info = self._find_preset_item(recommended)
            if item_info:
                preset_list, item = item_info
                if item.flags() & Qt.ItemFlag.ItemIsEnabled:
                    self._preset_tabs.setCurrentWidget(preset_list.parentWidget())
                    preset_list.setCurrentItem(item)
                    self._on_preset_clicked(item)
                    return

        for preset_list in self._all_preset_lists():
            for i in range(preset_list.count()):
                item = preset_list.item(i)
                if item.flags() & Qt.ItemFlag.ItemIsEnabled:
                    self._preset_tabs.setCurrentWidget(preset_list.parentWidget())
                    preset_list.setCurrentItem(item)
                    self._on_preset_clicked(item)
                    return

    def _recommended_preset_name(self, count: int) -> str | None:
        if count <= 1:
            return None
        if count == 2:
            return "vsplit"
        if count == 3:
            return "center_hero"
        if count == 4:
            return "grid_2x2"
        return "catalog"

    def _refresh_preset_item_states(self, count: int, recommended: str | None) -> None:
        for preset_list in self._all_preset_lists():
            for i in range(preset_list.count()):
                item = preset_list.item(i)
                preset_name = item.data(Qt.ItemDataRole.UserRole)
                preset = self._registry.get(preset_name)
                if not preset:
                    continue
                enabled = preset.supports_image_count(count)
                flags = item.flags()
                if enabled:
                    item.setFlags(flags | Qt.ItemFlag.ItemIsEnabled)
                else:
                    item.setFlags(flags & ~Qt.ItemFlag.ItemIsEnabled)
                row = preset_list.itemWidget(item)
                if isinstance(row, PresetListItemWidget):
                    row.set_state(enabled, preset_name == recommended)
        self._refresh_selection_styles()

    def _refresh_selection_styles(self) -> None:
        for preset_list in self._all_preset_lists():
            current_item = preset_list.currentItem()
            for i in range(preset_list.count()):
                item = preset_list.item(i)
                row = preset_list.itemWidget(item)
                if isinstance(row, PresetListItemWidget):
                    is_selected = (
                        current_item is not None
                        and item is current_item
                        and bool(item.flags() & Qt.ItemFlag.ItemIsEnabled)
                    )
                    row.set_selected(is_selected)

    def _make_preset_item_widget(self, preset: PresetDef) -> PresetListItemWidget:
        return PresetListItemWidget(
            preset.display_name,
            _PRESET_PREVIEWS.get(preset.name, "使いやすい定番プリセット"),
            self._preset_count_badge(preset),
        )

    def _preset_count_badge(self, preset: PresetDef) -> str:
        if preset.min_images == preset.max_images:
            return f"{preset.min_images}枚"
        return f"{preset.min_images}-{preset.max_images}枚"

    def _refresh_recommendation_label(self) -> None:
        self._recommendation_label.setText(
            self._recommendation_text(
                self._current_image_count,
                self._last_recommended_preset,
                self._current_tab_key,
            )
        )

    def _recommendation_text(self, count: int, recommended: str | None, tab_key: str) -> str:
        if count <= 1:
            return "2枚以上を選択してください"

        tab_label = next((label for key, label, _ in _PRESET_TABS if key == tab_key), "プリセット")
        label = self._registry.get(recommended or "")
        recommended_label = label.display_name if label else "利用可能"
        guidance = {
            "two": "左右比較を中心に選びやすいタブです",
            "three": "主役を置く構成や横3枚の見せ方に向いています",
            "four_plus": "4枚以上をまとめるときの基準タブです",
        }.get(tab_key, "用途に合わせて選びやすいタブです")
        return f"{tab_label} / {count}枚: おすすめは {recommended_label}。{guidance}"

    def _on_preset_clicked(self, item: QListWidgetItem) -> None:
        if not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
            return
        preset_name = item.data(Qt.ItemDataRole.UserRole)
        preset = self._registry.get(preset_name)
        if preset:
            self._current_preset = preset
            self._param_widget.set_preset(preset)
            self._refresh_assignment_ui()
            self.preset_changed.emit(preset_name)

    def _slot_role_names(self, preset: PresetDef) -> list[str]:
        count = min(len(self._available_entries), preset.max_images)
        if count < preset.min_images:
            return []

        if preset.name in ("vsplit", "diagonal_wipe"):
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

    def _default_assignment_paths(self, preset: PresetDef) -> list[str]:
        entries = list(self._available_entries)
        usable = min(len(entries), preset.max_images)
        if usable < preset.min_images:
            return []

        if preset.name == "center_hero" and usable == 3:
            ordered = [entries[1], entries[0], entries[2]]
            preferred = [str(entry.path) for entry in ordered]
            remaining = [str(entry.path) for entry in entries if str(entry.path) not in preferred]
            return preferred + remaining

        return [str(entry.path) for entry in entries]

    def _adapt_assignment_paths(self, preset: PresetDef) -> list[str]:
        next_roles = self._slot_role_names(preset)
        if not next_roles:
            return []

        available_paths = [str(entry.path) for entry in self._available_entries]
        current_paths = [path for path in self._assigned_paths if path in available_paths]
        if not current_paths:
            return self._default_assignment_paths(preset)

        next_assigned = [""] * len(next_roles)
        remaining_paths = list(dict.fromkeys(current_paths))

        current_hero = self._hero_slot_index(self._current_role_names)
        next_hero = self._hero_slot_index(next_roles)
        if (
            current_hero is not None
            and next_hero is not None
            and current_hero < len(self._assigned_paths)
        ):
            hero_path = self._assigned_paths[current_hero]
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
        return front + tail

    def _hero_slot_index(self, role_names: list[str]) -> int | None:
        for idx, role_name in enumerate(role_names):
            if "主役" in role_name:
                return idx
        return None

    def _coerce_assignment_paths(self, assigned_paths: list[str]) -> list[str]:
        if not self._current_preset:
            return []

        available_paths = [str(entry.path) for entry in self._available_entries]
        available_path_set = set(available_paths)
        kept = []
        for path in assigned_paths:
            if path in available_path_set and path not in kept:
                kept.append(path)
        defaults = self._default_assignment_paths(self._current_preset)
        for path in defaults:
            if path not in kept:
                kept.append(path)
        for path in available_paths:
            if path not in kept:
                kept.append(path)
        return kept

    def _refresh_assignment_ui(self) -> None:
        if not self._current_preset:
            self._current_role_names = []
            self._assignment_widget.set_context([], [])
            self._assignment_hint.setText("プリセットを選択してください")
            self._assignment_roles.setText("")
            return

        role_names = self._slot_role_names(self._current_preset)
        self._current_role_names = list(role_names)
        if not role_names:
            self._assignment_widget.set_context([], [])
            self._assignment_hint.setText("このプリセットに必要な枚数を選択してください")
            self._assignment_roles.setText("")
            return

        self._assigned_paths = self._coerce_assignment_paths(self._assigned_paths)
        self._assignment_hint.setText(self._assignment_hint_text(self._assigned_paths))
        self._assignment_roles.setText(self._assignment_roles_text(role_names))
        self._assignment_widget.set_context(
            self._available_entries,
            role_names,
            self._assigned_paths,
        )
        self._assigned_paths = self._assignment_widget.get_assigned_paths()
        self._assignment_hint.setText(self._assignment_hint_text(self._assigned_paths))

    def _on_assignment_changed(self, assigned_paths: list[str]) -> None:
        self._assigned_paths = list(assigned_paths)
        self._assignment_hint.setText(self._assignment_hint_text(assigned_paths))
        self.assignment_changed.emit(list(self._assigned_paths))

    def _assignment_hint_text(self, assigned_paths: list[str]) -> str:
        if not self._current_role_names:
            return "プリセットに合わせて仮配置します"

        non_empty = [path for path in assigned_paths if path]
        if len(non_empty) != len(set(non_empty)):
            return "同じ画像が複数枠に入っています"
        if len(non_empty) < len(self._current_role_names):
            return "足りない枠があります"
        return "中央プレビューの持ち手をドラッグして位置変更"

    def _assignment_roles_text(self, role_names: list[str]) -> str:
        return "使用枠: " + " / ".join(
            f"{idx + 1}.{role_name}"
            for idx, role_name in enumerate(role_names)
        )


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
