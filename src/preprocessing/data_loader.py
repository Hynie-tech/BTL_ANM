"""Doc du lieu flow co nhan, chuan hoa nhan, chia train/val/test (stratified)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from ..config import ROOT, path_of


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    name = path.name.lower()
    if name.endswith(".parquet"):
        return pd.read_parquet(path)
    if name.endswith(".csv") or name.endswith(".csv.gz"):
        return pd.read_csv(path)
    raise ValueError(f"Dinh dang khong ho tro: {path}")


def load_raw(cfg: dict) -> pd.DataFrame:
    """Doc file goc. Nhan (Label) -> str; dac trung -> float32 de tiet kiem RAM."""
    p = ROOT / cfg["paths"]["input_data"]
    if not p.exists():
        raise FileNotFoundError(
            f"Khong thay {p}. Hay copy file .parquet vao data/input/ (xem README)."
        )
    df = read_table(p)
    return normalize(df, cfg)


def normalize(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    lab = cfg["data"]["label_col"]
    df = df.copy()
    df[lab] = df[lab].astype(str).str.strip()
    feats = [c for c in df.columns if c != lab]
    df[feats] = df[feats].astype("float32")
    return df


def feature_columns(df: pd.DataFrame, cfg: dict) -> list[str]:
    return [c for c in df.columns if c != cfg["data"]["label_col"]]


def to_xy(df: pd.DataFrame, cfg: dict):
    """Tra ve X (DataFrame), y nhi phan (1 = tan cong), attack_type (Series chuoi)."""
    lab, ben = cfg["data"]["label_col"], cfg["data"]["benign_label"]
    X = df[feature_columns(df, cfg)]
    attack_type = df[lab]
    y = (attack_type != ben).astype(np.int8).to_numpy()
    return X, y, attack_type


def make_splits(df: pd.DataFrame, cfg: dict) -> dict[str, np.ndarray]:
    """Chia stratified theo loai nhan. Luu CHI SO (khong luu ban sao du lieu)."""
    lab = cfg["data"]["label_col"]
    s = cfg["data"]["split"]
    seed = cfg["project"]["seed"]
    idx = np.arange(len(df))
    strat = df[lab].to_numpy()
    tr, rest = train_test_split(idx, train_size=s["train"], stratify=strat, random_state=seed)
    val_share = s["val"] / (s["val"] + s["test"])
    va, te = train_test_split(rest, train_size=val_share, stratify=strat[rest], random_state=seed)
    return {"train": np.sort(tr), "val": np.sort(va), "test": np.sort(te)}


def splits_path(cfg: dict) -> Path:
    return path_of(cfg, "processed_dir", "splits.npz")


def save_splits(splits: dict[str, np.ndarray], cfg: dict) -> Path:
    p = splits_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(p, **splits)
    return p


def load_splits(df: pd.DataFrame, cfg: dict) -> dict[str, np.ndarray]:
    p = splits_path(cfg)
    if p.exists():
        z = np.load(p)
        sp = {k: z[k] for k in ("train", "val", "test")}
        if sum(len(v) for v in sp.values()) == len(df):
            return sp
    sp = make_splits(df, cfg)
    save_splits(sp, cfg)
    return sp
