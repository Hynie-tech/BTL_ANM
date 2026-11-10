"""Ve hinh cho bao cao (matplotlib, backend Agg - chay duoc tren may khong man hinh)."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import precision_recall_curve  # noqa: E402

plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.grid": True,
                     "grid.alpha": 0.25, "axes.spines.top": False, "axes.spines.right": False})
C = {"logreg": "#d95f02", "random_forest": "#1b9e77", "base": "#4c72b0", "drift": "#c44e52",
     "grey": "#8c8c8c"}


def _save(fig, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return str(path)


def class_distribution(counts: dict, path):
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    names, vals = list(counts), list(counts.values())
    ax[0].bar(names, vals, color=[C["base"], C["drift"], C["drift"]][: len(names)])
    ax[0].set_title("Số flow theo nhãn (tuyến tính)")
    for i, v in enumerate(vals):
        ax[0].text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=8)
    ax[1].bar(names, vals, color=[C["base"], C["drift"], C["drift"]][: len(names)])
    ax[1].set_yscale("log"); ax[1].set_title("Số flow theo nhãn (log) - mất cân bằng lớp")
    return _save(fig, path)


def pr_curves(curves: dict, path, marks: dict | None = None, title="Precision-Recall (tập test)"):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for name, (y, s) in curves.items():
        p, r, _ = precision_recall_curve(y, s)
        ax.plot(r, p, label=name, color=C.get(name, None), lw=2)
    for name, pts in (marks or {}).items():
        for lab, (r, p) in pts.items():
            ax.scatter([r], [p], s=45, zorder=5, label=f"{name}: {lab}")
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.set_title(title)
    ax.set_xlim(0.0, 1.01); ax.set_ylim(0.0, 1.02); ax.legend(fontsize=7, loc="lower left")
    return _save(fig, path)


def confusion_pair(cms: dict, path):
    fig, axes = plt.subplots(1, len(cms), figsize=(4.2 * len(cms), 3.6))
    axes = np.atleast_1d(axes)
    for ax, (name, cm) in zip(axes, cms.items()):
        cm = np.asarray(cm)
        ax.imshow(cm, cmap="Blues"); ax.grid(False)
        ax.set_xticks([0, 1], ["Benign", "Attack"]); ax.set_yticks([0, 1], ["Benign", "Attack"])
        ax.set_xlabel("Dự đoán"); ax.set_ylabel("Thực tế"); ax.set_title(name, fontsize=10)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black")
    return _save(fig, path)


def threshold_tradeoff(rows: list[dict], path, marks: dict | None = None, title=""):
    t = [r["threshold"] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8))
    ax[0].plot(t, [r["precision"] for r in rows], label="Precision", color="#1b9e77", lw=2)
    ax[0].plot(t, [r["recall"] for r in rows], label="Recall", color="#d95f02", lw=2)
    ax[0].plot(t, [r["f1"] for r in rows], label="F1", color="#7570b3", lw=1.5, ls="--")
    ax[0].set_xlabel("Ngưỡng điểm số"); ax[0].set_title("Precision / Recall / F1 theo ngưỡng " + title)
    ax[1].plot(t, [r["fp_per_100k_flows"] for r in rows], color=C["drift"], lw=2)
    ax[1].set_yscale("symlog", linthresh=1); ax[1].set_xlabel("Ngưỡng điểm số")
    ax[1].set_title("Cảnh báo giả (FP) / 100.000 flow")
    for name, v in (marks or {}).items():
        for a in ax:
            a.axvline(v, color=C["grey"], ls=":", lw=1)
        ax[0].text(v, 0.02, name, rotation=90, fontsize=7, va="bottom", ha="right")
    ax[0].legend(fontsize=8)
    return _save(fig, path)


def prevalence_curve(series: dict, path, mark=None):
    """series: name -> (recall, fpr)."""
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    p = np.logspace(-5, -0.5, 200)
    for name, (rec, fpr) in series.items():
        prec = rec * p / (rec * p + fpr * (1 - p))
        ax.plot(p, prec, label=f"{name} (TPR={rec:.3f}, FPR={fpr:.5f})", color=C.get(name), lw=2)
    if mark:
        ax.axvline(mark, color=C["grey"], ls=":"); ax.text(mark, 0.05, " giả định triển khai", fontsize=7)
    ax.set_xscale("log"); ax.set_xlabel("Tỷ lệ tấn công thực tế (prevalence)")
    ax.set_ylabel("Precision kỳ vọng"); ax.set_ylim(0, 1.02); ax.legend(fontsize=7)
    ax.set_title("Base-rate fallacy: precision sụp khi tấn công hiếm")
    return _save(fig, path)


def scenario_performance(results: dict, path, metrics=("precision", "recall", "f1")):
    """results: {scenario: {model: {metric: v}}}."""
    scen = list(results)
    models = list(next(iter(results.values())))
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.6 * len(metrics), 3.8), sharey=True)
    w = 0.8 / len(models)
    for ax, m in zip(axes, metrics):
        for i, mod in enumerate(models):
            vals = [results[s][mod][m] for s in scen]
            ax.bar(np.arange(len(scen)) + i * w, vals, w, label=mod, color=C.get(mod))
        ax.set_xticks(np.arange(len(scen)) + w * (len(models) - 1) / 2, scen, rotation=25, ha="right", fontsize=8)
        ax.set_title(m); ax.set_ylim(0, 1.05)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=len(models), bbox_to_anchor=(0.5, -0.1), fontsize=9)
    fig.suptitle("Hiệu năng với ngưỡng cố định của v1 khi dữ liệu drift", y=1.02)
    return _save(fig, path)


def psi_bars(tab, path, psi_warn, psi_alert, title="", top=15):
    t = tab.head(top).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    col = ["#c44e52" if v >= psi_alert else "#dd8452" if v >= psi_warn else "#4c72b0" for v in t["psi"]]
    ax.barh(t["feature"], t["psi"], color=col)
    ax.axvline(psi_warn, color="orange", ls="--", lw=1); ax.axvline(psi_alert, color="red", ls="--", lw=1)
    ax.set_xlabel("PSI"); ax.set_title(f"Top {top} đặc trưng drift mạnh nhất - {title}")
    return _save(fig, path)


def psi_heatmap(mat, path, psi_alert):
    """mat: DataFrame (feature x scenario)."""
    fig, ax = plt.subplots(figsize=(1.6 * mat.shape[1] + 3, 0.28 * len(mat) + 1.5))
    im = ax.imshow(np.clip(mat.to_numpy(), 0, 2 * psi_alert * 2), aspect="auto", cmap="YlOrRd")
    ax.grid(False)
    ax.set_xticks(range(mat.shape[1]), mat.columns, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(mat)), mat.index, fontsize=7)
    fig.colorbar(im, ax=ax, label="PSI (cắt ở %.1f)" % (4 * psi_alert))
    ax.set_title("PSI của các đặc trưng drift mạnh nhất, theo kịch bản")
    return _save(fig, path)


def score_hist(base, drift_scores: dict, thr: dict, path, title="Phân phối điểm số mô hình"):
    fig, ax = plt.subplots(figsize=(7.5, 4))
    bins = np.linspace(0, 1, 41)
    ax.hist(base, bins=bins, alpha=0.5, label="baseline (test)", color=C["base"], density=True)
    for n, s in drift_scores.items():
        ax.hist(s, bins=bins, histtype="step", lw=1.6, label=n, density=True)
    for k, v in thr.items():
        ax.axvline(v, ls=":", color=C["grey"]); ax.text(v, ax.get_ylim()[1] * 0.9, k, rotation=90, fontsize=7)
    ax.set_yscale("log"); ax.set_xlabel("Điểm P(attack)"); ax.legend(fontsize=7); ax.set_title(title)
    return _save(fig, path)


def lines(df, x, ys: dict, path, title, xlabel, ylabel="Điểm", ylim=(0, 1.02), xlog=False):
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for lab, col in ys.items():
        ax.plot(df[x], df[col], marker="o", label=lab, lw=2)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title); ax.set_ylim(*ylim)
    if xlog:
        ax.set_xscale("symlog", linthresh=0.01)
    ax.legend(fontsize=8)
    return _save(fig, path)


def workload_bars(rows: list[dict], path):
    """rows: [{prevalence, analyst_shifts_per_day, queue_precision}]"""
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    x = [f"{r['prevalence']:.3%}" for r in rows]
    ax[0].bar(x, [r["analyst_shifts_per_day"] for r in rows], color=C["drift"])
    ax[0].set_ylabel("Số ca analyst / ngày"); ax[0].set_xlabel("Tỷ lệ tấn công thực tế")
    ax[0].set_title("Khối lượng xác minh dự kiến")
    ax[1].bar(x, [r["queue_precision"] for r in rows], color=C["base"])
    ax[1].set_ylim(0, 1.02); ax[1].set_xlabel("Tỷ lệ tấn công thực tế")
    ax[1].set_title("Tỷ lệ cảnh báo trong hàng đợi là tấn công thật")
    return _save(fig, path)
