"""個別ダウンロード実行ワーカー（temp_dir方式）"""

import logging
import re
import time
from pathlib import Path

import httpx

from PySide6.QtCore import QObject, Signal, QRunnable

from civitai_downloader.constants import (
    APP_USER_AGENT,
    DOWNLOAD_CHUNK_SIZE,
    DOWNLOAD_TIMEOUT,
    MAX_RETRY_COUNT,
    RETRY_WAIT_429,
    RETRY_WAIT_5XX,
)

logger = logging.getLogger(__name__)


class DownloadWorkerSignals(QObject):
    """ワーカー用シグナル"""
    progress = Signal(str, object, object)    # job_id, downloaded, total
    finished = Signal(str, bool, str, str)    # job_id, success, error, result_path
    filename_resolved = Signal(str, str)      # job_id, real_filename


class DownloadWorker(QRunnable):
    """API経由ダウンロードワーカー（temp_dir方式）"""

    def __init__(
        self,
        job_id: str,
        version_id: int | None,
        download_url: str,
        api_key: str,
        temp_dir: str,
        filename: str,
    ):
        super().__init__()
        self.signals = DownloadWorkerSignals()
        self._job_id = job_id
        self._version_id = version_id
        self._download_url = download_url
        self._api_key = api_key
        self._temp_dir = Path(temp_dir)
        self._filename = filename
        self._cancelled = False
        self._part_path: Path | None = None
        self._final_path: Path | None = None
        self.setAutoDelete(True)

    def run(self):
        try:
            self._execute_download()
        except Exception as e:
            logger.error(f"ワーカーエラー [{self._job_id}]: {e}")
            self.signals.finished.emit(self._job_id, False, str(e), "")

    def _execute_download(self):
        """ダウンロード本体"""
        # ダウンロードURL決定
        url = self._download_url
        if not url or "civitai.com" not in url:
            if self._version_id and self._version_id > 0:
                url = f"https://civitai.com/api/download/models/{self._version_id}"
            else:
                self.signals.finished.emit(
                    self._job_id, False, "ダウンロードURLが無効です", ""
                )
                return

        headers = {"User-Agent": APP_USER_AGENT}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        self._temp_dir.mkdir(parents=True, exist_ok=True)
        final_path = self._temp_dir / self._filename
        part_path = Path(str(final_path) + ".part")
        self._final_path = final_path
        self._part_path = part_path

        for attempt in range(MAX_RETRY_COUNT):
            if self._cancelled:
                self._cleanup_temp_files()
                self.signals.finished.emit(self._job_id, False, "キャンセル", "")
                return

            try:
                req_headers = dict(headers)

                # レジューム判定
                initial_bytes = 0
                if part_path.exists():
                    initial_bytes = part_path.stat().st_size
                    req_headers["Range"] = f"bytes={initial_bytes}-"

                with httpx.stream(
                    "GET", url, headers=req_headers,
                    follow_redirects=True, timeout=httpx.Timeout(10.0, read=300.0)
                ) as resp:

                    # Range非対応
                    if resp.status_code == 416:
                        initial_bytes = 0
                        part_path.unlink(missing_ok=True)
                        req_headers.pop("Range", None)
                        resp.close()
                        with httpx.stream(
                            "GET", url, headers=req_headers,
                            follow_redirects=True, timeout=DOWNLOAD_TIMEOUT
                        ) as resp2:
                            self._do_download(resp2, part_path, final_path, 0)
                        break

                    if resp.status_code == 429:
                        logger.warning(
                            f"レート制限 (429)。{RETRY_WAIT_429}秒待機 (試行{attempt+1})"
                        )
                        resp.close()
                        time.sleep(RETRY_WAIT_429)
                        continue

                    if resp.status_code >= 500:
                        logger.warning(
                            f"サーバーエラー ({resp.status_code})。{RETRY_WAIT_5XX}秒待機 (試行{attempt+1})"
                        )
                        resp.close()
                        time.sleep(RETRY_WAIT_5XX)
                        continue

                    if resp.status_code in (401, 403):
                        self.signals.finished.emit(
                            self._job_id, False,
                            f"認証エラー (HTTP {resp.status_code}): APIキーを確認してください",
                            "",
                        )
                        return

                    if resp.status_code == 404:
                        self.signals.finished.emit(
                            self._job_id, False,
                            "モデルが見つかりません (HTTP 404)",
                            "",
                        )
                        return

                    if resp.status_code not in (200, 206):
                        self.signals.finished.emit(
                            self._job_id, False, f"HTTP {resp.status_code}", ""
                        )
                        return

                    # Content-Type検証: HTML/JSONレスポンスはモデルファイルではない
                    content_type = resp.headers.get("content-type", "")
                    if "text/html" in content_type:
                        self.signals.finished.emit(
                            self._job_id, False,
                            "サーバーがHTMLページを返しました（認証エラーまたはモデル非公開の可能性）",
                            "",
                        )
                        return

                    # Content-Dispositionからファイル名を取得
                    real_filename = self._extract_filename_from_headers(resp.headers)
                    if real_filename and real_filename != self._filename:
                        self._filename = real_filename
                        final_path = self._temp_dir / self._filename
                        part_path = Path(str(final_path) + ".part")
                        self._final_path = final_path
                        self._part_path = part_path
                        self.signals.filename_resolved.emit(self._job_id, real_filename)

                    self._do_download(resp, part_path, final_path, initial_bytes)
                    break

            except httpx.TimeoutException:
                logger.warning(f"タイムアウト (試行{attempt+1})")
                if attempt == MAX_RETRY_COUNT - 1:
                    self.signals.finished.emit(self._job_id, False, "タイムアウト", "")
                    return
                time.sleep(RETRY_WAIT_5XX)

            except OSError as e:
                logger.error(f"ファイルI/Oエラー: {e}")
                self.signals.finished.emit(self._job_id, False, str(e), "")
                return

            except Exception as e:
                logger.error(f"予期しないエラー: {e}")
                self.signals.finished.emit(self._job_id, False, str(e), "")
                return

    def _do_download(self, resp, part_path: Path, final_path: Path, initial_bytes: int):
        """ストリーミングダウンロード処理"""
        total = int(resp.headers.get("content-length", 0)) + initial_bytes
        downloaded = initial_bytes

        mode = "ab" if resp.status_code == 206 else "wb"
        with open(part_path, mode) as f:
            for chunk in resp.iter_bytes(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if self._cancelled:
                    self._cleanup_temp_files()
                    self.signals.finished.emit(self._job_id, False, "キャンセル", "")
                    return
                f.write(chunk)
                downloaded += len(chunk)
                self.signals.progress.emit(self._job_id, downloaded, total)

        # .part → temp_dir内の最終名にリネーム
        part_path.rename(final_path)
        result_path = str(final_path)
        logger.info(f"DL完了: {self._filename} → {result_path}")
        self.signals.finished.emit(self._job_id, True, "", result_path)

    @staticmethod
    def _extract_filename_from_headers(headers) -> str:
        """Content-Dispositionヘッダーからファイル名を抽出"""
        cd = headers.get("content-disposition", "")
        if not cd:
            return ""

        # filename*=UTF-8''...（RFC 5987）を優先
        match = re.search(r"filename\*=(?:UTF-8|utf-8)''(.+?)(?:;|$)", cd)
        if match:
            from urllib.parse import unquote
            return unquote(match.group(1).strip())

        # filename="..."
        match = re.search(r'filename="(.+?)"', cd)
        if match:
            return match.group(1).strip()

        # filename=...（引用符なし）
        match = re.search(r"filename=(\S+?)(?:;|$)", cd)
        if match:
            return match.group(1).strip()

        return ""

    def cancel(self):
        self._cancelled = True

    def _cleanup_temp_files(self):
        """キャンセル時に temp_dir の残骸を消す"""
        for path in (self._part_path, self._final_path):
            if not path:
                continue
            try:
                path.unlink(missing_ok=True)
            except OSError as exc:
                logger.warning(
                    "一時ファイル削除失敗 [%s]: %s",
                    self._job_id,
                    exc,
                )
