"""推奨プリセット機能"""

import logging

from PySide6.QtCore import QObject, Signal, QRunnable

from civitai_downloader.constants import RECOMMEND_KEYWORDS
from civitai_downloader.core.civitai_api import CivitaiApiClient, extract_model_info_from_version

logger = logging.getLogger(__name__)


def recommend_preset(api_type: str, presets: list[dict]) -> str | None:
    """
    モデルタイプに基づいて推奨プリセットを決定する。

    Args:
        api_type: CivitaiのモデルタイプAPI値（例: "Checkpoint", "LORA"）
        presets: folder_presetsのリスト

    Returns:
        推奨preset_id。該当なしの場合はNone。
    """
    keywords = RECOMMEND_KEYWORDS.get(api_type, [])
    if not keywords or not presets:
        return None

    for preset in presets:
        name_lower = preset.get("name", "").lower()
        for kw in keywords:
            if kw in name_lower:
                return preset["id"]

    return None


class RecommendSignals(QObject):
    """RecommendTask用シグナル"""
    done = Signal(str, str, str, object, str)  # job_id, preset_id, api_type, model_id, model_name


class RecommendTask(QRunnable):
    """API呼び出し→推奨プリセット決定→シグナルで結果返却"""

    def __init__(
        self,
        job_id: str,
        version_id: int,
        api_key: str,
        presets: list[dict],
    ):
        super().__init__()
        self.signals = RecommendSignals()
        self._job_id = job_id
        self._version_id = version_id
        self._api_key = api_key
        self._presets = presets
        self.setAutoDelete(True)

    def run(self):
        try:
            client = CivitaiApiClient(self._api_key)
            try:
                version_data = client.get_model_version(self._version_id)
                if not version_data:
                    logger.warning(
                        f"推奨プリセット: バージョン情報取得失敗 (version_id={self._version_id})"
                    )
                    return

                info = extract_model_info_from_version(version_data)
                api_type = info.get("model_type", "")
                model_id = info.get("model_id", 0)
                model_name = info.get("model_name", "")

                preset_id = recommend_preset(api_type, self._presets)

                self.signals.done.emit(
                    self._job_id,
                    preset_id or "",
                    api_type,
                    model_id,
                    model_name,
                )
            finally:
                client.close()

        except Exception as e:
            logger.error(f"推奨プリセットタスクエラー [{self._job_id}]: {e}")
