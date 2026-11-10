"""Chuong trinh 2 - Huan luyen 2 mo hinh co ban (Logistic Regression, Random Forest),
chon nguong tren VALIDATION, dang ky vao registry (versioning) va chay quality gate."""
import argparse
import shutil

from _common import *  # noqa: F401,F403
from src.training.trainer import train_and_register
from src.utils import dataframe_fingerprint


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true", help="xoa registry cu truoc khi huan luyen")
    args = ap.parse_args()
    cfg, log = setup("train_models")
    reg_dir = path_of(cfg, "registry_dir")
    if args.fresh and reg_dir.exists():
        for child in reg_dir.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    reg = registry(cfg)

    df, sp = load_data(cfg)
    Xtr, ytr, _ = subset(df, sp["train"], cfg)
    Xva, yva, _ = subset(df, sp["val"], cfg)
    fp = dataframe_fingerprint(df.iloc[sp["train"]])
    summary = {}
    for name in (cfg["models"]["primary"], cfg["models"]["secondary"]):
        log.info("== Huan luyen %s tren %s flow ==", name, f"{len(Xtr):,}")
        r = train_and_register(name, cfg, Xtr, ytr, Xva, yva, reg, fp)
        summary[name] = r
        m = r["val_at_operating"]
        log.info("%s %s | F1=%.4f P=%.4f R=%.4f | gate=%s | %.1fs", name, r["version"], m["f1"],
                 m["precision"], m["recall"], "PASS->production" if r["gate_passed"] else "FAIL->staging",
                 r["fit_seconds"])
        log.info("   nguong: %s", {k: round(v, 4) for k, v in r["thresholds"].items()})
    save_json(summary, metrics_path(cfg, "training_summary.json"))


if __name__ == "__main__":
    main()
