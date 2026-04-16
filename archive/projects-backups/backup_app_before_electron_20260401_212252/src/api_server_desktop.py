"""
Post Manager desktop server entrypoint.

Electron などのデスクトップシェルから起動する前提で、
uvicorn の auto-reload を無効にした専用入口を提供する。
"""

import sys

import uvicorn


if __name__ == "__main__":
    # Electron 側へ残すログは UTF-8 で統一して文字化けを避ける。
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
