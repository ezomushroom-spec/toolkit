import uuid
from dataclasses import dataclass, field
from typing import Literal

ShortcutType = Literal["application", "folder", "file"]


@dataclass
class Shortcut:
    name: str
    path: str
    type: ShortcutType = "application"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Shortcut":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            path=data["path"],
            type=data.get("type", "application"),
        )
