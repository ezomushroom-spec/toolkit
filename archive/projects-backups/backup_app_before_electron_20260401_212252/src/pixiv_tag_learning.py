"""
Post Manager - Pixiv tag learning
Phase 2 の軽量な保存時学習を担当する。
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LEARNING_PATH = DATA_DIR / "pixiv_tag_learning.json"
LEARNING_BACKUP_PATH = DATA_DIR / "pixiv_tag_learning.json.bak"
LEARNING_CORRUPT_PATH = DATA_DIR / "pixiv_tag_learning.json.corrupt"


def _default_state() -> dict:
    return {
        "version": 1,
        "updated_at": "",
        "tag_counts": {},
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _split_tags(value: str) -> list[str]:
    seen = set()
    tags: list[str] = []
    for raw in str(value or "").replace("\u3000", " ").split():
        tag = raw.strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


def _sanitize_state(payload: object) -> dict:
    state = _default_state()
    if not isinstance(payload, dict):
        return state

    state["version"] = int(payload.get("version", 1) or 1)
    state["updated_at"] = str(payload.get("updated_at", "") or "")

    raw_counts = payload.get("tag_counts", {})
    clean_counts: Dict[str, int] = {}
    if isinstance(raw_counts, dict):
        for raw_tag, raw_count in raw_counts.items():
            tag = str(raw_tag).strip()
            if not tag:
                continue
            try:
                count = int(raw_count)
            except (TypeError, ValueError):
                continue
            if count > 0:
                clean_counts[tag] = count

    state["tag_counts"] = clean_counts
    return state


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            try:
                shutil.copy2(path, LEARNING_BACKUP_PATH)
            except Exception:
                pass
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def load_learning_state() -> Tuple[dict, str]:
    if not LEARNING_PATH.exists():
        return _default_state(), ""

    try:
        with open(LEARNING_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return _sanitize_state(payload), ""
    except Exception:
        warning = "Pixivタグ学習データが破損していたため再生成しました。"
        try:
            LEARNING_PATH.replace(LEARNING_CORRUPT_PATH)
        except Exception:
            pass
        return _default_state(), warning


def get_learning_counts() -> Dict[str, int]:
    state, _warning = load_learning_state()
    return dict(state.get("tag_counts", {}))


def record_saved_tags(tags_value: str) -> dict:
    tags = _split_tags(tags_value)
    if not tags:
        return {
            "updated": False,
            "warning": "",
            "recovered": False,
        }

    state, load_warning = load_learning_state()
    tag_counts = dict(state.get("tag_counts", {}))
    for tag in tags:
        tag_counts[tag] = int(tag_counts.get(tag, 0)) + 1

    state["version"] = 1
    state["updated_at"] = _now_iso()
    state["tag_counts"] = tag_counts

    try:
        _atomic_write_json(LEARNING_PATH, state)
    except Exception:
        return {
            "updated": False,
            "warning": "Pixivタグ学習を保存できませんでした。",
            "recovered": False,
        }

    return {
        "updated": True,
        "warning": load_warning,
        "recovered": bool(load_warning),
    }
