"""Chuong trinh 1 - Kham pha du lieu (EDA), kiem tra chat luong, chia train/val/test."""
from _common import *  # noqa: F401,F403
from src.utils import dataframe_fingerprint
from src.visualization import plot_results as plots


def main():
    cfg, log = setup("01_prepare")
    lab = cfg["data"]["label_col"]
    df, sp = load_data(cfg)
    X, y, at = to_xy(df, cfg)
    log.info("Du lieu: %s dong x %s dac trung", f"{len(df):,}", X.shape[1])

    counts = at.value_counts().to_dict()
    const_cols = X.columns[X.nunique() <= 1].tolist()
    eda = {
        "n_rows": len(df), "n_features": X.shape[1],
        "label_counts": counts,
        "attack_prevalence": float(y.mean()),
        "majority_baseline_accuracy": float(1 - y.mean()),
        "n_duplicate_rows_after_float32": int(df.duplicated().sum()),
        "n_missing": int(df.isna().sum().sum()),
        "n_inf": int(np.isinf(X.to_numpy(dtype="float64")).sum()),
        "n_constant_features": len(const_cols), "constant_features": const_cols,
        "has_timestamp": cfg["data"]["has_timestamp"],
    }
    splits = {}
    for name, idx in sp.items():
        part = df.iloc[idx]
        splits[name] = {"n": int(len(idx)), "label_counts": part[lab].value_counts().to_dict(),
                        "attack_prevalence": float((part[lab] != cfg["data"]["benign_label"]).mean()),
                        "fingerprint": dataframe_fingerprint(part)}
    eda["splits"] = splits

    # Dac trung phan biet nhat (so sanh trung vi benign vs attack, theo thang log) - chi de mo ta
    med = X.groupby(at.where(at == cfg["data"]["benign_label"], "Attack")).median().T
    eda["note_top_features"] = "Xem notebooks/01_explore_data.ipynb cho thong ke chi tiet"
    save_json(eda, metrics_path(cfg, "eda.json"))
    plots.class_distribution(counts, fig_path(cfg, "01_class_distribution.png"))

    log.info("Nhan: %s | prevalence tan cong = %.3f%% | accuracy 'luon bao Benign' = %.2f%%",
             counts, 100 * eda["attack_prevalence"], 100 * eda["majority_baseline_accuracy"])
    log.info("Trung lap: %d | NaN: %d | Inf: %d | cot hang so: %d",
             eda["n_duplicate_rows_after_float32"], eda["n_missing"], eda["n_inf"], eda["n_constant_features"])
    for k, v in splits.items():
        log.info("Split %-5s n=%s  prevalence=%.3f%%", k, f"{v['n']:,}", 100 * v["attack_prevalence"])


if __name__ == "__main__":
    main()
