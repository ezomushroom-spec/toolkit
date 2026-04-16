from __future__ import annotations

import json
from pathlib import Path

from app.core.state.settings import AppSettings


class SettingsRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> AppSettings:
        try:
            if not self.path.exists():
                return AppSettings()
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return AppSettings(**payload)
        except Exception:  # noqa: BLE001
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(settings.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
