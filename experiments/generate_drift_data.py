"""Chuong trinh 4 - Tao cac tap du lieu co PHAN PHOI THAY DOI (drift mo phong) tu tap test."""
from _common import *  # noqa: F401,F403
from src.simulation.drift_scenarios import make_scenario, time_columns, rate_columns


def main():
    cfg, log = setup("04_drift_data")
    df, sp = load_data(cfg)
    pool = get_pool(df, sp, cfg)
    lab, ben = cfg["data"]["label_col"], cfg["data"]["benign_label"]
    out_dir = path_of(cfg, "drift_dir")
    out_dir.mkdir(parents=True, exist_ok=True)
    feats = [c for c in pool.columns if c != lab]

    manifest = {
        "source": "mau stratified tu TAP TEST (mo hinh chua tung huan luyen/chon nguong tren du lieu nay)",
        "pool_rows": int(len(pool)), "pool_prevalence": float((pool[lab] != ben).mean()),
        "time_features_scaled": time_columns(feats), "rate_features_inversely_scaled": rate_columns(feats),
        "warning": "DU LIEU MO PHONG co kiem soat de minh hoa drift; khong phai luu luong that.",
        "scenarios": {},
    }
    for i, (name, params) in enumerate(cfg["drift"]["scenarios"].items()):
        d = make_scenario(pool, name, params, cfg, seed=cfg["project"]["seed"] + i)
        d.to_csv(out_dir / f"{name}.csv.gz", index=False, float_format="%.7g", compression="gzip")
        manifest["scenarios"][name] = {
            "params": params, "n_rows": int(len(d)), "n_attack": int((d[lab] != ben).sum()),
            "prevalence": float((d[lab] != ben).mean()),
            "file": f"data/drift/{name}.csv.gz",
        }
        log.info("%-18s rows=%s attacks=%d (%.3f%%)", name, f"{len(d):,}", (d[lab] != ben).sum(),
                 100 * (d[lab] != ben).mean())
    save_json(manifest, out_dir / "manifest.json")


if __name__ == "__main__":
    main()
