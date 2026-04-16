from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass(frozen=True)
class WildcardDraft:
    name: str
    token: str
    items: tuple[str, ...]
    source_file_name: str
    updated_at: str

    @classmethod
    def create(
        cls,
        name: str,
        token: str,
        items: tuple[str, ...],
        source_file_name: str,
    ) -> "WildcardDraft":
        return cls(
            name=name,
            token=token,
            items=items,
            source_file_name=source_file_name,
            updated_at=datetime.now().isoformat(timespec="seconds"),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "WildcardDraft":
        return cls(
            name=str(data.get("name", "")),
            token=str(data.get("token", "")),
            items=tuple(str(item) for item in data.get("items", []) if str(item).strip()),
            source_file_name=str(data.get("source_file_name", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "token": self.token,
            "items": list(self.items),
            "source_file_name": self.source_file_name,
            "updated_at": self.updated_at,
        }


class WildcardDraftStore:
    def __init__(self, drafts_path: Path):
        self.drafts_path = drafts_path

    def load_all(self) -> dict[str, WildcardDraft]:
        if not self.drafts_path.exists():
            return {}

        try:
            data = json.loads(self.drafts_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

        if not isinstance(data, list):
            return {}

        drafts = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            draft = WildcardDraft.from_dict(item)
            if draft.name:
                drafts[draft.name] = draft
        return drafts

    def save_all(self, drafts: dict[str, WildcardDraft]) -> None:
        self.drafts_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [draft.to_dict() for draft in sorted(drafts.values(), key=lambda item: item.name.casefold())]
        self.drafts_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def upsert(self, draft: WildcardDraft) -> dict[str, WildcardDraft]:
        drafts = self.load_all()
        drafts[draft.name] = draft
        self.save_all(drafts)
        return drafts

    def delete(self, name: str) -> dict[str, WildcardDraft]:
        drafts = self.load_all()
        drafts.pop(name, None)
        self.save_all(drafts)
        return drafts
