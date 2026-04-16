"""
Post Manager - Pixiv popular tag collection helper
人気タグの棚卸し原料を raw / review へ分離保存する補助スクリプト。
既存の suggest / learning ランタイムには接続しない。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from config import Paths


RAW_PATH = Paths.DATA / "pixiv_popular_tag_collection_raw.jsonl"
REVIEW_PATH = Paths.DATA / "pixiv_popular_tag_collection_review.csv"
RAW_VERSION = 1
REVIEW_VERSION = 1
ALLOWED_SOURCE_TYPES = {"search", "tag_page", "work"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def normalize_tag(tag: str) -> str:
    return " ".join(str(tag or "").strip().split()).casefold()


def clean_tag(tag: str) -> str:
    return " ".join(str(tag or "").strip().split())


def dedupe_keep_order(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def parse_tags(tag_values: list[str], tags_file: str = "") -> list[str]:
    tags: list[str] = []
    for value in tag_values:
        tag = clean_tag(value)
        if tag:
            tags.append(tag)

    if tags_file:
        with open(tags_file, "r", encoding="utf-8") as handle:
            for line in handle:
                tag = clean_tag(line)
                if tag:
                    tags.append(tag)

    tags = dedupe_keep_order(tags)
    if not tags:
        raise ValueError("At least one tag is required. Use --tag or --tags-file.")
    return tags


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_raw_record(record: dict) -> None:
    ensure_parent(RAW_PATH)
    with open(RAW_PATH, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def iter_raw_records() -> list[dict]:
    if not RAW_PATH.exists():
        return []

    records: list[dict] = []
    with open(RAW_PATH, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            payload = line.strip()
            if not payload:
                continue
            try:
                item = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
            if isinstance(item, dict):
                records.append(item)
    return records


def atomic_write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    ensure_parent(path)
    fd, temp_path = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            if rows:
                writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def add_raw(args: argparse.Namespace) -> None:
    source_type = str(args.source_type or "").strip()
    if source_type not in ALLOWED_SOURCE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_SOURCE_TYPES))
        raise ValueError(f"--source-type must be one of: {allowed}")

    source_key = clean_tag(args.source_key)
    if not source_key:
        raise ValueError("--source-key is required.")

    tags = parse_tags(args.tag or [], args.tags_file or "")
    record = {
        "version": RAW_VERSION,
        "collected_at": now_iso(),
        "source_type": source_type,
        "source_key": source_key,
        "page_url": str(args.page_url or "").strip(),
        "context_note": str(args.context_note or "").strip(),
        "tags": tags,
    }
    append_raw_record(record)
    print(f"Added raw record: {source_type} / {source_key} / {len(tags)} tags")


def build_review(_args: argparse.Namespace) -> None:
    records = iter_raw_records()
    aggregated: dict[str, dict] = {}

    for record in records:
        source_type = clean_tag(record.get("source_type", ""))
        source_key = clean_tag(record.get("source_key", ""))
        collected_at = str(record.get("collected_at", "")).strip()
        tags = record.get("tags", [])
        if not isinstance(tags, list):
            continue

        unique_tags = dedupe_keep_order([clean_tag(tag) for tag in tags if clean_tag(tag)])
        for tag in unique_tags:
            normalized = normalize_tag(tag)
            if not normalized:
                continue

            item = aggregated.get(normalized)
            if item is None:
                item = {
                    "version": REVIEW_VERSION,
                    "tag": tag,
                    "normalized_tag": normalized,
                    "decision": "",
                    "note": "",
                    "observed_count": 0,
                    "source_types": set(),
                    "source_keys": set(),
                    "latest_collected_at": collected_at,
                    "sample_sources": [],
                }
                aggregated[normalized] = item

            item["observed_count"] += 1
            item["source_types"].add(source_type)
            if source_key:
                item["source_keys"].add(source_key)

            if collected_at and collected_at > item["latest_collected_at"]:
                item["latest_collected_at"] = collected_at

            sample_source = f"{source_type}:{source_key}" if source_key else source_type
            if sample_source and sample_source not in item["sample_sources"] and len(item["sample_sources"]) < 5:
                item["sample_sources"].append(sample_source)

    rows: list[dict] = []
    for item in sorted(aggregated.values(), key=lambda value: (-value["observed_count"], value["tag"])):
        rows.append({
            "version": item["version"],
            "tag": item["tag"],
            "normalized_tag": item["normalized_tag"],
            "decision": item["decision"],
            "note": item["note"],
            "observed_count": item["observed_count"],
            "source_types": "|".join(sorted(v for v in item["source_types"] if v)),
            "source_key_count": len(item["source_keys"]),
            "latest_collected_at": item["latest_collected_at"],
            "sample_sources": " | ".join(item["sample_sources"]),
        })

    fieldnames = [
        "version",
        "tag",
        "normalized_tag",
        "decision",
        "note",
        "observed_count",
        "source_types",
        "source_key_count",
        "latest_collected_at",
        "sample_sources",
    ]
    atomic_write_csv(REVIEW_PATH, rows, fieldnames)
    print(f"Built review file: {REVIEW_PATH} ({len(rows)} rows)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pixiv popular tag collection helper"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_raw_parser = subparsers.add_parser(
        "add-raw",
        help="Append one raw observation record",
    )
    add_raw_parser.add_argument(
        "--source-type",
        required=True,
        help="Observation source type: search, tag_page, work",
    )
    add_raw_parser.add_argument(
        "--source-key",
        required=True,
        help="Search word, page label, or work title",
    )
    add_raw_parser.add_argument(
        "--tag",
        action="append",
        help="Observed tag. Repeat for multiple tags.",
    )
    add_raw_parser.add_argument(
        "--tags-file",
        help="UTF-8 text file with one tag per line",
    )
    add_raw_parser.add_argument(
        "--page-url",
        help="Optional page URL or memo",
    )
    add_raw_parser.add_argument(
        "--context-note",
        help="Optional observation note",
    )
    add_raw_parser.set_defaults(func=add_raw)

    build_review_parser = subparsers.add_parser(
        "build-review",
        help="Aggregate raw observations into a review CSV",
    )
    build_review_parser.set_defaults(func=build_review)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
