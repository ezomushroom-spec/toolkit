from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from app.core.engine.context import ExecutionContext
from app.core.engine.executor import RecipeExecutor
from app.core.image_io.path_resolver import OutputPathResolver
from app.core.image_io.reader import ImageReader
from app.core.image_io.writer import ImageWriter
from app.core.recipe.loader import RecipeLoader
from app.core.recipe.models import Recipe, RecipeStep
from app.core.recipe.schema import STEP_LABELS, build_default_params
from app.core.recipe.serializer import RecipeSerializer


class EditorViewModel:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.executor = RecipeExecutor()
        self.recipe = Recipe.create()
        self.current_image_path: Path | None = None
        self.current_image: np.ndarray | None = None
        self.preview_image: np.ndarray | None = None
        self.current_recipe_path: Path | None = None
        self.dirty = False
        self.logger = logger

    def open_image(self, path: Path) -> np.ndarray:
        self.current_image_path = path
        self.current_image = ImageReader.read(path)
        if self.logger is not None:
            self.logger.info("画像を読み込み: %s", path)
        return self.render_preview()

    def render_preview(self) -> np.ndarray:
        if self.current_image is None:
            raise ValueError("画像が開かれていません。")
        self.preview_image = self.executor.run(self.current_image, self.recipe, self.preview_context())
        return self.preview_image

    @staticmethod
    def preview_context() -> ExecutionContext:
        return ExecutionContext(is_preview=True)

    def export_image(self, output_dir: Path) -> Path:
        if self.current_image is None or self.current_image_path is None:
            raise ValueError("画像が開かれていません。")
        rendered = self.executor.run(self.current_image, self.recipe, ExecutionContext())
        output_path = OutputPathResolver.build_output_path(self.current_image_path, output_dir, self.recipe.recipe_name)
        ImageWriter.write(rendered, output_path)
        if self.logger is not None:
            self.logger.info("画像を書き出し: source=%s output=%s recipe=%s", self.current_image_path, output_path, self.recipe.recipe_name)
        return output_path

    def add_step(self, step_type: str) -> RecipeStep:
        step = RecipeStep.create(step_type, build_default_params(step_type))
        self.recipe.steps.append(step)
        self.recipe.touch()
        self.dirty = True
        return step

    def remove_step(self, index: int) -> None:
        if 0 <= index < len(self.recipe.steps):
            self.recipe.steps.pop(index)
            self.recipe.touch()
            self.dirty = True

    def move_step(self, index: int, offset: int) -> int:
        new_index = index + offset
        if not (0 <= index < len(self.recipe.steps) and 0 <= new_index < len(self.recipe.steps)):
            return index
        self.recipe.steps[index], self.recipe.steps[new_index] = self.recipe.steps[new_index], self.recipe.steps[index]
        self.recipe.touch()
        self.dirty = True
        return new_index

    def save_recipe(self, path: Path) -> None:
        self.current_recipe_path = path
        RecipeSerializer.save(self.recipe, path)
        self.dirty = False
        if self.logger is not None:
            self.logger.info("レシピを保存: %s", path)

    def load_recipe(self, path: Path) -> None:
        self.recipe = RecipeLoader.load(path)
        self.current_recipe_path = path
        self.dirty = False
        if self.logger is not None:
            self.logger.info("レシピを読込: %s", path)

    def step_label(self, step_type: str) -> str:
        return STEP_LABELS.get(step_type, step_type)
