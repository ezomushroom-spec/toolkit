import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config_manager import ConfigManager
from app.services.hotkey_service import HotkeyService
from app.services.tray_service import TrayService
from app.ui.main_window import LauncherApp
from app.utils.path_utils import get_asset_path


def main() -> None:
    config = ConfigManager()
    app = LauncherApp(config)

    def on_hotkey() -> None:
        app.after(0, app.toggle_visibility)

    def on_tray_show() -> None:
        app.after(0, app.show_window)

    def on_tray_exit() -> None:
        app.after(0, app.quit_app)

    hotkey_service = HotkeyService(config.hotkey, on_hotkey)
    tray_service = TrayService(
        icon_path=get_asset_path("icon.ico"),
        app_name="Launcher V2 Remake",
        on_show=on_tray_show,
        on_exit=on_tray_exit,
    )

    hotkey_service.start()
    tray_service.start()
    app.attach_runtime_services(hotkey_service, tray_service)
    app.show_window()

    try:
        app.mainloop()
    finally:
        hotkey_service.stop()
        tray_service.stop()
        config.shutdown()


if __name__ == "__main__":
    main()
