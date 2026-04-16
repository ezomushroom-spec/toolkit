from pathlib import Path
import tempfile
import unittest

from src.image_prompt_desktop.wildcard_draft_store import WildcardDraft, WildcardDraftStore


class WildcardDraftStoreTests(unittest.TestCase):
    def test_upsert_load_and_delete_draft(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = WildcardDraftStore(Path(temp_dir) / "data" / "wildcard_drafts.json")
            draft = WildcardDraft.create(
                name="view",
                token="__view__",
                items=("from side", "from above"),
                source_file_name="view.txt",
            )

            store.upsert(draft)
            loaded = store.load_all()

            self.assertEqual(loaded["view"].items, ("from side", "from above"))

            after_delete = store.delete("view")

        self.assertNotIn("view", after_delete)

    def test_invalid_draft_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "wildcard_drafts.json"
            path.write_text("{ invalid json", encoding="utf-8")

            self.assertEqual(WildcardDraftStore(path).load_all(), {})


if __name__ == "__main__":
    unittest.main()
