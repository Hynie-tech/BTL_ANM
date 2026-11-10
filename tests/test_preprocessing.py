import unittest

import numpy as np
import pandas as pd

import conftest  # noqa: F401
from conftest import CFG, toy_xy
from src.models.model_builder import build_pipeline, score
from src.preprocessing.data_loader import make_splits, to_xy
from src.preprocessing.feature_pipeline import replace_inf, signed_log1p


class TestFeaturePipeline(unittest.TestCase):
    def test_replace_inf(self):
        out = replace_inf(np.array([[1.0, np.inf], [-np.inf, 2.0]]))
        self.assertTrue(np.isnan(out[0, 1]) and np.isnan(out[1, 0]))

    def test_replace_inf_does_not_mutate_input(self):
        a = np.array([[np.inf]], dtype="float32")
        replace_inf(a)
        self.assertTrue(np.isinf(a[0, 0]))

    def test_signed_log1p_keeps_sign_and_order(self):
        x = np.array([-100.0, -1.0, 0.0, 1.0, 100.0])
        y = signed_log1p(x)
        self.assertTrue(np.all(np.diff(y) > 0))
        self.assertEqual(y[2], 0.0)
        self.assertAlmostEqual(y[0], -y[4])

    def test_pipelines_handle_inf_nan_constant(self):
        X, y = toy_xy()
        for name in ("logreg", "random_forest"):
            pipe = build_pipeline(name, CFG).fit(X, y)
            s = score(pipe, X)
            self.assertTrue(((s >= 0) & (s <= 1)).all())
            self.assertGreater(s[y == 1].mean(), s[y == 0].mean())
            self.assertEqual(pipe.named_steps["var"].get_support().sum(), 3)  # bo cot hang so

    def test_unknown_model(self):
        with self.assertRaises(ValueError):
            build_pipeline("khong_co", CFG)


class TestSplits(unittest.TestCase):
    def test_splits_disjoint_cover_and_stratified(self):
        rng = np.random.default_rng(0)
        lab = rng.choice(["Benign", "FTP-Patator", "SSH-Patator"], 5000, p=[0.95, 0.03, 0.02])
        df = pd.DataFrame({"x": rng.normal(size=5000), "Label": lab})
        sp = make_splits(df, CFG)
        allidx = np.concatenate(list(sp.values()))
        self.assertEqual(len(allidx), len(set(allidx)))
        self.assertEqual(len(allidx), len(df))
        prev = [(df.iloc[i]["Label"] != "Benign").mean() for i in sp.values()]
        self.assertLess(max(prev) - min(prev), 0.01)
        X, y, at = to_xy(df.iloc[sp["train"]], CFG)
        self.assertEqual(set(np.unique(y)), {0, 1})


if __name__ == "__main__":
    unittest.main()
