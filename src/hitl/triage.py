"""Human-in-the-loop: phan luong canh bao (triage), mo phong analyst xac minh,
uoc luong khoi luong cong viec, va lay mau kiem tra (audit) phan bi bo qua."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..evaluation.thresholds import AlertPolicy

QUEUE_PRIORITY = {"P1_alert": 1, "P2_review": 2, "P3_spotcheck": 3, "AUDIT": 4, "P3_logged": 0, "ignore": 0}
HUMAN_QUEUES = ("P1_alert", "P2_review", "P3_spotcheck")
NO_HUMAN = ("ignore", "P3_logged")


def build_review_queue(s_primary, s_secondary, pol_primary: AlertPolicy, thr_agree: float,
                       cfg: dict, seed: int = 0, flow_ids=None) -> pd.DataFrame:
    """Quy tac phan luong (dua tren DONG THUAN cua 2 mo hinh). Chi mo hinh chinh dinh nghia cac vung
    (alert/review/ignore); mo hinh phu cho tin hieu 'dong y' khi diem >= thr_agree.
      P1_alert     : primary=ALERT  va secondary dong y     -> 2 mo hinh cung bao, xu ly uu tien
      P2_review    : primary=ALERT nhung secondary khong dong y, hoac primary=REVIEW -> nguoi xac minh
      P3_spotcheck : primary=IGNORE nhung secondary dong y  -> bat dong; chi KIEM TRA MAU (p3_review_fraction),
                     phan con lai 'P3_logged' chi ghi log. Ty le bat dong cung la tin hieu drift.
      AUDIT        : mau ngau nhien nho trong phan 'ignore' de uoc luong ty le bo sot
      ignore       : chi ghi log"""
    zp = pol_primary.zones(s_primary)
    agree = np.asarray(s_secondary) >= thr_agree
    q = np.full(len(zp), "ignore", dtype=object)
    q[(zp == "alert") & agree] = "P1_alert"
    q[((zp == "alert") & ~agree) | (zp == "review")] = "P2_review"
    rng = np.random.default_rng(seed)
    p3 = np.where((zp == "ignore") & agree)[0]
    q[p3] = "P3_logged"
    if len(p3):
        k = int(round(cfg["hitl"]["p3_review_fraction"] * len(p3)))
        q[rng.choice(p3, k, replace=False)] = "P3_spotcheck"
    ign = np.where(q == "ignore")[0]
    n_aud = int(round(cfg["hitl"]["audit_rate"] * len(q)))
    if n_aud and len(ign):
        q[rng.choice(ign, min(n_aud, len(ign)), replace=False)] = "AUDIT"

    df = pd.DataFrame({
        "flow_id": np.arange(len(q)) if flow_ids is None else flow_ids,
        "score_primary": s_primary, "score_secondary": s_secondary,
        "zone_primary": zp, "secondary_agrees": agree, "queue": q,
    })
    df["priority"] = df["queue"].map(QUEUE_PRIORITY)
    return df


def simulate_analyst(queue_df: pd.DataFrame, y_true, error_rate: float, seed: int = 0) -> pd.DataFrame:
    """Analyst xem cac flow trong hang doi nguoi (P1,P2,P3,AUDIT) va ket luan.
    Phan ket luan bang nhan that nhung sai voi xac suat `error_rate` (con nguoi khong hoan hao)."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y_true).astype(int)
    df = queue_df.copy()
    df["y_true"] = y
    reviewed = df["queue"].isin(HUMAN_QUEUES + ("AUDIT",)).to_numpy()
    flip = rng.random(len(df)) < error_rate
    verdict = np.where(flip, 1 - y, y)
    df["analyst_verdict"] = np.where(reviewed, verdict, -1)  # -1 = khong ai xem
    return df


def project_workload(tpr_q: float, fpr_q: float, prevalence: float, hitl_cfg: dict) -> dict:
    """Ngoai suy khoi luong analyst o ty le tan cong THUC TE (prevalence), dung Bayes.
    Canh bao duoc GOP (aggregation): tan cong thuc -> 1 ticket / `flows_per_attack_alert` flow,
    canh bao gia -> 1 ticket / `flows_per_fp_alert` flow. Ca hai la gia dinh trong config."""
    n = hitl_cfg["flows_per_day"]
    tp_flows = prevalence * tpr_q * n
    fp_flows = (1 - prevalence) * fpr_q * n
    tp_alerts = tp_flows / hitl_cfg["flows_per_attack_alert"]
    fp_alerts = fp_flows / hitl_cfg["flows_per_fp_alert"]
    alerts = tp_alerts + fp_alerts
    minutes = alerts * hitl_cfg["minutes_per_alert"]
    return {"prevalence": prevalence, "queue_rate_flows": (tp_flows + fp_flows) / n,
            "queue_flows_per_day": tp_flows + fp_flows,
            "tp_alerts_per_day": tp_alerts, "fp_alerts_per_day": fp_alerts,
            "queue_items_per_day": alerts, "analyst_minutes_per_day": minutes,
            "analyst_shifts_per_day": minutes / hitl_cfg["analyst_minutes_per_shift"],
            "queue_precision": tp_alerts / alerts if alerts else 0.0,
            "queue_precision_flow_level": tp_flows / (tp_flows + fp_flows) if (tp_flows + fp_flows) else 0.0}


