"""Do drift: PSI (Population Stability Index) + KS cho tung dac trung, drift cua diem so mo hinh,
ty le canh bao. Day la giam sat KHONG can nhan (label-free) - chi la tin hieu som."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


def psi(ref, cur, n_bins: int = 10, eps: float = 1e-4) -> float:
    ref = np.asarray(ref, dtype=np.float64)
    cur = np.asarray(cur, dtype=np.float64)
    ref, cur = ref[np.isfinite(ref)], cur[np.isfinite(cur)]
    if len(ref) == 0 or len(cur) == 0:
        return float("nan")
    inner = np.unique(np.quantile(ref, np.linspace(0, 1, n_bins + 1)[1:-1]))
    k = len(inner) + 1
    # bin dong ben phai (x <= canh): gia tri 0 chiem da so van tach duoc khoi gia tri > 0
    r = np.bincount(np.digitize(ref, inner, right=True), minlength=k) / len(ref)
    c = np.bincount(np.digitize(cur, inner, right=True), minlength=k) / len(cur)
    r, c = np.clip(r, eps, None), np.clip(c, eps, None)
    return float(np.sum((c - r) * np.log(c / r)))


def band_psi(ref_scores, cur_scores, edges, eps: float = 1e-4) -> float:
    """PSI cua diem so tren cac DAI VAN HANH (vd: <t_review | review | >=nguong van hanh).
    PSI theo decile khong hieu qua voi diem so ~97% nam o mot bin (lop tan cong hiem), nen dung dai
    van hanh: bat duoc viec khoi luong 'chay' tu vung canh bao sang vung xem xet / bo qua."""
    e = np.concatenate([[-np.inf], np.unique(np.asarray(edges, dtype=float)), [np.inf]])
    r = np.histogram(ref_scores, bins=e)[0] / len(ref_scores)
    c = np.histogram(cur_scores, bins=e)[0] / len(cur_scores)
    r, c = np.clip(r, eps, None), np.clip(c, eps, None)
    return float(np.sum((c - r) * np.log(c / r)))


def psi_status(v: float, warn: float, alert: float) -> str:
    if not np.isfinite(v):
        return "n/a"
    return "ALERT" if v >= alert else ("WARN" if v >= warn else "OK")


def feature_drift_table(ref: pd.DataFrame, cur: pd.DataFrame, mcfg: dict,
                        features: list[str] | None = None, max_ks: int = 20000,
                        seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    features = features or list(ref.columns)
    rows = []
    for f in features:
        r, c = ref[f].to_numpy(), cur[f].to_numpy()
        v = psi(r, c)
        rs = rng.choice(r, min(len(r), max_ks), replace=False)
        cs = rng.choice(c, min(len(c), max_ks), replace=False)
        ks = ks_2samp(rs, cs).statistic
        rows.append({"feature": f, "psi": v, "ks": float(ks),
                     "status": psi_status(v, mcfg["psi_warn"], mcfg["psi_alert"])})
    return pd.DataFrame(rows).sort_values("psi", ascending=False).reset_index(drop=True)


def summarize_drift(tab: pd.DataFrame, score_psi: float, alert_rate: float,
                    base_alert_rate: float, mcfg: dict) -> dict:
    n = len(tab)
    n_alert = int((tab["status"] == "ALERT").sum())
    n_warn = int((tab["status"] == "WARN").sum())
    share = n_alert / n if n else 0.0
    ratio = alert_rate / base_alert_rate if base_alert_rate > 0 else float("nan")
    lo, hi = mcfg["alert_rate_ratio_warn"]
    reasons = []
    if share >= mcfg["feature_share_alert"]:
        reasons.append(f"{share:.0%} feature co PSI >= {mcfg['psi_alert']}")
    if np.isfinite(score_psi) and score_psi >= mcfg["score_psi_alert"]:
        reasons.append(f"PSI theo dai diem so = {score_psi:.2f}")
    if np.isfinite(ratio) and not (lo <= ratio <= hi):
        reasons.append(f"ty le du doan tan cong x{ratio:.2f} so voi baseline")
    return {
        "n_features": n, "n_feature_alert": n_alert, "n_feature_warn": n_warn,
        "share_feature_alert": share, "max_psi": float(tab["psi"].max()),
        "top_features": tab.head(5)["feature"].tolist(),
        "score_psi": float(score_psi), "alert_rate": float(alert_rate),
        "alert_rate_ratio": float(ratio),
        "label_free_status": "DRIFT" if reasons else "STABLE",
        "reasons": reasons,
    }
