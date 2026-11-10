import unittest

import numpy as np

import conftest  # noqa: F401
from conftest import CFG, toy_flows
from src.monitoring.drift_detector import band_psi, feature_drift_table, psi, summarize_drift
from src.simulation.drift_scenarios import make_scenario, rate_columns, time_columns


class TestPSI(unittest.TestCase):
    def test_same_distribution_small(self):
        rng = np.random.default_rng(1)
        self.assertLess(psi(rng.normal(size=20000), rng.normal(size=20000)), 0.02)

    def test_shift_large(self):
        a = np.random.default_rng(1).normal(size=20000)
        self.assertGreater(psi(a, a + 1.5), 0.25)

    def test_constant_reference_detects_change(self):
        self.assertGreater(psi(np.zeros(1000), np.r_[np.zeros(500), np.ones(500)]), 0.25)

    def test_band_psi_detects_mass_moving_between_bands(self):
        ref = np.r_[np.full(980, 0.01), np.full(20, 0.9)]
        cur = np.r_[np.full(980, 0.01), np.full(20, 0.3)]
        self.assertGreater(band_psi(ref, cur, [0.15, 0.4]), 0.1)

    def test_feature_table_flags_shifted_feature(self):
        a, b = toy_flows(seed=0), toy_flows(seed=1)
        b["Flow Duration"] *= 3
        t = feature_drift_table(a.drop(columns="Label"), b.drop(columns="Label"),
                                {"psi_warn": 0.1, "psi_alert": 0.25})
        self.assertEqual(t.iloc[0]["feature"], "Flow Duration")
        self.assertEqual(t.iloc[0]["status"], "ALERT")

    def test_summary_flags_alert_rate_drop(self):
        a = toy_flows(seed=0).drop(columns="Label")
        t = feature_drift_table(a, a, CFG["monitoring"])
        s = summarize_drift(t, score_psi=0.0, alert_rate=0.01, base_alert_rate=0.1, mcfg=CFG["monitoring"])
        self.assertEqual(s["label_free_status"], "DRIFT")
        s2 = summarize_drift(t, 0.0, 0.1, 0.1, CFG["monitoring"])
        self.assertEqual(s2["label_free_status"], "STABLE")


class TestScenarios(unittest.TestCase):
    def test_column_detection(self):
        cols = list(toy_flows().columns)
        self.assertIn("Flow Duration", time_columns(cols))
        self.assertIn("Flow Packets/s", rate_columns(cols))

    def test_evasion_only_changes_attacks_and_keeps_consistency(self):
        base = toy_flows()
        d = make_scenario(base, "evasion_low_slow", {"attack_time_scale_median": 8.0,
                          "attack_time_scale_sigma": 0.2}, CFG, seed=0)
        att = (base["Label"] != "Benign").to_numpy()
        self.assertTrue(np.allclose(d.loc[~att, "Flow Duration"], base.loc[~att, "Flow Duration"]))
        ratio = d.loc[att, "Flow Duration"].to_numpy() / base.loc[att, "Flow Duration"].to_numpy()
        self.assertGreater(np.median(ratio), 5)
        pb = base.loc[att, "Flow Duration"] * base.loc[att, "Flow Packets/s"]
        pd_ = d.loc[att, "Flow Duration"] * d.loc[att, "Flow Packets/s"]
        self.assertTrue(np.allclose(pb, pd_, rtol=1e-3))
        self.assertTrue((d["Label"] == base["Label"]).all())

    def test_covariate_changes_all_flows(self):
        base = toy_flows()
        d = make_scenario(base, "covariate_network", {"time_scale_median": 2.0, "time_scale_sigma": 0.1}, CFG, 0)
        self.assertGreater(np.median(d["Flow Duration"] / base["Flow Duration"]), 1.5)

    def test_prevalence_resample(self):
        d = make_scenario(toy_flows(20000), "prevalence_low", {"attack_prevalence": 0.005}, CFG, 0)
        self.assertLess(abs((d["Label"] != "Benign").mean() - 0.005), 0.001)

    def test_unknown_scenario(self):
        with self.assertRaises(ValueError):
            make_scenario(toy_flows(), "khong_ton_tai", {}, CFG, seed=0)


if __name__ == "__main__":
    unittest.main()
