"""一括検索バックグラウンドワーカー"""

import logging

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from civitai_downloader.core.civitai_api import CivitaiApiClient

logger = logging.getLogger(__name__)


class _Signals(QObject):
    finished = Signal(list, dict)  # items, metadata
    error = Signal(str)


class BatchSearchWorker(QRunnable):
    """Civitai APIでモデルを検索するバックグラウンドタスク"""

    def __init__(
        self,
        api_key: str = "",
        username: str = "",
        query: str = "",
        tag: str = "",
        model_type: str = "",
        page: int = 1,
        limit: int = 20,
    ):
        super().__init__()
        self.signals = _Signals()
        self._api_key = api_key
        self._username = username
        self._query = query
        self._tag = tag
        self._model_type = model_type
        self._page = page
        self._limit = limit

    @Slot()
    def run(self):
        try:
            with CivitaiApiClient(api_key=self._api_key) as client:
                result = client.search_models(
                    username=self._username,
                    query=self._query,
                    tag=self._tag,
                    model_type=self._model_type,
                    page=self._page,
                    limit=self._limit,
                )

            if not result:
                self.signals.error.emit("APIから結果を取得できませんでした")
                return

            items = result.get("items", [])
            metadata = result.get("metadata", {})

            # 必要な情報だけ抽出
            models = []
            for item in items:
                model_id = item.get("id", 0)
                name = item.get("name", f"Model {model_id}")
                model_type = item.get("type", "")
                creator = item.get("creator", {}).get("username", "")
                models.append({
                    "model_id": model_id,
                    "name": name,
                    "type": model_type,
                    "creator": creator,
                })

            self.signals.finished.emit(models, metadata)

        except Exception as e:
            logger.error(f"一括検索エラー: {e}")
            self.signals.error.emit(str(e))
