import tempfile
import unittest

import numpy as np

import conftest  # noqa: F401
from conftest import CFG, toy_xy
from src.models.model_registry import ModelRegistry
from src.training.trainer import (decide_promotion, make_thresholds, passes_quality_gate,
                                  retrain_candidate, train_and_register)


class TestTrainer(unittest.TestCase):
    def test_gate(self):
        g = CFG["quality_gate"]
        self.assertTrue(passes_quality_gate({"recall": 0.99, "precision": 0.99, "f1": 0.99}, g))
        self.assertFalse(passes_quality_gate({"recall": 0.5, "precision": 0.99, "f1": 0.66}, g))

    def test_train_and_register_promotes_good_model(self):
        X, y = toy_xy(6000, seed=1)
        # lam bai de de (tach ro) de qua gate
        X["a"] = X["a"] + 6 * y
        Xtr, ytr, Xva, yva = X.iloc[:4000], y[:4000], X.iloc[4000:], y[4000:]
        with tempfile.TemporaryDirectory() as d:
            reg = ModelRegistry(d)
            r = train_and_register("random_forest", {**CFG, "models": {**CFG["models"], "random_forest": {
                **CFG["models"]["random_forest"], "n_estimators": 10, "n_jobs": 1}}},
                Xtr, ytr, Xva, yva, reg, fingerprint="abc")
            self.assertEqual(r["version"], "v1")
            self.assertTrue(r["gate_passed"])
            self.assertEqual(reg.get_version("random_forest", stage="production"), "v1")
            self.assertLessEqual(r["thresholds"]["t_review"], r["thresholds"]["t_alert"])

    def test_retrain_candidate_returns_thresholds(self):
        X, y = toy_xy(3000)
        w = np.ones(len(y))
        pipe, thr, m = retrain_candidate("logreg", CFG, X, y, w, X, y)
        self.assertIn("operating", thr)
        self.assertGreater(m["average_precision"], 0.5)

    def test_decide_promotion(self):
        ok = {"recall": 0.99, "precision": 0.99}
        self.assertTrue(decide_promotion(0.1, 0.0, ok, CFG))
        self.assertFalse(decide_promotion(-0.01, 0.0, ok, CFG))               # khong tot hon tren drift
        self.assertFalse(decide_promotion(0.1, 0.5, ok, CFG))                 # thoai lui tren du lieu goc


if __name__ == "__main__":
    unittest.main()
