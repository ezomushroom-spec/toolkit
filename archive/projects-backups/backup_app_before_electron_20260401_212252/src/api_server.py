"""
Post Manager - FastAPI サーバー
モダンなWeb UIでPost Managerを操作するためのAPIサーバー
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# パス設定
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
WEB_DIR = BASE_DIR / "web"
CSV_PATH = BASE_DIR / "data" / "posts.csv"

sys.path.insert(0, str(SRC_DIR))

# 既存モジュールのインポート
from app_schema import (
    EXISTING_FILE_POLICY_SKIP,
    PROCESS_STATUS_COMPLETED,
    PROCESS_STATUS_FAILED,
    PROCESS_STATUS_RUNNING,
    PROCESS_STATUS_TERMINATED,
    RUN_STEPS,
    SettingsModel,
    TaskModel,
    WEB_RUN_ALL_STEPS,
    default_settings_dict,
)
import manager
import pixiv_tag_learning
import pixiv_tag_support

# ==============================
# ログ管理 (WebSocket用)
# ==============================

class LogManager:
    """WebSocketクライアントへのログブロードキャスト"""
    def __init__(self):
        self.connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for conn in self.connections:
            try:
                await conn.send_text(message)
            except:
                pass

log_manager = LogManager()


def safe_console_text(value) -> str:
    """Windows コンソールでも崩れにくい ASCII 安全文字列へ寄せる"""
    text = str(value)
    try:
        return text.encode("ascii", errors="backslashreplace").decode("ascii")
    except Exception:
        return repr(text)


def build_response(success: bool, message: str = "", **payload) -> dict:
    """UI向けの共通レスポンスを返す"""
    response = {
        "success": success,
        "message": message,
    }
    response.update(payload)
    if "runtime" not in response:
        response["runtime"] = get_runtime_status()
    return response


def get_tasks_payload(tasks: Optional[list] = None) -> dict:
    """最新タスク一覧をレスポンスへ載せる"""
    current_tasks = tasks if tasks is not None else manager.load_tasks()
    return {
        "tasks": current_tasks,
        "count": len(current_tasks),
    }


def build_learning_payload(tags_value: str) -> dict:
    """Pixivタグ学習結果を UI へ返しやすい payload に整える"""
    result = pixiv_tag_learning.record_saved_tags(tags_value)
    return {
        "learning_updated": result.get("updated", False),
        "learning_warning": result.get("warning", ""),
        "learning_recovered": result.get("recovered", False),
    }


def ensure_not_busy():
    """実行中は破壊的変更 API を拒否する"""
    if current_execution["active"]:
        raise HTTPException(
            status_code=409,
            detail=f"Processing in progress: {current_execution['step']}"
        )


# ==============================
# FastAPI アプリケーション
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    print("Post Manager API Server starting...")
    print(f"Base directory: {safe_console_text(BASE_DIR)}")
    yield
    # 終了時処理
    print("Server shutting down...")

app = FastAPI(
    title="Post Manager API",
    description="Pixiv/Patreon/Discord投稿管理API",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTPエラーも UI が扱いやすい形へそろえる"""
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(False, message=message, detail=exc.detail),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """予期しない例外のレスポンスを統一する"""
    print(f"Unhandled API error: {exc}", file=sys.stderr)
    return JSONResponse(
        status_code=500,
        content=build_response(
            False,
            message="サーバー内部でエラーが発生しました。ログを確認してから再試行してください。",
        ),
    )


# ==============================
# API エンドポイント
# ==============================

@app.get("/api/tasks")
async def get_tasks():
    """タスク一覧を取得"""
    return build_response(True, "Tasks loaded", **get_tasks_payload())


@app.post("/api/tasks")
async def add_task(task: TaskModel):
    """タスクを追加"""
    ensure_not_busy()
    tasks = manager.load_tasks()
    saved_task = task.dict()
    tasks.append(saved_task)
    manager.save_tasks(tasks)
    return build_response(
        True,
        "Task added",
        task=saved_task,
        **get_tasks_payload(tasks),
        **build_learning_payload(saved_task.get("tags", "")),
    )


