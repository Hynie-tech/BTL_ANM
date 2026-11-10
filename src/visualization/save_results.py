"""Luu ket qua thuc nghiem: JSON + bang CSV (results/tables), bao cao markdown (results/reports)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import path_of
from ..utils import save_json


def save_metrics(cfg: dict, name: str, obj) -> Path:
    p = path_of(cfg, "metrics_dir", name)
    save_json(obj, p)
    return p


def save_table(cfg: dict, name: str, df: pd.DataFrame, float_format: str = "%.6g") -> Path:
    p = path_of(cfg, "metrics_dir", name)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, float_format=float_format)
    return p


def save_markdown(cfg: dict, key: str, name: str, text: str) -> Path:
    """key: 'reports_dir' (results/reports) hoac 'docs_results_dir' (docs/06_results)."""
    p = path_of(cfg, key, name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p
