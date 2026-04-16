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

import pixiv_tag_learning

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SEED_TAGS_PATH = DATA_DIR / "pixiv_seed_tags.json"
BUNDLED_TAGS_PATH = DATA_DIR / "pixiv_bundled_vocabulary_tags.json"
SEED_WORKS_PATH = DATA_DIR / "pixiv_seed_works.json"

WHITESPACE_RE = re.compile(r"[\s\u3000]+")
NORMALIZE_RE = re.compile(r"[\s\u3000_\-]+")
TOKEN_SPLIT_RE = re.compile(r"[\s\u3000_\-:/\\()\[\]{}.,]+")


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


def extract_context_tokens(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for raw in TOKEN_SPLIT_RE.split(value or ""):
            token = normalize_text(raw)
            if token:
                tokens.add(token)
    return tokens


def load_json_list(path: Path) -> list[dict]:
    try:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, list) else []
    except Exception:
        return []


def load_tag_catalog(path: Path) -> list[dict]:
    catalog: list[dict] = []
    for item in load_json_list(path):
        tag = str(item.get("tag", "")).strip()
        if not tag:
            continue
        aliases = [str(alias).strip() for alias in item.get("aliases", []) if str(alias).strip()]
        catalog.append({
            "tag": tag,
            "aliases": aliases,
            "category": str(item.get("category", "")).strip(),
            "usage_count": int(item.get("usage_count", 0) or 0),
            "legacy_category": str(item.get("legacy_category", "")).strip(),
        })
    return catalog


def load_seed_tags() -> list[dict]:
    return load_tag_catalog(SEED_TAGS_PATH)


def load_bundled_tags() -> list[dict]:
    return load_tag_catalog(BUNDLED_TAGS_PATH)


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
    search_values = [
        title or "",
        caption_pixiv or "",
        extract_folder_hint(target_folder),
    ]
    search_blob = normalize_text(" ".join(search_values))
    search_tokens = extract_context_tokens(*search_values)
    if not search_blob:
        return []

    matched: list[dict] = []
    for work in works:
        score = 0
        direct_match = False

        primary_name = normalize_text(work.get("name", ""))
        if primary_name and primary_name in search_blob:
            score = max(score, 80)
            direct_match = True

        for alias in work.get("aliases", []):
            normalized_alias = normalize_text(alias)
            if normalized_alias and normalized_alias in search_blob:
                score = max(score, 76)
                direct_match = True

        series_name = normalize_text(work.get("series", ""))
        if series_name and series_name in search_blob:
            score = max(score, 72)
            direct_match = True

        character_hits = 0
        matched_characters: list[str] = []
        for character in work.get("characters", []):
            normalized_character = normalize_text(character)
            if not normalized_character:
                continue

            matched_by_suffix = any(
                len(token) >= 2 and normalized_character.endswith(token)
                for token in search_tokens
            )

            if normalized_character in search_tokens or matched_by_suffix:
                character_hits += 1
                matched_characters.append(character)

        if character_hits and score:
            score += min(character_hits, 2) * 6
        elif character_hits >= 2:
            score = 58

        if score:
            matched.append({
                **work,
                "match_score": score,
                "direct_match": direct_match,
                "character_hits": character_hits,
                "matched_characters": matched_characters,
            })
    return matched


def build_category_maps(seed_tags: list[dict], works: list[dict]) -> tuple[dict[str, str], set[str], set[str]]:
    seed_category_map: dict[str, str] = {}
    for item in seed_tags:
        category = str(item.get("category", "")).strip()
        values = [item.get("tag", ""), *item.get("aliases", [])]
        for value in values:
            normalized = normalize_text(str(value))
            if normalized:
                seed_category_map[normalized] = category

    work_tag_names: set[str] = set()
    character_names: set[str] = set()
    for work in works:
        for value in [work.get("name", ""), work.get("series", ""), *work.get("aliases", []), *work.get("related_tags", [])]:
            normalized = normalize_text(str(value))
            if normalized:
                work_tag_names.add(normalized)
        for character in work.get("characters", []):
            normalized_character = normalize_text(str(character))
            if normalized_character:
                character_names.add(normalized_character)

    return seed_category_map, work_tag_names, character_names


def classify_meaning_category(
    tag: str,
    *,
    default_category: str = "content",
    seed_category_map: dict[str, str],
    work_tag_names: set[str],
    character_names: set[str],
) -> str:
    normalized_tag = normalize_text(tag)
    seed_category = seed_category_map.get(normalized_tag, "")
    if seed_category == "rating":
        return "rating"
    if seed_category == "character":
        return "character"
    if normalized_tag in character_names:
        return "character"
    if normalized_tag in work_tag_names:
        return "work"
    return default_category


def classify_content_subcategory(
    tag: str,
    *,
    seed_category_map: dict[str, str],
) -> str:
    normalized_tag = normalize_text(tag)
    seed_category = seed_category_map.get(normalized_tag, "")
    if seed_category == "costume":
        return "costume"
    if seed_category == "attribute":
        return "fetish"
    if seed_category == "act":
        return "act"
    if seed_category == "situation":
        return "play"
    return "other"


