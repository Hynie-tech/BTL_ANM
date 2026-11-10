import tempfile
import unittest

import conftest  # noqa: F401
from conftest import CFG, toy_xy
from src.models.model_builder import build_pipeline, score
from src.models.model_inspector import describe, kept_feature_names, top_features
from src.models.model_registry import ModelRegistry


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.X, self.y = toy_xy()
        self.pipe = build_pipeline("logreg", CFG).fit(self.X, self.y)
        self.kw = dict(metrics={"f1": 0.9}, thresholds={"operating": 0.5}, params={}, data_fingerprint="x",
                       feature_names=list(self.X.columns))

    def test_version_promote_rollback_load(self):
        with tempfile.TemporaryDirectory() as d:
            reg = ModelRegistry(d)
            v1 = reg.register("m", self.pipe, **self.kw); reg.promote("m", v1)
            v2 = reg.register("m", self.pipe, parent_version=v1, **self.kw); reg.promote("m", v2)
            self.assertEqual((v1, v2), ("v1", "v2"))
            self.assertEqual(reg.get_version("m", stage="production"), "v2")
            self.assertEqual(reg.rollback("m"), "v1")
            est, meta = reg.load("m", stage="production")
            self.assertEqual(meta["version"], "v1")
            self.assertEqual(len(meta["model_sha256"]), 64)
            self.assertAlmostEqual(float(score(est, self.X)[0]), float(score(self.pipe, self.X)[0]))

    def test_rollback_without_archived_raises(self):
        with tempfile.TemporaryDirectory() as d:
            reg = ModelRegistry(d)
            reg.promote("m", reg.register("m", self.pipe, **self.kw))
            with self.assertRaises(RuntimeError):
                reg.rollback("m")

    def test_unknown_model_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(KeyError):
                ModelRegistry(d).get_version("khong_co")


class TestInspector(unittest.TestCase):
    def test_top_features_and_kept(self):
        X, y = toy_xy()
        for name in ("logreg", "random_forest"):
            pipe = build_pipeline(name, CFG).fit(X, y)
            self.assertNotIn("const", kept_feature_names(pipe, list(X.columns)))
            self.assertEqual(top_features(pipe, list(X.columns), 3)[0]["feature"], "a")
            self.assertEqual(describe(pipe)["n_features_kept"], 3)


if __name__ == "__main__":
    unittest.main()
