"""ブラウズタブ（WebView） — v3.1: ダイアログ廃止、DM委譲"""

import logging
import os
import shutil
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QMenu,
)
from civitai_downloader.ui.widgets import IconButton, PrimaryButton
from PySide6.QtCore import Qt, QUrl, Slot, Signal
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

from civitai_downloader.constants import DEFAULT_START_URL
from civitai_downloader.ui.batch_dialog import BatchDialog
from civitai_downloader.core.url_parser import extract_model_id_from_page_url
from civitai_downloader.db.connection import Database
from civitai_downloader.db import repository as repo
from civitai_downloader.app import get_app_data_dir

logger = logging.getLogger(__name__)


def _prepare_webengine_paths() -> tuple[str, str]:
    """WebEngine の保存先を準備する。

    旧版や前回強制終了時の cache 配下がロックされていると
    Chromium 側で初期化失敗が出るため、HTTP キャッシュは起動ごとの
    runtime ディレクトリに分離する。
    Cookie / LocalStorage などの永続データは従来どおり `storage` に残す。
    """
    web_data_dir = os.path.join(get_app_data_dir(), "webengine")
    storage_path = os.path.join(web_data_dir, "storage")
    legacy_cache_path = os.path.join(web_data_dir, "cache")
    cache_root = os.path.join(web_data_dir, "cache_runtime")
    cache_path = os.path.join(
        cache_root,
        f"cache_{os.getpid()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    )
    shared_dictionary_path = os.path.join(storage_path, "Shared Dictionary")
    shared_dictionary_reset_marker = os.path.join(
        storage_path, ".shared_dictionary_reset_v1"
    )

    os.makedirs(web_data_dir, exist_ok=True)
    os.makedirs(storage_path, exist_ok=True)
    os.makedirs(cache_root, exist_ok=True)

    _archive_legacy_cache(legacy_cache_path)
    _cleanup_old_runtime_caches(cache_root)

    os.makedirs(cache_path, exist_ok=True)
    _reset_broken_shared_dictionary(
        shared_dictionary_path,
        shared_dictionary_reset_marker,
    )
    return cache_path, storage_path


def _cleanup_old_runtime_caches(cache_root: str) -> None:
    """前回以前の runtime キャッシュを可能なら削除する"""
    for name in os.listdir(cache_root):
        path = os.path.join(cache_root, name)
        if not os.path.isdir(path):
            continue
        try:
            shutil.rmtree(path)
        except Exception as exc:
            logger.debug("WebEngine runtimeキャッシュ削除をスキップ: %s (%s)", path, exc)


def _archive_legacy_cache(legacy_cache_path: str) -> None:
    """旧キャッシュを可能なら退避する。

    退避失敗でも新しいキャッシュ側で継続できれば十分なので、例外は握りつぶしてログ化だけ行う。
    """
    if not os.path.isdir(legacy_cache_path):
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_path = f"{legacy_cache_path}_legacy_{timestamp}"
    try:
        shutil.move(legacy_cache_path, archived_path)
        logger.info("旧WebEngineキャッシュを退避: %s -> %s", legacy_cache_path, archived_path)
    except Exception as exc:
        logger.warning("旧WebEngineキャッシュの退避に失敗: %s", exc)


def _reset_broken_shared_dictionary(
    shared_dictionary_path: str,
    reset_marker_path: str,
) -> None:
    """Shared Dictionary の破損を一度だけ退避する。

    Chromium の共有辞書 DB が壊れていると起動のたびに
    `Invalid total_dict_size detected` が出続けるため、
    Cookie や LocalStorage を維持したまま当該補助データだけ再生成させる。
    """
    if os.path.exists(reset_marker_path):
        return

    if os.path.isdir(shared_dictionary_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_path = f"{shared_dictionary_path}_legacy_{timestamp}"
        try:
            shutil.move(shared_dictionary_path, archived_path)
            logger.info(
                "破損疑いのShared Dictionaryを退避: %s -> %s",
                shared_dictionary_path,
                archived_path,
            )
        except Exception as exc:
            logger.warning("Shared Dictionaryの退避に失敗: %s", exc)
            return

    try:
        with open(reset_marker_path, "w", encoding="utf-8") as fh:
            fh.write("shared_dictionary_reset_v1\n")
    except Exception as exc:
        logger.warning("Shared Dictionaryリセットマーカー作成に失敗: %s", exc)


class _BrowsePage(QWebEnginePage):
    """新ウィンドウリクエストを同一ページで処理し、JSログを抑制するページ"""

    def javaScriptConsoleMessage(self, level, message, line, source):
        pass

    def createWindow(self, window_type):
        """target="_blank" や window.open() を同一ページ内で処理"""
        return self

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """全てのナビゲーションを許可（リダイレクト含む）"""
        return True


class BrowseTab(QWidget):
    """Civitaiブラウズ用WebViewタブ"""

    download_intercepted = Signal(object, int, str)

    def __init__(self, db: Database, download_manager=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._download_manager = download_manager

        self._setup_ui()
        self._setup_webview()
        self._load_initial_url()

    def _setup_ui(self):
        """UIレイアウト構築"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        nav_layout = QHBoxLayout()

        self._btn_back = IconButton("←")
        self._btn_forward = IconButton("→")
        self._btn_reload = IconButton("↻")

        self._url_bar = QLineEdit()
        self._url_bar.setPlaceholderText("URLを入力...")

        self._btn_go = IconButton("▶")

        self._btn_batch = PrimaryButton("一括追加")
        self._btn_batch.clicked.connect(self._on_batch_add)

        nav_layout.addWidget(self._btn_back)
        nav_layout.addWidget(self._btn_forward)
        nav_layout.addWidget(self._btn_reload)
        nav_layout.addWidget(self._url_bar)
        nav_layout.addWidget(self._btn_go)
        nav_layout.addWidget(self._btn_batch)

        layout.addLayout(nav_layout)

        self._web_view = QWebEngineView()
        layout.addWidget(self._web_view)

    def _setup_webview(self):
        """WebEngineの設定"""
        # 永続プロファイル（Cookie維持）
        self._profile = QWebEngineProfile("civitai_downloader", self)

        # キャッシュ・ストレージパスを明示的に設定
        cache_path, storage_path = _prepare_webengine_paths()
        self._profile.setCachePath(cache_path)
        self._profile.setPersistentStoragePath(storage_path)

        self._profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )

        # ダウンロード横取りフック
        self._profile.downloadRequested.connect(self._on_download_requested)

        # ページ設定（新ウィンドウ処理 + JSログ抑制）
        page = _BrowsePage(self._profile, self._web_view)
        self._web_view.setPage(page)

        # ナビゲーションボタン接続
        self._btn_back.clicked.connect(self._web_view.back)
        self._btn_forward.clicked.connect(self._web_view.forward)
        self._btn_reload.clicked.connect(self._web_view.reload)
        self._btn_go.clicked.connect(self._navigate_to_url_bar)
        self._url_bar.returnPressed.connect(self._navigate_to_url_bar)

        # URL変更時にバーを更新
        self._web_view.urlChanged.connect(self._on_url_changed)

        # 右クリックメニュー（モデルリンクのダウンロード用）
        self._web_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._web_view.customContextMenuRequested.connect(
            self._show_context_menu
        )

    def _load_initial_url(self):
        """起動時のURL読み込み"""
        last_url = repo.get_setting(self._db, "last_url", DEFAULT_START_URL)
        self._url_bar.setText(last_url)
        self._web_view.load(QUrl(last_url))

    @Slot()
    def _navigate_to_url_bar(self):
        """URLバーの内容へ遷移"""
        url_text = self._url_bar.text().strip()
        if url_text and not url_text.startswith(("http://", "https://")):
            url_text = "https://" + url_text
        if url_text:
            self._web_view.load(QUrl(url_text))

    @Slot(QUrl)
    def _on_url_changed(self, url: QUrl):
        """URLバーをリアルタイム更新"""
        self._url_bar.setText(url.toString())

    @Slot()
    def _show_context_menu(self, pos):
        """WebView上の右クリックメニュー"""
        menu = QMenu(self)

        # リンクURLを取得
        context = self._web_view.lastContextMenuRequest()
        link_url = context.linkUrl().toString() if context else ""

        # CivitaiモデルURLならダウンロードメニューを表示
        if link_url and extract_model_id_from_page_url(link_url):
            dl_action = QAction("ダウンロードキューに追加", self)
            dl_action.triggered.connect(
                lambda: self._enqueue_from_link(link_url)
            )
            menu.addAction(dl_action)
            menu.addSeparator()

        # デフォルトのWebViewメニュー項目を追加
        page = self._web_view.page()
        if context:
            if link_url:
                copy_link = QAction("リンクをコピー", self)
                copy_link.triggered.connect(
                    lambda: self._copy_to_clipboard(link_url)
                )
                menu.addAction(copy_link)
            if not context.selectedText() == "":
                copy_text = page.action(QWebEnginePage.WebAction.Copy)
                if copy_text:
                    menu.addAction(copy_text)

        back_action = page.action(QWebEnginePage.WebAction.Back)
        forward_action = page.action(QWebEnginePage.WebAction.Forward)
        reload_action = page.action(QWebEnginePage.WebAction.Reload)
        menu.addAction(back_action)
        menu.addAction(forward_action)
        menu.addAction(reload_action)

        menu.exec(self._web_view.mapToGlobal(pos))

    def _enqueue_from_link(self, link_url: str):
        """リンクURLからダウンロードキューに追加"""
        if self._download_manager:
            if self._download_manager.enqueue_from_page_url(link_url):
                logger.info(f"右クリックからキュー追加: {link_url}")

    def _copy_to_clipboard(self, text: str):
        """テキストをクリップボードにコピー"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)

    @Slot(object)
    def _on_download_requested(self, download):
        """ダウンロードリクエストの横取り処理 → DownloadManagerに委譲"""
        if self._download_manager:
            handled = self._download_manager.handle_download_requested(
                download, self._web_view
            )
            if handled:
                return

        # 非モデルファイルはWebViewに委譲（デフォルト動作に任せる）
        # handle_download_requestedがFalseを返した場合、ダウンロードは
        # キャンセルされていないのでWebViewが処理する

    def load_url(self, url: str):
        """外部からURL遷移を指示"""
        self._url_bar.setText(url)
        self._web_view.load(QUrl(url))

    @Slot()
    def _on_batch_add(self):
        """一括追加ダイアログを表示"""
        api_key = repo.get_setting(self._db, "api_key", "")
        dialog = BatchDialog(
            web_view=self._web_view,
            api_key=api_key,
            parent=self,
        )
        if dialog.exec() == BatchDialog.DialogCode.Accepted:
            models = dialog.get_selected_models()
            if models and self._download_manager:
                count = self._download_manager.enqueue_batch(models)
                logger.info(f"一括追加完了: {count}件")

    def save_current_url(self):
        """現在のURLを設定に保存"""
        current_url = self._web_view.url().toString()
        if current_url:
            repo.set_setting(self._db, "last_url", current_url)
            logger.info(f"URL保存: {current_url}")
