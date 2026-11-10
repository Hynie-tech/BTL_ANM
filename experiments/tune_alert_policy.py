"""Chuong trinh 6 - De xuat nguong canh bao 3 vung + quy trinh nguoi xac minh (human-in-the-loop).
Tinh khoi luong analyst, phan tich base-rate, mo phong hang doi xac minh tren du lieu goc va drift."""
from _common import *  # noqa: F401,F403
from src.evaluation.metrics import at_threshold, precision_at_prevalence, threshold_table
from src.evaluation.thresholds import AlertPolicy
from src.models.model_builder import score
from src.hitl.triage import (HUMAN_QUEUES, build_review_queue, capacity_thresholds, project_workload,
                               simulate_analyst, summarize_triage)
from src.visualization import plot_results as plots


def triage_eval(sP, sS, y, polP, thr_agree, cfg, seed):
    q = build_review_queue(sP, sS, polP, thr_agree, cfg, seed=seed)
    err = cfg["hitl"]["analyst_error_rate"]
    qa = simulate_analyst(q, y, err, seed=seed)
    summ = summarize_triage(qa, err)
    # can tren ly tuong: analyst khong sai (de tach anh huong cua sai sot con nguoi)
    summ["system_recall_if_analyst_perfect"] = summarize_triage(simulate_analyst(q, y, 0.0, seed=seed))["system_recall"]
    return qa, summ