def build_pixiv_tag_suggestions(
    *,
    title: str = "",
    caption_pixiv: str = "",
    target_folder: str = "",
    current_tags: str = "",
    browse_vocabulary: bool = False,
    tag_query: str = "",
    tasks: Iterable[dict] = (),
) -> list[dict]:
    selected_tags = set(split_pixiv_tags(current_tags))
    suggestions: dict[str, dict] = {}
    seed_tags = load_seed_tags()
    bundled_tags = load_bundled_tags()
    seed_works = load_seed_works()
    all_tag_catalog = [*seed_tags, *bundled_tags]
    seed_category_map, work_tag_names, character_names = build_category_maps(all_tag_catalog, seed_works)

    if browse_vocabulary:
        return build_pixiv_tag_vocabulary_browser(
            current_tags=current_tags,
            tag_query=tag_query,
            seed_tags=seed_tags,
            bundled_tags=bundled_tags,
            seed_works=seed_works,
            seed_category_map=seed_category_map,
            work_tag_names=work_tag_names,
            character_names=character_names,
        )

    def register(
        tag: str,
        source: str,
        score: int,
        group_order: int = 50,
        meaning_category: str = "content",
        content_subcategory: str = "other",
    ):
        clean_tag = tag.strip()
        if not clean_tag:
            return
        payload = suggestions.get(clean_tag)
        if (
            payload is None
            or score > payload["score"]
            or (score == payload["score"] and group_order < payload["group_order"])
        ):
            suggestions[clean_tag] = {
                "tag": clean_tag,
                "source": source,
                "score": score,
                "group_order": group_order,
                "meaning_category": meaning_category,
                "content_subcategory": content_subcategory if meaning_category == "content" else "",
                "selected": clean_tag in selected_tags,
            }

    history_counter = build_history_counter(tasks)
    learning_counter = Counter(pixiv_tag_learning.get_learning_counts())

    for tag, count in learning_counter.most_common(12):
        register(
            tag,
            "learning",
            200 + count,
            0,
            meaning_category := classify_meaning_category(
                tag,
                default_category="content",
                seed_category_map=seed_category_map,
                work_tag_names=work_tag_names,
                character_names=character_names,
            ),
            classify_content_subcategory(
                tag,
                seed_category_map=seed_category_map,
            ) if meaning_category == "content" else "",
        )

    for tag, count in history_counter.most_common(12):
        register(
            tag,
            "history",
            100 + count,
            1,
            meaning_category := classify_meaning_category(
                tag,
                default_category="content",
                seed_category_map=seed_category_map,
                work_tag_names=work_tag_names,
                character_names=character_names,
            ),
            classify_content_subcategory(
                tag,
                seed_category_map=seed_category_map,
            ) if meaning_category == "content" else "",
        )

    matched_works = detect_work_matches(title, caption_pixiv, target_folder, seed_works)
    for work in matched_works:
        base_score = int(work.get("match_score", 80))
        register(work["name"], "works", base_score, 2, "work")
        for tag in work.get("related_tags", []):
            register(tag, "works", base_score - 4, 4, "work")
        matched_characters = list(work.get("matched_characters", []))
        if work.get("direct_match"):
            for character in matched_characters:
                register(character, "works", base_score - 2, 3, "character")
            fallback_characters = [
                character
                for character in work.get("characters", [])[:3]
                if character not in matched_characters
            ]
            for character in fallback_characters:
                register(character, "works", base_score - 8, 5, "character")
        else:
            for character in matched_characters:
                register(character, "works", base_score - 8, 3, "character")

    search_blob = normalize_text(" ".join([title or "", caption_pixiv or "", extract_folder_hint(target_folder)]))

    def register_search_match(item: dict, source: str, base_score: int, group_order: int):
        register(
            item["tag"],
            source,
            base_score,
            group_order,
            meaning_category := classify_meaning_category(
                item["tag"],
                default_category="content",
                seed_category_map=seed_category_map,
                work_tag_names=work_tag_names,
                character_names=character_names,
            ),
            classify_content_subcategory(
                item["tag"],
                seed_category_map=seed_category_map,
            ) if meaning_category == "content" else "",
        )

    for item in seed_tags:
        candidates = [item["tag"], *item.get("aliases", [])]
        normalized_candidates = [normalize_text(value) for value in candidates if value]
        if search_blob and any(token and token in search_blob for token in normalized_candidates):
            register_search_match(item, "seed", 60, 6)

    for item in bundled_tags:
        candidates = [item["tag"], *item.get("aliases", [])]
        normalized_candidates = [normalize_text(value) for value in candidates if value]
        if search_blob and any(token and token in search_blob for token in normalized_candidates):
            usage_count = int(item.get("usage_count", 0) or 0)
            register_search_match(item, "bundle", 48 + min(usage_count, 12), 7)

    if len(suggestions) < 10:
        for item in seed_tags:
            register_search_match(item, "seed", 40, 6)
            if len(suggestions) >= 18:
                break

    ordered = sorted(
        suggestions.values(),
        key=lambda item: (-item["score"], item["group_order"], item["tag"])
    )
    return ordered[:18]


