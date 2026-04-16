"""テーブル定義・マイグレーション"""

from civitai_downloader.db.connection import Database

# 旧テーブル（リメイクのため削除対象）
_OLD_TABLES = ["bundles"]

# テーブル作成SQL
_TABLES = [
    # settings テーブル
    """
    CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    # folder_presets テーブル（旧bundlesの代替）
    """
    CREATE TABLE IF NOT EXISTS folder_presets (
        id         TEXT PRIMARY KEY,
        name       TEXT NOT NULL,
        path       TEXT DEFAULT '',
        sort_order INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """,
    # download_jobs テーブル
    """
    CREATE TABLE IF NOT EXISTS download_jobs (
        id                TEXT PRIMARY KEY,
        model_version_id  INTEGER,
        model_id          INTEGER,
        model_name        TEXT DEFAULT '',
        model_type        TEXT DEFAULT '',
        filename          TEXT NOT NULL,
        download_url      TEXT DEFAULT '',
        page_url          TEXT DEFAULT '',
        status            TEXT NOT NULL DEFAULT 'pending',
        preset_id         TEXT,
        dest_path         TEXT DEFAULT '',
        temp_path         TEXT DEFAULT '',
        bytes_downloaded  INTEGER DEFAULT 0,
        bytes_total       INTEGER DEFAULT 0,
        error_message     TEXT DEFAULT '',
        created_at        TEXT NOT NULL,
        updated_at        TEXT NOT NULL,
        FOREIGN KEY (preset_id) REFERENCES folder_presets(id) ON DELETE SET NULL
    )
    """,
    # download_jobsのステータスインデックス
    """
    CREATE INDEX IF NOT EXISTS idx_jobs_status ON download_jobs(status)
    """,
    # tracked_models テーブル
    """
    CREATE TABLE IF NOT EXISTS tracked_models (
        model_id            INTEGER PRIMARY KEY,
        model_name          TEXT DEFAULT '',
        latest_version_id   INTEGER NOT NULL,
        latest_version_name TEXT DEFAULT '',
        model_type          TEXT DEFAULT '',
        checked_at          TEXT NOT NULL
    )
    """,
    # notifications テーブル
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id                TEXT PRIMARY KEY,
        model_id          INTEGER NOT NULL,
        model_name        TEXT DEFAULT '',
        new_version_id    INTEGER NOT NULL,
        new_version_name  TEXT DEFAULT '',
        model_url         TEXT NOT NULL,
        is_read           INTEGER NOT NULL DEFAULT 0,
        detected_at       TEXT NOT NULL,
        FOREIGN KEY (model_id) REFERENCES tracked_models(model_id)
    )
    """,
]

# 設定の初期値
_DEFAULT_SETTINGS = {
    "api_key": "",
    "max_concurrent": "3",
    "last_url": "https://civitai.com/models",
    "log_max_bytes": "10485760",
    "dir_temp": "",
    "dir_unsorted": "",
    "theme": "dark",
}

_DOWNLOAD_JOB_COLUMNS = {
    "model_version_id": "ALTER TABLE download_jobs ADD COLUMN model_version_id INTEGER",
    "model_id": "ALTER TABLE download_jobs ADD COLUMN model_id INTEGER",
    "model_name": "ALTER TABLE download_jobs ADD COLUMN model_name TEXT DEFAULT ''",
    "model_type": "ALTER TABLE download_jobs ADD COLUMN model_type TEXT DEFAULT ''",
    "download_url": "ALTER TABLE download_jobs ADD COLUMN download_url TEXT DEFAULT ''",
    "page_url": "ALTER TABLE download_jobs ADD COLUMN page_url TEXT DEFAULT ''",
    "preset_id": "ALTER TABLE download_jobs ADD COLUMN preset_id TEXT",
    "dest_path": "ALTER TABLE download_jobs ADD COLUMN dest_path TEXT DEFAULT ''",
    "temp_path": "ALTER TABLE download_jobs ADD COLUMN temp_path TEXT DEFAULT ''",
    "bytes_downloaded": "ALTER TABLE download_jobs ADD COLUMN bytes_downloaded INTEGER DEFAULT 0",
    "bytes_total": "ALTER TABLE download_jobs ADD COLUMN bytes_total INTEGER DEFAULT 0",
    "error_message": "ALTER TABLE download_jobs ADD COLUMN error_message TEXT DEFAULT ''",
    "updated_at": "ALTER TABLE download_jobs ADD COLUMN updated_at TEXT DEFAULT ''",
}


def _get_existing_columns(cursor, table_name: str) -> set[str]:
    return {
        row[1]
        for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    }


def _ensure_download_jobs_columns(cursor):
    """既存のdownload_jobsへ不足列を後方互換で追加する"""
    existing_columns = _get_existing_columns(cursor, "download_jobs")
    for column_name, sql in _DOWNLOAD_JOB_COLUMNS.items():
        if column_name not in existing_columns:
            cursor.execute(sql)


def initialize_database(database: Database):
    """全テーブルを作成し、初期値を挿入する"""
    conn = database.get_connection()
    cursor = conn.cursor()

    # 旧テーブルの検出と削除（リメイクのため）
    existing = {
        row[0]
        for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    for old_table in _OLD_TABLES:
        if old_table in existing:
            cursor.execute(f"DROP TABLE IF EXISTS {old_table}")

    # テーブル作成
    for sql in _TABLES:
        cursor.execute(sql)

    # 既存DBの軽量マイグレーション
    if "download_jobs" in existing:
        _ensure_download_jobs_columns(cursor)

    # 設定初期値の挿入（存在しない場合のみ）
    for key, value in _DEFAULT_SETTINGS.items():
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    # 不要な旧設定キーの削除
    cursor.execute("DELETE FROM settings WHERE key = 'default_bundle_id'")

    conn.commit()
