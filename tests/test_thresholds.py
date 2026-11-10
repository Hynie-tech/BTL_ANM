import unittest

import numpy as np

import conftest  # noqa: F401
from conftest import CFG
from src.evaluation.thresholds import (AlertPolicy, build_policy, threshold_for_precision,
                                       threshold_for_recall, threshold_max_f1, threshold_min_cost)


class TestThresholds(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        self.y = np.r_[np.ones(500), np.zeros(5000)].astype(int)
        self.s = np.r_[rng.beta(5, 2, 500), rng.beta(1, 8, 5000)]

    def test_precision_target_met(self):
        t = threshold_for_precision(self.y, self.s, 0.9)
        self.assertGreaterEqual(self.y[self.s >= t].mean(), 0.9)

    def test_recall_target_met(self):
        t = threshold_for_recall(self.y, self.s, 0.95)
        self.assertGreaterEqual((self.s >= t)[self.y == 1].mean(), 0.95)

    def test_cost_threshold_prefers_recall_when_fn_expensive(self):
        self.assertLess(threshold_min_cost(self.y, self.s, 100, 1), threshold_min_cost(self.y, self.s, 1, 100))

    def test_max_f1_in_range(self):
        self.assertTrue(0 <= threshold_max_f1(self.y, self.s) <= 1)

    def test_policy_zones(self):
        z = AlertPolicy(t_review=0.2, t_alert=0.6).zones([0.1, 0.2, 0.59, 0.6, 0.99])
        self.assertEqual(list(z), ["ignore", "review", "review", "alert", "alert"])

    def test_build_policy_review_not_above_alert(self):
        pol, extra = build_policy(self.y, self.s, CFG)
        self.assertLessEqual(pol.t_review, pol.t_alert)
        self.assertIn("t_min_cost", extra)


if __name__ == "__main__":
    unittest.main()
