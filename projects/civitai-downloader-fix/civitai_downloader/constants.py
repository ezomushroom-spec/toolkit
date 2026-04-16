"""定数・Enum定義"""

from enum import Enum

# アプリ情報
APP_NAME = "CivitaiModelDownloader"
APP_VERSION = "3.1"
APP_USER_AGENT = f"{APP_NAME}/{APP_VERSION}"

# デフォルト設定値
DEFAULT_MAX_CONCURRENT = 3
DEFAULT_START_URL = "https://civitai.com/models"
DEFAULT_LOG_MAX_BYTES = 10_485_760  # 10MB

# Civitai API
CIVITAI_BASE_URL = "https://civitai.com"
CIVITAI_API_BASE = f"{CIVITAI_BASE_URL}/api/v1"
API_RATE_LIMIT_INTERVAL = 1.0  # 秒

# ダウンロード設定
DOWNLOAD_CHUNK_SIZE = 131072  # 128KB
DOWNLOAD_TIMEOUT = 30.0
MAX_RETRY_COUNT = 3
RETRY_WAIT_429 = 60  # 秒
RETRY_WAIT_5XX = 30  # 秒


class JobStatus(str, Enum):
    """ダウンロードジョブの状態"""
    PENDING_UNRESOLVED = "pending_unresolved"
    PENDING = "pending"
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# 状態の表示名マッピング
JOB_STATUS_DISPLAY = {
    JobStatus.PENDING_UNRESOLVED.value: "ID未確定",
    JobStatus.PENDING.value: "待機",
    JobStatus.QUEUED.value: "開始待ち",
    JobStatus.DOWNLOADING.value: "DL中",
    JobStatus.COMPLETED.value: "完了",
    JobStatus.FAILED.value: "失敗",
    JobStatus.SKIPPED.value: "スキップ",
}

# 推奨プリセットキーワードマッピング
# Civitai APIのモデルタイプ → 推奨プリセット名のキーワード
class AppTheme(str, Enum):
    """アプリケーションテーマ"""
    DARK = "dark"
    LIGHT = "light"


RECOMMEND_KEYWORDS: dict[str, list[str]] = {
    "Checkpoint": ["checkpoint", "model", "sd"],
    "TextualInversion": ["embedding", "textual", "ti"],
    "LORA": ["lora"],
    "LoCon": ["lora", "locon"],
    "VAE": ["vae"],
    "Controlnet": ["controlnet", "control"],
    "Upscaler": ["upscaler", "upscale", "esrgan"],
    "Hypernetwork": ["hypernetwork", "embedding"],
    "AestheticGradient": ["aesthetic", "embedding"],
    "Poses": ["pose", "controlnet"],
    "Wildcards": ["wildcard"],
    "Workflows": ["workflow"],
    "MotionModule": ["motion", "animate"],
}
