"""
Post Manager - 共通スキーマ定義
Task / Settings / 実行状態の語彙を Python 側で一元化する。
"""

from typing import Dict, Any, Iterable, Mapping, Tuple

from pydantic import BaseModel


TASK_FIELD_DEFAULTS: Dict[str, str] = {
    "target_folder": "",
    "title": "",
    "caption_pixiv": "",
    "caption_patreon": "",
    "caption_discord": "",
    "tags": "",
    "schedule": "",
    "zip_password": "",
    "patreon_tier": "",
    "discord_channel": "",
    "zip_url": "",
}
TASK_FIELDS: Tuple[str, ...] = tuple(TASK_FIELD_DEFAULTS.keys())

DERIVED_TASK_FIELDS: Tuple[str, ...] = ("count", "image_count")

SETTINGS_FIELD_DEFAULTS: Dict[str, str] = {
    "mega_email": "",
    "mega_password": "",
    "discord_webhook_url": "",
    "template_pixiv": "{caption_pixiv}",
    "template_patreon": "{caption_patreon}",
    "template_discord": "{caption_discord}",
}
SETTINGS_FIELDS: Tuple[str, ...] = tuple(SETTINGS_FIELD_DEFAULTS.keys())

RUN_STEPS: Tuple[str, ...] = ("clean", "mega", "pixiv", "patreon", "discord")
CLI_ALL_STEP = "all"
WEB_RUN_ALL_STEPS: Tuple[str, ...] = ("clean", "mega", "discord")

PROCESS_STATUS_RUNNING = "running"
PROCESS_STATUS_COMPLETED = "completed"
PROCESS_STATUS_TERMINATED = "terminated"
PROCESS_STATUS_FAILED = "failed"
PROCESS_STATUSES: Tuple[str, ...] = (
    PROCESS_STATUS_RUNNING,
    PROCESS_STATUS_COMPLETED,
    PROCESS_STATUS_TERMINATED,
    PROCESS_STATUS_FAILED,
)

EXISTING_FILE_POLICY_PROMPT = "prompt"
EXISTING_FILE_POLICY_SKIP = "skip"
EXISTING_FILE_POLICY_OVERWRITE = "overwrite"
EXISTING_FILE_POLICIES: Tuple[str, ...] = (
    EXISTING_FILE_POLICY_PROMPT,
    EXISTING_FILE_POLICY_SKIP,
    EXISTING_FILE_POLICY_OVERWRITE,
)


class TaskModel(BaseModel):
    """投稿タスクの永続項目"""

    target_folder: str = ""
    title: str = ""
    caption_pixiv: str = ""
    caption_patreon: str = ""
    caption_discord: str = ""
    tags: str = ""
    schedule: str = ""
    zip_password: str = ""
    patreon_tier: str = ""
    discord_channel: str = ""
    zip_url: str = ""


class SettingsModel(BaseModel):
    """設定ファイルに保存される項目"""

    mega_email: str = ""
    mega_password: str = ""
    discord_webhook_url: str = ""
    template_pixiv: str = "{caption_pixiv}"
    template_patreon: str = "{caption_patreon}"
    template_discord: str = "{caption_discord}"


class RunStepRequest(BaseModel):
    """ステップ実行リクエスト"""

    step: str


def hydrate_task_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """
    CSV/API 由来の task を既知フィールドで補完しつつ、未知フィールドは保持する。
    """
    hydrated: Dict[str, Any] = dict(TASK_FIELD_DEFAULTS)
    extras = dict(record)
    hydrated.update(extras)
    return hydrated


def hydrate_task_records(records: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    """task 配列を共通フィールドで補完する。"""
    return [hydrate_task_record(record) for record in records]


def default_settings_dict() -> Dict[str, str]:
    """Settings の初期値を新しい dict で返す。"""
    return dict(SETTINGS_FIELD_DEFAULTS)
