import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication

from core.layout_engine import LayoutEngine
from core.presets import PresetRegistry
from ui.main_window import MainWindow


class RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self._temp_dir.name)

    def tearDown(self):
        self._temp_dir.cleanup()

    def _make_image_file(self, name: str, color: str) -> Path:
        path = self.temp_path / name
        Image.new("RGB", (800, 600), color=color).save(path)
        return path

    def test_comparison_presets_define_split_ratio(self):
        registry = PresetRegistry()
        registry.load_builtin()

        expected = [
            "vsplit",
            "hsplit",
            "arrow_compare",
            "label_compare",
            "bg_color_split",
            "blur_border",
            "fade_transition",
            "diagonal_wipe",
        ]
        for preset_name in expected:
            preset = registry.get(preset_name)
            self.assertIsNotNone(preset, preset_name)
            self.assertIn("split_ratio", preset.parameters, preset_name)

    def test_diagonal_slot_polygons_match_split_structure(self):
        engine = LayoutEngine()

        polygons = engine.compute_slot_polygons(
            "diagonal_wipe",
            {"split_ratio": 0.5, "angle": 30},
            (1200, 900),
            2,
        )

        self.assertEqual(set(polygons.keys()), {0, 1})
        self.assertEqual(len(polygons[0]), 4)
        self.assertEqual(len(polygons[1]), 4)
        self.assertEqual(polygons[0][0], (0.0, 0.0))
        self.assertEqual(polygons[0][-1], (0.0, 900.0))
        self.assertEqual(polygons[1][1], (1200.0, 0.0))
        self.assertEqual(polygons[1][2], (1200.0, 900.0))

    def test_catalog_asymmetric_fill_mode_is_accepted(self):
        registry = PresetRegistry()
        registry.load_builtin()
        preset = registry.get("catalog")
        self.assertIsNotNone(preset)

        engine = LayoutEngine()
        images = [
            Image.new("RGB", (600, 400), "red"),
            Image.new("RGB", (600, 400), "blue"),
        ]
        result = engine.compose(
            preset,
            images,
            {"gap": 4, "bg_color": "#000000", "fill_mode": "asymmetric"},
            (1200, 900),
        )

        self.assertEqual(result.size, (1200, 900))

    def test_hero_top_strip_bounds_cover_expected_slots(self):
        engine = LayoutEngine()
        bounds = engine.compute_cell_bounds(
            "hero_top_strip",
            {"gap": 4, "top_ratio": 0.66},
            (1200, 900),
            4,
        )

        self.assertEqual(set(bounds.keys()), {0, 1, 2, 3})
        self.assertEqual(bounds[0], (0, 0, 1200, int(900 * 0.66)))
        self.assertEqual(bounds[1][1], int(900 * 0.66) + 4)
        self.assertEqual(bounds[2][1], int(900 * 0.66) + 4)
        self.assertEqual(bounds[3][1], int(900 * 0.66) + 4)

    def test_project_state_round_trip_restores_core_fields(self):
        image_a = self._make_image_file("a.jpg", "red")
        image_b = self._make_image_file("b.jpg", "blue")

        window = MainWindow()
        try:
            window._on_images_dropped([image_a, image_b])
            preset = window.preset_registry.get("diagonal_wipe")
            self.assertIsNotNone(preset)
            window.preset_panel.select_preset("diagonal_wipe", preset.get_defaults())
            window._on_preset_changed("diagonal_wipe")
            window._current_work_id = "WORK-001"
            window._current_params["split_ratio"] = 0.62
            window._current_params["angle"] = 25
            window.preset_panel.set_param_value("split_ratio", 0.62)
            window.preset_panel.set_param_value("angle", 25)
            window._assigned_image_paths = [str(image_b), str(image_a)]
            window.preset_panel.set_assigned_paths(window._assigned_image_paths)
            window._crop_offsets_by_path = {
                str(image_a): (0.1, -0.2, 1.3),
                str(image_b): (-0.1, 0.2, 1.1),
            }

            saved = window._serialize_project_state()

            restored = MainWindow()
            try:
                restored._restore_project_state(saved)

                self.assertEqual(restored._current_work_id, "WORK-001")
                self.assertIsNotNone(restored._current_preset)
                self.assertEqual(restored._current_preset.name, "diagonal_wipe")
                self.assertEqual(restored._current_params["split_ratio"], 0.62)
                self.assertEqual(restored._current_params["angle"], 25)
                self.assertEqual(
                    restored._assigned_image_paths,
                    [str(image_b), str(image_a)],
                )
                self.assertEqual(
                    restored._crop_offsets_by_path[str(image_a)],
                    (0.1, -0.2, 1.3),
                )
                self.assertEqual(
                    restored._crop_offsets_by_path[str(image_b)],
                    (-0.1, 0.2, 1.1),
                )
                self.assertEqual(
                    [str(entry.path) for entry in restored._selected_images],
                    [str(image_a), str(image_b)],
                )
            finally:
                restored.close()
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
