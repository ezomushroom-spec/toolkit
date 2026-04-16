"""
Post Manager - 統合管理モジュール
CLIからの各種投稿処理の統合実行を担当
"""

import csv
import os
import sys
import time
import argparse
import zipfile
from playwright.sync_api import sync_playwright

from config import Paths, BrowserConfig, BASE_DIR, CSV_PATH
from app_schema import (
    CLI_ALL_STEP,
    EXISTING_FILE_POLICY_PROMPT,
    RUN_STEPS,
    TASK_FIELDS,
    hydrate_task_records,
)
from utils import (
    load_secrets, load_templates, apply_template,
    sanitize_filename, resolve_path, launch_browser
)
from preprocessor import clean_and_zip, upload_to_mega
from uploader_discord import send_discord_notification
import uploader_patreon
import uploader as pixiv_uploader


def load_tasks():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        tasks = list(reader)
    return hydrate_task_records(tasks)

def save_tasks(tasks):
    fieldnames = list(tasks[0].keys()) if tasks else list(TASK_FIELDS)
    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if tasks:
            writer.writerows(tasks)





def run_clean(tasks, existing_zip_policy=EXISTING_FILE_POLICY_PROMPT):
    print("\n[1. Clean & Zip]")
    updated = False
    for task in tasks:
        title = task.get('title')
        target_folder = task.get('target_folder')
        
        # パス解決
        resolved_path = resolve_path(target_folder)
        target_folder = str(resolved_path)

        if not target_folder or not os.path.exists(target_folder):
            print(f"Skipping {title}: Folder not found at {target_folder}")
            continue

        print(f"Processing: {title}")
        
        # 既存Zipの確認
        safe_name = sanitize_filename(os.path.basename(os.path.normpath(target_folder)))
        
        zip_name = f"{safe_name}.zip"
        zip_path = str(Paths.DIST / zip_name)
        
        if os.path.exists(zip_path):
            print(f"Zip file '{zip_name}' already exists.")
            choice = existing_zip_policy
            if existing_zip_policy == EXISTING_FILE_POLICY_PROMPT:
                # Zipがある＝処理済みとみなしてスキップ確認を入れる
                while True:
                    choice = input("  Zip exists. [S]kip Clean&Zip / [O]verwrite? (s/o): ").strip().lower()
                    if choice in ['s', 'skip', 'o', 'overwrite']:
                        break
                    print("  Please enter 's' or 'o'.")

            if choice in ['s', 'skip']:
                print("  Skipping zip creation (Using existing).")
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        count = len([n for n in zf.namelist() if n.lower().endswith(('.png', '.jpg', '.jpeg'))])
                except Exception:
                    count = 0

                task['count'] = count
                task['image_count'] = count
                continue

            if choice not in ['o', 'overwrite']:
                raise ValueError(f"Unknown existing_zip_policy: {existing_zip_policy}")

        # clean_and_zipは (zip_path, count) を返す
        zip_path, count = clean_and_zip(target_folder, title)
        if zip_path:
            task['count'] = count 
            task['image_count'] = count # エイリアスとして image_count も追加
            # 枚数を保持するためにupdated=Trueにはしない（CSVには保存しないため）
            # ただし、もしCSVに保存したければカラム追加が必要。
            # 今回は実行中のメモリ保持だけで対応する。

    return updated

def run_mega(tasks, existing_file_policy=EXISTING_FILE_POLICY_PROMPT):
    print("\n[2. MEGA Upload]")
    updated = False
    
    for task in tasks:
        title = task.get('title')
        zip_url = task.get('zip_url', '')
        
        if zip_url:
            print(f"Skipping {title}: Already has Link.")
            continue
        
        target_folder = task.get('target_folder')
        safe_name = sanitize_filename(os.path.basename(os.path.normpath(target_folder)))
        zip_name = f"{safe_name}.zip"
        zip_path = str(Paths.DIST / zip_name)
        
        if not os.path.exists(zip_path):
            print(f"Skipping {title}: Zip file not found at {zip_path}. Run --clean first.")
            continue

        print(f"Uploading: {title}")
        link = upload_to_mega(zip_path, existing_file_policy=existing_file_policy)
        if link:
            task['zip_url'] = link
            print(f"Updated CSV with link: {link}")
            updated = True
            
    if updated:
        save_tasks(tasks)
    return updated

