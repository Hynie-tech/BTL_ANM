"""Tien ich chung: seed, logging, JSON, fingerprint du lieu, bang markdown."""
from __future__ import annotations

import hashlib
import json
import logging
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def get_logger(name: str = "btl_anm") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger


class _Encoder(json.JSONEncoder):
    def default(self, o):  # noqa: D401
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return None if np.isnan(o) else float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, Path):
            return str(o)
        return super().default(o)


def save_json(obj, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, cls=_Encoder)


def load_json(path: str | Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dataframe_fingerprint(df: pd.DataFrame) -> str:
    """Dau van sha256 cua mot DataFrame (shape + ten cot + tong hash hang).
    Dung de ghi vao metadata mo hinh -> biet mo hinh duoc huan luyen tren du lieu nao."""
    h = hashlib.sha256()
    h.update(str(df.shape).encode())
    h.update("|".join(map(str, df.columns)).encode())
    row_hash = pd.util.hash_pandas_object(df, index=False).to_numpy()
    h.update(np.uint64(row_hash.sum(dtype=np.uint64)).tobytes())
    return h.hexdigest()[:16]


def file_sha256(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def md_table(rows: list[list], headers: list[str]) -> str:
    """Bang markdown don gian (khong can thu vien tabulate)."""
    def fmt(v):
        if isinstance(v, float):
            return f"{v:.4f}" if abs(v) < 1000 else f"{v:,.0f}"
        return str(v)

    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(fmt(v) for v in r) + " |")
    return "\n".join(out)
