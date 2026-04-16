from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.image_prompt_desktop.core import CanonicalPaths, PromptRepository
from src.image_prompt_desktop.main_window import MainWindow
from src.image_prompt_desktop.session_store import SessionStore
from src.image_prompt_desktop.situation_store import SituationStore
from src.image_prompt_desktop.style import APP_STYLE
from src.image_prompt_desktop.wildcard_draft_store import WildcardDraftStore


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Image Prompt Desktop")
    app.setStyleSheet(APP_STYLE)

    canonical_root = Path(r"E:\自作アプリ集\新しいフォルダー (2)")
    repository = PromptRepository(CanonicalPaths.from_root(canonical_root))
    session_store = SessionStore(Path(__file__).parent / "data" / "session.json")
    situation_store = SituationStore(Path(__file__).parent / "data" / "situations.json")
    wildcard_draft_store = WildcardDraftStore(Path(__file__).parent / "data" / "wildcard_drafts.json")

    window = MainWindow(repository, session_store, situation_store, wildcard_draft_store)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
