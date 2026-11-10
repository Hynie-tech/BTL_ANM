"""Kham pha mo hinh da huan luyen: cot nao duoc giu, dac trung nao quan trong."""
from __future__ import annotations

import numpy as np
from sklearn.pipeline import Pipeline


def kept_feature_names(pipe: Pipeline, feature_names: list[str]) -> list[str]:
    mask = pipe.named_steps["var"].get_support()
    return [f for f, m in zip(feature_names, mask) if m]


def top_features(pipe: Pipeline, feature_names: list[str], k: int = 15) -> list[dict]:
    """Do quan trong (Random Forest) hoac |he so| (Logistic Regression)."""
    names = kept_feature_names(pipe, feature_names)
    m = pipe.named_steps["model"]
    imp = m.feature_importances_ if hasattr(m, "feature_importances_") else np.abs(m.coef_[0])
    order = np.argsort(imp)[::-1][:k]
    return [{"feature": names[i], "importance": float(imp[i])} for i in order]


def describe(pipe: Pipeline) -> dict:
    """Tom tat cac buoc cua pipeline (de dua vao docs / model card)."""
    return {"steps": [n for n, _ in pipe.steps], "model": type(pipe.named_steps["model"]).__name__,
            "n_features_kept": int(pipe.named_steps["var"].get_support().sum())}
