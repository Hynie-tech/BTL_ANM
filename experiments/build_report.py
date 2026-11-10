"""Chuong trinh 9 - Tu dong tong hop ket qua thuc nghiem thanh reports/ket_qua_thuc_nghiem.md
(moi con so lay truc tiep tu results/tables/*.json de khop voi lan chay thuc te)."""
import json

from _common import *  # noqa: F401,F403
import pandas as pd
from src.utils import md_table
from src.visualization.save_results import save_markdown, save_table


def J(cfg, name):
    p = metrics_path(cfg, name)
    return load_json(p) if p.exists() else None


def pc(x, d=2):
    return "n/a" if x is None or x != x else f"{100 * x:.{d}f}%"


def main():
    cfg, log = setup("09_report")
    eda, ev, drift, pol = J(cfg, "eda.json"), J(cfg, "test_evaluation.json"), J(cfg, "drift_monitoring.json"), J(cfg, "alert_policy_hitl.json")
    rt, noise, tr = J(cfg, "retrain_comparison.json"), J(cfg, "label_noise.json"), J(cfg, "training_summary.json")
    man = load_json(path_of(cfg, "drift_dir", "manifest.json")) if path_of(cfg, "drift_dir", "manifest.json").exists() else None
    prim, sec = cfg["models"]["primary"], cfg["models"]["secondary"]
    L = []
    A = L.append
    MARK = {}
    A("# Kết quả thực nghiệm (sinh tự động)\n")
    A("> File này do `experiments/build_report.py` tạo ra từ `results/tables/*.json`. "
      "Chạy lại pipeline sẽ cập nhật toàn bộ số liệu. Diễn giải và hạn chế: xem `docs/`.\n")

    # 1. Du lieu
    A("## 1. Dữ liệu và cách chia tập\n")
    lc = eda["label_counts"]
    A(f"- {eda['n_rows']:,} flow × {eda['n_features']} đặc trưng; nhãn: " + ", ".join(f"{k}={v:,}" for k, v in lc.items()) + ".")
    A(f"- Tỷ lệ tấn công **{pc(eda['attack_prevalence'])}** → bộ phân loại ‘luôn báo Benign’ đạt accuracy **{pc(eda['majority_baseline_accuracy'])}** nhưng recall = 0. "
      "Vì vậy báo cáo dùng precision/recall/F1/FP thay vì accuracy.")
    A(f"- {eda['n_constant_features']} đặc trưng hằng số (bị loại trong pipeline); NaN={eda['n_missing']}, Inf={eda['n_inf']}; "
      f"{eda['n_duplicate_rows_after_float32']} dòng trùng sau khi ép float32. Dữ liệu **không có timestamp** → chia ngẫu nhiên phân tầng (xem hạn chế).")
    rows = [[k, v["n"], f"{v['attack_prevalence']:.3%}", v["fingerprint"]] for k, v in eda["splits"].items()]
    A("\n" + md_table(rows, ["Tập", "Số flow", "Tỷ lệ tấn công", "Fingerprint"]) + "\n")
    A("![class](figures/01_class_distribution.png)\n")

    # 2. Danh gia
    MARK["s2"] = len(L)
    A("## 2. Hai mô hình cơ bản - đánh giá trên tập test\n")
    A(f"Mô hình: **{prim}** (mô hình chính) và **{sec}** (mô hình phụ). Ngưỡng ‘operating’ = ngưỡng tối đa F1 chọn trên **validation** (không chọn trên test).\n")
    rows = []
    for n, r in ev["models"].items():
        for lab, m in r["operating_points"].items():
            rows.append([n, r["version"], lab, round(m["threshold"], 4), m["precision"], m["recall"], m["f1"], m["fp"], m["fn"], m["fp_per_100k_flows"], m["accuracy"]])
    A(md_table(rows, ["Mô hình", "Ver", "Điểm vận hành", "Ngưỡng", "Precision", "Recall", "F1", "FP", "FN", "FP/100k flow", "Accuracy"]) + "\n")
    b = ev["majority_baseline"]
    A(f"Baseline ‘luôn Benign’: accuracy={b['accuracy']:.4f}, recall={b['recall']:.2f}, F1={b['f1']:.2f}.\n")
    A("Recall theo loại tấn công (tại ngưỡng operating): " + "; ".join(
        f"{n}: " + ", ".join(f"{k}={v:.4f}" for k, v in r["recall_by_attack_type"].items()) for n, r in ev["models"].items()) + ".\n")
    A("![pr](figures/03_pr_curves.png)\n\n![cm](figures/03_confusion_matrices.png)\n")
    A("Đặc trưng quan trọng nhất (top 5): " + "; ".join(
        f"{n}: " + ", ".join(x["feature"] for x in r["top_features"][:5]) for n, r in ev["models"].items()) + ".\n")

    # 3. Base rate
    MARK["s3"] = len(L)
    if pol:
        A("## 3. Cảnh báo giả và ‘base-rate fallacy’\n")
        A("Precision đo trên tập test phụ thuộc vào tỷ lệ tấn công của tập đó. Nếu ngoài đời tấn công hiếm hơn, precision kỳ vọng (công thức Bayes từ recall và FPR đo được) giảm mạnh:\n")
        pv = pol["precision_vs_prevalence"]
        keys = list(next(iter(pv.values())).keys())
        A(md_table([[n] + [v[k] for k in keys] for n, v in pv.items()], ["Mô hình"] + [f"p={k}" for k in keys]) + "\n")
        pp = pol["precision_vs_prevalence_pessimistic"]; fu = pol["fpr_upper95"]
        A("FPR đo được dựa trên rất ít cảnh báo giả nên không chắc chắn. Với cận trên 95% của FPR (Clopper-Pearson) - " +
          "; ".join(f"{n}: {fu[n]['fp']} FP/{fu[n]['n_benign']:,} benign → FPR ≤ {fu[n]['fpr_upper95']:.2e}" for n in fu) + " - precision kỳ vọng (kịch bản bi quan):\n")
        A(md_table([[n] + [v[k] for k in keys] for n, v in pp.items()], ["Mô hình"] + [f"p={k}" for k in keys]) + "\n")
        A("![prev](figures/06_precision_vs_prevalence.png)\n")

    # 4. Drift
    MARK["s4"] = len(L)
    if man and drift:
        A("## 4. Drift: tập dữ liệu thay đổi phân phối và giám sát\n")
        A("Cảnh báo: các tập dưới đây là **mô phỏng có kiểm soát** từ tập test, không phải lưu lượng thật.\n")
        A(md_table([[k, v["n_rows"], v["n_attack"], f"{v['prevalence']:.3%}", json.dumps(v["params"], ensure_ascii=False)] for k, v in man["scenarios"].items()],
                   ["Kịch bản", "Số flow", "Số tấn công", "Tỷ lệ", "Tham số"]) + "\n")
        rows = []
        for sname, r in drift.items():
            for n in (prim, sec):
                m = r["models"][n]; p = m["performance_at_frozen_threshold"]
                rows.append([sname, n, f"{m['n_feature_alert']}/{m['n_features']}", m["score_psi"], m["alert_rate_ratio"],
                             m["label_free_status"], p["precision"], p["recall"], p["f1"], p["fp"], m["perf_status"], "CÓ" if m["silent_failure"] else "-"])
        A(md_table(rows, ["Kịch bản", "Mô hình", "Feature PSI≥ngưỡng", "PSI dải điểm", "Tỷ lệ dự đoán TC (so baseline)", "Giám sát không nhãn", "Precision", "Recall", "F1", "FP", "Hiệu năng (có nhãn)", "Drift im lặng"]) + "\n")
        A("Ngưỡng của mô hình được **đóng băng** ở giá trị chọn trên validation. ‘Giám sát không nhãn’ = PSI đặc trưng/dải điểm + tỷ lệ dự đoán tấn công; "
          "‘hiệu năng (có nhãn)’ = F1 giảm quá ngưỡng so với nhóm control (không drift).\n")
        A("![perf](figures/05_performance_under_drift.png)\n\n![psi](figures/05_psi_heatmap.png)\n\n![score](figures/05_score_distribution.png)\n")
        # diễn giải tu dong
        ctrl = drift["control (khong drift)"]["models"][prim]["performance_at_frozen_threshold"]["f1"]
        notes = []
        for sname, r in drift.items():
            if sname.startswith("control"):
                continue
            m = r["models"][prim]
            notes.append(f"- `{sname}` ({prim}): F1 {ctrl:.3f} → {m['performance_at_frozen_threshold']['f1']:.3f}; "
                         f"recall {m['performance_at_frozen_threshold']['recall']:.3f}; số feature có PSI vượt ngưỡng: {m['n_feature_alert']}/{m['n_features']}; "
                         f"giám sát không nhãn: **{m['label_free_status']}**" + (f" ({'; '.join(m['reasons'])})" if m['reasons'] else "") + ".")
        A("**Đọc kết quả:**\n\n" + "\n".join(notes) + "\n")

    # 5. Nguong + HITL
    MARK["s5"] = len(L)
    if pol:
        A("## 5. Ngưỡng cảnh báo đề xuất và quy trình con người xác minh\n")
        P = pol["policy"]
        A(f"Chính sách 3 vùng dựa trên **{P['primary']}** (ngưỡng chọn trên validation): `score ≥ {P['t_alert']:.4f}` → **ALERT**; "
          f"`{P['t_review']:.4f} ≤ score < {P['t_alert']:.4f}` → **REVIEW**; còn lại → **IGNORE** (ghi log + lấy mẫu audit). "
          f"Mô hình phụ ({P['secondary']}) cho tín hiệu ‘đồng ý’ khi điểm ≥ {P['secondary_agree_threshold']:.4f}.\n")
        zs = pol["zones_test_primary"]
        A(md_table([[k, v["n"], f"{v['share']:.3%}", v["attacks"], v["benign"], v["precision"]] for k, v in zs.items()], ["Vùng", "Số flow", "Tỷ lệ", "Tấn công thật", "Benign (cảnh báo giả)", "Precision vùng"]) + "\n")
        cb = pol["cost_by_threshold"]
        A(f"Chi phí kỳ vọng (FN={cb['cost_fn']}, FP={cb['cost_fp']}) trên test:\n")
        A(md_table([[k, round(v["threshold"], 4), v["fp"], v["fn"], v["precision"], v["recall"], v["expected_cost"]] for k, v in cb["rows"].items()],
                   ["Ngưỡng", "Giá trị", "FP", "FN", "Precision", "Recall", "Chi phí"]) + "\n")
        A("![thr](figures/06_threshold_tradeoff.png)\n")
        t = pol["triage_test"]
        A("### Hàng đợi xác minh (mô phỏng analyst)\n")
        A(md_table([[k, v["n"], f"{v['share']:.3%}", v["true_attacks"], v["true_precision"]] for k, v in t["queues"].items()],
                   ["Hàng đợi", "Số flow", "Tỷ lệ", "Tấn công thật", "Precision thật"]) + "\n")
        A(f"- Recall chỉ-máy (ngưỡng operating): **{pol['auto_only_recall_at_operating']:.4f}**; recall máy+người (analyst sai {cfg['hitl']['analyst_error_rate']:.0%}): **{t['system_recall']:.4f}**; "
          f"nếu analyst hoàn hảo: {t['system_recall_if_analyst_perfect']:.4f}. Sai sót của analyst tự nó bỏ sót {t['attacks_wrongly_dismissed_by_analyst']} tấn công → cần quy tắc 2 người duyệt khi bác bỏ cảnh báo điểm cao.")
        if t.get("audit"):
            a = t["audit"]
            A(f"- Audit ngẫu nhiên {a['n_audit']} flow trong vùng bị bỏ qua: giới hạn phát hiện ≈ {a['detection_limit_rule_of_three']:.1%} (quy tắc ba). "
              f"Số tấn công thật bị bỏ sót là {a['true_missed_attacks']} flow ≈ tỷ lệ nhỏ hơn nhiều giới hạn này → audit ngẫu nhiên **không** đủ để ước lượng tỷ lệ bỏ sót hiếm; cần audit phân tầng theo điểm số và săn mối đe dọa.")
        A("\n### Hàng đợi trên các kịch bản drift\n")
        A(md_table([[k, v["recall_auto_only"], v["recall_with_human"], v["recall_with_human_if_analyst_perfect"], f"{v['human_queue_share']:.3%}", v["missed_in_ignore"], f"{v['p3_disagreement_rate']:.3%}"]
                    for k, v in pol["triage_by_scenario"].items()],
                   ["Kịch bản", "Recall chỉ-máy", "Recall máy+người", "…nếu analyst hoàn hảo", "Tỷ lệ flow vào hàng đợi người", "Tấn công lọt vùng IGNORE", "Tỷ lệ bất đồng 2 mô hình"]) + "\n")
        A("### Khối lượng analyst theo tỷ lệ tấn công thực tế (ngoại suy)\n")
        hc = cfg["hitl"]
        A(f"Giả định (sửa trong `configs/config.yaml`): {hc['flows_per_day']:,} flow/ngày; {hc['flows_per_attack_alert']} flow tấn công gộp thành 1 ticket; "
          f"{hc['flows_per_fp_alert']} flow cảnh báo giả gộp thành 1 ticket; {hc['minutes_per_alert']} phút/ticket; ca {hc['analyst_minutes_per_shift']} phút.\n")
        A(md_table([[f"{w['prevalence']:.3%}", w["tp_alerts_per_day"], w["fp_alerts_per_day"], w["analyst_shifts_per_day"], w["queue_precision"], w["queue_precision_flow_level"]]
                    for w in pol["workload_projection"]], ["Tỷ lệ tấn công", "Ticket thật/ngày", "Ticket giả/ngày", "Ca analyst/ngày", "Precision ticket", "Precision mức flow"]) + "\n")
        c = pol["capacity_threshold"]
        if c["chosen"]:
            A(f"Với {c['shifts_available']} ca analyst/ngày và tỷ lệ tấn công {c['deploy_prevalence']:.2%}, ngưỡng REVIEW ‘vừa sức’ thấp nhất là **{c['chosen']['threshold']:.4f}** "
              f"(recall test {c['chosen']['recall']:.4f}, cần {c['chosen']['analyst_shifts_per_day']:.2f} ca/ngày); ngưỡng REVIEW theo mục tiêu recall cần {c['at_t_review']['analyst_shifts_per_day']:.2f} ca/ngày. "
              f"Ngưỡng REVIEW khuyến nghị = max(hai ngưỡng) = **{pol['recommended_review_threshold']:.4f}**.\n")
        A("![wl](figures/06_workload_projection.png)\n")

    # 6. Retrain
    MARK["s6"] = len(L)
    if rt:
        A("## 6. Vòng đời: retrain, versioning, quality gate\n")
        A(f"Kịch bản kích hoạt: `{rt['scenario']}`; dữ liệu feedback (nhãn trễ) trọng số ×{rt['feedback_weight']}.\n")
        for n, r in rt["models"].items():
            A(f"**{n}** - quyết định: **{r['decision']}** (ΔF1 trên drift = {r['f1_gain_on_drift']:+.3f}; thoái lui trên dữ liệu gốc = {r['f1_regression_on_original']:+.3f}).\n")
            A(md_table([[k, v["drift_eval"]["precision"], v["drift_eval"]["recall"], v["drift_eval"]["f1"], v["drift_eval"]["fp"], v["original_test"]["f1"]] for k, v in r["table"].items()],
                       ["Phương án", "Precision (drift)", "Recall (drift)", "F1 (drift)", "FP (drift)", "F1 (dữ liệu gốc)"]) + "\n")
            if r["rollback_drill"]:
                A(f"Rollback drill: quay về {r['rollback_drill']['rolled_back_to']} rồi promote lại {r['rollback_drill']['then_repromoted']} thành công.\n")

    # 7. Noise
    MARK["s7"] = len(L)
    if noise:
        A("## 7. Nhiễu nhãn trong dữ liệu huấn luyện (poisoning mức khái niệm)\n")
        rows = [[r["noise_type"], f"{r['rate']:.0%}", r["model"], r["precision"], r["recall"], r["f1"], r["average_precision"]] for r in sorted(noise["rows"], key=lambda r: (r["noise_type"], r["model"], r["rate"]))]
        A(md_table(rows, ["Loại nhiễu", "Tỷ lệ", "Mô hình", "Precision", "Recall", "F1", "AP"]) + "\n\n![noise](figures/08_label_noise.png)\n")
    MARK["end"] = len(L)
    A("\n---\nXem `docs/06_results/conclusion.md` va `docs/04_design/` để biết giả định và hạn chế khi diễn giải các con số trên.")
    full = "\n".join(L)
    save_markdown(cfg, "reports_dir", "ket_qua_thuc_nghiem.md", full.replace("](figures/", "](../figures/"))
    save_markdown(cfg, "docs_results_dir", "experiment_results.md", full.replace("](figures/", "](../../results/figures/"))
    ev_txt = "# Kết quả đánh giá mô hình (sinh tự động)\n\n" + "\n".join(L[MARK["s2"]:MARK["s4"]]) if "s4" in MARK else ""
    save_markdown(cfg, "docs_results_dir", "evaluation_results.md", ev_txt.replace("](figures/", "](../../results/figures/"))
    save_markdown(cfg, "docs_results_dir", "conclusion.md", conclusion(cfg, ev, drift, pol, rt, noise))
    # bang CSV de dua thang vao bao cao/Excel
    if ev:
        save_table(cfg, "test_metrics.csv", pd.DataFrame([
            {"model": n, "version": r["version"], "operating_point": lab, **{k: m[k] for k in ("threshold", "precision", "recall", "f1", "fp", "fn", "fpr", "accuracy", "fp_per_100k_flows")}}
            for n, r in ev["models"].items() for lab, m in r["operating_points"].items()]))
    if drift:
        save_table(cfg, "drift_summary.csv", pd.DataFrame([
            {"scenario": sn, "model": n, **{k: m[k] for k in ("n_feature_alert", "score_psi", "alert_rate_ratio", "label_free_status", "perf_status", "silent_failure")},
             **m["performance_at_frozen_threshold"]} for sn, r in drift.items() for n, m in r["models"].items()]))
    if rt:
        save_table(cfg, "retrain_comparison.csv", pd.DataFrame([
            {"model": n, "option": k, **{f"drift_{a}": b for a, b in v["drift_eval"].items()}, **{f"orig_{a}": b for a, b in v["original_test"].items()}}
            for n, r in rt["models"].items() for k, v in r["table"].items()]))
    if noise:
        save_table(cfg, "label_noise.csv", pd.DataFrame(noise["rows"]))
    log.info("Da ghi results/reports/ket_qua_thuc_nghiem.md, docs/06_results/*.md va results/tables/*.csv")


