"""
Post Manager - 共通ユーティリティモジュール
プロジェクト全体で使用するヘルパー関数を集約
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union
from playwright.sync_api import sync_playwright, BrowserContext

from config import Paths, BrowserConfig


# ==============================================
# 設定ファイルの読み込み
# ==============================================

def load_secrets() -> Dict[str, Any]:
    """
    secrets.yaml を読み込む
    
    Returns:
        dict: 設定内容。読み込み失敗時は空辞書
    """
    try:
        with open(Paths.SECRETS, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_templates() -> Dict[str, str]:
    """
    templates.yaml を読み込む
    
    Returns:
        dict: テンプレート内容。読み込み失敗時は空辞書
    """
    try:
        with open(Paths.TEMPLATES, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not load templates.yaml: {e}")
        return {}


# ==============================================
# 文字列ユーティリティ
# ==============================================

def sanitize_filename(name: str) -> str:
    """
    ファイル名に使用できる安全な文字列を生成
    
    Args:
        name: 元の文字列
        
    Returns:
        str: 安全な文字列（英数字、スペース、ハイフン、アンダースコア、ドットのみ）
    """
    return "".join([c for c in name if c.isalnum() or c in (' ', '-', '_', '.')]).strip()


def apply_template(template_str: str, task: Dict[str, Any]) -> str:
    """
    テンプレート文字列にtaskの値を埋め込む
    
    Args:
        template_str: テンプレート文字列（{key}形式のプレースホルダー）
        task: 値を含む辞書
        
    Returns:
        str: 埋め込み後の文字列
    """
    if not template_str:
        return ""
    try:
        formatted = template_str.format(**task)
        return formatted
    except KeyError as e:
        print(f"Template Error: Missing key {e} in csv data.")
        return template_str
    except Exception as e:
        print(f"Template Error: {e}")
        return template_str


# ==============================================
# パスユーティリティ
# ==============================================

def resolve_path(path: Union[str, Path]) -> Path:
    """
    相対パスを絶対パスに解決
    
    Args:
        path: パス文字列またはPathオブジェクト
        
    Returns:
        Path: 解決されたパス
    """
    p = Path(path)
    if not p.is_absolute():
        potential = Paths.SRC.parent / path
        if potential.exists():
            return potential
    return p


def get_folder_name(target_folder: str) -> str:
    """
    ターゲットフォルダから安全なフォルダ名を取得
    
    Args:
        target_folder: ターゲットフォルダパス
        
    Returns:
        str: 安全なフォルダ名
    """
    import os
    folder_name = os.path.basename(os.path.normpath(target_folder))
    return sanitize_filename(folder_name)


# ==============================================
# ブラウザユーザビリティ
# ==============================================

def launch_browser(playwright_instance=None) -> tuple:
    """
    共通設定でブラウザを起動
    
    Args:
        playwright_instance: 既存のPlaywrightインスタンス（オプション）
        
    Returns:
        tuple: (browser_context, playwright_instance, should_stop_playwright)
    """
    should_stop_p = False
    p = playwright_instance
    
    if p is None:
        p = sync_playwright().start()
        should_stop_p = True
    
    print("Launching browser...")
    
    try:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(Paths.BROWSER_PROFILE),
            headless=BrowserConfig.HEADLESS,
            channel=BrowserConfig.CHANNEL,
            args=BrowserConfig.ARGS,
            ignore_default_args=BrowserConfig.IGNORE_DEFAULT_ARGS,
            viewport=BrowserConfig.VIEWPORT
        )
        # Playwrightインスタンスへの参照を保持
        browser._playwright = p if should_stop_p else None
        return browser, p, should_stop_p
    except Exception as e:
        print(f"Error launching browser: {e}")
        if should_stop_p and p:
            p.stop()
        raise


def close_browser_safely(browser: Optional[BrowserContext], playwright_instance=None):
    """
    ブラウザを安全にクローズ
    
    Args:
        browser: BrowserContextオブジェクト
        playwright_instance: Playwrightインスタンス
    """
    if browser:
        try:
            browser.close()
        except Exception:
            pass
    
    if playwright_instance:
        try:
            playwright_instance.stop()
        except Exception:
            pass