def summarize_triage(df: pd.DataFrame, error_rate: float = 0.0) -> dict:
    """df: ket qua cua simulate_analyst. Tinh hieu qua he thong nguoi-may."""
    n = len(df)
    out = {"n_flows": n, "queues": {}}
    for q in ("P1_alert", "P2_review", "P3_spotcheck", "P3_logged", "AUDIT", "ignore"):
        sub = df[df["queue"] == q]
        out["queues"][q] = {
            "n": int(len(sub)), "share": len(sub) / n,
            "true_attacks": int(sub["y_true"].sum()),
            "true_precision": float(sub["y_true"].mean()) if len(sub) else float("nan"),
        }
    attacks = int(df["y_true"].sum())
    human = df[df["queue"].isin(HUMAN_QUEUES)]
    caught = int(((human["analyst_verdict"] == 1) & (human["y_true"] == 1)).sum())
    false_dismissed = int(((human["analyst_verdict"] == 0) & (human["y_true"] == 1)).sum())
    missed_ign = int(df[df["queue"].isin(NO_HUMAN + ("AUDIT",))]["y_true"].sum())
    fp_cleared = int(((human["y_true"] == 0) & (human["analyst_verdict"] == 0)).sum())
    fp_confirmed = int(((human["y_true"] == 0) & (human["analyst_verdict"] == 1)).sum())
    out.update({
        "attacks_total": attacks, "attacks_caught_by_human": caught,
        "attacks_wrongly_dismissed_by_analyst": false_dismissed,
        "attacks_missed_in_ignore": missed_ign,
        "system_recall": caught / attacks if attacks else float("nan"),
        "human_queue_size": int(len(human)), "human_queue_share": len(human) / n,
        "false_alarms_cleared": fp_cleared, "false_alarms_confirmed_wrongly": fp_confirmed,
    })
    aud = df[df["queue"] == "AUDIT"]
    ign = df[df["queue"].isin(NO_HUMAN + ("AUDIT",))]
    if len(aud):
        k, n_a = int((aud["analyst_verdict"] == 1).sum()), len(aud)
        out["audit"] = audit_estimate(k, n_a, len(ign), error_rate, int(ign["y_true"].sum()))
    return out


def audit_estimate(k: int, n_audit: int, n_ignored: int, analyst_error: float, true_missed: int) -> dict:
    """Uoc luong ty le bo sot tu mau audit. Hieu chinh sai so analyst (Rogan-Gladen) va
    cho can tren 95% (Clopper-Pearson). LUU Y: mau nho chi phat hien duoc ty le bo sot >~ 3/n."""
    from scipy.stats import beta
    p_hat = k / n_audit
    p = float(np.clip((p_hat - analyst_error) / (1 - 2 * analyst_error), 0, 1))
    upper = float(beta.ppf(0.95, k + 1, n_audit - k)) if k < n_audit else 1.0
    return {"n_audit": n_audit, "verdict_positive": k, "miss_rate_corrected": p,
            "miss_rate_upper95_raw": upper, "detection_limit_rule_of_three": 3 / n_audit,
            "estimated_missed_attacks": p * n_ignored, "true_missed_attacks": true_missed}


def capacity_thresholds(y, score, prevalence: float, hitl_cfg: dict, grid=None) -> list[dict]:
    """Voi moi nguong xem xet t: recall, FPR -> khoi luong analyst/ngay o ty le tan cong thuc te.
    Dung de chon nguong 'vua suc' nhan luc (capacity-aware threshold)."""
    y = np.asarray(y); s = np.asarray(score)
    grid = np.unique(np.quantile(s[s > 0], np.linspace(0, 0.9999, 400))) if grid is None else grid
    rows = []
    for t in grid:
        flag = s >= t
        tpr = float(flag[y == 1].mean()); fpr = float(flag[y == 0].mean())
        w = project_workload(tpr, fpr, prevalence, hitl_cfg)
        rows.append({"threshold": float(t), "recall": tpr, "fpr": fpr, **w})
    return rows
