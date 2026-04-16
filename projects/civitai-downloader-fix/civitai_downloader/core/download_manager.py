"""キュー管理・並列制御（v3.1仕様準拠）"""

import logging
import os
from typing import Any

from PySide6.QtCore import QObject, Signal, QThreadPool

from civitai_downloader.constants import JobStatus, CIVITAI_BASE_URL
from civitai_downloader.db.connection import Database
from civitai_downloader.db import repository as repo
from civitai_downloader.core.download_worker import DownloadWorker
from civitai_downloader.core.file_mover import FileMover
from civitai_downloader.core.recommender import RecommendTask
from civitai_downloader.core.resolve_worker import VersionResolveTask
from civitai_downloader.core.url_parser import (
    extract_version_id,
    extract_model_id_from_page_url,
    is_model_extension,
    is_non_model_extension,
)
from civitai_downloader.app import get_temp_dir, get_unsorted_dir

logger = logging.getLogger(__name__)


class DownloadManager(QObject):
    """v3.1仕様の3層分離: DownloadManager / DownloadWorker / FileMover"""

    job_added = Signal(str)          # job_id
    job_updated = Signal(str)        # job_id
    job_finished = Signal(str, str)  # job_id, status

    def __init__(self, db: Database, max_concurrent: int = 3):
        super().__init__()
        self._db = db
        self._max_concurrent = max_concurrent
        self._active: dict[str, Any] = {}  # job_id → worker
        self._thread_pool = QThreadPool.globalInstance()
        self._presets_cache: list[dict] = []
        self._shutting_down = False

    @property
    def has_slot(self) -> bool:
        return len(self._active) < self._max_concurrent

    def set_max_concurrent(self, value: int):
        self._max_concurrent = max(1, value)
        repo.set_setting(self._db, "max_concurrent", str(self._max_concurrent))

    def refresh_presets_cache(self):
        """プリセットキャッシュを更新"""
        if self._shutting_down:
            return
        self._presets_cache = repo.get_all_presets(self._db)

    def get_presets_cache(self) -> list[dict]:
        """プリセットキャッシュを取得"""
        return self._presets_cache

    # ──── WebView起点のダウンロード判定 ────

    def handle_download_requested(self, download, webview) -> bool:
        """
        WebViewのdownloadRequestedシグナルから呼ばれる。
        モデルファイルならキューに登録してTrue、非モデルならFalse。
        """
        if self._shutting_down:
            download.cancel()
            return True

        url = download.url().toString()
        filename = download.suggestedFileName()

        logger.info(f"ダウンロードリクエスト検出: {url} ({filename})")

        # モデルダウンロードURL判定
        version_id = extract_version_id(url)
        is_model = version_id is not None

        # 拡張子フォールバック判定
        if not is_model and filename:
            if is_model_extension(filename):
                is_model = True
            elif is_non_model_extension(filename):
                is_model = False

        if not is_model:
            return False

        # WebViewのDLは常にキャンセル（API経由で再取得する）
        download.cancel()

        # ページURLを取得
        page_url = ""
        if webview:
            page_url = webview.url().toString()

        if version_id:
            self._enqueue_resolved(
                version_id=version_id,
                filename=filename,
                download_url=url,
                page_url=page_url,
            )
        else:
            self._enqueue_unresolved(
                filename=filename,
                download_url=url,
                page_url=page_url,
            )

        return True

    def _enqueue_resolved(
        self,
        version_id: int,
        filename: str,
        download_url: str,
        page_url: str = "",
        preset_id: str | None = None,
    ):
        """version_id確定済みのジョブをPENDINGで登録"""
        job_id = repo.insert_job(
            self._db,
            filename=filename,
            download_url=download_url,
            page_url=page_url,
            model_version_id=version_id,
            preset_id=preset_id,
            status=JobStatus.PENDING.value,
        )
        logger.info(f"ジョブ作成(PENDING): {job_id} ({filename})")
        self.job_added.emit(job_id)

        # 推奨プリセットタスクを起動
        self._start_recommend_task(job_id, version_id)

    def _enqueue_unresolved(
        self,
        filename: str,
        download_url: str,
        page_url: str = "",
    ):
        """version_id未確定のジョブをPENDING_UNRESOLVEDで登録"""
        job_id = repo.insert_job(
            self._db,
            filename=filename,
            download_url=download_url,
            page_url=page_url,
            status=JobStatus.PENDING_UNRESOLVED.value,
        )
        logger.info(f"ジョブ作成(PENDING_UNRESOLVED): {job_id} ({filename})")
        self.job_added.emit(job_id)

        # バージョン解決タスクを起動
        if page_url:
            self._start_resolve_task(job_id, page_url)

    # ──── ページURLからのキュー追加 ────

    def enqueue_from_page_url(self, page_url: str) -> bool:
        """モデルページURLからキューに追加（サムネイル右クリック用）"""
        model_id = extract_model_id_from_page_url(page_url)
        if not model_id:
            logger.warning(f"モデルID抽出失敗: {page_url}")
            return False

        filename = f"model_{model_id}（解決中）"
        self._enqueue_unresolved(
            filename=filename,
            download_url="",
            page_url=page_url,
        )
        return True

    # ──── 一括キュー追加 ────

    def enqueue_batch(self, models: list[dict]) -> int:
        """
        複数モデルを一括でキューに追加。
        各モデルは {"model_id": int, "name": str, "url": str} の形式。
        戻り値: 追加件数
        """
        count = 0
        for m in models:
            url = m.get("url", "")
            if url and self.enqueue_from_page_url(url):
                count += 1
        logger.info(f"一括追加: {count}/{len(models)}件をキューに追加")
        return count

    # ──── 手動開始 ────

    def start_selected(self, job_ids: list[str]):
        """選択されたジョブを開始"""
        if self._shutting_down:
            return
        for job_id in job_ids:
            job = repo.get_job(self._db, job_id)
            if job and self.can_start(job):
                repo.update_job(self._db, job_id, status=JobStatus.QUEUED.value)
                self.job_updated.emit(job_id)
        self._process_queue()

    def start_all_pending(self):
        """全PENDING（開始可能な）ジョブを開始"""
        if self._shutting_down:
            return
        jobs = repo.get_jobs_by_status(self._db, JobStatus.PENDING.value)
        for job in jobs:
            if self.can_start(job):
                repo.update_job(self._db, job["id"], status=JobStatus.QUEUED.value)
                self.job_updated.emit(job["id"])
        self._process_queue()

    def retry_job(self, job_id: str):
        """失敗ジョブをPENDINGに戻す"""
        if self._shutting_down:
            return
        job = repo.get_job(self._db, job_id)
        if not job or job["status"] != JobStatus.FAILED.value:
            return
        if not job.get("model_version_id") and job.get("page_url"):
            repo.update_job(
                self._db, job_id,
                status=JobStatus.PENDING_UNRESOLVED.value,
                error_message="",
            )
            self.job_updated.emit(job_id)
            self._start_resolve_task(job_id, job["page_url"])
            return
        repo.update_job(
            self._db, job_id,
            status=JobStatus.PENDING.value,
            error_message="",
        )
        self.job_updated.emit(job_id)

    def cancel_job(self, job_id: str):
        """ジョブをキャンセル"""
        if self._shutting_down:
            return
        worker = self._active.get(job_id)
        if worker:
            worker.cancel()
        else:
            job = repo.get_job(self._db, job_id)
            if job and job["status"] in (
                JobStatus.PENDING.value,
                JobStatus.PENDING_UNRESOLVED.value,
                JobStatus.QUEUED.value,
            ):
                repo.update_job(
                    self._db, job_id,
                    status=JobStatus.FAILED.value,
                    error_message="キャンセル",
                )
                self.job_updated.emit(job_id)

    def delete_job(self, job_id: str):
        """ジョブを削除（DL中はキャンセル後）"""
        worker = self._active.get(job_id)
        if worker:
            worker.cancel()
            self._active.pop(job_id, None)
        self._cleanup_job_temp_files(job_id)
        conn = self._db.get_connection()
        conn.execute("DELETE FROM download_jobs WHERE id = ?", (job_id,))
        conn.commit()

    def can_start(self, job: dict) -> bool:
        """ジョブが開始可能かチェック"""
        if job["status"] not in (JobStatus.PENDING.value,):
            return False
        # version_idが必要
        if not job.get("model_version_id"):
            return False
        # プリセットのパスが有効か（設定されていればチェック）
        preset_id = job.get("preset_id")
        if preset_id:
            preset = repo.get_preset(self._db, preset_id)
            if preset and preset.get("path") and not os.path.isdir(preset["path"]):
                return False
        return True

    def shutdown(self):
        """全ワーカーを停止"""
        self._shutting_down = True
        for worker in self._active.values():
            worker.cancel()
        self._thread_pool.waitForDone(5000)
        self._active.clear()

    # ──── キュー処理 ────

    def _process_queue(self):
        """QUEUED→DL枠割当"""
        if self._shutting_down:
            return
        while self.has_slot:
            next_job = repo.get_next_job_by_status(self._db, JobStatus.QUEUED.value)
            if not next_job:
                break
            self._start_download(next_job)

    def _start_download(self, job: dict):
        """ワーカーを生成してDL開始"""
        if self._shutting_down:
            return
        job_id = job["id"]
        api_key = repo.get_setting(self._db, "api_key", "")
        temp_dir = get_temp_dir()

        # ダウンロードURL決定
        download_url = job.get("download_url", "")
        version_id = job.get("model_version_id")

        worker = DownloadWorker(
            job_id=job_id,
            version_id=version_id,
            download_url=download_url,
            api_key=api_key,
            temp_dir=temp_dir,
            filename=job["filename"],
        )
        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_download_finished)
        worker.signals.filename_resolved.connect(self._on_filename_resolved)

        self._active[job_id] = worker
        repo.update_job(
            self._db, job_id,
            status=JobStatus.DOWNLOADING.value,
            temp_path=os.path.join(temp_dir, job["filename"]),
        )

        self._thread_pool.start(worker)
        self.job_updated.emit(job_id)
        logger.info(f"DL開始: {job_id} ({job['filename']})")

    # ──── シグナルハンドラ ────

    def _on_progress(self, job_id: str, downloaded, total):
        if self._shutting_down:
            return
        repo.update_job(
            self._db, job_id,
            bytes_downloaded=downloaded,
            bytes_total=total,
        )
        self.job_updated.emit(job_id)

    def _on_filename_resolved(self, job_id: str, filename: str):
        """ダウンロード開始時にContent-Dispositionから実ファイル名が判明"""
        if self._shutting_down:
            return
        repo.update_job(self._db, job_id, filename=filename)
        self.job_updated.emit(job_id)
        logger.info(f"ファイル名確定: {job_id} → {filename}")

    def _on_download_finished(self, job_id: str, success: bool, error: str, result_path: str):
        """DL完了/失敗時の後処理"""
        self._active.pop(job_id, None)
        if self._shutting_down:
            return
        try:
            if success and result_path:
                # ファイル移動
                job = repo.get_job(self._db, job_id)
                if not job:
                    logger.info(f"削除済みジョブの完了通知を破棄: {job_id}")
                    return

                preset_path = ""
                preset_id = job.get("preset_id")
                if preset_id:
                    preset = repo.get_preset(self._db, preset_id)
                    if preset:
                        preset_path = preset.get("path", "")

                unsorted_dir = get_unsorted_dir()

                try:
                    status, dest_path = FileMover.move_to_dest(
                        result_path, job["filename"], preset_path, unsorted_dir
                    )
                    if status == "skipped":
                        repo.update_job(
                            self._db, job_id,
                            status=JobStatus.SKIPPED.value,
                            dest_path=dest_path,
                        )
                        self.job_finished.emit(job_id, JobStatus.SKIPPED.value)
                    else:
                        repo.update_job(
                            self._db, job_id,
                            status=JobStatus.COMPLETED.value,
                            dest_path=dest_path,
                        )
                        self.job_finished.emit(job_id, JobStatus.COMPLETED.value)
                        self._register_tracking_for_job(job_id)

                except OSError as e:
                    # 移動失敗→unsortedにフォールバック
                    logger.error(f"ファイル移動失敗: {e}")
                    try:
                        _fb_status, fb_dest = FileMover.move_to_dest(
                            result_path, job["filename"], "", unsorted_dir
                        )
                        repo.update_job(
                            self._db, job_id,
                            status=JobStatus.COMPLETED.value,
                            dest_path=fb_dest,
                            error_message=f"移動失敗（Unsortedに保存）: {e}",
                        )
                        self.job_finished.emit(job_id, JobStatus.COMPLETED.value)
                        self._register_tracking_for_job(job_id)
                    except OSError as e2:
                        repo.update_job(
                            self._db, job_id,
                            status=JobStatus.FAILED.value,
                            error_message=f"ファイル移動完全失敗: {e2}",
                        )
                        self.job_finished.emit(job_id, JobStatus.FAILED.value)
            else:
                repo.update_job(
                    self._db, job_id,
                    status=JobStatus.FAILED.value,
                    error_message=error,
                )
                self.job_finished.emit(job_id, JobStatus.FAILED.value)
                logger.warning(f"DL失敗: {job_id} - {error}")
        finally:
            self._process_queue()

    def _on_recommend_done(
        self, job_id: str, preset_id: str, api_type: str, model_id, model_name: str
    ):
        """推奨プリセット決定→UIスレッドでDB更新"""
        if self._shutting_down:
            return
        job = repo.get_job(self._db, job_id)
        if not job:
            return

        updates: dict = {
            "model_type": api_type,
            "model_id": model_id,
            "model_name": model_name,
        }
        # プリセットが未設定で推奨がある場合のみ設定
        if preset_id and not job.get("preset_id"):
            updates["preset_id"] = preset_id

        repo.update_job(self._db, job_id, **updates)
        self.job_updated.emit(job_id)

    def _on_resolve_done(
        self, job_id: str, version_id, api_type: str, model_id, model_name: str,
        filename: str = "",
    ):
        """バージョン解決完了→UIスレッドでDB更新"""
        if self._shutting_down:
            return
        job = repo.get_job(self._db, job_id)
        if not job:
            return

        updates = dict(
            model_version_id=version_id,
            model_type=api_type,
            model_id=model_id,
            model_name=model_name,
            status=JobStatus.PENDING.value,
            download_url=f"{CIVITAI_BASE_URL}/api/download/models/{version_id}",
        )

        # APIから取得したファイル名でプレースホルダーを置換
        if filename:
            updates["filename"] = filename

        repo.update_job(self._db, job_id, **updates)
        self.job_updated.emit(job_id)

        # 推奨プリセットタスクも起動
        self._start_recommend_task(job_id, version_id)

    def _on_resolve_failed(self, job_id: str, error_message: str):
        """バージョン解決失敗時にジョブを失敗状態へ更新"""
        if self._shutting_down:
            return
        job = repo.get_job(self._db, job_id)
        if not job:
            return
        repo.update_job(
            self._db, job_id,
            status=JobStatus.FAILED.value,
            error_message=error_message,
        )
        self.job_updated.emit(job_id)
        self.job_finished.emit(job_id, JobStatus.FAILED.value)
        logger.warning(f"バージョン解決失敗: {job_id} - {error_message}")

    # ──── 補助タスク起動 ────

    def _start_recommend_task(self, job_id: str, version_id: int):
        """推奨プリセット判定タスクを起動"""
        if self._shutting_down:
            return
        api_key = repo.get_setting(self._db, "api_key", "")
        task = RecommendTask(
            job_id=job_id,
            version_id=version_id,
            api_key=api_key,
            presets=self._presets_cache,
        )
        task.signals.done.connect(self._on_recommend_done)
        self._thread_pool.start(task)

    def _start_resolve_task(self, job_id: str, page_url: str):
        """バージョン解決タスクを起動"""
        if self._shutting_down:
            return
        api_key = repo.get_setting(self._db, "api_key", "")
        task = VersionResolveTask(
            job_id=job_id,
            page_url=page_url,
            api_key=api_key,
        )
        task.signals.resolved.connect(self._on_resolve_done)
        task.signals.failed.connect(self._on_resolve_failed)
        self._thread_pool.start(task)

    # ──── モデル追跡登録 ────

    def _register_tracking_for_job(self, job_id: str):
        """DL完了時にモデルを追跡リストに登録"""
        if self._shutting_down:
            return
        job = repo.get_job(self._db, job_id)
        if job and job.get("model_id") and job.get("model_version_id"):
            repo.register_tracking(
                self._db,
                model_id=job["model_id"],
                model_name=job.get("model_name", ""),
                version_id=job["model_version_id"],
                version_name="",
                model_type=job.get("model_type", ""),
            )

    def _cleanup_job_temp_files(self, job_id: str):
        """DB に残っている temp_path とその .part を削除する"""
        job = repo.get_job(self._db, job_id)
        if not job:
            return

        temp_path = job.get("temp_path", "")
        if not temp_path:
            return

        cleanup_targets = [temp_path, temp_path + ".part"]
        for target in cleanup_targets:
            try:
                os.remove(target)
            except FileNotFoundError:
                continue
            except OSError as exc:
                logger.warning("一時ファイル削除失敗 [%s]: %s", job_id, exc)
