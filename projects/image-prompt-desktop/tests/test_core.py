from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.image_prompt_desktop.core import (
    CanonicalPaths,
    PromptRepository,
    normalize_wildcard_name,
    parse_wildcard_text,
    tag_category_name,
)


class CoreTests(unittest.TestCase):
    def test_normalize_wildcard_name(self):
        self.assertEqual(normalize_wildcard_name(Path("__view__.txt")), "view")
        self.assertEqual(normalize_wildcard_name(Path("tipo_location.txt")), "tipo_location")

    def test_parse_wildcard_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "view.txt"
            record = parse_wildcard_text("view", source, "# camera view\nfrom side\n\nfrom above")

        self.assertEqual(record.name, "view")
        self.assertEqual(record.token, "__view__")
        self.assertEqual(record.description, "camera view")
        self.assertEqual(record.items, ("from side", "from above"))
        self.assertEqual(record.total_items, 2)

    def test_random_wildcard_item_reads_full_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wildcard_dir = root / "data" / "wildcards"
            wildcard_dir.mkdir(parents=True)
            (wildcard_dir / "view.txt").write_text("from side\nfrom above\n", encoding="utf-8")

            repository = PromptRepository(CanonicalPaths.from_root(root))
            item = repository.random_wildcard_item("view")

        self.assertIn(item, {"from side", "from above"})

    def test_tag_category_name(self):
        self.assertEqual(tag_category_name(0), "一般")
        self.assertEqual(tag_category_name(4), "キャラクター")
        self.assertEqual(tag_category_name(999), "その他")

    def test_search_tags_uses_read_only_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            database = data_dir / "prompts.db"

            conn = sqlite3.connect(database)
            try:
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
                conn.execute(
                    "INSERT INTO tags (name, category, count, aliases) VALUES (?, ?, ?, ?)",
                    ("school_uniform", 0, 1200, "uniform"),
                )
                conn.execute(
                    "INSERT INTO tags (name, category, count, aliases) VALUES (?, ?, ?, ?)",
                    ("school_bag", 0, 400, ""),
                )
                conn.execute(
                    "INSERT INTO tags (name, category, count, aliases) VALUES (?, ?, ?, ?)",
                    ("school_character", 4, 900, ""),
                )
                conn.commit()
            finally:
                conn.close()

            repository = PromptRepository(CanonicalPaths.from_root(root))
            tags = repository.search_tags("school", limit=10)
            character_tags = repository.search_tags("school", limit=10, category=4)

        self.assertEqual([tag.name for tag in tags], ["school_uniform", "school_character", "school_bag"])
        self.assertEqual(tags[0].category_name, "一般")
        self.assertEqual(tags[0].aliases, ("uniform",))
        self.assertEqual([tag.name for tag in character_tags], ["school_character"])


if __name__ == "__main__":
    unittest.main()
