from pathlib import Path
import tempfile
import unittest

from src.image_prompt_desktop.session_store import SessionStore, WorkSession


class SessionStoreTests(unittest.TestCase):
    def test_save_load_and_clear_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            session_path = Path(temp_dir) / "data" / "session.json"
            store = SessionStore(session_path)
            session = WorkSession.create("prompt text", "negative text")

            store.save(session)
            loaded = store.load()

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.prompt, "prompt text")
            self.assertEqual(loaded.negative_prompt, "negative text")

            store.clear()
            self.assertIsNone(store.load())

    def test_invalid_session_returns_none(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            session_path = Path(temp_dir) / "session.json"
            session_path.write_text("{ invalid json", encoding="utf-8")

            self.assertIsNone(SessionStore(session_path).load())


if __name__ == "__main__":
    unittest.main()