def main():
    cfg, log = setup("06_policy_hitl")
    df, sp = load_data(cfg)
    reg = registry(cfg)
    prim, sec = cfg["models"]["primary"], cfg["models"]["secondary"]
    (pP, mP), (pS, mS) = reg.load(prim, version=cfg["models"]["baseline_version"]), reg.load(sec, version=cfg["models"]["baseline_version"])
    thrP, thrS = mP["thresholds"], mS["thresholds"]
    policy = AlertPolicy(t_review=thrP["t_review"], t_alert=thrP["t_alert"])
    thr_agree = thrS["operating"]
    seed, ap = cfg["project"]["seed"], cfg["alert_policy"]

    Xte, yte, _ = subset(df, sp["test"], cfg)
    sP, sS = score(pP, Xte), score(pS, Xte)
    out = {"policy": {**policy.to_dict(), "secondary_agree_threshold": thr_agree,
                      "primary": f"{prim}:{mP['version']}", "secondary": f"{sec}:{mS['version']}"}}

    # ---- 1) Bang nguong va chi phi ----
    grid = sorted(set(list(np.round(np.linspace(0.02, 0.98, 25), 3)) + [round(v, 4) for v in
                  (thrP["t_review"], thrP["t_alert"], thrP["operating"], thrP["t_min_cost"])]))
    rows = threshold_table(yte, sP, grid)
    out["threshold_sweep_primary"] = rows
    cost = {}
    for k, t in (("default_0.5", 0.5), ("operating", thrP["operating"]), ("t_alert", thrP["t_alert"]),
                 ("t_review", thrP["t_review"]), ("t_min_cost", thrP["t_min_cost"])):
        r = at_threshold(yte, sP, t)
        cost[k] = {"threshold": t, "fp": r["fp"], "fn": r["fn"], "precision": r["precision"], "recall": r["recall"],
                   "expected_cost": ap["cost_fn"] * r["fn"] + ap["cost_fp"] * r["fp"]}
    out["cost_by_threshold"] = {"cost_fn": ap["cost_fn"], "cost_fp": ap["cost_fp"], "rows": cost}
    plots.threshold_tradeoff(rows, fig_path(cfg, "06_threshold_tradeoff.png"),
                             marks={"t_review": thrP["t_review"], "t_alert": thrP["t_alert"]}, title=f"({prim})")

    # ---- 2) Thong ke 3 vung tren test ----
    z = policy.zones(sP)
    zs = {}
    for name in ("alert", "review", "ignore"):
        m = z == name
        zs[name] = {"n": int(m.sum()), "share": float(m.mean()), "attacks": int(yte[m].sum()),
                    "benign": int((1 - yte[m]).sum()),
                    "precision": float(yte[m].mean()) if m.any() else float("nan")}
    out["zones_test_primary"] = zs
    log.info("Vung (test) %s", {k: (v["n"], v["attacks"]) for k, v in zs.items()})

    # ---- 3) Hang doi xac minh tren TEST ----
    q, summ = triage_eval(sP, sS, yte, policy, thr_agree, cfg, seed)
    out["triage_test"] = summ
    op = at_threshold(yte, sP, thrP["operating"])
    out["auto_only_recall_at_operating"] = op["recall"]
    hq = q["queue"].isin(HUMAN_QUEUES).to_numpy()
    tpr_q = float(hq[yte == 1].mean()); fpr_q = float(hq[yte == 0].mean())
    out["queue_tpr_fpr"] = {"tpr_q": tpr_q, "fpr_q": fpr_q}
    log.info("Triage test: hang doi nguoi=%d (%.3f%% flow) | recall may+nguoi=%.4f (analyst hoan hao: %.4f) | recall chi may=%.4f",
             summ["human_queue_size"], 100 * summ["human_queue_share"], summ["system_recall"],
             summ["system_recall_if_analyst_perfect"], op["recall"])
    sample = q[q["queue"].isin(HUMAN_QUEUES + ("AUDIT",))].sort_values(["priority", "score_primary"],
                                                                         ascending=[True, False]).head(200)
    sample.drop(columns=["y_true", "analyst_verdict"]).to_csv(path_of(cfg, "predictions_dir", "review_queue_sample.csv"),
                                                              index=False, float_format="%.4f")

    # ---- 3b) Nguong 'vua suc' nhan luc o ty le tan cong thuc te ----
    cap = capacity_thresholds(yte, sP, ap["deploy_prevalence"], cfg["hitl"])
    avail = cfg["hitl"]["analyst_shifts_available"]
    ok = [r for r in cap if r["analyst_shifts_per_day"] <= avail]
    t_cap = min(ok, key=lambda r: r["threshold"]) if ok else None
    out["capacity_threshold"] = {"deploy_prevalence": ap["deploy_prevalence"], "shifts_available": avail,
                                 "chosen": t_cap, "feasible": bool(ok),
                                 "at_t_review": next(r for r in cap if r["threshold"] >= thrP["t_review"])}
    out["recommended_review_threshold"] = max(thrP["t_review"], t_cap["threshold"]) if t_cap else thrP["t_alert"]

    # ---- 4) Ngoai suy khoi luong analyst theo prevalence thuc te ----
    wl = [project_workload(tpr_q, fpr_q, p, cfg["hitl"])
          for p in (0.0001, ap["deploy_prevalence"], 0.005, 0.01, float(yte.mean()))]
    out["workload_projection"] = wl
    plots.workload_bars(wl, fig_path(cfg, "06_workload_projection.png"))
    series = {}
    for n, (pipe, meta) in ((prim, (pP, mP)), (sec, (pS, mS))):
        r = at_threshold(yte, score(pipe, Xte), meta["thresholds"]["operating"])
        series[n] = (r["recall"], max(r["fpr"], 1e-6))
        out.setdefault("precision_vs_prevalence", {})[n] = {
            f"{p:.3%}": precision_at_prevalence(r["recall"], r["fpr"], p) for p in (0.0001, 0.001, 0.01, 0.0235)}
        # FPR do duoc tu rat it FP -> khoang tin cay rong. Can tren 95% (Clopper-Pearson) cho FPR:
        from scipy.stats import beta
        nb = r["fp"] + r["tn"]
        fpr_up = float(beta.ppf(0.95, r["fp"] + 1, nb - r["fp"]))
        out.setdefault("fpr_upper95", {})[n] = {"fp": r["fp"], "n_benign": nb, "fpr": r["fpr"], "fpr_upper95": fpr_up}
        out.setdefault("precision_vs_prevalence_pessimistic", {})[n] = {
            f"{p:.3%}": precision_at_prevalence(r["recall"], fpr_up, p) for p in (0.0001, 0.001, 0.01, 0.0235)}
    plots.prevalence_curve(series, fig_path(cfg, "06_precision_vs_prevalence.png"), mark=ap["deploy_prevalence"])

    # ---- 5) Hang doi xac minh tren cac kich ban drift ----
    scen = {}
    for name in ["control"] + list(cfg["drift"]["scenarios"]):
        d = get_pool(df, sp, cfg) if name == "control" else load_scenario(cfg, name)
        Xd, yd, _ = to_xy(d, cfg)
        sPd, sSd = score(pP, Xd), score(pS, Xd)
        _, sm = triage_eval(sPd, sSd, yd, policy, thr_agree, cfg, seed)
        auto = at_threshold(yd, sPd, thrP["operating"])
        scen[name] = {"recall_auto_only": auto["recall"], "recall_with_human": sm["system_recall"],
                      "human_queue_share": sm["human_queue_share"], "attacks": sm["attacks_total"],
                      "recall_with_human_if_analyst_perfect": sm["system_recall_if_analyst_perfect"],
                      "missed_in_ignore": sm["attacks_missed_in_ignore"], "audit": sm.get("audit"),
                      "p3_disagreement_rate": float((sm["queues"]["P3_spotcheck"]["n"] + sm["queues"]["P3_logged"]["n"]) / sm["n_flows"])}
        log.info("%-18s recall(chi may)=%.3f -> recall(may+nguoi)=%.3f | hang doi nguoi=%.2f%%",
                 name, auto["recall"], sm["system_recall"], 100 * sm["human_queue_share"])
    out["triage_by_scenario"] = scen
    save_json(out, metrics_path(cfg, "alert_policy_hitl.json"))


if __name__ == "__main__":
    main()
