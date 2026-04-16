import json
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.models import MajorTab, Shortcut
from app.utils.path_utils import get_config_dir, get_legacy_config_file

CONFIG_VERSION = "2.0"
SAVE_DELAY_MS = 500


class ConfigManager:
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = Path(config_file) if config_file else get_config_dir() / "settings.json"
        self.version = CONFIG_VERSION
        self.hotkey = "alt+space"
        self.major_tabs: List[MajorTab] = []
        self.window_geometry = "1000x680"
        self.window_position: Optional[str] = None
        self.view_mode = "list"
        self.recent_apps: List[Dict] = []
        self.max_recent_apps = 10
        self.pinned_shortcuts: List[str] = []
        self.shortcut_hotkeys: Dict[str, str] = {}
        self.theme_name = "dark"
        self.collapsed_groups: Dict[str, bool] = {}
        self.usage_stats: Dict[str, int] = {}

        self._save_lock = threading.Lock()
        self._save_timer: Optional[threading.Timer] = None

        self._bootstrap_from_legacy_if_needed()
        self._load_config()

    def _bootstrap_from_legacy_if_needed(self) -> None:
        if self.config_file.exists():
            return
        legacy_file = get_legacy_config_file()
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        if legacy_file.exists():
            shutil.copy2(legacy_file, self.config_file)

    def _load_config(self) -> None:
        if not self.config_file.exists():
            self._create_default_config()
            return
        try:
            data = json.loads(self.config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._create_default_config()
            return

        self.version = data.get("version", CONFIG_VERSION)
        self.hotkey = data.get("hotkey", self.hotkey)
        self.major_tabs = [MajorTab.from_dict(item) for item in data.get("major_tabs", [])]
        self.window_geometry = data.get("window_geometry", self.window_geometry)
        self.window_position = data.get("window_position")
        self.view_mode = data.get("view_mode", self.view_mode)
        self.recent_apps = data.get("recent_apps", [])
        self.pinned_shortcuts = data.get("pinned_shortcuts", [])
        self.shortcut_hotkeys = data.get("shortcut_hotkeys", {})
        self.theme_name = data.get("theme_name", self.theme_name)
        self.collapsed_groups = data.get("collapsed_groups", {})
        self.usage_stats = data.get("usage_stats", {})

    def _create_default_config(self) -> None:
        self.major_tabs = [MajorTab(name="メイン")]
        self.save_config(immediate=True)

    def save_config(self, immediate: bool = False) -> None:
        if immediate:
            self._do_save()
        else:
            self._schedule_save()

    def _schedule_save(self) -> None:
        with self._save_lock:
            if self._save_timer:
                self._save_timer.cancel()
            self._save_timer = threading.Timer(SAVE_DELAY_MS / 1000, self._do_save)
            self._save_timer.daemon = True
            self._save_timer.start()

    def _do_save(self) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": self.version,
            "hotkey": self.hotkey,
            "major_tabs": [item.to_dict() for item in self.major_tabs],
            "window_geometry": self.window_geometry,
            "window_position": self.window_position,
            "view_mode": self.view_mode,
            "recent_apps": self.recent_apps,
            "pinned_shortcuts": self.pinned_shortcuts,
            "shortcut_hotkeys": self.shortcut_hotkeys,
            "theme_name": self.theme_name,
            "collapsed_groups": self.collapsed_groups,
            "usage_stats": self.usage_stats,
        }
        self.config_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def shutdown(self) -> None:
        with self._save_lock:
            if self._save_timer:
                self._save_timer.cancel()
                self._save_timer = None
        self._do_save()

    def add_major_tab(self, tab: MajorTab) -> None:
        self.major_tabs.append(tab)
        self.save_config()

    def remove_major_tab(self, tab_id: str) -> None:
        self.major_tabs = [tab for tab in self.major_tabs if tab.id != tab_id]
        self.save_config()

    def move_major_tab(self, tab_id: str, direction: int) -> None:
        for index, item in enumerate(self.major_tabs):
            if item.id == tab_id:
                new_index = max(0, min(len(self.major_tabs) - 1, index + direction))
                self.major_tabs.insert(new_index, self.major_tabs.pop(index))
                self.save_config()
                break

    def add_recent_app(self, path: str, name: str) -> None:
        self.recent_apps = [item for item in self.recent_apps if item.get("path") != path]
        self.recent_apps.insert(0, {"path": path, "name": name, "timestamp": datetime.now().isoformat()})
        self.recent_apps = self.recent_apps[: self.max_recent_apps]
        self.save_config()

    def clear_recent_apps(self) -> None:
        self.recent_apps = []
        self.save_config()

    def toggle_pin(self, shortcut_id: str) -> bool:
        if shortcut_id in self.pinned_shortcuts:
            self.pinned_shortcuts.remove(shortcut_id)
            self.save_config()
            return False
        self.pinned_shortcuts.append(shortcut_id)
        self.save_config()
        return True

    def is_pinned(self, shortcut_id: str) -> bool:
        return shortcut_id in self.pinned_shortcuts

    def set_group_collapsed(self, group_id: str, collapsed: bool) -> None:
        self.collapsed_groups[group_id] = collapsed
        self.save_config()

    def is_group_collapsed(self, group_id: str) -> bool:
        return self.collapsed_groups.get(group_id, False)

    def increment_usage(self, shortcut_id: str) -> None:
        self.usage_stats[shortcut_id] = self.usage_stats.get(shortcut_id, 0) + 1
        self.save_config()

    def find_all_shortcuts(self) -> List[tuple]:
        items = []
        for major_tab in self.major_tabs:
            for minor_tab in major_tab.minor_tabs:
                for group in minor_tab.groups:
                    for shortcut in group.shortcuts:
                        items.append((major_tab, minor_tab, group, shortcut))
        return items

    def find_shortcut_by_id(self, shortcut_id: str) -> Optional[Shortcut]:
        for _, _, _, shortcut in self.find_all_shortcuts():
            if shortcut.id == shortcut_id:
                return shortcut
        return None
