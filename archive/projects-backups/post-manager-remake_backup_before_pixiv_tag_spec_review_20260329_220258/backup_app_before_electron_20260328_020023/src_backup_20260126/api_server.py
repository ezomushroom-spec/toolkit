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

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# パス設定
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
WEB_DIR = BASE_DIR / "web"
CSV_PATH = BASE_DIR / "data" / "posts.csv"

sys.path.insert(0, str(SRC_DIR))

# 既存モジュールのインポート
import manager

# ==============================
# データモデル
# ==============================

class Task(BaseModel):
    """投稿タスク"""
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

class RunStepRequest(BaseModel):
    """ステップ実行リクエスト"""
    step: str  # clean, mega, pixiv, patreon, discord, all


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


# ==============================
# FastAPI アプリケーション
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    print(f"🚀 Post Manager API Server starting...")
    print(f"📂 Base directory: {BASE_DIR}")
    yield
    # 終了時処理
    print("👋 Server shutting down...")

app = FastAPI(
    title="Post Manager API",
    description="Pixiv/Patreon/Discord投稿管理API",
    version="1.0.0",
    lifespan=lifespan
)


# ==============================
# API エンドポイント
# ==============================

@app.get("/api/tasks")
async def get_tasks():
    """タスク一覧を取得"""
    tasks = manager.load_tasks()
    return {"tasks": tasks, "count": len(tasks)}


@app.post("/api/tasks")
async def add_task(task: Task):
    """タスクを追加"""
    tasks = manager.load_tasks()
    tasks.append(task.dict())
    manager.save_tasks(tasks)
    return {"success": True, "message": "Task added"}


@app.put("/api/tasks/{index}")
async def update_task(index: int, task: Task):
    """タスクを更新"""
    tasks = manager.load_tasks()
    if 0 <= index < len(tasks):
        tasks[index] = task.dict()
        manager.save_tasks(tasks)
        return {"success": True, "message": "Task updated"}
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/api/tasks/{index}")
async def delete_task(index: int):
    """タスクを削除"""
    tasks = manager.load_tasks()
    if 0 <= index < len(tasks):
        deleted = tasks.pop(index)
        manager.save_tasks(tasks)
        return {"success": True, "deleted": deleted}
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/api/run/{step}")
async def run_step(step: str):
    """ステップを実行"""
    tasks = manager.load_tasks()
    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks found")
    
    result = {"step": step, "success": False, "message": ""}
    
    try:
        if step == "clean":
            manager.run_clean(tasks)
            result["success"] = True
            result["message"] = "Clean & Zip completed"
        elif step == "mega":
            manager.run_mega(tasks)
            result["success"] = True
            result["message"] = "MEGA upload completed"
        elif step == "discord":
            manager.run_discord(tasks)
            result["success"] = True
            result["message"] = "Discord notification sent"
        elif step in ["pixiv", "patreon"]:
            # サブプロセスで実行
            process_result = await start_browser_process(step)
            result["success"] = process_result["success"]
            result["message"] = process_result["message"]
            result["process_id"] = process_result.get("process_id")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown step: {step}")
    except Exception as e:
        result["message"] = str(e)
    
    return result


# ==============================
# ブラウザプロセス管理
# ==============================

import subprocess
import threading
import uuid

# 実行中のプロセスを追跡
running_processes = {}

async def start_browser_process(step: str):
    """ブラウザ投稿プロセスをサブプロセスで開始"""
    process_id = str(uuid.uuid4())[:8]
    
    # コマンド構築
    if step == "pixiv":
        cmd = [sys.executable, str(SRC_DIR / "manager.py"), "--pixiv"]
    elif step == "patreon":
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
            "status": "running",
            "started_at": asyncio.get_event_loop().time()
        }
        
        # バックグラウンドでプロセス監視
        def monitor_process():
            process.wait()
            if process_id in running_processes:
                running_processes[process_id]["status"] = "completed"
        
        thread = threading.Thread(target=monitor_process, daemon=True)
        thread.start()
        
        step_name = "Pixiv" if step == "pixiv" else "Patreon"
        return {
            "success": True,
            "message": f"{step_name} 投稿プロセスを開始しました。ブラウザウィンドウで操作してください。",
            "process_id": process_id
        }
    except Exception as e:
        return {"success": False, "message": f"プロセス起動エラー: {str(e)}"}


@app.get("/api/process/{process_id}")
async def get_process_status(process_id: str):
    """プロセスのステータスを取得"""
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail="Process not found")
    
    proc_info = running_processes[process_id]
    return {
        "process_id": process_id,
        "step": proc_info["step"],
        "status": proc_info["status"]
    }


@app.delete("/api/process/{process_id}")
async def stop_process(process_id: str):
    """プロセスを停止"""
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail="Process not found")
    
    proc_info = running_processes[process_id]
    try:
        proc_info["process"].terminate()
        proc_info["status"] = "terminated"
        return {"success": True, "message": "Process terminated"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.get("/api/status")
async def get_status():
    """サーバーステータス"""
    return {
        "status": "running",
        "csv_exists": CSV_PATH.exists(),
        "web_dir_exists": WEB_DIR.exists()
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


# ==============================
# 設定管理 API
# ==============================

SECRETS_PATH = BASE_DIR / "config" / "secrets.yaml"
TEMPLATES_PATH = BASE_DIR / "config" / "templates.yaml"

class Settings(BaseModel):
    """設定データ"""
    mega_email: str = ""
    mega_password: str = ""
    discord_webhook_url: str = ""
    template_pixiv: str = "{caption_pixiv}"
    template_patreon: str = "{caption_patreon}"
    template_discord: str = "{caption_discord}"


def load_settings() -> dict:
    """設定ファイルを読み込む"""
    import yaml
    settings = {
        "mega_email": "",
        "mega_password": "",
        "discord_webhook_url": "",
        "template_pixiv": "{caption_pixiv}",
        "template_patreon": "{caption_patreon}",
        "template_discord": "{caption_discord}"
    }
    
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
async def update_settings(settings: Settings):
    """設定を更新"""
    current = load_settings()
    new_settings = settings.dict()
    
    # パスワードが空の場合は既存を維持
    if not new_settings["mega_password"]:
        new_settings["mega_password"] = current["mega_password"]
    
    save_settings(new_settings)
    return {"success": True, "message": "Settings saved"}


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
    print("📮 Post Manager - Web UI Server")
    print("=" * 50)
    print(f"🌐 Open: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
