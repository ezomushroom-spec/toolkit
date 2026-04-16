from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import sqlite3


@dataclass(frozen=True)
class CanonicalPaths:
    root: Path
    database: Path
    wildcards_dir: Path

    @classmethod
    def from_root(cls, root: Path) -> "CanonicalPaths":
        return cls(
            root=root,
            database=root / "data" / "prompts.db",
            wildcards_dir=root / "data" / "wildcards",
        )


@dataclass(frozen=True)
class PromptRecord:
    id: int
    prompt: str
    negative_prompt: str
    category: str
    tags: tuple[str, ...]
    favorite: bool
    created_at: str


@dataclass(frozen=True)
class WildcardRecord:
    name: str
    token: str
    description: str
    items: tuple[str, ...]
    total_items: int
    source_path: Path


@dataclass(frozen=True)
class TagRecord:
    name: str
    category: int
    category_name: str
    count: int
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class RepositorySnapshot:
    prompt_count: int
    tag_count: int
    categories: tuple[str, ...]
    prompts: tuple[PromptRecord, ...]
    wildcards: tuple[WildcardRecord, ...]


def parse_wildcard_text(name: str, source_path: Path, text: str) -> WildcardRecord:
    description = ""
    items: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            description = line[1:].strip()
            continue
        items.append(line)

    return WildcardRecord(
        name=name,
        token=f"__{name}__",
        description=description,
        items=tuple(items),
        total_items=len(items),
        source_path=source_path,
    )


def normalize_wildcard_name(file_path: Path) -> str:
    name = file_path.stem
    if name.startswith("__") and name.endswith("__") and len(name) > 4:
        return name[2:-2]
    return name


def tag_category_name(category: int) -> str:
    category_map = {
        0: "一般",
        1: "アーティスト",
        3: "作品",
        4: "キャラクター",
        5: "メタ",
    }
    return category_map.get(category, "その他")


class PromptRepository:
    def __init__(self, paths: CanonicalPaths):
        self.paths = paths

    def _readonly_database_uri(self) -> str:
        return f"{self.paths.database.resolve().as_uri()}?mode=ro&immutable=1"

    def load_snapshot(self, prompt_limit: int = 100, wildcard_limit: int = 80) -> RepositorySnapshot:
        return RepositorySnapshot(
            prompt_count=self.get_table_count("prompts"),
            tag_count=self.get_table_count("tags"),
            categories=self.get_prompt_categories(),
            prompts=self.get_prompts(limit=prompt_limit),
            wildcards=self.get_wildcards(limit=wildcard_limit),
        )

    def get_table_count(self, table_name: str) -> int:
        if table_name not in {"prompts", "tags"}:
            raise ValueError("未対応のテーブル名です。")
        if not self.paths.database.exists():
            return 0

        with sqlite3.connect(self._readonly_database_uri(), uri=True) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            return int(cursor.fetchone()[0])

    def get_prompt_categories(self) -> tuple[str, ...]:
        if not self.paths.database.exists():
            return tuple()

        with sqlite3.connect(self._readonly_database_uri(), uri=True) as conn:
            rows = conn.execute("SELECT DISTINCT category FROM prompts ORDER BY category").fetchall()
            return tuple(str(row[0]) for row in rows if row[0])

    def get_prompts(self, limit: int = 100) -> tuple[PromptRecord, ...]:
        if not self.paths.database.exists():
            return tuple()

        query = """
            SELECT id, prompt, negative_prompt, category, tags, favorite, created_at
            FROM prompts
            ORDER BY created_at DESC
            LIMIT ?
        """
        with sqlite3.connect(self._readonly_database_uri(), uri=True) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (limit,)).fetchall()

        prompts: list[PromptRecord] = []
        for row in rows:
            tags = tuple(tag.strip() for tag in str(row["tags"] or "").split(",") if tag.strip())
            prompts.append(
                PromptRecord(
                    id=int(row["id"]),
                    prompt=str(row["prompt"] or ""),
                    negative_prompt=str(row["negative_prompt"] or ""),
                    category=str(row["category"] or "未分類"),
                    tags=tags,
                    favorite=bool(row["favorite"]),
                    created_at=str(row["created_at"] or ""),
                )
            )
        return tuple(prompts)

    def get_wildcards(self, limit: int = 80) -> tuple[WildcardRecord, ...]:
        if not self.paths.wildcards_dir.exists():
            return tuple()

        wildcards: list[WildcardRecord] = []
        for file_path in sorted(self.paths.wildcards_dir.glob("*.txt"), key=lambda item: item.name.casefold()):
            name = normalize_wildcard_name(file_path)
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            wildcard = parse_wildcard_text(name, file_path, text)
            wildcards.append(
                WildcardRecord(
                    name=wildcard.name,
                    token=wildcard.token,
                    description=wildcard.description,
                    items=wildcard.items[:limit],
                    total_items=wildcard.total_items,
                    source_path=wildcard.source_path,
                )
            )
        return tuple(wildcards)

    def random_wildcard_item(self, name: str) -> str:
        for pattern in (f"{name}.txt", f"__{name}__.txt"):
            file_path = self.paths.wildcards_dir / pattern
            if file_path.exists():
                wildcard = parse_wildcard_text(name, file_path, file_path.read_text(encoding="utf-8", errors="ignore"))
                return random.choice(wildcard.items) if wildcard.items else ""
        return ""

    def search_tags(self, query: str, limit: int = 50, category: int | None = None) -> tuple[TagRecord, ...]:
        normalized_query = query.strip()
        if not normalized_query or not self.paths.database.exists():
            return tuple()

        sql = "SELECT name, category, count, aliases FROM tags WHERE name LIKE ?"
        params: list[object] = [f"%{normalized_query}%"]
        if category is not None:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY count DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self._readonly_database_uri(), uri=True) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()

        tags: list[TagRecord] = []
        for row in rows:
            tag_category = int(row["category"])
            aliases = tuple(alias.strip() for alias in str(row["aliases"] or "").split(",") if alias.strip())
            tags.append(
                TagRecord(
                    name=str(row["name"]),
                    category=tag_category,
                    category_name=tag_category_name(tag_category),
                    count=int(row["count"] or 0),
                    aliases=aliases,
                )
            )
        return tuple(tags)
