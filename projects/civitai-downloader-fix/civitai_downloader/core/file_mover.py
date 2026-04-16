"""ファイル移動責務"""

import logging
import os
import shutil

logger = logging.getLogger(__name__)


class FileMover:
    """temp_dir内のファイルをプリセットパスまたはUnsortedへ移動する"""

    @staticmethod
    def move_to_dest(
        temp_file: str,
        filename: str,
        preset_path: str | None,
        unsorted_dir: str,
    ) -> tuple[str, str]:
        """
        ファイルを最終保存先へ移動する。

        Args:
            temp_file: temp_dir内のダウンロード済みファイルパス
            filename: 最終ファイル名
            preset_path: プリセットで指定された保存先パス（空やNoneならunsorted）
            unsorted_dir: 未分類保存先ディレクトリ

        Returns:
            (status, dest_path)
            status: "completed" or "skipped"

        Raises:
            OSError: ファイル移動に失敗した場合
        """
        # 保存先ディレクトリ決定
        dest_dir = preset_path if preset_path else unsorted_dir
        os.makedirs(dest_dir, exist_ok=True)

        dest_path = os.path.join(dest_dir, filename)

        # 同名ファイルが既に存在→スキップ
        if os.path.exists(dest_path):
            # temp_fileを削除（不要）
            try:
                os.remove(temp_file)
            except OSError:
                pass
            logger.info(f"スキップ（同名存在）: {dest_path}")
            return "skipped", dest_path

        # 移動実行
        shutil.move(temp_file, dest_path)
        logger.info(f"ファイル移動: {temp_file} → {dest_path}")
        return "completed", dest_path
