import csv
import os
import time
import sys
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# パス設定（スクリプトの位置を基準にする）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "posts.csv")
USER_DATA_DIR = os.path.join(BASE_DIR, "browser_profile")

def validate_paths():
    """必要なファイルやディレクトリの存在確認"""
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return False
    if not os.path.exists(USER_DATA_DIR):
        print(f"Creating user data directory at {USER_DATA_DIR}")
        os.makedirs(USER_DATA_DIR, exist_ok=True)
    return True

def process_task(page, task):
    """
    1つのタスク（1ページ）に対して入力処理を行う関数
    """
    print(f"Processing: {task.get('title', 'No Title')}")
    
    # フォルダチェック
    base_dir = task.get('target_folder', '')
    if not os.path.isabs(base_dir):
        potential_path = os.path.join(BASE_DIR, base_dir)
        if os.path.exists(potential_path):
            base_dir = potential_path

    # Pixiv用画像フォルダ: Pixivサブフォルダがあればそちら、なければtarget_folder直下
    img_dir = os.path.join(base_dir, "Pixiv")
    
    if not os.path.exists(img_dir):
        # target_folder直下を使用
        if os.path.exists(base_dir):
            img_dir = base_dir
            print(f"  Using base folder for images: {img_dir}")
        else:
            print(f"  Skipping: Folder not found -> {base_dir}")
            return False

    # 投稿画面へ遷移
    try:
        print("  Navigating to upload page...")
        target_url = "https://www.pixiv.net/illustration/create"
        page.goto(target_url, timeout=60000)
        
        # ページ読み込み待機
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        # ログインが必要かどうかの判定
        needs_login = False
        if "login" in page.url or "accounts.pixiv.net" in page.url:
            needs_login = True
        else:
            try:
                page.locator('input[type="file"]').wait_for(state="attached", timeout=5000)
            except:
                needs_login = True

        if needs_login:
            print("  !!! Login required in this tab !!!")
            if "illustration/create" not in page.url:
                page.goto(target_url)

        # 画像アップロード
        print("  Uploading images...")
        files = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        files.sort()
        
        if not files:
            print("  No image files found in folder.")
            return False
            
        # ファイル選択inputを探してアップロード
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(files)
        
        # アップロード完了待ち
        time.sleep(2)

        # 各種テキスト入力
        print("  Filling metadata...")
        page.get_by_placeholder("タイトル").fill(task['title'])
        # キャプションはmanagerから渡されたテンプレート適用済みのものを使用
        # manager.py経由: task['caption']にテンプレート適用済み、直接実行: task['caption_pixiv']
        caption = task.get('caption', task.get('caption_pixiv', ''))
        page.locator("textarea").first.fill(caption.replace('\\n', '\n'))
        
        # タグ入力
        tag_input = page.get_by_placeholder("タグ", exact=False)
        for tag in task['tags'].split():
            if not tag.strip(): continue
            tag_input.fill(tag.strip())
            tag_input.press("Enter")
            time.sleep(0.1)

        # R-18設定
        print("  Setting R-18...")
        try:
            r18_radio = page.locator('input[name="x_restrict"][value="r18"]')
            if r18_radio.count() > 0:
                r18_radio.check()
            else:
                page.locator("label").filter(has_text="R-18").first.click()
        except Exception as e:
             print(f"  Warning: 'R-18' selection failed: {e}")

        # AI設定
        print("  Setting AI Generated...")
        ai_section = page.locator("div").filter(has_text="AI生成作品").last
        yes_btn = ai_section.get_by_text("はい", exact=True)
        if yes_btn.count() > 0:
            yes_btn.click()
        else:
            print("  Warning: AI setting 'Yes' button not found.")

        # コレクション掲載設定
        print("  Unchecking 'Allow added to collection'...")
        try:
            collection_label = page.locator("label").filter(has_text="他のユーザーによるコレクションへの掲載を受け付ける").first
            if collection_label.count() > 0:
                 collection_input = collection_label.locator("input[type='checkbox']")
                 if collection_input.count() > 0:
                     if collection_input.is_checked():
                         collection_input.uncheck()
                 else:
                     collection_label.click()
            else:
                 container = page.locator("div").filter(has_text="他のユーザーによるコレクションへの掲載を受け付ける").last
                 target_checkbox = container.locator("input[type='checkbox']")
                 if target_checkbox.count() > 0 and target_checkbox.is_checked():
                     target_checkbox.uncheck()
        except Exception as e:
            print(f"  Warning: Could not uncheck collection setting: {e}")

        # 予約投稿設定
        schedule = task.get('schedule', '').strip()
        if schedule:
            print(f"  Setting Schedule: {schedule} ...")
            try:
                reserve_check = page.locator('input[name="reserve"]')
                if reserve_check.count() > 0:
                    if not reserve_check.is_checked():
                        reserve_check.click()
                        print("  -> Schedule mode toggled (click).")
                        time.sleep(1.0)

                    if ' ' in schedule:
                        date_str, time_str = schedule.split(' ', 1)
                    else:
                        date_str = schedule
                        time_str = "00:00"

                    target_dt = datetime.strptime(date_str, "%Y/%m/%d")
                    if os.name == 'nt':
                        target_date_text = target_dt.strftime("%Y年%m月%d日").replace("月0", "月")
                    else:
                        target_date_text = target_dt.strftime("%Y年%m月%-d日")

                    schedule_area = page.locator("div").filter(has=reserve_check).last
                    dropdowns = schedule_area.locator("div[tabindex='0']")
                    
                    if dropdowns.count() >= 2:
                        # --- 日付選択 ---
                        date_dropdown = dropdowns.nth(0)
                        current_date = date_dropdown.text_content()
                        if target_date_text not in current_date:
                            date_dropdown.click()
                            time.sleep(0.5)
                            target_option = page.get_by_text(target_date_text, exact=True)
                            if target_option.count() > 0:
                                target_option.last.scroll_into_view_if_needed()
                                target_option.last.click()
                                print(f"  -> Selected Date: {target_date_text}")
                            else:
                                print(f"  Warning: Date option '{target_date_text}' not found.")
                        time.sleep(0.2)

                        # --- 時間選択 ---
                        time_dropdown = dropdowns.nth(1)
                        current_time = time_dropdown.text_content()
                        if time_str not in current_time:
                            time_dropdown.click()
                            time.sleep(0.5)
                            time_option = page.get_by_text(time_str, exact=True)
                            if time_option.count() > 0:
                                time_option.last.scroll_into_view_if_needed()
                                time_option.last.click()
                                print(f"  -> Selected Time: {time_str}")
                            else:
                                print(f"  Warning: Time option '{time_str}' not found.")
                    else:
                        print("  Warning: Date/Time dropdowns not found.")
                else:
                    print("  Warning: Schedule checkbox 'input[name=reserve]' not found.")
            except Exception as e:
                 print(f"  Error setting schedule: {e}")
                 import traceback
                 traceback.print_exc()

        print(f"  Done setup for: {task['title']}")
        return True

    except Exception as e:
        print(f"  Error processing task: {e}")
        import traceback
        traceback.print_exc()
        return False

