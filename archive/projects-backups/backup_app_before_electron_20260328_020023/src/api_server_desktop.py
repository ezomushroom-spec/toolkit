"""
Post Manager desktop server entrypoint.

Electron などのデスクトップシェルから起動する前提で、
uvicorn の auto-reload を無効にした専用入口を提供する。
"""

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
