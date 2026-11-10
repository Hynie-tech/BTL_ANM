"""Chuong trinh 8 - Thi nghiem nhieu nhan (label noise) o MUC KHAI NIEM cho chu de poisoning du lieu huan luyen.
Chi dao nhan ngau nhien trong tap huan luyen cua chinh chung ta de do do ben cua mo hinh;
khong mo phong ky thuat tan cong cu the."""
from _common import *  # noqa: F401,F403
from sklearn.base import clone
from src.evaluation.metrics import at_threshold, threshold_free
from src.models.model_builder import build_pipeline, score


def corrupt(y, kind, rate, rng):
    y = y.copy()
    if kind == "uniform":          # nhieu ngau nhien: dao nhan cua `rate` tren TOAN BO mau
        idx = rng.choice(len(y), int(rate * len(y)), replace=False)
        y[idx] = 1 - y[idx]
    else:                          # 'attack_to_benign': `rate` cua mau tan cong bi gan nham la Benign
        att = np.where(y == 1)[0]
        idx = rng.choice(att, int(rate * len(att)), replace=False)
        y[idx] = 0
    return y


def main():
    cfg, log = setup("08_label_noise")
    ln = cfg["label_noise"]; seed = cfg["project"]["seed"]
    df, sp = load_data(cfg)
    Xtr, ytr, _ = subset(df, sp["train"], cfg)
    Xte, yte, _ = subset(df, sp["test"], cfg)
    cfg_fast = {**cfg, "models": {**cfg["models"], "random_forest": {**cfg["models"]["random_forest"],
                                                                      "n_estimators": ln["rf_n_estimators"]}}}
    rows = []
    for kind in ("uniform", "attack_to_benign"):
        for rate in ln["rates"]:
            if rate == 0.0 and kind != "uniform":
                continue
            rng = np.random.default_rng(seed)
            yn = corrupt(ytr, kind, rate, rng)
            for name in (cfg["models"]["primary"], cfg["models"]["secondary"]):
                pipe = build_pipeline(name, cfg_fast).fit(Xtr, yn)
                s = score(pipe, Xte)
                m = at_threshold(yte, s, 0.5)
                rows.append({"noise_type": kind if rate > 0 else "none", "rate": rate, "model": name,
                             "precision": m["precision"], "recall": m["recall"], "f1": m["f1"], "fp": m["fp"],
                             "fn": m["fn"], **threshold_free(yte, s)})
                log.info("%-16s rate=%.2f %-14s P=%.3f R=%.3f F1=%.3f AP=%.3f", kind, rate, name,
                         m["precision"], m["recall"], m["f1"], rows[-1]["average_precision"])
    # nhieu 0% dung chung cho ca hai loai
    base = [r for r in rows if r["noise_type"] == "none"]
    for r in base:
        rows.append({**r, "noise_type": "attack_to_benign"})
    save_json({"note": "Danh gia tren test sach, nguong co dinh 0.5, nhan huan luyen bi lam nhieu.",
               "rows": rows}, metrics_path(cfg, "label_noise.json"))
    import pandas as pd_
    t = pd_.DataFrame(rows)
    from src.visualization import plot_results as plots
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
    for a, kind, ttl in zip(ax, ("uniform", "attack_to_benign"),
                            ("Nhiễu ngẫu nhiên (đảo nhãn toàn bộ)", "Tấn công bị gán nhầm là Benign")):
        for n in t["model"].unique():
            s = t[(t["noise_type"].isin([kind])) & (t["model"] == n)].sort_values("rate")
            a.plot(s["rate"], s["recall"], marker="o", label=f"{n} recall", color=plots.C[n], lw=2)
            a.plot(s["rate"], s["precision"], marker="s", ls="--", label=f"{n} precision", color=plots.C[n], alpha=.6)
        a.set_title(ttl, fontsize=10); a.set_xlabel("Tỷ lệ nhãn bị nhiễu"); a.set_ylim(0, 1.02)
    ax[0].set_ylabel("Điểm (test sạch, ngưỡng 0.5)"); ax[0].legend(fontsize=7)
    plots._save(fig, fig_path(cfg, "08_label_noise.png"))


if __name__ == "__main__":
    main()
