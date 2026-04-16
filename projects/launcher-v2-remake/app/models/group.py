import uuid
from dataclasses import dataclass, field
from typing import List

from .shortcut import Shortcut


@dataclass
class Group:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    shortcuts: List[Shortcut] = field(default_factory=list)

    def add_shortcut(self, shortcut: Shortcut) -> None:
        self.shortcuts.append(shortcut)

    def remove_shortcut(self, shortcut_id: str) -> None:
        self.shortcuts = [item for item in self.shortcuts if item.id != shortcut_id]

    def move_shortcut(self, shortcut_id: str, direction: int) -> None:
        for index, item in enumerate(self.shortcuts):
            if item.id == shortcut_id:
                new_index = max(0, min(len(self.shortcuts) - 1, index + direction))
                self.shortcuts.insert(new_index, self.shortcuts.pop(index))
                break

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "shortcuts": [shortcut.to_dict() for shortcut in self.shortcuts],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Group":
        group = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
        )
        group.shortcuts = [Shortcut.from_dict(item) for item in data.get("shortcuts", [])]
        return group
