"""Chuong trinh 7 - Khep kin vong doi: khi co drift + nhan tre -> retrain, so sanh v1 vs v2, quality gate,
promote len production, va 'rollback drill'. Cung so sanh phuong an re hon: chi chinh lai nguong."""
from _common import *  # noqa: F401,F403
from sklearn.model_selection import train_test_split
from src.evaluation.metrics import at_threshold, threshold_free
from src.evaluation.thresholds import build_policy
from src.models.model_builder import score
from src.training.trainer import decide_promotion, retrain_candidate
from src.utils import dataframe_fingerprint


def split_feedback(d, cfg, seed):
    r = cfg["retrain"]; lab = cfg["data"]["label_col"]
    idx = np.arange(len(d))
    fb, rest = train_test_split(idx, train_size=r["feedback_fraction"], stratify=d[lab], random_state=seed)
    val_share = r["val_fraction"] / (1 - r["feedback_fraction"])
    va, ev = train_test_split(rest, train_size=val_share, stratify=d[lab].iloc[rest], random_state=seed)
    return d.iloc[fb], d.iloc[va], d.iloc[ev]


def main():
    cfg, log = setup("07_retrain")
    rcfg, gate, seed = cfg["retrain"], cfg["quality_gate"], cfg["project"]["seed"]
    df, sp = load_data(cfg)
    reg = registry(cfg)
    Xtr, ytr, _ = subset(df, sp["train"], cfg)
    Xva, yva, _ = subset(df, sp["val"], cfg)
    Xte, yte, _ = subset(df, sp["test"], cfg)

    drift_df = load_scenario(cfg, rcfg["scenario"])
    fb, dval, dev = split_feedback(drift_df, cfg, seed)
    Xfb, yfb, _ = to_xy(fb, cfg); Xdv, ydv, _ = to_xy(dval, cfg); Xde, yde, _ = to_xy(dev, cfg)
    log.info("Kich ban '%s': feedback=%d (tan cong=%d) | val=%d | eval=%d (tan cong=%d)",
             rcfg["scenario"], len(yfb), yfb.sum(), len(ydv), len(yde), yde.sum())

    w = rcfg["feedback_weight"]
    Xnew = pd.concat([Xtr, Xfb], ignore_index=True)
    ynew = np.concatenate([ytr, yfb])
    sw = np.concatenate([np.ones(len(ytr)), np.full(len(yfb), w)])
    Xv2 = pd.concat([Xva] + [Xdv] * int(w), ignore_index=True)     # validation: goc + drift (lap theo trong so)
    yv2 = np.concatenate([yva] + [ydv] * int(w))
    fp2 = dataframe_fingerprint(pd.concat([df.iloc[sp["train"]], fb], ignore_index=True))

    report = {"scenario": rcfg["scenario"], "feedback_weight": w, "models": {}}
    for name in (cfg["models"]["primary"], cfg["models"]["secondary"]):
        p1, m1 = reg.load(name, version=cfg["models"]["baseline_version"])
        v1, t1 = m1["version"], m1["thresholds"]
        s1_de, s1_te = score(p1, Xde), score(p1, Xte)

        # Phuong an A: giu v1, chi chinh lai nguong tren validation moi (re, nhanh)
        s1_v2 = score(p1, Xv2)
        pol, ex = build_policy(yv2, s1_v2, cfg)
        t_recal = ex["t_f1_max"]

        # Phuong an B: retrain v2 tren train + feedback (co trong so)
        p2, thr2, m_v2 = retrain_candidate(name, cfg, Xnew, ynew, sw, Xv2, yv2)
        s2_de, s2_te = score(p2, Xde), score(p2, Xte)

        rows = {
            f"{v1} (khong doi)": {"drift": at_threshold(yde, s1_de, t1["operating"]), "orig": at_threshold(yte, s1_te, t1["operating"])},
            f"{v1} + chinh lai nguong": {"drift": at_threshold(yde, s1_de, t_recal), "orig": at_threshold(yte, s1_te, t_recal)},
            "v2 retrain": {"drift": at_threshold(yde, s2_de, thr2["operating"]), "orig": at_threshold(yte, s2_te, thr2["operating"])},
        }
        f = lambda r: {k: r[k] for k in ("precision", "recall", "f1", "fp", "fn", "fp_per_100k_flows", "threshold")}
        tab = {k: {"drift_eval": f(v["drift"]), "original_test": f(v["orig"])} for k, v in rows.items()}

        v1_key, v2_key = f"{v1} (khong doi)", "v2 retrain"
        f1_gain = tab[v2_key]["drift_eval"]["f1"] - tab[v1_key]["drift_eval"]["f1"]
        regress = tab[v1_key]["original_test"]["f1"] - tab[v2_key]["original_test"]["f1"]
        gate_ok = decide_promotion(f1_gain, regress, m_v2, cfg)
        v2 = reg.register(name, p2, metrics=m_v2, thresholds=thr2, params=cfg["models"][name],
                          data_fingerprint=fp2, feature_names=list(Xtr.columns), parent_version=v1,
                          notes=f"Retrain sau drift '{rcfg['scenario']}': train + feedback x{w}.")
        decision = "PROMOTE" if gate_ok else "KEEP v1 (v2 giu o staging)"
        if gate_ok:
            reg.promote(name, v2)
        # Rollback drill: chung minh co the quay lai ban cu, roi dua v2 len lai
        drill = None
        if gate_ok:
            back = reg.rollback(name); reg.promote(name, v2)
            drill = {"rolled_back_to": back, "then_repromoted": v2}
        report["models"][name] = {"v1": v1, "v2": v2, "table": tab, "f1_gain_on_drift": f1_gain,
                                  "f1_regression_on_original": regress, "gate_passed": bool(gate_ok),
                                  "decision": decision, "rollback_drill": drill,
                                  "history": reg.versions(name)}
        for k, v in tab.items():
            log.info("%-14s %-24s drift: P=%.3f R=%.3f F1=%.3f | goc: F1=%.3f", name, k,
                     v["drift_eval"]["precision"], v["drift_eval"]["recall"], v["drift_eval"]["f1"],
                     v["original_test"]["f1"])
        log.info("%-14s -> %s", name, decision)
    save_json(report, metrics_path(cfg, "retrain_comparison.json"))


if __name__ == "__main__":
    main()
