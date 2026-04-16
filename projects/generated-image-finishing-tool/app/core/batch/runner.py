from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.core.batch.models import BatchItemResult, BatchResult
from app.core.engine.context import ExecutionContext
from app.core.engine.executor import RecipeExecutor
from app.core.errors.codes import ErrorCode
from app.core.errors.exceptions import AppError
from app.core.image_io.path_resolver import OutputPathResolver
from app.core.image_io.reader import ImageReader
from app.core.image_io.writer import ImageWriter
from app.core.recipe.models import Recipe


class BatchRunner:
    def __init__(self, executor: RecipeExecutor | None = None) -> None:
        self.executor = executor or RecipeExecutor()
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def reset_cancel(self) -> None:
        self._cancel_requested = False

    def run(
        self,
        input_dir: Path,
        output_dir: Path,
        recipe: Recipe,
        on_progress: Callable[[int, int, Path], None] | None = None,
    ) -> BatchResult:
        self.reset_cancel()
        result = BatchResult()
        self._validate_directories(input_dir, output_dir)
        reserved_names: set[str] = set()
        try:
            targets = sorted(path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() in ImageReader.SUPPORTED_EXTENSIONS)
        except OSError as exc:
            raise AppError(
                ErrorCode.INPUT_FILE_NOT_FOUND,
                "入力フォルダを読み取れませんでした。",
                str(input_dir),
                "フォルダの存在と権限を確認してください。",
            ) from exc
        total = len(targets)

        for index, source in enumerate(targets, start=1):
            if self._cancel_requested:
                result.cancelled = True
                break
            if on_progress is not None:
                on_progress(index, total, source)
            try:
                image = ImageReader.read(source)
                rendered = self.executor.run(image, recipe, ExecutionContext())
                output_path = OutputPathResolver.build_output_path(source, output_dir, recipe.recipe_name, reserved_names)
                reserved_names.add(output_path.name)
                ImageWriter.write(rendered, output_path)
                result.successes.append(BatchItemResult(source, output_path, True, "成功"))
            except AppError as exc:
                result.failures.append(BatchItemResult(source, None, False, exc.message))
            except Exception:  # noqa: BLE001
                result.failures.append(BatchItemResult(source, None, False, "処理中に予期しないエラーが発生しました。ログを確認してください。"))
            finally:
                result.processed += 1
        return result

    @staticmethod
    def _validate_directories(input_dir: Path, output_dir: Path) -> None:
        if not input_dir.exists() or not input_dir.is_dir():
            raise AppError(
                ErrorCode.INPUT_FILE_NOT_FOUND,
                "入力フォルダが見つかりません。",
                str(input_dir),
                "入力フォルダを選び直してください。",
            )
        if not output_dir.exists() or not output_dir.is_dir():
            raise AppError(
                ErrorCode.BATCH_INVALID_OUTPUT_DIR,
                "出力フォルダが見つかりません。",
                str(output_dir),
                "出力フォルダを選び直してください。",
            )
