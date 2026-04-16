from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.ui.windows.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("生成画像向け仕上げレシピ適用ツール")
    app.setOrganizationName("codex")

    workspace = Path(__file__).resolve().parent.parent
    window = MainWindow(workspace)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
