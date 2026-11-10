"""Huan luyen, chon nguong tren VALIDATION, dang ky vao registry, quality gate, retrain."""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from ..evaluation.metrics import at_threshold, threshold_free
from ..evaluation.thresholds import build_policy
from ..models.model_builder import build_pipeline, score
from ..models.model_inspector import kept_feature_names
from ..models.model_registry import ModelRegistry


def passes_quality_gate(metrics: dict, gate: dict) -> bool:
    return bool(metrics["recall"] >= gate["min_recall"] and metrics["precision"] >= gate["min_precision"]
                and metrics["f1"] >= gate["min_f1"])


def make_thresholds(y_val, s_val, cfg: dict) -> dict:
    """operating = nguong toi da F1 tren validation; t_alert / t_review cho chinh sach 3 vung."""
    policy, extra = build_policy(y_val, s_val, cfg)
    return {"operating": extra["t_f1_max"], "t_alert": policy.t_alert, "t_review": policy.t_review,
            "t_min_cost": extra["t_min_cost"], "default": 0.5}


def train_and_register(name: str, cfg: dict, Xtr, ytr, Xva, yva, registry: ModelRegistry,
                       fingerprint: str, notes: str = "") -> dict:
    """Huan luyen -> chon nguong tren validation -> dang ky (staging) -> quality gate -> promote."""
    pipe = build_pipeline(name, cfg)
    t0 = time.time()
    pipe.fit(Xtr, ytr)
    fit_s = time.time() - t0

    s_val = score(pipe, Xva)
    thr = make_thresholds(yva, s_val, cfg)
    m_op = at_threshold(yva, s_val, thr["operating"])
    m_op.update(threshold_free(yva, s_val))
    passed = passes_quality_gate(m_op, cfg["quality_gate"])
    version = registry.register(
        name, pipe, metrics={**m_op, "split": "validation", "fit_seconds": fit_s}, thresholds=thr,
        params=cfg["models"][name], data_fingerprint=fingerprint, feature_names=list(Xtr.columns),
        notes=notes or "Huan luyen ban dau tren train split; nguong chon tren validation.")
    if passed:
        registry.promote(name, version)
    return {"version": version, "gate_passed": passed, "fit_seconds": fit_s, "val_at_operating": m_op,
            "thresholds": thr, "n_features_kept": len(kept_feature_names(pipe, list(Xtr.columns)))}


def retrain_candidate(name: str, cfg: dict, X_new, y_new, sample_weight, X_val, y_val):
    """Huan luyen phien ban ung vien (v2) tren du lieu moi (train + feedback co trong so).
    Tra ve (pipeline, thresholds, metrics tren validation moi)."""
    pipe = build_pipeline(name, cfg)
    pipe.fit(X_new, y_new, model__sample_weight=sample_weight)
    s_val = score(pipe, X_val)
    thr = make_thresholds(y_val, s_val, cfg)
    m = {**at_threshold(y_val, s_val, thr["operating"]), **threshold_free(y_val, s_val),
         "split": "validation(goc+drift)"}
    return pipe, thr, m


def decide_promotion(f1_gain_on_drift: float, regression_on_original: float, val_metrics: dict,
                     cfg: dict) -> bool:
    """Quality gate khi retrain: phai tot hon tren drift, khong thoai lui tren du lieu goc,
    va dat nguong toi thieu."""
    r, g = cfg["retrain"], cfg["quality_gate"]
    return bool(f1_gain_on_drift > 0 and regression_on_original <= r["max_regression"]
                and val_metrics["recall"] >= g["min_recall"] and val_metrics["precision"] >= g["min_precision"])
