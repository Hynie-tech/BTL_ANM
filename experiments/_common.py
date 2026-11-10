"""Ham dung chung cho cac chuong trinh thuc nghiem (khong chua logic nghien cuu).
Chay tu thu muc goc project:  python experiments/<ten_file>.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.config import load_config, path_of  # noqa: E402
from src.preprocessing.data_loader import load_raw, load_splits, to_xy, read_table, normalize  # noqa: E402
from src.models.model_registry import ModelRegistry  # noqa: E402
from src.utils import get_logger, seed_everything, save_json, load_json  # noqa: E402

__all__ = ["ROOT", "np", "pd", "setup", "load_data", "subset", "registry", "metrics_path",
           "fig_path", "load_scenario", "get_pool", "path_of", "to_xy", "save_json", "load_json"]


def setup(name: str):
    cfg = load_config()
    seed_everything(cfg["project"]["seed"])
    return cfg, get_logger(name)


def load_data(cfg):
    df = load_raw(cfg)
    sp = load_splits(df, cfg)
    return df, sp


def subset(df, idx, cfg):
    return to_xy(df.iloc[idx], cfg)


def registry(cfg) -> ModelRegistry:
    return ModelRegistry(path_of(cfg, "registry_dir"))


def metrics_path(cfg, name: str) -> Path:
    return path_of(cfg, "metrics_dir", name)


def fig_path(cfg, name: str) -> Path:
    return path_of(cfg, "figures_dir", name)


def get_pool(df, sp, cfg) -> pd.DataFrame:
    """Tap 'pool' = mau stratified tu TAP TEST (mo hinh chua tung thay) -> nguon tao du lieu drift."""
    from sklearn.model_selection import train_test_split
    lab = cfg["data"]["label_col"]
    test = df.iloc[sp["test"]]
    n = min(cfg["drift"]["pool_size"], len(test))
    if n >= len(test):
        return test.reset_index(drop=True)
    idx, _ = train_test_split(np.arange(len(test)), train_size=n, stratify=test[lab].to_numpy(),
                              random_state=cfg["project"]["seed"])
    return test.iloc[np.sort(idx)].reset_index(drop=True)


def load_scenario(cfg, name: str) -> pd.DataFrame:
    p = path_of(cfg, "drift_dir", f"{name}.csv.gz")
    return normalize(read_table(p), cfg)
