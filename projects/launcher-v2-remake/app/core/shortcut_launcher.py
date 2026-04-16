import ctypes
import os
import subprocess
from typing import Callable, Optional

from app.models import Shortcut


class ShortcutLauncher:
    def __init__(
        self,
        on_launch_success: Optional[Callable[[Shortcut], None]] = None,
        on_launch_error: Optional[Callable[[Shortcut, str], None]] = None,
    ):
        self.on_launch_success = on_launch_success
        self.on_launch_error = on_launch_error

    def launch(self, shortcut: Shortcut, as_admin: bool = False) -> bool:
        try:
            if not os.path.exists(shortcut.path):
                self._report_error(shortcut, f"パスが見つかりません: {shortcut.path}")
                return False
            return self._launch_as_admin(shortcut) if as_admin else self._launch_normal(shortcut)
        except Exception as exc:
            self._report_error(shortcut, str(exc))
            return False

    def _launch_normal(self, shortcut: Shortcut) -> bool:
        working_dir = os.path.dirname(shortcut.path) or None
        if os.path.isdir(shortcut.path):
            os.startfile(shortcut.path)
        else:
            subprocess.Popen(f'"{shortcut.path}"', shell=True, cwd=working_dir)
        if self.on_launch_success:
            self.on_launch_success(shortcut)
        return True

    def _launch_as_admin(self, shortcut: Shortcut) -> bool:
        working_dir = os.path.dirname(shortcut.path)
        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", shortcut.path, None, working_dir, 1)
        if result <= 32:
            self._report_error(shortcut, f"管理者起動失敗 (エラーコード: {result})")
            return False
        if self.on_launch_success:
            self.on_launch_success(shortcut)
        return True

    def _report_error(self, shortcut: Shortcut, message: str) -> None:
        if self.on_launch_error:
            self.on_launch_error(shortcut, message)
