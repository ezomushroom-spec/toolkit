"""version_id補完タスク（ページURLからバージョンID確定）"""

import logging

from PySide6.QtCore import QObject, Signal, QRunnable

from civitai_downloader.core.civitai_api import CivitaiApiClient
from civitai_downloader.core.url_parser import (
    extract_model_id_from_page_url,
    extract_version_id_from_page_url,
)

logger = logging.getLogger(__name__)


class ResolveSignals(QObject):
    """VersionResolveTask用シグナル"""
    resolved = Signal(str, object, str, object, str, str)  # job_id, version_id, api_type, model_id, model_name, filename
    failed = Signal(str, str)  # job_id, error_message


class VersionResolveTask(QRunnable):
    """ページURLからmodelId抽出→API→version_id確定"""

    def __init__(
        self,
        job_id: str,
        page_url: str,
        api_key: str,
    ):
        super().__init__()
        self.signals = ResolveSignals()
        self._job_id = job_id
        self._page_url = page_url
        self._api_key = api_key
        self.setAutoDelete(True)

    def run(self):
        try:
            # ページURLからバージョンIDが直接取れるか試す
            version_id = extract_version_id_from_page_url(self._page_url)

            if version_id:
                # バージョンIDからモデル情報を取得
                client = CivitaiApiClient(self._api_key)
                try:
                    version_data = client.get_model_version(version_id)
                    if version_data:
                        from civitai_downloader.core.civitai_api import extract_model_info_from_version
                        info = extract_model_info_from_version(version_data)
                        self.signals.resolved.emit(
                            self._job_id,
                            version_id,
                            info.get("model_type", ""),
                            info.get("model_id", 0),
                            info.get("model_name", ""),
                            info.get("filename", ""),
                        )
                        return
                finally:
                    client.close()

            # ページURLからモデルIDを抽出
            model_id = extract_model_id_from_page_url(self._page_url)
            if not model_id:
                message = "モデルページURLからモデルIDを抽出できません"
                logger.warning(f"解決失敗: {message} [{self._job_id}]")
                self.signals.failed.emit(self._job_id, message)
                return

            # モデルIDから最新バージョンを取得
            client = CivitaiApiClient(self._api_key)
            try:
                model_data = client.get_model(model_id)
                if not model_data:
                    message = f"モデル情報を取得できません (model_id={model_id})"
                    logger.warning(f"解決失敗: {message} [{self._job_id}]")
                    self.signals.failed.emit(self._job_id, message)
                    return

                versions = model_data.get("modelVersions", [])
                if not versions:
                    message = f"利用可能なバージョンがありません (model_id={model_id})"
                    logger.warning(f"解決失敗: {message} [{self._job_id}]")
                    self.signals.failed.emit(self._job_id, message)
                    return

                latest = versions[0]
                resolved_version_id = latest.get("id", 0)
                model_name = model_data.get("name", "")
                model_type = model_data.get("type", "")

                # ファイル名を取得（バージョンのfiles配列の先頭）
                filename = ""
                latest_files = latest.get("files", [])
                if latest_files:
                    filename = latest_files[0].get("name", "")

                if resolved_version_id:
                    self.signals.resolved.emit(
                        self._job_id,
                        resolved_version_id,
                        model_type,
                        model_id,
                        model_name,
                        filename,
                    )
                    logger.info(
                        f"バージョン解決完了: {model_name} → version_id={resolved_version_id}"
                    )
            finally:
                client.close()

        except Exception as e:
            logger.error(f"バージョン解決タスクエラー [{self._job_id}]: {e}")
            self.signals.failed.emit(self._job_id, str(e))
