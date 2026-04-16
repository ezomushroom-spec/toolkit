from __future__ import annotations

import logging
from pathlib import Path

from app.core.batch.models import BatchResult
from app.core.batch.runner import BatchRunner
from app.core.recipe.models import Recipe


class BatchViewModel:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.runner = BatchRunner()
        self.logger = logger

    def run(self, input_dir: Path, output_dir: Path, recipe: Recipe, on_progress) -> BatchResult:
        if self.logger is not None:
            self.logger.info("一括適用を開始: input=%s output=%s recipe=%s", input_dir, output_dir, recipe.recipe_name)
        result = self.runner.run(input_dir, output_dir, recipe, on_progress)
        if self.logger is not None:
            self.logger.info(
                "一括適用を終了: processed=%s success=%s failure=%s cancelled=%s",
                result.processed,
                len(result.successes),
                len(result.failures),
                result.cancelled,
            )
        return result

    def cancel(self) -> None:
        self.runner.request_cancel()
        if self.logger is not None:
            self.logger.info("一括適用の中断要求")
