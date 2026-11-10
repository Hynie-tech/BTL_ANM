import unittest

import numpy as np

import conftest  # noqa: F401
from conftest import CFG
from src.evaluation.thresholds import AlertPolicy
from src.hitl.triage import (audit_estimate, build_review_queue, capacity_thresholds, project_workload,
                             simulate_analyst, summarize_triage)


class TestTriage(unittest.TestCase):
    def test_queue_rules(self):
        pol = AlertPolicy(t_review=0.2, t_alert=0.6)
        sP = np.array([0.9, 0.9, 0.4, 0.05, 0.05, 0.01])
        sS = np.array([0.99, 0.10, 0.10, 0.99, 0.10, 0.10])
        cfg = {**CFG, "hitl": {**CFG["hitl"], "audit_rate": 0.0, "p3_review_fraction": 1.0}}
        q = build_review_queue(sP, sS, pol, 0.5, cfg)
        self.assertEqual(list(q["queue"]), ["P1_alert", "P2_review", "P2_review", "P3_spotcheck", "ignore", "ignore"])

    def test_summary_recall_with_perfect_analyst(self):
        rng = np.random.default_rng(0)
        y = (rng.random(5000) < 0.05).astype(int)
        sP = np.where(y == 1, 0.95, 0.02)
        cfg = {**CFG, "hitl": {**CFG["hitl"], "audit_rate": 0.01}}
        q = simulate_analyst(build_review_queue(sP, sP, AlertPolicy(0.2, 0.6), 0.5, cfg), y, 0.0)
        s = summarize_triage(q, 0.0)
        self.assertEqual(s["system_recall"], 1.0)
        self.assertEqual(s["false_alarms_confirmed_wrongly"], 0)

    def test_analyst_error_lowers_recall(self):
        rng = np.random.default_rng(0)
        y = (rng.random(20000) < 0.05).astype(int)
        sP = np.where(y == 1, 0.95, 0.02)
        q = build_review_queue(sP, sP, AlertPolicy(0.2, 0.6), 0.5, {**CFG, "hitl": {**CFG["hitl"], "audit_rate": 0.0}})
        r0 = summarize_triage(simulate_analyst(q, y, 0.0, 1), 0.0)["system_recall"]
        r1 = summarize_triage(simulate_analyst(q, y, 0.1, 1), 0.1)["system_recall"]
        self.assertLess(r1, r0)

    def test_workload_monotonic(self):
        h = CFG["hitl"]
        a = project_workload(0.99, 0.001, 0.01, h); b = project_workload(0.99, 0.01, 0.01, h)
        c = project_workload(0.99, 0.001, 0.0001, h)
        self.assertGreater(b["analyst_shifts_per_day"], a["analyst_shifts_per_day"])
        self.assertLess(c["queue_precision"], a["queue_precision"])

    def test_audit_estimate_corrects_analyst_error(self):
        # 3% analyst sai, mau toan benign: ~3% 'duong tinh' -> uoc luong sau hieu chinh ~ 0
        e = audit_estimate(k=3, n_audit=100, n_ignored=10000, analyst_error=0.03, true_missed=0)
        self.assertEqual(e["miss_rate_corrected"], 0.0)
        self.assertAlmostEqual(e["detection_limit_rule_of_three"], 0.03)

    def test_capacity_thresholds_fewer_shifts_at_higher_threshold(self):
        rng = np.random.default_rng(0)
        y = (rng.random(20000) < 0.05).astype(int)
        s = np.where(y == 1, rng.beta(5, 2, 20000), rng.beta(1, 8, 20000))
        rows = capacity_thresholds(y, s, 0.001, CFG["hitl"])
        self.assertGreaterEqual(rows[0]["analyst_shifts_per_day"], rows[-1]["analyst_shifts_per_day"])


if __name__ == "__main__":
    unittest.main()
