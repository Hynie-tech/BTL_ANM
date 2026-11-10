import tempfile
import unittest
from pathlib import Path

import pandas as pd

import conftest  # noqa: F401
from conftest import CFG
from src.utils import load_json, md_table
from src.visualization import plot_results as plots
from src.visualization.save_results import save_markdown, save_metrics, save_table


class TestSaveResults(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = self._tmp.name
        self.cfg = {**CFG, "paths": {**CFG["paths"], "metrics_dir": f"{t}/tables", "reports_dir": f"{t}/reports",
                                     "figures_dir": f"{t}/figs"}}

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_metrics_numpy_safe(self):
        import numpy as np
        p = save_metrics(self.cfg, "m.json", {"a": np.float32(1.5), "b": np.arange(3)})
        self.assertEqual(load_json(p), {"a": 1.5, "b": [0, 1, 2]})

    def test_save_table_and_markdown(self):
        p = save_table(self.cfg, "t.csv", pd.DataFrame({"x": [1, 2]}))
        self.assertEqual(pd.read_csv(p)["x"].tolist(), [1, 2])
        q = save_markdown(self.cfg, "reports_dir", "r.md", "# xin chào")
        self.assertEqual(q.read_text(encoding="utf-8"), "# xin chào")

    def test_md_table(self):
        s = md_table([[1, 0.12345]], ["a", "b"])
        self.assertIn("| a | b |", s)
        self.assertIn("0.1235", s)

    def test_figure_is_written(self):
        out = plots.class_distribution({"Benign": 100, "FTP-Patator": 5}, Path(self.cfg["paths"]["figures_dir"]) / "x.png")
        self.assertTrue(Path(out).exists() and Path(out).stat().st_size > 1000)


if __name__ == "__main__":
    unittest.main()