def build_pixiv_tag_vocabulary_browser(
    *,
    current_tags: str = "",
    tag_query: str = "",
    seed_tags: list[dict],
    bundled_tags: list[dict],
    seed_works: list[dict],
    seed_category_map: dict[str, str],
    work_tag_names: set[str],
    character_names: set[str],
) -> list[dict]:
    selected_tags = set(split_pixiv_tags(current_tags))
    normalized_query = normalize_text(tag_query)
    combined_items: list[dict] = []

    def matches_query(item: dict) -> bool:
        if not normalized_query:
            return True
        for value in [item.get("tag", ""), *item.get("aliases", [])]:
            if normalized_query in normalize_text(str(value)):
                return True
        return False

    def source_priority(source: str) -> int:
        if source == "seed":
            return 0
        return 1

    def subcategory_priority(subcategory: str) -> int:
        order = {
            "fetish": 0,
            "costume": 1,
            "play": 2,
            "act": 3,
            "other": 4,
        }
        return order.get(subcategory, 9)

    def meaning_priority(category: str) -> int:
        order = {
            "rating": 0,
            "work": 1,
            "character": 2,
            "content": 3,
        }
        return order.get(category, 9)

    for source, items in (("seed", seed_tags), ("bundle", bundled_tags)):
        for item in items:
            tag = str(item.get("tag", "")).strip()
            if not tag or not matches_query(item):
                continue
            meaning_category = classify_meaning_category(
                tag,
                default_category="content",
                seed_category_map=seed_category_map,
                work_tag_names=work_tag_names,
                character_names=character_names,
            )
            content_subcategory = ""
            if meaning_category == "content":
                content_subcategory = classify_content_subcategory(
                    tag,
                    seed_category_map=seed_category_map,
                )
            combined_items.append({
                "tag": tag,
                "source": source,
                "score": 0,
                "group_order": 6 if source == "seed" else 7,
                "meaning_category": meaning_category,
                "content_subcategory": content_subcategory,
                "selected": tag in selected_tags,
                "usage_count": int(item.get("usage_count", 0) or 0),
            })

    for work in seed_works:
        for tag in [work.get("name", ""), *work.get("related_tags", [])]:
            clean_tag = str(tag).strip()
            if not clean_tag or not matches_query({"tag": clean_tag, "aliases": []}):
                continue
            combined_items.append({
                "tag": clean_tag,
                "source": "works",
                "score": 0,
                "group_order": 4,
                "meaning_category": "work",
                "content_subcategory": "",
                "selected": clean_tag in selected_tags,
                "usage_count": 0,
            })

        for character in work.get("characters", []):
            clean_tag = str(character).strip()
            if not clean_tag or not matches_query({"tag": clean_tag, "aliases": []}):
                continue
            combined_items.append({
                "tag": clean_tag,
                "source": "works",
                "score": 0,
                "group_order": 5,
                "meaning_category": "character",
                "content_subcategory": "",
                "selected": clean_tag in selected_tags,
                "usage_count": 0,
            })

    deduped: dict[str, dict] = {}
    for item in combined_items:
        existing = deduped.get(item["tag"])
        if existing is None:
            deduped[item["tag"]] = item
            continue
        if source_priority(item["source"]) < source_priority(existing["source"]):
            deduped[item["tag"]] = item
            continue
        if item["usage_count"] > existing["usage_count"]:
            deduped[item["tag"]] = item

    content_grouped: dict[str, list[dict]] = {
        "fetish": [],
        "costume": [],
        "play": [],
        "act": [],
        "other": [],
    }
    high_level_grouped: dict[str, list[dict]] = {
        "rating": [],
        "work": [],
        "character": [],
    }
    for item in deduped.values():
        if item["meaning_category"] == "content":
            content_grouped[item["content_subcategory"]].append(item)
        else:
            high_level_grouped[item["meaning_category"]].append(item)

    result: list[dict] = []
    limit_per_group = 24 if normalized_query else 12
    for category in ["rating", "work", "character"]:
        items = sorted(
            high_level_grouped[category],
            key=lambda item: (
                source_priority(item["source"]),
                -item["usage_count"],
                item["tag"]
            )
        )
        result.extend(items[:limit_per_group])
    for subcategory in ["fetish", "costume", "play", "act", "other"]:
        items = sorted(
            content_grouped[subcategory],
            key=lambda item: (
                source_priority(item["source"]),
                -item["usage_count"],
                item["tag"]
            )
        )
        result.extend(items[:limit_per_group])

    return sorted(
        result,
        key=lambda item: (
            meaning_priority(item["meaning_category"]),
            subcategory_priority(item["content_subcategory"]) if item["meaning_category"] == "content" else -1,
            source_priority(item["source"]),
            -item["usage_count"],
            item["tag"]
        )
    )
