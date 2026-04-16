import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.image_prompt_desktop.core import CanonicalPaths, PromptRepository
from src.image_prompt_desktop.main_window import MainWindow
from src.image_prompt_desktop.session_store import SessionStore, WorkSession
from src.image_prompt_desktop.situation_store import SituationDraft, SituationStore
from src.image_prompt_desktop.wildcard_draft_store import WildcardDraftStore


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_saved_session_restores_editor_and_saved_situation_appears_in_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "canonical"
            data_dir = root / "data"
            wildcard_dir = data_dir / "wildcards"
            wildcard_dir.mkdir(parents=True)
            (wildcard_dir / "view.txt").write_text("from side\nfrom above\n", encoding="utf-8")

            database = data_dir / "prompts.db"
            conn = sqlite3.connect(database)
            try:
                conn.execute(
                    """
                    CREATE TABLE prompts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt TEXT DEFAULT '',
                        negative_prompt TEXT DEFAULT '',
                        category TEXT DEFAULT '',
                        tags TEXT DEFAULT '',
                        favorite INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT ''
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        category INTEGER DEFAULT 0,
                        count INTEGER DEFAULT 0,
                        aliases TEXT DEFAULT ''
                    )
                    """
                )
                conn.commit()
            finally:
                conn.close()

            session_store = SessionStore(Path(temp_dir) / "data" / "session.json")
            session_store.save(WorkSession.create("session prompt", "session negative"))

            situation_store = SituationStore(Path(temp_dir) / "data" / "situations.json")
            situation_store.save_all(
                (
                    SituationDraft.create(
                        name="夜の校舎",
                        prompt="night school",
                        negative_prompt="low quality",
                    ),
                )
            )

            window = MainWindow(
                PromptRepository(CanonicalPaths.from_root(root)),
                session_store,
                situation_store,
                WildcardDraftStore(Path(temp_dir) / "data" / "wildcard_drafts.json"),
            )
            try:
                self.assertEqual(window.prompt_edit.toPlainText(), "session prompt")
                self.assertEqual(window.negative_edit.toPlainText(), "session negative")
                self.assertFalse(window.prompt_list_empty_label.isVisible())
                self.assertTrue(
                    any(
                        "夜の校舎" in window.prompt_list.item(index).text()
                        for index in range(window.prompt_list.count())
                    )
                )
            finally:
                window.close()


if __name__ == "__main__":
    unittest.main()
