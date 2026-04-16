"""
Post Manager - Pixiv tag support
Phase 1 の軽量な Pixiv タグ候補生成を担当する。
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SEED_TAGS_PATH = DATA_DIR / "pixiv_seed_tags.json"
SEED_WORKS_PATH = DATA_DIR / "pixiv_seed_works.json"

WHITESPACE_RE = re.compile(r"[\s\u3000]+")
NORMALIZE_RE = re.compile(r"[\s\u3000_\-]+")


def split_pixiv_tags(value: str) -> list[str]:
    if not value:
        return []
    tags: list[str] = []
    seen: set[str] = set()
    for raw in WHITESPACE_RE.split(value.strip()):
        tag = raw.strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


def normalize_text(value: str) -> str:
    return NORMALIZE_RE.sub("", (value or "").strip().lower())


def load_json_list(path: Path) -> list[dict]:
    try:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, list) else []
    except Exception:
        return []


def load_seed_tags() -> list[dict]:
    seeds: list[dict] = []
    for item in load_json_list(SEED_TAGS_PATH):
        tag = str(item.get("tag", "")).strip()
        if not tag:
            continue
        aliases = [str(alias).strip() for alias in item.get("aliases", []) if str(alias).strip()]
        seeds.append({
            "tag": tag,
            "aliases": aliases,
            "category": str(item.get("category", "")).strip(),
        })
    return seeds


def load_seed_works() -> list[dict]:
    works: list[dict] = []
    for item in load_json_list(SEED_WORKS_PATH):
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        works.append({
            "id": str(item.get("id", "")).strip(),
            "name": name,
            "aliases": [str(alias).strip() for alias in item.get("aliases", []) if str(alias).strip()],
            "series": str(item.get("series", "")).strip(),
            "characters": [str(v).strip() for v in item.get("characters", []) if str(v).strip()],
            "related_tags": [str(v).strip() for v in item.get("related_tags", []) if str(v).strip()],
        })
    return works


def build_history_counter(tasks: Iterable[dict]) -> Counter:
    counter: Counter = Counter()
    for task in tasks:
        for tag in split_pixiv_tags(str(task.get("tags", ""))):
            counter[tag] += 1
    return counter


def extract_folder_hint(target_folder: str) -> str:
    if not target_folder:
        return ""
    try:
        return Path(target_folder).name
    except Exception:
        return target_folder


def detect_work_matches(title: str, caption_pixiv: str, target_folder: str, works: list[dict]) -> list[dict]:
    search_blob = normalize_text(" ".join([
        title or "",
        caption_pixiv or "",
        extract_folder_hint(target_folder),
    ]))
    if not search_blob:
        return []

    matched: list[dict] = []
    for work in works:
        names = [work["name"], *work.get("aliases", [])]
        normalized_names = [normalize_text(name) for name in names if name]
        if any(name and name in search_blob for name in normalized_names):
            matched.append(work)
    return matched


def build_pixiv_tag_suggestions(
    *,
    title: str = "",
    caption_pixiv: str = "",
    target_folder: str = "",
    current_tags: str = "",
    tasks: Iterable[dict] = (),
) -> list[dict]:
    selected_tags = set(split_pixiv_tags(current_tags))
    suggestions: dict[str, dict] = {}

    def register(tag: str, source: str, score: int):
        clean_tag = tag.strip()
        if not clean_tag:
            return
        payload = suggestions.get(clean_tag)
        if payload is None or score > payload["score"]:
            suggestions[clean_tag] = {
                "tag": clean_tag,
                "source": source,
                "score": score,
                "selected": clean_tag in selected_tags,
            }

    history_counter = build_history_counter(tasks)
    for tag, count in history_counter.most_common(12):
        register(tag, "history", 100 + count)

    matched_works = detect_work_matches(title, caption_pixiv, target_folder, load_seed_works())
    for work in matched_works:
        register(work["name"], "works", 80)
        for tag in work.get("related_tags", []):
            register(tag, "works", 76)
        for character in work.get("characters", [])[:3]:
            register(character, "works", 72)

    seed_tags = load_seed_tags()
    search_blob = normalize_text(" ".join([title or "", caption_pixiv or "", extract_folder_hint(target_folder)]))
    for item in seed_tags:
        candidates = [item["tag"], *item.get("aliases", [])]
        normalized_candidates = [normalize_text(value) for value in candidates if value]
        if search_blob and any(token and token in search_blob for token in normalized_candidates):
            register(item["tag"], "seed", 60)

    if len(suggestions) < 10:
        for item in seed_tags:
            register(item["tag"], "seed", 40)
            if len(suggestions) >= 10:
                break

    ordered = sorted(
        suggestions.values(),
        key=lambda item: (-item["score"], item["tag"])
    )
    return ordered[:12]