@app.put("/api/tasks/{index}")
async def update_task(index: int, task: TaskModel):
    """タスクを更新"""
    ensure_not_busy()
    tasks = manager.load_tasks()
    if 0 <= index < len(tasks):
        updated_task = task.dict()
        tasks[index] = updated_task
        manager.save_tasks(tasks)
        return build_response(
            True,
            "Task updated",
            index=index,
            task=updated_task,
            **get_tasks_payload(tasks),
            **build_learning_payload(updated_task.get("tags", "")),
        )
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/api/tasks/{index}")
async def delete_task(index: int):
    """タスクを削除"""
    ensure_not_busy()
    tasks = manager.load_tasks()
    if 0 <= index < len(tasks):
        deleted = tasks.pop(index)
        manager.save_tasks(tasks)
        return build_response(
            True,
            "Task deleted",
            index=index,
            deleted=deleted,
            **get_tasks_payload(tasks),
        )
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/api/run/{step}")
async def run_step(step: str):
    """ステップを実行"""
    if current_execution["active"]:
        return build_response(
            False,
            f"別の処理が進行中です: {current_execution['step']}",
            step=step,
        )

    tasks = manager.load_tasks()
    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks found")
    
    result = {"step": step, "success": False, "message": ""}
    
    try:
        if step == RUN_STEPS[0]:
            set_current_execution(step=step, kind="sync", message="Clean & Zip を実行中です。")
            manager.run_clean(tasks, existing_zip_policy=EXISTING_FILE_POLICY_SKIP)
            result["success"] = True
            result["message"] = "Clean & Zip completed (existing zip: skip)"
        elif step == RUN_STEPS[1]:
            set_current_execution(step=step, kind="sync", message="MEGA Upload を実行中です。")
            manager.run_mega(tasks, existing_file_policy=EXISTING_FILE_POLICY_SKIP)
            result["success"] = True
            result["message"] = "MEGA upload completed (existing file: skip)"
        elif step == RUN_STEPS[4]:
            set_current_execution(step=step, kind="sync", message="Discord 通知を送信中です。")
            manager.run_discord(tasks)
            result["success"] = True
            result["message"] = "Discord notification sent"
        elif step in RUN_STEPS[2:4]:
            # サブプロセスで実行
            process_result = await start_browser_process(step)
            result["success"] = process_result["success"]
            result["message"] = process_result["message"]
            result["process_id"] = process_result.get("process_id")
            result["requires_user_action"] = process_result.get("requires_user_action", False)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown step: {step}")
    except Exception as e:
        result["message"] = str(e)
    finally:
        if step in (RUN_STEPS[0], RUN_STEPS[1], RUN_STEPS[4]) and current_execution["step"] == step:
            clear_current_execution(
                message=result["message"] or "処理が終了しました。",
                message_level="success" if result["success"] else "error",
            )
    
    return build_response(
        result["success"],
        result["message"],
        step=step,
        process_id=result.get("process_id"),
        requires_user_action=result.get("requires_user_action", False),
    )


# ==============================
# ブラウザプロセス管理
# ==============================

import subprocess
import threading
import uuid
import time

# 実行中のプロセスを追跡
running_processes = {}
current_execution = {
    "active": False,
    "step": "",
    "kind": "",
    "message": "",
    "message_level": "info",
    "process_id": None,
    "started_at": None,
}


def serialize_process_info(process_id: str, info: dict) -> dict:
    """UI向けのプロセス状態を整形する"""
    return {
        "process_id": process_id,
        "step": info["step"],
        "status": info["status"],
        "started_at": info.get("started_at"),
        "finished_at": info.get("finished_at"),
        "return_code": info.get("return_code"),
    }


def get_runtime_status() -> dict:
    """現在の実行状態を返す"""
    active_processes = [
        serialize_process_info(pid, info)
        for pid, info in running_processes.items()
        if info["status"] == PROCESS_STATUS_RUNNING
    ]
    recent_processes = [
        serialize_process_info(pid, info)
        for pid, info in running_processes.items()
        if info["status"] != PROCESS_STATUS_RUNNING
    ]
    recent_processes.sort(key=lambda item: item.get("finished_at") or 0, reverse=True)
    execution = dict(current_execution)
    execution["status"] = PROCESS_STATUS_RUNNING if current_execution["active"] else "idle"
    execution["elapsed_seconds"] = (
        round(max(time.time() - current_execution["started_at"], 0), 1)
        if current_execution["started_at"]
        else 0
    )
    return {
        "execution": execution,
        "active_processes": active_processes,
        "recent_processes": recent_processes[:5],
        "web_run_all_steps": list(WEB_RUN_ALL_STEPS),
    }


def set_current_execution(
    step: str,
    kind: str,
    message: str = "",
    process_id: str | None = None,
    message_level: str = "info",
):
    current_execution["active"] = True
    current_execution["step"] = step
    current_execution["kind"] = kind
    current_execution["message"] = message
    current_execution["message_level"] = message_level
    current_execution["process_id"] = process_id
    current_execution["started_at"] = time.time()


def clear_current_execution(message: str = "", message_level: str = "info"):
    current_execution["active"] = False
    current_execution["step"] = ""
    current_execution["kind"] = ""
    current_execution["message"] = message
    current_execution["message_level"] = message_level
    current_execution["process_id"] = None
    current_execution["started_at"] = None