def run_pixiv(tasks, browser=None):
    print("\n[3. Pixiv Upload]")
    templates = load_templates()
    pixiv_tmpl = templates.get('pixiv', '{caption_pixiv}')
    
    processed_tasks = []
    for task in tasks:
        caption = apply_template(pixiv_tmpl, task)
        p_task = task.copy()
        p_task['caption'] = caption
        processed_tasks.append(p_task)

    try:
        if hasattr(pixiv_uploader, 'run'):
            # browserオブジェクトを受け取る
            return pixiv_uploader.run(processed_tasks, browser_context=browser)
        else:
            print("Error: uploader.py does not support 'run(tasks)'.")
            return None
    except Exception as e:
        print(f"Pixiv Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_patreon(tasks, browser=None):
    print("\n[4. Patreon Upload]")
    templates = load_templates()
    patreon_tmpl = templates.get('patreon', '{caption_patreon}')
    
    processed_tasks = []
    for task in tasks:
        caption = apply_template(patreon_tmpl, task)
        p_task = task.copy()
        p_task['caption'] = caption
        processed_tasks.append(p_task)

    try:
        # browserオブジェクトを受け取る
        return uploader_patreon.upload_patreon(processed_tasks, browser_context=browser)
    except Exception as e:
        print(f"Patreon Error: {e}")
        return None

def run_discord(tasks):
    print("\n[5. Discord Notification]")
    secrets = load_secrets()
    webhook_url = secrets.get('discord', {}).get('webhook_url')
    if not webhook_url:
        print("Discord Webhook URL not set.")
        return

    templates = load_templates()
    discord_tmpl = templates.get('discord', '{caption_discord}')

    for task in tasks:
        title = task.get('title')
        zip_url = task.get('zip_url')
        target_folder = task.get('target_folder')

        # パス解決
        resolved_path = resolve_path(target_folder)
        target_folder = str(resolved_path)
        
        if zip_url:
            # サムネイル画像の検索 (patreon_thum* または 直下のjpg)
            thumb_path = None
            if os.path.exists(target_folder):
                # 優先: patreon_thum
                for f in os.listdir(target_folder):
                    if "patreon_thum" in f.lower() and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        thumb_path = os.path.join(target_folder, f)
                        break
                # 次点: Pixivフォルダの1枚目
                if not thumb_path:
                    pixiv_dir = os.path.join(target_folder, "Pixiv")
                    if os.path.exists(pixiv_dir):
                        files = [f for f in os.listdir(pixiv_dir) if f.lower().endswith(('.jpg', '.png'))]
                        if files:
                            files.sort()
                            thumb_path = os.path.join(pixiv_dir, files[0])

            message = apply_template(discord_tmpl, task)
            
            print(f"Sending Discord for: {title}")
            send_discord_notification(
                webhook_url,
                title,
                message,
                zip_url=zip_url,
                image_path=thumb_path
            )
            time.sleep(1)
        else:
            print(f"Skipping {title}: No Zip URL.")

def main():
    parser = argparse.ArgumentParser(description="Multi-Platform Content Uploader")
    parser.add_argument("--clean", action="store_true", help=f"Step 1: {RUN_STEPS[0]} metadata and create Zip")
    parser.add_argument("--mega", action="store_true", help=f"Step 2: Upload Zip to {RUN_STEPS[1].upper()}")
    parser.add_argument("--pixiv", action="store_true", help=f"Step 3: Upload to {RUN_STEPS[2].capitalize()}")
    parser.add_argument("--patreon", action="store_true", help=f"Step 4: Upload to {RUN_STEPS[3].capitalize()}")
    parser.add_argument("--discord", action="store_true", help=f"Step 5: Notify {RUN_STEPS[4].capitalize()}")
    parser.add_argument(f"--{CLI_ALL_STEP}", action="store_true", help="Run ALL steps sequentially")
    
    args = parser.parse_args()
    
    tasks = load_tasks()
    # ... (タスクロード、モード選択など) ...
    if not tasks:
        print("No tasks found in CSV.")
        return

    if not any([args.clean, args.mega, args.pixiv, args.patreon, args.discord, args.all]):
        # ... (モード選択) ...
        print("Select Action:")
        print("1. Clean & Zip")
        print("2. MEGA Upload")
        print("3. Pixiv")
        print("4. Patreon")
        print("5. Discord")
        print("9. All Steps")
        mode = input("Select [1-5, 9]: ").strip()
        
        if mode == '1': args.clean = True
        elif mode == '2': args.mega = True
        elif mode == '3': args.pixiv = True
        elif mode == '4': args.patreon = True
        elif mode == '5': args.discord = True
        elif mode == '9': args.all = True
        else:
            print("Cancelled.")
            return

    if args.all:
        args.clean = True
        args.mega = True
        args.pixiv = True
        args.patreon = True
        args.discord = True

    # ブラウザオブジェクト保持用リスト
    browsers = []
    
    # Playwrightの一元管理 (PixivまたはPatreonが有効な場合)
    p = None
    browser_context = None
    USER_DATA_DIR = os.path.join(BASE_DIR, "browser_profile")
    
    if args.pixiv or args.patreon:
        while True:
            try:
                if p is None:
                    p = sync_playwright().start()
                
                print("Launching shared browser context...")
                browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=USER_DATA_DIR,
                    headless=False,
                    channel="chrome",
                    args=[
                        "--start-maximized",
                        "--no-first-run",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars"
                    ],
                    ignore_default_args=["--enable-automation"],
                    viewport={"width": 1920, "height": 1080}
                )
                browsers.append(browser_context)
                break # 成功したらループを抜ける
            except Exception as e:
                print(f"Error starting Playwright/Browser: {e}")
                print("\n!!! Browser Launch Failed !!!")
                print("It seems the browser is already open or the user data directory is locked.")
                print("Please CLOSE all existing Chrome windows opened by this tool and press Enter to retry.")
                choice = input(">>> Press Enter to Retry (or 'q' to quit): ").strip().lower()
                if choice == 'q':
                    if p: p.stop()
                    return

    if args.clean:
        run_clean(tasks)
    
    if args.mega:
        run_mega(tasks)

    if args.pixiv:
        # ブラウザコンテキストを渡す
        if browser_context:
            run_pixiv(tasks, browser=browser_context)

    if args.patreon:
        # ブラウザコンテキストを渡す
        if browser_context:
            run_patreon(tasks, browser=browser_context)

    if args.discord:
        run_discord(tasks)

    print("\nAll processes completed.")
    
    if browsers:
        print("Browsers are kept open. Please review and close manually.")
        input("Press Enter to exit (Browsers will be closed)...")
        for b in browsers:
            try: b.close()
            except: pass
    
    if p:
        p.stop()


if __name__ == "__main__":
    main()
