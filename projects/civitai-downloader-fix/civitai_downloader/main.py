"""エントリポイント（v3.1）"""

import sys
import os
import logging
from logging.handlers import RotatingFileHandler

from civitai_downloader.app import create_application, get_app_data_dir
from civitai_downloader.db.connection import Database
from civitai_downloader.db.models import initialize_database
from civitai_downloader.db import repository as repo
from civitai_downloader.ui.main_window import MainWindow
from civitai_downloader.ui.browse_tab import BrowseTab
from civitai_downloader.ui.download_tab import DownloadTab
from civitai_downloader.ui.notification_tab import NotificationTab
from civitai_downloader.ui.settings_tab import SettingsTab
from civitai_downloader.core.download_manager import DownloadManager
from civitai_downloader.core.update_checker import UpdateChecker
from civitai_downloader.ui.theme import ThemeManager


def setup_logging(db: Database):
    """ログ設定"""
    log_dir = get_app_data_dir()
    max_bytes = int(repo.get_setting(db, "log_max_bytes", "10485760"))
    log_path = os.path.join(log_dir, "civitai_downloader.log")

    handler = RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)


def main():
    app = create_application()

    # Database初期化
    db = Database()
    db.connect()
    initialize_database(db)

    # ログ初期化
    setup_logging(db)
    logger = logging.getLogger(__name__)
    logger.info("アプリケーション起動 (v3.1)")

    # ダウンロードマネージャー
    max_concurrent = int(repo.get_setting(db, "max_concurrent", "3"))
    download_manager = DownloadManager(db=db, max_concurrent=max_concurrent)
    download_manager.refresh_presets_cache()

    # 更新チェッカー
    update_checker = UpdateChecker()

    # テーマ初期化
    theme_manager = ThemeManager(db=db)
    theme_manager.load_saved_theme()

    # メインウィンドウ
    window = MainWindow()

    # 各タブ生成
    browse_tab = BrowseTab(db=db, download_manager=download_manager)
    download_tab = DownloadTab(db=db, download_manager=download_manager)
    notification_tab = NotificationTab(db=db, update_checker=update_checker)
    settings_tab = SettingsTab(db=db, theme_manager=theme_manager)

    # タブ設定
    window.setup_tabs(browse_tab, download_tab, notification_tab, settings_tab)

    # 通知タブのバッジ更新
    unread_count = repo.get_unread_notification_count(db)
    window.update_notification_badge(unread_count)

    # アクティブダウンロード数のバッジ更新
    active_count = repo.get_active_job_count(db)
    window.update_download_badge(active_count)

    # シグナル接続: キュー追加→トースト通知
    def on_job_added_toast(job_id):
        job = repo.get_job(db, job_id)
        if job:
            window.show_toast(f"キューに追加: {job['filename']}")

    download_manager.job_added.connect(on_job_added_toast)

    # シグナル接続: ダウンロードバッジ
    download_manager.job_updated.connect(
        lambda _: window.update_download_badge(repo.get_active_job_count(db))
    )
    download_manager.job_finished.connect(
        lambda _jid, _st: window.update_download_badge(repo.get_active_job_count(db))
    )

    # シグナル接続: 更新チェック完了→通知バッジ
    update_checker.check_finished.connect(
        lambda: window.update_notification_badge(repo.get_unread_notification_count(db))
    )

    # シグナル接続: 更新チェックで新バージョン検出→DB操作（UIスレッド）
    def on_new_version_found(model_id, model_name, version_id, version_name, model_url):
        repo.create_notification(
            db,
            model_id=model_id,
            model_name=model_name,
            new_version_id=version_id,
            new_version_name=version_name,
            model_url=model_url,
        )
        repo.update_tracked_model(db, model_id, version_id, version_name)

    update_checker.new_version_found.connect(on_new_version_found)

    # 通知クリック→ブラウズタブ遷移
    notification_tab.navigate_requested.connect(browse_tab.load_url)
    notification_tab.navigate_requested.connect(lambda _: window.switch_to_browse_tab())

    # 通知既読→バッジ更新
    notification_tab.notification_read.connect(
        lambda: window.update_notification_badge(repo.get_unread_notification_count(db))
    )

    # 設定変更→ダウンロードマネージャー反映
    settings_tab.max_concurrent_changed.connect(download_manager.set_max_concurrent)

    # プリセット変更→キャッシュ更新
    settings_tab.presets_changed.connect(download_manager.refresh_presets_cache)
    settings_tab.presets_changed.connect(download_tab.reload_presets)

    # アプリ終了時の処理
    def on_about_to_quit():
        logger.info("アプリケーション終了")
        browse_tab.save_current_url()
        update_checker.shutdown()
        download_manager.shutdown()
        db.close()

    app.aboutToQuit.connect(on_about_to_quit)

    # 起動時に更新チェック実行
    tracked = repo.get_all_tracked_models(db)
    api_key = repo.get_setting(db, "api_key", "")
    update_checker.start_check(tracked, api_key)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