async def start_browser_process(step: str):
    """ブラウザ投稿プロセスをサブプロセスで開始"""
    process_id = str(uuid.uuid4())[:8]
    
    # コマンド構築
    if step == RUN_STEPS[2]:
        cmd = [sys.executable, str(SRC_DIR / "manager.py"), "--pixiv"]
    elif step == RUN_STEPS[3]:
        cmd = [sys.executable, str(SRC_DIR / "manager.py"), "--patreon"]
    else:
        return {"success": False, "message": f"Unknown step: {step}"}
    
    try:
        # サブプロセスを起動（新しいコンソールウィンドウで対話的に実行）
        # 注意: stdout/stderrをPIPEにすると対話入力ができなくなるため設定しない
        process = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=os.environ.copy()  # 環境変数を継承
        )
        
        # プロセス情報を保存
        running_processes[process_id] = {
            "process": process,
            "step": step,
            "status": PROCESS_STATUS_RUNNING,
            "started_at": time.time(),
            "finished_at": None,
            "return_code": None,
        }
        set_current_execution(
            step=step,
            kind="browser_process",
            message="ブラウザ確認待ちです。別ウィンドウで内容を確認してください。",
            process_id=process_id,
            message_level="info",
        )
        
        # バックグラウンドでプロセス監視
        def monitor_process():
            return_code = process.wait()
            if process_id in running_processes:
                running_processes[process_id]["return_code"] = return_code
                running_processes[process_id]["finished_at"] = time.time()
                if running_processes[process_id]["status"] != PROCESS_STATUS_TERMINATED:
                    running_processes[process_id]["status"] = (
                        PROCESS_STATUS_COMPLETED if return_code == 0 else PROCESS_STATUS_FAILED
                    )
            if current_execution.get("process_id") == process_id:
                clear_current_execution(
                    message=(
                        "ブラウザ投稿プロセスが完了しました。"
                        if return_code == 0
                        else f"ブラウザ投稿プロセスがエラー終了しました (code: {return_code})。"
                    ),
                    message_level="success" if return_code == 0 else "error",
                )
        
        thread = threading.Thread(target=monitor_process, daemon=True)
        thread.start()
        
        step_name = "Pixiv" if step == RUN_STEPS[2] else "Patreon"
        return {
            "success": True,
            "message": f"{step_name} 投稿プロセスを開始しました。ブラウザウィンドウで操作してください。",
            "process_id": process_id,
            "requires_user_action": True,
        }
    except Exception as e:
        return {"success": False, "message": f"プロセス起動エラー: {str(e)}"}


@app.get("/api/process/{process_id}")
async def get_process_status(process_id: str):
    """プロセスのステータスを取得"""
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail="Process not found")
    
    proc_info = running_processes[process_id]
    process_payload = serialize_process_info(process_id, proc_info)
    return build_response(True, "Process status loaded", **process_payload)


@app.delete("/api/process/{process_id}")
async def stop_process(process_id: str):
    """プロセスを停止"""
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail="Process not found")
    
    proc_info = running_processes[process_id]
    try:
        process = proc_info["process"]
        if process.poll() is None:
            if current_execution.get("process_id") == process_id:
                set_current_execution(
                    step=proc_info["step"],
                    kind="browser_process",
                    message="ブラウザ投稿プロセスを停止中です。終了までお待ちください。",
                    process_id=process_id,
                    message_level="warning",
                )
            process.terminate()
            try:
                await asyncio.to_thread(process.wait, 5)
            except subprocess.TimeoutExpired:
                process.kill()
                await asyncio.to_thread(process.wait, 5)

        proc_info["status"] = PROCESS_STATUS_TERMINATED
        proc_info["finished_at"] = time.time()
        proc_info["return_code"] = process.returncode
        if current_execution.get("process_id") == process_id:
            clear_current_execution(message="ブラウザ投稿プロセスを停止しました。", message_level="warning")
        return build_response(True, "Process terminated", **serialize_process_info(process_id, proc_info))
    except Exception as e:
        return build_response(False, str(e), process_id=process_id)


@app.get("/api/runtime-status")
async def runtime_status():
    """現在の実行状態を取得"""
    return get_runtime_status()


@app.get("/api/status")
async def get_status():
    """サーバーステータス"""
    return {
        "status": "running",
        "csv_exists": CSV_PATH.exists(),
        "web_dir_exists": WEB_DIR.exists(),
        "runtime": get_runtime_status(),
    }


# ==============================
# フォルダ参照 API
# ==============================

import string

