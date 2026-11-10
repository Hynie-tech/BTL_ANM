"""Kiem thu tich hop: du lieu gia lap -> train -> nguong -> hang doi nguoi -> drift -> bao cao."""
import tempfile
import unittest

import numpy as np
import pandas as pd

import conftest  # noqa: F401
from conftest import CFG
from src.evaluation.metrics import at_threshold
from src.evaluation.thresholds import AlertPolicy
from src.hitl.triage import build_review_queue, simulate_analyst, summarize_triage
from src.models.model_builder import score
from src.models.model_registry import ModelRegistry
from src.monitoring.drift_detector import band_psi, feature_drift_table, summarize_drift
from src.preprocessing.data_loader import to_xy
from src.simulation.drift_scenarios import make_scenario
from src.training.trainer import train_and_register


def synthetic_flows(n=8000, seed=0):
    rng = np.random.default_rng(seed)
    att = rng.random(n) < 0.05
    dur = np.where(att, rng.lognormal(9, 0.3, n), rng.lognormal(12, 1.0, n))
    pk = np.where(att, rng.integers(3, 8, n), rng.integers(2, 60, n))
    df = pd.DataFrame({"Flow Duration": dur, "Flow IAT Mean": dur / pk, "Flow Packets/s": pk / dur * 1e6,
                       "Total Fwd Packets": pk, "Fwd Packet Length Max": rng.normal(100, 30, n) + 80 * att})
    df["Label"] = np.where(att, "SSH-Patator", "Benign")
    return df.astype({c: "float32" for c in df.columns if c != "Label"})


class TestEndToEnd(unittest.TestCase):
    def test_full_lifecycle_on_synthetic_data(self):
        cfg = {**CFG, "models": {**CFG["models"], "random_forest": {**CFG["models"]["random_forest"],
                                                                      "n_estimators": 20, "n_jobs": 1}}}
        df = synthetic_flows()
        tr, va, te = df.iloc[:4800], df.iloc[4800:6400], df.iloc[6400:]
        Xtr, ytr, _ = to_xy(tr, cfg); Xva, yva, _ = to_xy(va, cfg); Xte, yte, _ = to_xy(te, cfg)
        with tempfile.TemporaryDirectory() as d:
            reg = ModelRegistry(d)
            r = train_and_register("random_forest", cfg, Xtr, ytr, Xva, yva, reg, "fp")
            r2 = train_and_register("logreg", cfg, Xtr, ytr, Xva, yva, reg, "fp")
            pipeP, mP = reg.load("random_forest", "v1"); pipeS, mS = reg.load("logreg", "v1")
            thr = mP["thresholds"]
            sP, sS = score(pipeP, Xte), score(pipeS, Xte)
            m = at_threshold(yte, sP, thr["operating"])
            self.assertGreater(m["f1"], 0.9)

            pol = AlertPolicy(thr["t_review"], thr["t_alert"])
            q = simulate_analyst(build_review_queue(sP, sS, pol, mS["thresholds"]["operating"], cfg), yte, 0.0)
            self.assertGreater(summarize_triage(q, 0.0)["system_recall"], 0.9)

            # drift: lam cham tan cong -> hieu nang chi-may tut, phat hien duoc qua ty le du doan
            dd = make_scenario(te.reset_index(drop=True), "evasion_low_slow",
                               {"attack_time_scale_median": 30.0, "attack_time_scale_sigma": 0.1}, cfg, 0)
            Xd, yd, _ = to_xy(dd, cfg)
            sd = score(pipeP, Xd)
            self.assertLess(at_threshold(yd, sd, thr["operating"])["recall"], m["recall"])
            tab = feature_drift_table(Xva, Xd, cfg["monitoring"])
            base = float((score(pipeP, Xva) >= thr["operating"]).mean())
            s = summarize_drift(tab, band_psi(score(pipeP, Xva), sd, [thr["t_review"], thr["operating"], thr["t_alert"]]),
                                float((sd >= thr["operating"]).mean()), base, cfg["monitoring"])
            self.assertIn(s["label_free_status"], ("DRIFT", "STABLE"))


if __name__ == "__main__":
    unittest.main()
