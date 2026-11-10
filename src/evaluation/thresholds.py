"""Chon nguong canh bao tu TAP VALIDATION (khong bao gio tu tap test).
Co 3 chien luoc: theo precision muc tieu, theo recall muc tieu, theo chi phi (cost-sensitive)."""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
from sklearn.metrics import precision_recall_curve


def threshold_for_precision(y, score, target: float) -> float:
    """Nguong THAP NHAT sao cho precision >= target (toi da hoa recall khi van giu precision)."""
    prec, _, thr = precision_recall_curve(y, score)
    ok = np.where(prec[:-1] >= target)[0]
    return float(thr[ok[0]]) if len(ok) else float(thr[-1])


def threshold_for_recall(y, score, target: float) -> float:
    """Nguong CAO NHAT sao cho recall >= target (it canh bao gia nhat van bat du tan cong)."""
    prec, rec, thr = precision_recall_curve(y, score)
    ok = np.where(rec[:-1] >= target)[0]
    return float(thr[ok[-1]]) if len(ok) else float(thr[0])


def threshold_min_cost(y, score, c_fn: float, c_fp: float, grid: int = 1000) -> float:
    y = np.asarray(y)
    cands = np.unique(np.quantile(score, np.linspace(0, 1, grid)))
    best, best_c = 0.5, np.inf
    for t in cands:
        pred = score >= t
        fn = int(((y == 1) & ~pred).sum())
        fp = int(((y == 0) & pred).sum())
        c = c_fn * fn + c_fp * fp
        if c < best_c:
            best, best_c = float(t), c
    return best


def threshold_max_f1(y, score) -> float:
    prec, rec, thr = precision_recall_curve(y, score)
    f1 = 2 * prec[:-1] * rec[:-1] / np.clip(prec[:-1] + rec[:-1], 1e-12, None)
    return float(thr[int(np.argmax(f1))])


@dataclass
class AlertPolicy:
    """Chinh sach 3 vung:  score >= t_alert -> ALERT (xu ly uu tien)
                          t_review <= score < t_alert -> REVIEW (nguoi xac minh)
                          score < t_review -> IGNORE (chi ghi log + lay mau kiem tra)"""
    t_review: float
    t_alert: float

    def zones(self, score) -> np.ndarray:
        s = np.asarray(score)
        z = np.full(len(s), "ignore", dtype=object)
        z[s >= self.t_review] = "review"
        z[s >= self.t_alert] = "alert"
        return z

    def to_dict(self) -> dict:
        return asdict(self)


def build_policy(y_val, s_val, cfg: dict) -> tuple[AlertPolicy, dict]:
    ap = cfg["alert_policy"]
    t_alert = threshold_for_precision(y_val, s_val, ap["target_precision_alert"])
    t_review = threshold_for_recall(y_val, s_val, ap["target_recall_review"])
    t_review = min(t_review, t_alert)  # vung review luon nam duoi vung alert
    extra = {
        "t_f1_max": threshold_max_f1(y_val, s_val),
        "t_min_cost": threshold_min_cost(y_val, s_val, ap["cost_fn"], ap["cost_fp"]),
        "default_0.5": 0.5,
    }
    return AlertPolicy(t_review=t_review, t_alert=t_alert), extra