def conclusion(cfg, ev, drift, pol, rt, noise) -> str:
    prim, sec = cfg["models"]["primary"], cfg["models"]["secondary"]
    op = lambda n: ev["models"][n]["operating_points"]["operating(F1-max on val)"]
    P, S = op(prim), op(sec)
    c = ["# Kết luận (sinh tự động từ kết quả lần chạy gần nhất)\n"]
    c.append("## Điều rút ra\n")
    c.append(f"1. **Accuracy đánh lừa.** Bộ phân loại ‘luôn Benign’ có accuracy {ev['majority_baseline']['accuracy']:.4f} nhưng recall 0. "
             f"Hai mô hình đều có accuracy > 0,99 nên chỉ phân biệt được qua precision/recall/F1/FP: {prim} F1={P['f1']:.4f} (FP={P['fp']}), {sec} F1={S['f1']:.4f} (FP={S['fp']}).")
    if drift:
        ctrl = drift["control (khong drift)"]["models"][prim]["performance_at_frozen_threshold"]["f1"]
        worst = min((k for k in drift if not k.startswith("control")), key=lambda k: drift[k]["models"][prim]["performance_at_frozen_threshold"]["f1"])
        wf = drift[worst]["models"][prim]["performance_at_frozen_threshold"]["f1"]
        c.append(f"2. **Điểm cao ≠ bền vững.** Khi phân phối đổi, F1 của {prim} giảm từ {ctrl:.3f} xuống {wf:.3f} (kịch bản `{worst}`) với ngưỡng đóng băng. "
                 f"Mô hình đơn giản hơn ({sec}) không nhất thiết kém hơn khi drift: độ bền phụ thuộc vào đặc trưng mà mô hình dựa vào.")
        silent = [(k, n) for k, r in drift.items() for n, m in r["models"].items() if m["silent_failure"]]
        c.append("3. **Giám sát không nhãn không đủ.** " + (
            "Có trường hợp hiệu năng giảm mà giám sát không nhãn vẫn báo ổn: " + "; ".join(f"`{k}`/{n}" for k, n in silent) + "." if silent else
            "Trong lần chạy này mọi trường hợp suy giảm đều bị giám sát không nhãn phát hiện, nhưng kịch bản `prevalence_low` cho thấy drift của tỉ lệ tấn công có thể báo động dù mô hình vẫn tốt, nên vẫn cần mẫu có nhãn."))
    if pol:
        t = pol["triage_test"]
        c.append(f"4. **Con người trong vòng lặp có giá trị và có chi phí.** Vùng REVIEW cứu recall khi mô hình chính mất tự tin (recall chỉ-máy → máy+người ở các kịch bản drift: xem bảng mục 5 của kết quả). "
                 f"Nhưng sai sót của analyst ({cfg['hitl']['analyst_error_rate']:.0%}) làm recall hệ thống là {t['system_recall']:.4f} thay vì {t['system_recall_if_analyst_perfect']:.4f} khi analyst hoàn hảo, nên cần kiểm soát hai người khi bác bỏ cảnh báo điểm cao.")
        w = pol["workload_projection"][1]
        c.append(f"5. **Base-rate fallacy.** Ở tỉ lệ tấn công giả định {w['prevalence']:.2%}, hàng đợi cần ≈ {w['analyst_shifts_per_day']:.1f} ca analyst/ngày và chỉ {w['queue_precision']:.1%} ticket là tấn công thật (theo các giả định gộp cảnh báo trong config).")
    if rt:
        r = rt["models"][prim]; tb = r["table"]; keys = list(tb)
        c.append(f"6. **Vòng đời khép kín.** Với {prim}: giữ v1 F1(drift)={tb[keys[0]]['drift_eval']['f1']:.3f}; chỉ chỉnh ngưỡng = {tb[keys[1]]['drift_eval']['f1']:.3f}; retrain v2 = {tb[keys[2]]['drift_eval']['f1']:.3f}, thoái lui trên dữ liệu gốc {r['f1_regression_on_original']:+.3f}; quyết định: {r['decision']}.")
    if noise:
        rows = [x for x in noise["rows"] if x["model"] == prim and x["noise_type"] == "attack_to_benign"]
        mx = max(rows, key=lambda x: x["rate"])
        c.append(f"7. **Nhiễu nhãn (khái niệm).** Với {mx['rate']:.0%} nhãn tấn công bị gán nhầm là Benign, {prim} có recall {mx['recall']:.3f}, F1 {mx['f1']:.3f} trên test sạch. Bộ dữ liệu này dễ và dư thừa nên không suy rộng cho kẻ tấn công chủ động.")
    c.append("\n## Giới hạn\nXem `docs/04_design/` và mục ‘Hạn chế’ trong `docs/01_project_management/project_plan.md`: dữ liệu dễ và hẹp, không có timestamp/IP, drift là mô phỏng, FPR ước lượng từ rất ít FP, giả định gộp cảnh báo chưa đo, một seed duy nhất.")
    return "\n".join(c) + "\n"


if __name__ == "__main__":
    import json
    main()