def run(tasks, browser_context=None):
    """
    外部から呼び出し可能な実行関数
    """
    print("=== Pixiv Auto Uploader Started (Module Mode) ===")
    if not validate_paths():
        return

    if not tasks:
        print("No tasks provided.")
        return

    print(f"Loaded {len(tasks)} tasks.")

    # ブラウザコンテキストの取得または起動
    browser = browser_context
    should_stop_p = False
    p = None
    
    if browser is None:
        p = sync_playwright().start()
        should_stop_p = True
        print("Launching browser (Local)...")
        try:
            browser = p.chromium.launch_persistent_context(
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
            if should_stop_p:
                browser._playwright = p
            else:
                browser._playwright = None
        except Exception as e:
            print(f"Error launching browser: {e}")
            if should_stop_p:
                p.stop()
            return

    opened_pages = []
    
    # ログインチェック用の一時ページ作成を削除し、タスクループ内で処理する

    for i, task in enumerate(tasks, 1):
        print(f"\n[{i}/{len(tasks)}] Setting up tab...")
        page = browser.new_page()
        process_task(page, task)
        opened_pages.append(page)
        time.sleep(1)

    print("\nAll tabs are ready.")
    print(">>> Please review all tabs and click 'Submit' manually.")
    # input(">>> Press Enter to close browser and finish...")
    # browser.close()
    return browser

def main():
    # CSV読み込み（単体実行時用）
    try:
        with open(CSV_PATH, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            tasks = list(reader)
        browser = run(tasks)
        if browser:
            input(">>> Press Enter to close browser and finish...")
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
