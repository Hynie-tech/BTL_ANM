"""Metric danh gia phat hien tan cong. Nhan manh precision / recall / F1 / FALSE POSITIVE,
khong chi accuracy (accuracy 'danh lua' khi lop tan cong hiem)."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (average_precision_score, matthews_corrcoef, roc_auc_score)


def _div(a, b):
    return float(a / b) if b else 0.0


def binary_report(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    precision = _div(tp, tp + fp)
    recall = _div(tp, tp + fn)
    fpr = _div(fp, fp + tn)
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": int(len(y_true)),
        "n_attack": tp + fn, "prevalence": _div(tp + fn, len(y_true)),
        "precision": precision, "recall": recall,
        "f1": _div(2 * precision * recall, precision + recall),
        "fpr": fpr, "fnr": _div(fn, tp + fn),
        "accuracy": _div(tp + tn, len(y_true)),
        "balanced_accuracy": 0.5 * (recall + _div(tn, tn + fp)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)) if len(np.unique(y_pred)) > 1 or len(np.unique(y_true)) > 1 else 0.0,
        "fp_per_100k_flows": _div(fp, len(y_true)) * 100_000,
    }


def threshold_free(y_true, score) -> dict:
    y_true = np.asarray(y_true)
    if len(np.unique(y_true)) < 2:
        return {"average_precision": float("nan"), "roc_auc": float("nan")}
    return {"average_precision": float(average_precision_score(y_true, score)),
            "roc_auc": float(roc_auc_score(y_true, score))}


def at_threshold(y_true, score, thr: float) -> dict:
    rep = binary_report(y_true, (np.asarray(score) >= thr).astype(int))
    rep["threshold"] = float(thr)
    return rep


def precision_at_prevalence(recall: float, fpr: float, prevalence: float) -> float:
    """Cong thuc Bayes: precision that su neu ty le tan cong ngoai doi thuc = prevalence.
    precision = TPR*p / (TPR*p + FPR*(1-p)).  (Axelsson 2000: base-rate fallacy)"""
    num = recall * prevalence
    den = num + fpr * (1 - prevalence)
    return _div(num, den)


def majority_baseline(y_true) -> dict:
    """Bo phan loai 'luon bao Benign': accuracy rat cao nhung recall = 0."""
    return binary_report(y_true, np.zeros_like(np.asarray(y_true)))


def threshold_table(y_true, score, thresholds) -> list[dict]:
    rows = []
    for t in thresholds:
        r = at_threshold(y_true, score, t)
        rows.append({k: r[k] for k in ("threshold", "precision", "recall", "f1", "fpr", "fp", "fn",
                                       "fp_per_100k_flows")})
    return rows
