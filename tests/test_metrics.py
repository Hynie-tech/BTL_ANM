import unittest

import numpy as np

import conftest  # noqa: F401
from src.evaluation.metrics import (at_threshold, binary_report, majority_baseline,
                                    precision_at_prevalence, threshold_table)


class TestMetrics(unittest.TestCase):
    def test_binary_report_counts(self):
        y = np.array([1, 1, 1, 0, 0, 0, 0, 0])
        p = np.array([1, 1, 0, 1, 0, 0, 0, 0])
        r = binary_report(y, p)
        self.assertEqual((r["tp"], r["fp"], r["fn"], r["tn"]), (2, 1, 1, 4))
        self.assertAlmostEqual(r["precision"], 2 / 3)
        self.assertAlmostEqual(r["recall"], 2 / 3)
        self.assertAlmostEqual(r["fpr"], 1 / 5)
        self.assertAlmostEqual(r["fp_per_100k_flows"], 100_000 / 8)

    def test_majority_baseline_accuracy_trap(self):
        r = majority_baseline(np.array([1] * 2 + [0] * 98))
        self.assertAlmostEqual(r["accuracy"], 0.98)
        self.assertEqual((r["recall"], r["f1"]), (0.0, 0.0))

    def test_precision_at_prevalence_bayes(self):
        self.assertAlmostEqual(precision_at_prevalence(1.0, 0.01, 0.01), 0.01 / (0.01 + 0.99 * 0.01))
        self.assertLess(precision_at_prevalence(0.99, 0.001, 1e-4), precision_at_prevalence(0.99, 0.001, 1e-2))

    def test_zero_division_safe(self):
        r = binary_report(np.zeros(5), np.zeros(5))
        self.assertEqual((r["precision"], r["recall"], r["f1"]), (0.0, 0.0, 0.0))

    def test_at_threshold_and_table(self):
        y = np.array([0, 0, 1, 1]); s = np.array([0.1, 0.6, 0.4, 0.9])
        self.assertEqual(at_threshold(y, s, 0.5)["tp"], 1)
        rows = threshold_table(y, s, [0.2, 0.5, 0.8])
        self.assertEqual([r["threshold"] for r in rows], [0.2, 0.5, 0.8])
        self.assertGreaterEqual(rows[0]["recall"], rows[-1]["recall"])  # nguong cao -> recall giam


if __name__ == "__main__":
    unittest.main()
