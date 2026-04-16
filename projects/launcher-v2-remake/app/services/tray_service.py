import threading
from pathlib import Path
from typing import Callable, Optional

from PIL import Image

try:
    import pystray
    from pystray import MenuItem as Item

    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False


class TrayService:
    def __init__(
        self,
        icon_path: Path,
        app_name: str,
        on_show: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
    ):
        self.icon_path = Path(icon_path)
        self.app_name = app_name
        self.on_show = on_show
        self.on_exit = on_exit
        self._icon = None
        self._thread = None

    def start(self) -> bool:
        if not HAS_PYSTRAY:
            return False
        if self._icon:
            return True
        try:
            menu = pystray.Menu(Item("表示", self._handle_show, default=True), Item("終了", self._handle_exit))
            self._icon = pystray.Icon(self.app_name, self._load_icon(), self.app_name, menu)
            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
            return True
        except Exception:
            self._icon = None
            return False

    def stop(self) -> None:
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def _load_icon(self) -> Image.Image:
        if self.icon_path.exists():
            try:
                return Image.open(self.icon_path)
            except Exception:
                pass
        return Image.new("RGB", (64, 64), color="#2f855a")

    def _handle_show(self, icon=None, item=None) -> None:
        if self.on_show:
            self.on_show()

    def _handle_exit(self, icon=None, item=None) -> None:
        if self.on_exit:
            self.on_exit()
