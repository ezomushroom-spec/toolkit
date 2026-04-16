"""
Narrative Thumbnail Studio - エントリーポイント
差分設計ツールによるサムネイル構造化・検証基盤
"""
import sys
from pathlib import Path

# core/ui をモジュールとして認識させるためパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.main_window import MainWindow


def main() -> None:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Narrative Thumbnail Studio")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")

    # 日本語フォント設定
    font_candidates = ["BIZ UDGothic", "Meiryo", "MS Gothic", "Yu Gothic"]
    font = QFont()
    for fname in font_candidates:
        f = QFont(fname, 10)
        if f.exactMatch() or f.family() == fname:
            font = f
            break
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
