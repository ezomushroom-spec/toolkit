import sys

from PySide6.QtWidgets import QApplication

from postflow.config import APP_NAME, STYLE_PATH
from postflow.db.database_manager import DatabaseManager
from postflow.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    if STYLE_PATH.exists():
        app.setStyleSheet(STYLE_PATH.read_text(encoding="utf-8"))

    database_manager = DatabaseManager()
    database_manager.initialize()

    window = MainWindow(database_manager=database_manager)
    window.show()
    return app.exec()
