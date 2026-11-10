"""Cac buoc tien xu ly dac trung (nam TRONG sklearn Pipeline de tranh ro ri du lieu)."""
from __future__ import annotations

import numpy as np
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import FunctionTransformer, StandardScaler


def replace_inf(X):
    """Doi +/-Inf thanh NaN (de buoc impute xu ly)."""
    X = np.array(X, dtype=np.float64, copy=True)
    X[~np.isfinite(X)] = np.nan
    return X


def signed_log1p(X):
    """Nen thang do cho dac trung co duoi rat nang (Flow Duration, Bytes/s...).
    Giu dau vi mot so dac trung CICFlowMeter co the am."""
    X = np.asarray(X, dtype=np.float64)
    return np.sign(X) * np.log1p(np.abs(X))


def common_steps() -> list:
    """Xu ly Inf/NaN + loai cot hang so (vd cac cot Bulk = 0). Hoc CHI tu tap train."""
    return [
        ("inf", FunctionTransformer(replace_inf, validate=False)),
        ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("var", VarianceThreshold(0.0)),
    ]


def scaling_steps() -> list:
    """Dung cho mo hinh tuyen tinh: nen log co dau + chuan hoa."""
    return [
        ("log", FunctionTransformer(signed_log1p, validate=False)),
        ("scale", StandardScaler()),
    ]
