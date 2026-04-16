from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass(frozen=True)
class WorkSession:
    prompt: str
    negative_prompt: str
    updated_at: str

    @classmethod
    def create(cls, prompt: str, negative_prompt: str) -> "WorkSession":
        return cls(
            prompt=prompt,
            negative_prompt=negative_prompt,
            updated_at=datetime.now().isoformat(timespec="seconds"),
        )


class SessionStore:
    def __init__(self, session_path: Path):
        self.session_path = session_path

    def load(self) -> WorkSession | None:
        if not self.session_path.exists():
            return None

        try:
            data = json.loads(self.session_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(data, dict):
            return None

        return WorkSession(
            prompt=str(data.get("prompt", "")),
            negative_prompt=str(data.get("negative_prompt", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def save(self, session: WorkSession) -> None:
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "prompt": session.prompt,
            "negative_prompt": session.negative_prompt,
            "updated_at": session.updated_at,
        }
        self.session_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def clear(self) -> None:
        if self.session_path.exists():
            self.session_path.unlink()
