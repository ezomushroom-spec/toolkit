from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class SituationDraft:
    id: str
    name: str
    prompt: str
    negative_prompt: str
    tags: tuple[str, ...]
    wildcards: tuple[str, ...]
    notes: str
    updated_at: str

    @classmethod
    def create(
        cls,
        name: str,
        prompt: str,
        negative_prompt: str,
        tags: tuple[str, ...] = tuple(),
        wildcards: tuple[str, ...] = tuple(),
        notes: str = "",
    ) -> "SituationDraft":
        return cls(
            id=str(uuid4()),
            name=name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            tags=tags,
            wildcards=wildcards,
            notes=notes,
            updated_at=datetime.now().isoformat(timespec="seconds"),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "SituationDraft":
        return cls(
            id=str(data.get("id", "")) or str(uuid4()),
            name=str(data.get("name", "")),
            prompt=str(data.get("prompt", "")),
            negative_prompt=str(data.get("negative_prompt", "")),
            tags=tuple(str(item) for item in data.get("tags", []) if str(item).strip()),
            wildcards=tuple(str(item) for item in data.get("wildcards", []) if str(item).strip()),
            notes=str(data.get("notes", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "tags": list(self.tags),
            "wildcards": list(self.wildcards),
            "notes": self.notes,
            "updated_at": self.updated_at,
        }


class SituationStore:
    def __init__(self, situations_path: Path):
        self.situations_path = situations_path

    def load_all(self) -> tuple[SituationDraft, ...]:
        if not self.situations_path.exists():
            return tuple()

        try:
            data = json.loads(self.situations_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return tuple()

        if not isinstance(data, list):
            return tuple()

        return tuple(SituationDraft.from_dict(item) for item in data if isinstance(item, dict))

    def save_all(self, drafts: tuple[SituationDraft, ...]) -> None:
        self.situations_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [draft.to_dict() for draft in drafts]
        self.situations_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def upsert(self, draft: SituationDraft) -> tuple[SituationDraft, ...]:
        drafts = list(self.load_all())
        for index, existing in enumerate(drafts):
            if existing.id == draft.id:
                drafts[index] = draft
                break
        else:
            drafts.insert(0, draft)

        result = tuple(drafts)
        self.save_all(result)
        return result
