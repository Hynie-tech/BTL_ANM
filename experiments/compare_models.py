"""Chuong trinh 3 (BT1) - So sanh 2 mo hinh: danh gia tren TAP TEST (chi dung 1 lan, nguong lay tu validation).
Bao cao precision / recall / F1 / false positive, khong chi accuracy."""
from _common import *  # noqa: F401,F403
from src.evaluation.metrics import (at_threshold, binary_report, majority_baseline,
                                      precision_at_prevalence, threshold_free)
from src.models.model_builder import score
from src.models.model_inspector import top_features
from src.visualization import plot_results as plots


def main():
    cfg, log = setup("03_evaluate")
    df, sp = load_data(cfg)
    Xte, yte, att = subset(df, sp["test"], cfg)
    reg = registry(cfg)
    out = {"n_test": int(len(yte)), "prevalence": float(yte.mean()),
           "majority_baseline": majority_baseline(yte), "models": {}}
    log.info("Baseline 'luon bao Benign': accuracy=%.4f nhung recall=%.2f",
             out["majority_baseline"]["accuracy"], out["majority_baseline"]["recall"])

    curves, cms, marks = {}, {}, {}
    for name in (cfg["models"]["primary"], cfg["models"]["secondary"]):
        pipe, meta = reg.load(name, version=cfg["models"]["baseline_version"])
        thr = meta["thresholds"]
        s = score(pipe, Xte)
        res = {"version": meta["version"], "thresholds": thr, **threshold_free(yte, s), "operating_points": {}}
        for label, key in (("default_0.5", "default"), ("operating(F1-max on val)", "operating"),
                           ("t_alert", "t_alert"), ("t_review", "t_review"), ("min_cost", "t_min_cost")):
            res["operating_points"][label] = at_threshold(yte, s, thr[key])
        op = res["operating_points"]["operating(F1-max on val)"]
        # Recall theo tung loai tan cong
        res["recall_by_attack_type"] = {
            t: float(((s >= thr["operating"]) & (att.to_numpy() == t)).sum() / max(1, (att.to_numpy() == t).sum()))
            for t in sorted(att.unique()) if t != cfg["data"]["benign_label"]}
        # Ngoai suy precision o ty le tan cong thuc te thap (base-rate fallacy)
        res["precision_at_prevalence"] = {
            f"{p:.4%}": precision_at_prevalence(op["recall"], op["fpr"], p)
            for p in (cfg["alert_policy"]["deploy_prevalence"], 0.0001, 0.01, op["prevalence"])}
        # Giai thich: do quan trong dac trung (RF) / he so (LogReg)
        res["top_features"] = top_features(pipe, list(Xte.columns), 15)
        out["models"][name] = res
        curves[name] = (yte, s)
        cms[f"{name} ({meta['version']}) @ operating"] = [[op["tn"], op["fp"]], [op["fn"], op["tp"]]]
        marks[name] = {"operating": (op["recall"], op["precision"])}
        log.info("%-14s AP=%.4f | @operating: P=%.4f R=%.4f F1=%.4f FP=%d (%.1f/100k flow)",
                 name, res["average_precision"], op["precision"], op["recall"], op["f1"], op["fp"],
                 op["fp_per_100k_flows"])
        log.info("   recall theo loai: %s", {k: round(v, 4) for k, v in res["recall_by_attack_type"].items()})

        # hinh feature importance
        import matplotlib.pyplot as plt
        t = res["top_features"][::-1]
        fig, ax = plt.subplots(figsize=(6.5, 4.6))
        ax.barh([x["feature"] for x in t], [x["importance"] for x in t], color=plots.C[name])
        ax.set_title(f"Top 15 đặc trưng quan trọng - {name}")
        plots._save(fig, fig_path(cfg, f"03_feature_importance_{name}.png"))

    plots.pr_curves(curves, fig_path(cfg, "03_pr_curves.png"), marks=marks)
    plots.confusion_pair(cms, fig_path(cfg, "03_confusion_matrices.png"))
    save_json(out, metrics_path(cfg, "test_evaluation.json"))


if __name__ == "__main__":
    main()
