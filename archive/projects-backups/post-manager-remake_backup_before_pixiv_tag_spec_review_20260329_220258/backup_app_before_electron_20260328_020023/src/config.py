"""
Post Manager - 共通設定モジュール
プロジェクト全体で使用するパス、定数、設定を一元管理
"""

import os
from pathlib import Path

# ベースディレクトリ（プロジェクトルート）
BASE_DIR = Path(__file__).parent.parent

# ==============================================
# パス定義
# ==============================================

class Paths:
    """プロジェクト内の各種パス"""
    
    # ディレクトリ
    SRC = BASE_DIR / "src"
    WEB = BASE_DIR / "web"
    DATA = BASE_DIR / "data"
    CONFIG = BASE_DIR / "config"
    DIST = BASE_DIR / "dist"
    BROWSER_PROFILE = BASE_DIR / "browser_profile"
    
    # ファイル
    CSV = DATA / "posts.csv"
    SECRETS = CONFIG / "secrets.yaml"
    TEMPLATES = CONFIG / "templates.yaml"


# ==============================================
# ブラウザ設定（Playwright）
# ==============================================

class BrowserConfig:
    """Playwright ブラウザ起動設定"""
    
    CHANNEL = "chrome"
    HEADLESS = False
    VIEWPORT = {"width": 1920, "height": 1080}
    
    ARGS = [
        "--start-maximized",
        "--no-first-run",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars"
    ]
    
    IGNORE_DEFAULT_ARGS = ["--enable-automation"]


# ==============================================
# 画像ファイル拡張子
# ==============================================

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif')
IMAGE_EXTENSIONS_NO_GIF = ('.png', '.jpg', '.jpeg')


# ==============================================
# 後方互換性のためのエイリアス
# ==============================================

# 文字列パスが必要な場合用
CSV_PATH = str(Paths.CSV)
USER_DATA_DIR = str(Paths.BROWSER_PROFILE)
DIST_DIR = str(Paths.DIST)
CONFIG_PATH = str(Paths.SECRETS)
TEMPLATES_PATH = str(Paths.TEMPLATES)

# 一部モジュールがBASE_DIRを直接参照する場合用
# Pathオブジェクトでもstrでも動作するよう文字列で提供
