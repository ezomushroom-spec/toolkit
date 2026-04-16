from typing import Callable

try:
    import keyboard

    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False


class HotkeyService:
    def __init__(self, hotkey: str, callback: Callable[[], None]):
        self.hotkey = hotkey
        self.callback = callback
        self._running = False

    def start(self) -> bool:
        if not HAS_KEYBOARD:
            return False
        if self._running:
            return True
        try:
            keyboard.add_hotkey(self.hotkey, self.callback, suppress=False)
            self._running = True
            return True
        except Exception:
            return False

    def stop(self) -> None:
        if not self._running or not HAS_KEYBOARD:
            return
        try:
            keyboard.remove_hotkey(self.hotkey)
        except Exception:
            pass
        self._running = False
