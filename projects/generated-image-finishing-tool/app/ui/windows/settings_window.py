from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

from app.core.state.repositories import SettingsRepository


class SettingsWindow(QWidget):
    def __init__(self, settings_repo: SettingsRepository) -> None:
        super().__init__()
        self.settings_repo = settings_repo
        self.settings = settings_repo.load()
        self.setWindowTitle("設定")
        self.resize(480, 220)

        self.input_edit = QLineEdit(self.settings.recent_input_dir)
        self.output_edit = QLineEdit(self.settings.recent_output_dir)
        self.recipe_edit = QLineEdit(self.settings.recent_recipe_path)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("最近の入力先", self.input_edit)
        form.addRow("最近の出力先", self.output_edit)
        form.addRow("最近のレシピ", self.recipe_edit)
        layout.addLayout(form)

        save_button = QPushButton("保存")
        save_button.clicked.connect(self._save)
        layout.addWidget(save_button)

    def _save(self) -> None:
        self.settings.recent_input_dir = self.input_edit.text().strip()
        self.settings.recent_output_dir = self.output_edit.text().strip()
        self.settings.recent_recipe_path = self.recipe_edit.text().strip()
        self.settings_repo.save(self.settings)
        self.close()
