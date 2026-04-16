"""Civitai REST APIクライアント（クラスベース）"""

import logging
import time

import httpx

from civitai_downloader.constants import (
    CIVITAI_API_BASE,
    CIVITAI_BASE_URL,
    APP_USER_AGENT,
    API_RATE_LIMIT_INTERVAL,
    DOWNLOAD_TIMEOUT,
)

logger = logging.getLogger(__name__)


class CivitaiApiClient:
    """Civitai APIクライアント（スレッドごとにインスタンスを生成する想定）"""

    def __init__(self, api_key: str = ""):
        self._api_key = api_key
        self._last_call: float = 0.0
        self._client = httpx.Client(
            headers=self._make_headers(),
            timeout=DOWNLOAD_TIMEOUT,
            follow_redirects=True,
        )

    def _make_headers(self) -> dict:
        """共通ヘッダーを生成"""
        headers = {"User-Agent": APP_USER_AGENT}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _rate_limit(self):
        """API呼び出し間に最低1秒のインターバルを確保"""
        now = time.monotonic()
        wait = max(0, API_RATE_LIMIT_INTERVAL - (now - self._last_call))
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def get_model_version(self, version_id: int) -> dict | None:
        """
        モデルバージョン情報を取得する。
        GET /api/v1/model-versions/{modelVersionId}
        """
        self._rate_limit()
        url = f"{CIVITAI_API_BASE}/model-versions/{version_id}"

        try:
            resp = self._client.get(url)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(
                f"バージョン情報取得失敗: HTTP {resp.status_code} (version_id={version_id})"
            )
            return None
        except Exception as e:
            logger.error(f"バージョン情報取得エラー: {e}")
            return None

    def get_model(self, model_id: int) -> dict | None:
        """
        モデル情報を取得する。
        GET /api/v1/models/{modelId}
        """
        self._rate_limit()
        url = f"{CIVITAI_API_BASE}/models/{model_id}"

        try:
            resp = self._client.get(url)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(
                f"モデル情報取得失敗: HTTP {resp.status_code} (model_id={model_id})"
            )
            return None
        except Exception as e:
            logger.error(f"モデル情報取得エラー: {e}")
            return None

    def search_models(
        self,
        username: str = "",
        query: str = "",
        tag: str = "",
        model_type: str = "",
        page: int = 1,
        limit: int = 20,
    ) -> dict | None:
        """
        モデル一覧を検索する。
        GET /api/v1/models
        """
        self._rate_limit()
        params: dict = {"page": page, "limit": limit}
        if username:
            params["username"] = username
        if query:
            params["query"] = query
        if tag:
            params["tag"] = tag
        if model_type:
            params["types"] = model_type

        url = f"{CIVITAI_API_BASE}/models"
        try:
            resp = self._client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(f"モデル検索失敗: HTTP {resp.status_code}")
            return None
        except Exception as e:
            logger.error(f"モデル検索エラー: {e}")
            return None

    def close(self):
        """クライアントを閉じる"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def get_download_url(version_id: int, api_key: str = "") -> str:
    """ダウンロードURLを構築"""
    url = f"{CIVITAI_BASE_URL}/api/download/models/{version_id}"
    if api_key:
        url += f"?token={api_key}"
    return url


def extract_model_info_from_version(version_data: dict) -> dict:
    """
    バージョンAPIレスポンスからモデル情報を抽出。

    Returns:
        {"model_id": int, "model_name": str, "model_type": str,
         "version_name": str, "download_url": str}
    """
    model_id = version_data.get("modelId", 0)
    model_name = version_data.get("model", {}).get("name", "")
    model_type = version_data.get("model", {}).get("type", "")
    version_name = version_data.get("name", "")

    # ダウンロードURL・ファイル名（files配列の先頭）
    download_url = ""
    filename = ""
    files = version_data.get("files", [])
    if files:
        download_url = files[0].get("downloadUrl", "")
        filename = files[0].get("name", "")

    return {
        "model_id": model_id,
        "model_name": model_name,
        "model_type": model_type,
        "version_name": version_name,
        "download_url": download_url,
        "filename": filename,
    }
