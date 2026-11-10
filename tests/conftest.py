"""Cau hinh chung cho kiem thu: dua thu muc goc vao sys.path va cung cap du lieu do choi."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.config import load_config  # noqa: E402

CFG = load_config()


def toy_xy(n: int = 3000, seed: int = 0):
    """Du lieu tong hop nho: 1 cot hang so, 1 gia tri Inf, 1 gia tri NaN."""
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < 0.1).astype(int)
    X = pd.DataFrame({"a": rng.normal(size=n) + 3 * y, "b": rng.lognormal(3, 1, n),
                      "const": np.ones(n), "c": rng.normal(size=n)})
    X.loc[5, "b"] = np.inf
    X.loc[9, "c"] = np.nan
    return X, y


def toy_flows(n: int = 4000, seed: int = 0) -> pd.DataFrame:
    """Bang flow gia lap co cot thoi gian/toc do va nhan chuoi (de thu mo phong drift)."""
    rng = np.random.default_rng(seed)
    dur = rng.lognormal(10, 1, n).astype("float32")
    pk = rng.integers(2, 50, n).astype("float32")
    lab = np.where(rng.random(n) < 0.1, "SSH-Patator", "Benign")
    return pd.DataFrame({"Flow Duration": dur, "Flow IAT Mean": dur / pk,
                         "Flow Packets/s": pk / dur * 1e6, "Total Fwd Packets": pk, "Label": lab})
