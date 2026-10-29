"""Run the actual Python example embedded in both article translations."""
from html import unescape
from pathlib import Path
import re
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "insights/opencv-pixelflaeche-konturflaeche-python.html",
    "en/insights/opencv-pixel-area-contour-area-python.html",
]

def example(file):
    return unescape(re.search(
        r'<code class="language-python">(.*?)</code>',
        (ROOT / file).read_text(encoding="utf-8"), re.S
    )[1])

scope = {"__name__": "article_test"}
exec(compile(example(PAGES[0]), PAGES[0], "exec"), scope)
compare = scope["compare_areas"]


class AreaTests(unittest.TestCase):
    def test_translations_match(self):
        self.assertEqual(example(PAGES[0]), example(PAGES[1]))

    def test_square_and_hole(self):
        square = np.zeros((20, 20), dtype=np.uint8)
        square[5:15, 5:15] = 255
        original = square.copy()
        self.assertEqual(compare(square), {
            "objects": 1, "pixel_areas": [100],
            "outer_contour_areas": [81.0],
        })
        np.testing.assert_array_equal(square, original)
        square[8:12, 8:12] = 0
        self.assertEqual(compare(square), {
            "objects": 1, "pixel_areas": [84],
            "outer_contour_areas": [81.0],
        })

    def test_diagonal_connectivity(self):
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[3, 3] = mask[4, 4] = 255
        self.assertEqual(compare(mask, 4)["pixel_areas"], [1, 1])
        self.assertEqual(compare(mask, 8)["pixel_areas"], [2])

    def test_empty_foreground_and_single_pixel(self):
        mask = np.zeros((10, 10), dtype=np.uint8)
        self.assertEqual(compare(mask), {
            "objects": 0, "pixel_areas": [], "outer_contour_areas": [],
        })
        mask[3, 3] = 255
        self.assertEqual(compare(mask), {
            "objects": 1, "pixel_areas": [1], "outer_contour_areas": [0.0],
        })

    def test_invalid_inputs(self):
        for value in (None, [], np.zeros((2, 2, 3), np.uint8),
                      np.zeros((2, 2), float), np.zeros((0, 0), np.uint8),
                      np.ones((2, 2), np.uint8)):
            with self.subTest(value=str(type(value))):
                with self.assertRaises(ValueError):
                    compare(value)
        with self.assertRaises(ValueError):
            compare(np.zeros((10, 10), np.uint8), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
