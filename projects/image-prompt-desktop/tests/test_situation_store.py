from pathlib import Path
import tempfile
import unittest

from src.image_prompt_desktop.situation_store import SituationDraft, SituationStore


class SituationStoreTests(unittest.TestCase):
    def test_upsert_and_load_situation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SituationStore(Path(temp_dir) / "data" / "situations.json")
            draft = SituationDraft.create(
                name="雨の路地",
                prompt="rainy alley",
                negative_prompt="low quality",
                tags=("rain", "alley"),
                wildcards=("__view__",),
                notes="夜景向け",
            )

            store.upsert(draft)
            loaded = store.load_all()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].name, "雨の路地")
        self.assertEqual(loaded[0].tags, ("rain", "alley"))
        self.assertEqual(loaded[0].wildcards, ("__view__",))

    def test_invalid_situation_file_returns_empty_tuple(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "situations.json"
            path.write_text("{ invalid json", encoding="utf-8")

            self.assertEqual(SituationStore(path).load_all(), tuple())


if __name__ == "__main__":
    unittest.main()
