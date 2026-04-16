"""全テーブルのCRUD操作（Databaseインスタンス経由）"""

import uuid
from datetime import datetime, timezone

from civitai_downloader.constants import JobStatus
from civitai_downloader.db.connection import Database


def _now_iso() -> str:
    """現在時刻をISO8601で返す"""
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    """UUID生成"""
    return str(uuid.uuid4())


# ──────────────────────────────────────────
# settings
# ──────────────────────────────────────────

def get_setting(db: Database, key: str, default: str = "") -> str:
    conn = db.get_connection()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", (key,)
    ).fetchone()
    return row["value"] if row else default


def set_setting(db: Database, key: str, value: str):
    conn = db.get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()


# ──────────────────────────────────────────
# folder_presets
# ──────────────────────────────────────────

def get_all_presets(db: Database) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT * FROM folder_presets ORDER BY sort_order, name"
    ).fetchall()
    return [dict(r) for r in rows]


def get_preset(db: Database, preset_id: str) -> dict | None:
    conn = db.get_connection()
    row = conn.execute(
        "SELECT * FROM folder_presets WHERE id = ?", (preset_id,)
    ).fetchone()
    return dict(row) if row else None


def create_preset(db: Database, name: str, path: str = "", sort_order: int = 0) -> str:
    conn = db.get_connection()
    pid = _new_id()
    now = _now_iso()
    conn.execute(
        """INSERT INTO folder_presets (id, name, path, sort_order, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (pid, name, path, sort_order, now),
    )
    conn.commit()
    return pid


def update_preset(db: Database, preset_id: str, **fields):
    conn = db.get_connection()
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [preset_id]
    conn.execute(
        f"UPDATE folder_presets SET {set_clause} WHERE id = ?", values
    )
    conn.commit()


def delete_preset(db: Database, preset_id: str):
    conn = db.get_connection()
    conn.execute("DELETE FROM folder_presets WHERE id = ?", (preset_id,))
    conn.commit()


# ──────────────────────────────────────────
# download_jobs
# ──────────────────────────────────────────

def get_all_jobs(db: Database) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT * FROM download_jobs ORDER BY created_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def get_job(db: Database, job_id: str) -> dict | None:
    conn = db.get_connection()
    row = conn.execute(
        "SELECT * FROM download_jobs WHERE id = ?", (job_id,)
    ).fetchone()
    return dict(row) if row else None


def insert_job(
    db: Database,
    filename: str,
    download_url: str = "",
    page_url: str = "",
    model_version_id: int | None = None,
    preset_id: str | None = None,
    status: str = JobStatus.PENDING.value,
) -> str:
    conn = db.get_connection()
    jid = _new_id()
    now = _now_iso()
    conn.execute(
        """INSERT INTO download_jobs
           (id, model_version_id, filename, download_url, page_url,
            status, preset_id, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (jid, model_version_id, filename, download_url, page_url,
         status, preset_id, now, now),
    )
    conn.commit()
    return jid


def update_job(db: Database, job_id: str, **fields):
    """ジョブの任意のフィールドを更新"""
    conn = db.get_connection()
    if not fields:
        return
    fields["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [job_id]
    conn.execute(
        f"UPDATE download_jobs SET {set_clause} WHERE id = ?", values
    )
    conn.commit()


def get_jobs_by_status(db: Database, status: str) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT * FROM download_jobs WHERE status = ? ORDER BY created_at ASC",
        (status,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_next_job_by_status(db: Database, status: str) -> dict | None:
    conn = db.get_connection()
    row = conn.execute(
        """SELECT * FROM download_jobs
           WHERE status = ?
           ORDER BY created_at ASC
           LIMIT 1""",
        (status,),
    ).fetchone()
    return dict(row) if row else None


def get_active_job_count(db: Database) -> int:
    conn = db.get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM download_jobs WHERE status IN (?, ?)",
        (JobStatus.DOWNLOADING.value, JobStatus.QUEUED.value),
    ).fetchone()
    return row["cnt"]


def apply_recommendation(
    db: Database,
    job_id: str,
    preset_id: str,
    model_id: int,
    model_name: str,
    model_type: str,
):
    """推奨プリセットをジョブに適用（PENDING/PENDING_UNRESOLVEDの場合のみ）"""
    conn = db.get_connection()
    conn.execute(
        """UPDATE download_jobs
           SET preset_id = ?, model_id = ?, model_name = ?,
               model_type = ?, updated_at = ?
           WHERE id = ? AND status IN (?, ?)""",
        (preset_id, model_id, model_name, model_type, _now_iso(),
         job_id, JobStatus.PENDING.value, JobStatus.PENDING_UNRESOLVED.value),
    )
    conn.commit()


# ──────────────────────────────────────────
# tracked_models
# ──────────────────────────────────────────

def get_all_tracked_models(db: Database) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute("SELECT * FROM tracked_models").fetchall()
    return [dict(r) for r in rows]


def register_tracking(
    db: Database,
    model_id: int,
    model_name: str,
    version_id: int,
    version_name: str,
    model_type: str,
):
    conn = db.get_connection()
    now = _now_iso()
    conn.execute(
        """INSERT INTO tracked_models
           (model_id, model_name, latest_version_id,
            latest_version_name, model_type, checked_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(model_id) DO UPDATE SET
               latest_version_id = MAX(excluded.latest_version_id, latest_version_id),
               latest_version_name = CASE
                   WHEN excluded.latest_version_id > latest_version_id
                   THEN excluded.latest_version_name
                   ELSE latest_version_name END,
               checked_at = excluded.checked_at""",
        (model_id, model_name, version_id, version_name, model_type, now),
    )
    conn.commit()


def update_tracked_model(
    db: Database,
    model_id: int,
    latest_version_id: int,
    latest_version_name: str,
):
    conn = db.get_connection()
    conn.execute(
        """UPDATE tracked_models
           SET latest_version_id = ?, latest_version_name = ?, checked_at = ?
           WHERE model_id = ?""",
        (latest_version_id, latest_version_name, _now_iso(), model_id),
    )
    conn.commit()


# ──────────────────────────────────────────
# notifications
# ──────────────────────────────────────────

def get_all_notifications(db: Database) -> list[dict]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT * FROM notifications ORDER BY detected_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def get_unread_notification_count(db: Database) -> int:
    conn = db.get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM notifications WHERE is_read = 0"
    ).fetchone()
    return row["cnt"]


def create_notification(
    db: Database,
    model_id: int,
    model_name: str,
    new_version_id: int,
    new_version_name: str,
    model_url: str,
) -> str:
    conn = db.get_connection()
    nid = _new_id()
    now = _now_iso()
    conn.execute(
        """INSERT INTO notifications
           (id, model_id, model_name, new_version_id,
            new_version_name, model_url, detected_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (nid, model_id, model_name, new_version_id,
         new_version_name, model_url, now),
    )
    conn.commit()
    prune_notifications(db)
    return nid


def mark_notification_read(db: Database, notification_id: str):
    conn = db.get_connection()
    conn.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ?",
        (notification_id,),
    )
    conn.commit()


def mark_all_notifications_read(db: Database):
    conn = db.get_connection()
    conn.execute("UPDATE notifications SET is_read = 1")
    conn.commit()


def delete_all_notifications(db: Database):
    """通知履歴をすべて削除する"""
    conn = db.get_connection()
    conn.execute("DELETE FROM notifications")
    conn.commit()


def prune_notifications(db: Database, keep_latest: int = 100):
    """通知履歴を最新 keep_latest 件だけ残す"""
    conn = db.get_connection()
    conn.execute(
        """DELETE FROM notifications
           WHERE id NOT IN (
               SELECT id FROM notifications
               ORDER BY detected_at DESC
               LIMIT ?
           )""",
        (keep_latest,),
    )
    conn.commit()
