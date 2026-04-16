import uuid
from dataclasses import dataclass, field
from typing import List

from .group import Group


@dataclass
class MinorTab:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    groups: List[Group] = field(default_factory=list)

    def add_group(self, group: Group) -> None:
        self.groups.append(group)

    def remove_group(self, group_id: str) -> None:
        self.groups = [group for group in self.groups if group.id != group_id]

    def move_group(self, group_id: str, direction: int) -> None:
        for index, item in enumerate(self.groups):
            if item.id == group_id:
                new_index = max(0, min(len(self.groups) - 1, index + direction))
                self.groups.insert(new_index, self.groups.pop(index))
                break

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "groups": [group.to_dict() for group in self.groups],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MinorTab":
        tab = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
        )
        tab.groups = [Group.from_dict(group) for group in data.get("groups", [])]
        return tab


@dataclass
class MajorTab:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    minor_tabs: List[MinorTab] = field(default_factory=list)

    def add_minor_tab(self, tab: MinorTab) -> None:
        self.minor_tabs.append(tab)

    def remove_minor_tab(self, tab_id: str) -> None:
        self.minor_tabs = [tab for tab in self.minor_tabs if tab.id != tab_id]

    def move_minor_tab(self, tab_id: str, direction: int) -> None:
        for index, item in enumerate(self.minor_tabs):
            if item.id == tab_id:
                new_index = max(0, min(len(self.minor_tabs) - 1, index + direction))
                self.minor_tabs.insert(new_index, self.minor_tabs.pop(index))
                break

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "minor_tabs": [tab.to_dict() for tab in self.minor_tabs],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MajorTab":
        tab = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
        )
        tab.minor_tabs = [MinorTab.from_dict(item) for item in data.get("minor_tabs", [])]
        return tab
