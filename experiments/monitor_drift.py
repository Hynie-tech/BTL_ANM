"""Chuong trinh 5 - Giam sat drift: (a) tin hieu KHONG can nhan (PSI/KS dac trung, diem so, ty le canh bao)
va (b) hieu nang CO nhan (nhan den tre). So sanh de thay 'drift im lang' (silent failure)."""
from _common import *  # noqa: F401,F403
from src.evaluation.metrics import at_threshold
from src.models.model_builder import score
from src.monitoring.drift_detector import band_psi, feature_drift_table, summarize_drift
from src.visualization import plot_results as plots


def main():
    cfg, log = setup("05_monitor")
    lab = cfg["data"]["label_col"]
    mcfg = cfg["monitoring"]
    df, sp = load_data(cfg)
    reg = registry(cfg)
    prim, sec = cfg["models"]["primary"], cfg["models"]["secondary"]
    models = {n: reg.load(n, version=cfg["models"]["baseline_version"]) for n in (prim, sec)}

    Xref, yref, _ = subset(df, sp["val"], cfg)       # tham chieu = validation (mo hinh chua fit)
    ref_scores = {n: score(p, Xref) for n, (p, _) in models.items()}

    pool = get_pool(df, sp, cfg)
    datasets = {"control (khong drift)": pool}
    for name in cfg["drift"]["scenarios"]:
        datasets[name] = load_scenario(cfg, name)

    results, perf, psi_cols, score_cur = {}, {}, {}, {}
    for dname, d in datasets.items():
        Xc, yc, _ = to_xy(d, cfg)
        tab = feature_drift_table(Xref, Xc, mcfg, seed=cfg["project"]["seed"])
        psi_cols[dname] = tab.set_index("feature")["psi"]
        res = {"n": int(len(yc)), "prevalence": float(yc.mean()), "models": {}}
        perf[dname] = {}
        for n, (pipe, meta) in models.items():
            thr = meta["thresholds"]
            s = score(pipe, Xc)
            base_flag = float((ref_scores[n] >= thr["operating"]).mean())   # ty le du doan 'tan cong'
            flag = float((s >= thr["operating"]).mean())
            edges = [thr["t_review"], thr["operating"], thr["t_alert"]]
            summ = summarize_drift(tab, band_psi(ref_scores[n], s, edges), flag, base_flag, mcfg)
            m = at_threshold(yc, s, thr["operating"])
            summ["performance_at_frozen_threshold"] = {k: m[k] for k in
                ("precision", "recall", "f1", "fpr", "fp", "fn", "tp", "fp_per_100k_flows", "n_attack")}
            res["models"][n] = summ
            perf[dname][n] = m
            if n == prim:
                score_cur[dname] = s
        res["top_drifting_features"] = tab.head(10).to_dict("records")
        results[dname] = res

    # So sanh voi F1 cua nhom 'control' de quyet dinh kich hoat retrain (can nhan)
    for dname, res in results.items():
        for n in models:
            f1_ctrl = results["control (khong drift)"]["models"][n]["performance_at_frozen_threshold"]["f1"]
            f1 = res["models"][n]["performance_at_frozen_threshold"]["f1"]
            drop = f1_ctrl - f1
            res["models"][n]["f1_drop_vs_control"] = drop
            res["models"][n]["perf_status"] = "DEGRADED" if drop > mcfg["f1_drop_trigger"] else "OK"
            lf, pf = res["models"][n]["label_free_status"], res["models"][n]["perf_status"]
            res["models"][n]["silent_failure"] = bool(lf == "STABLE" and pf == "DEGRADED")
            res["models"][n]["action"] = (
                "RETRAIN / DIEU TRA" if pf == "DEGRADED" else ("DIEU TRA (co drift dau vao)" if lf == "DRIFT" else "TIEP TUC GIAM SAT"))
        log.info("%-24s %s", dname, {n: (res["models"][n]["label_free_status"], res["models"][n]["perf_status"],
                                          round(res["models"][n]["performance_at_frozen_threshold"]["f1"], 3)) for n in models})

    # Hinh
    sc_perf = {k: {n: perf[k][n] for n in models} for k in perf}
    plots.scenario_performance(sc_perf, fig_path(cfg, "05_performance_under_drift.png"))
    top = sorted({f for d in psi_cols.values() for f in d.sort_values(ascending=False).head(8).index})
    mat = pd.DataFrame({k: v.reindex(top) for k, v in psi_cols.items()})
    mat = mat.loc[mat.max(axis=1).sort_values(ascending=False).index].head(20)
    plots.psi_heatmap(mat, fig_path(cfg, "05_psi_heatmap.png"), mcfg["psi_alert"])
    thr_p = models[prim][1]["thresholds"]
    plots.score_hist(ref_scores[prim], {k: v for k, v in score_cur.items() if k != "control (khong drift)"},
                     {"t_review": thr_p["t_review"], "t_alert": thr_p["t_alert"]},
                     fig_path(cfg, "05_score_distribution.png"), f"Phân phối điểm số - {prim}")
    save_json(results, metrics_path(cfg, "drift_monitoring.json"))


if __name__ == "__main__":
    main()
