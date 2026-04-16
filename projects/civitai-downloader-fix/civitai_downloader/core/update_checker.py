"""新バージョン検知（UIスレッドにDB操作を委譲）"""

import logging
import threading

from PySide6.QtCore import QObject, Signal

from civitai_downloader.core.civitai_api import CivitaiApiClient
from civitai_downloader.constants import CIVITAI_BASE_URL

logger = logging.getLogger(__name__)


class UpdateChecker(QObject):
    """追跡モデルの新バージョンをチェックする"""

    check_finished = Signal()
    check_progress = Signal(int, int)  # current, total（件数なので小さい値）
    # 新バージョン検出時にUIスレッドでDB操作するためのシグナル
    new_version_found = Signal(object, str, object, str, str)  # model_id, model_name, version_id, version_name, model_url
    model_checked = Signal(object, object, str)  # model_id, version_id, version_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start_check(self, tracked_models: list[dict], api_key: str = ""):
        """バックグラウンドで更新チェックを開始"""
        if self._running:
            logger.info("更新チェックは既に実行中です")
            return False
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_check,
            args=(tracked_models, api_key),
            daemon=True,
        )
        self._thread.start()
        return True

    def _run_check(self, models: list[dict], api_key: str):
        """全追跡モデルの更新チェック（バックグラウンドスレッド）"""
        try:
            total = len(models)
            logger.info(f"更新チェック開始: {total}モデル")

            client = CivitaiApiClient(api_key)
            try:
                for i, tracked in enumerate(models):
                    if self._stop_event.is_set():
                        logger.info("更新チェックを停止します")
                        break
                    model_id = tracked["model_id"]
                    current_version_id = tracked["latest_version_id"]

                    model_data = client.get_model(model_id)
                    if not model_data:
                        logger.warning(f"モデル情報取得失敗: model_id={model_id}")
                        if not self._stop_event.is_set():
                            self.check_progress.emit(i + 1, total)
                        continue

                    versions = model_data.get("modelVersions", [])
                    if not versions:
                        if not self._stop_event.is_set():
                            self.check_progress.emit(i + 1, total)
                        continue

                    latest = versions[0]
                    latest_version_id = latest.get("id", 0)
                    latest_version_name = latest.get("name", "")

                    if self._stop_event.is_set():
                        break

                    if latest_version_id != current_version_id:
                        # 新バージョン検出→シグナルでUIスレッドに通知
                        model_name = model_data.get("name", "")
                        model_url = f"{CIVITAI_BASE_URL}/models/{model_id}"

                        if not self._stop_event.is_set():
                            self.new_version_found.emit(
                                model_id, model_name,
                                latest_version_id, latest_version_name,
                                model_url,
                            )
                            self.model_checked.emit(
                                model_id, latest_version_id, latest_version_name
                            )
                        logger.info(
                            f"新バージョン検出: {model_name} → {latest_version_name}"
                        )

                    if not self._stop_event.is_set():
                        self.check_progress.emit(i + 1, total)
            finally:
                client.close()

            logger.info("更新チェック完了")

        except Exception as e:
            logger.error(f"更新チェックエラー: {e}")
        finally:
            self._running = False
            self._thread = None
            if not self._stop_event.is_set():
                self.check_finished.emit()

    def shutdown(self, timeout: float = 5.0):
        """更新チェックスレッドを停止待ちする"""
        self._stop_event.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)
