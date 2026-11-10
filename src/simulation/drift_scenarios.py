"""Tao tap du lieu co PHAN PHOI THAY DOI tu tap test (du lieu mo hinh chua tung thay).
Day la drift MO PHONG (synthetic) co kiem soat, khong phai du lieu that - tham so nam trong config.

Cac kich ban:
  covariate_network : ha tang cham di -> thoi gian (duration/IAT/active/idle) moi flow bi keo gian,
                      toc do (…/s) giam tuong ung.            -> covariate shift  P(X) doi
  prevalence_low    : ty le tan cong giam manh.               -> prior shift      P(Y) doi
  evasion_low_slow  : ke tan cong lam cham (low-and-slow) de
                      tranh phat hien; chi flow tan cong doi.  -> concept drift    P(X|Y) doi
  combined          : ca ba cung luc.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TIME_KEYS = ("Duration", "IAT", "Active", "Idle")


def time_columns(cols) -> list[str]:
    return [c for c in cols if any(k in c for k in TIME_KEYS)]


def rate_columns(cols) -> list[str]:
    return [c for c in cols if c.endswith("/s")]


def scale_time(df: pd.DataFrame, mask: np.ndarray, median: float, sigma: float,
               rng: np.random.Generator, feats: list[str]) -> pd.DataFrame:
    """Nhan cac cot thoi gian voi he so k ~ lognormal(median, sigma) (rieng tung flow),
    chia cac cot toc do cho cung k (de dac trung van nhat quan)."""
    if not mask.any():
        return df
    k = rng.lognormal(mean=np.log(median), sigma=sigma, size=int(mask.sum())).astype(np.float32)
    tcols, rcols = time_columns(feats), rate_columns(feats)
    df.loc[mask, tcols] = df.loc[mask, tcols].to_numpy() * k[:, None]
    df.loc[mask, rcols] = df.loc[mask, rcols].to_numpy() / k[:, None]
    return df


def resample_prevalence(df: pd.DataFrame, is_attack: np.ndarray, prevalence: float,
                        rng: np.random.Generator) -> pd.DataFrame:
    """Giu toan bo benign, lay mau lai tan cong sao cho ty le = prevalence."""
    ben_idx = np.where(~is_attack)[0]
    att_idx = np.where(is_attack)[0]
    n_att = max(1, int(round(prevalence * len(ben_idx) / (1 - prevalence))))
    n_att = min(n_att, len(att_idx))
    keep = np.concatenate([ben_idx, rng.choice(att_idx, n_att, replace=False)])
    return df.iloc[np.sort(keep)].reset_index(drop=True)


def make_scenario(base: pd.DataFrame, name: str, params: dict, cfg: dict, seed: int) -> pd.DataFrame:
    lab, ben = cfg["data"]["label_col"], cfg["data"]["benign_label"]
    rng = np.random.default_rng(seed)
    df = base.copy().reset_index(drop=True)
    feats = [c for c in df.columns if c != lab]
    is_att = (df[lab] != ben).to_numpy()

    if name in ("covariate_network", "combined"):
        df = scale_time(df, np.ones(len(df), bool), params["time_scale_median"],
                        params["time_scale_sigma"], rng, feats)
    if name in ("evasion_low_slow", "combined"):
        df = scale_time(df, is_att, params["attack_time_scale_median"],
                        params["attack_time_scale_sigma"], rng, feats)
    if name in ("prevalence_low", "combined"):
        df = resample_prevalence(df, (df[lab] != ben).to_numpy(), params["attack_prevalence"], rng)
    if name not in ("covariate_network", "evasion_low_slow", "prevalence_low", "combined"):
        raise ValueError(f"Kich ban khong biet: {name}")
    return df