@app.get("/api/browse")
async def browse_folder(path: str = ""):
    """フォルダ一覧を取得"""
    try:
        # パスが空の場合はドライブ一覧を返す
        if not path or path == "/":
            # Windowsのドライブ一覧を取得
            drives = []
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append({
                        "name": f"{letter}:",
                        "path": drive_path,
                        "type": "drive"
                    })
            return {"path": "", "items": drives, "parent": None}
        
        # 指定されたパスのフォルダ一覧を取得
        target_path = Path(path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not target_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        items = []
        try:
            for item in sorted(target_path.iterdir()):
                if item.is_dir():
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "type": "folder"
                    })
        except PermissionError:
            pass  # アクセス権限がない場合は空リストを返す
        
        # 親フォルダ
        parent = str(target_path.parent) if target_path.parent != target_path else None
        
        return {
            "path": str(target_path),
            "items": items,
            "parent": parent
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FolderValidation(BaseModel):
    path: str

@app.post("/api/validate-folder")
async def validate_folder(data: FolderValidation):
    """フォルダパスの存在確認"""
    path = Path(data.path)
    exists = path.exists() and path.is_dir()
    
    # フォルダ内の画像ファイル数をカウント
    image_count = 0
    if exists:
        try:
            image_count = len([f for f in path.iterdir() 
                              if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']])
        except PermissionError:
            pass
    
    return {
        "valid": exists,
        "path": str(path),
        "image_count": image_count
    }


@app.get("/api/pixiv-tags/suggest")
async def suggest_pixiv_tags(
    title: str = "",
    caption_pixiv: str = "",
    target_folder: str = "",
    current_tags: str = "",
):
    """Pixiv 用タグ候補を返す"""
    tasks = manager.load_tasks()
    suggestions = pixiv_tag_support.build_pixiv_tag_suggestions(
        title=title,
        caption_pixiv=caption_pixiv,
        target_folder=target_folder,
        current_tags=current_tags,
        tasks=tasks,
    )
    return build_response(
        True,
        "Pixiv tag suggestions loaded",
        suggestions=suggestions,
    )


# ==============================
# 設定管理 API
# ==============================

SECRETS_PATH = BASE_DIR / "config" / "secrets.yaml"
TEMPLATES_PATH = BASE_DIR / "config" / "templates.yaml"

def load_settings() -> dict:
    """設定ファイルを読み込む"""
    import yaml
    settings = default_settings_dict()
    
    # secrets.yaml
    if SECRETS_PATH.exists():
        try:
            with open(SECRETS_PATH, 'r', encoding='utf-8') as f:
                secrets = yaml.safe_load(f) or {}
                settings["mega_email"] = secrets.get("mega", {}).get("email", "")
                settings["mega_password"] = secrets.get("mega", {}).get("password", "")
                settings["discord_webhook_url"] = secrets.get("discord", {}).get("webhook_url", "")
        except:
            pass
    
    # templates.yaml
    if TEMPLATES_PATH.exists():
        try:
            with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f) or {}
                settings["template_pixiv"] = templates.get("pixiv", "{caption_pixiv}")
                settings["template_patreon"] = templates.get("patreon", "{caption_patreon}")
                settings["template_discord"] = templates.get("discord", "{caption_discord}")
        except:
            pass
    
    return settings


def save_settings(settings: dict):
    """設定ファイルを保存"""
    import yaml
    
    # secrets.yaml
    secrets = {
        "mega": {
            "email": settings.get("mega_email", ""),
            "password": settings.get("mega_password", "")
        },
        "discord": {
            "webhook_url": settings.get("discord_webhook_url", "")
        }
    }
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SECRETS_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(secrets, f, allow_unicode=True)
    
    # templates.yaml
    templates = {
        "pixiv": settings.get("template_pixiv", "{caption_pixiv}"),
        "patreon": settings.get("template_patreon", "{caption_patreon}"),
        "discord": settings.get("template_discord", "{caption_discord}")
    }
    with open(TEMPLATES_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(templates, f, allow_unicode=True)


@app.get("/api/settings")
async def get_settings():
    """設定を取得"""
    settings = load_settings()
    # パスワードはマスク
    if settings["mega_password"]:
        settings["mega_password_masked"] = "●" * 8
    return settings


@app.put("/api/settings")
async def update_settings(settings: SettingsModel):
    """設定を更新"""
    ensure_not_busy()
    current = load_settings()
    new_settings = settings.dict()
    
    # パスワードが空の場合は既存を維持
    if not new_settings["mega_password"]:
        new_settings["mega_password"] = current["mega_password"]
    
    save_settings(new_settings)
    return build_response(True, "Settings saved")


# ==============================
# WebSocket (ログストリーミング)
# ==============================

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await log_manager.connect(websocket)
    try:
        while True:
            # クライアントからのメッセージを待機（keepalive）
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)


# ==============================
# 静的ファイル配信
# ==============================

# Web UIディレクトリがあれば静的ファイルとして配信
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

@app.get("/")
async def root():
    """メインページを配信"""
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Post Manager API", "docs": "/docs"}


# ==============================
# エントリーポイント
# ==============================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("Post Manager - Web UI Server")
    print("=" * 50)
    print("Open: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
