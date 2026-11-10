"""Xay dung 2 mo hinh co ban (Logistic Regression, Random Forest) thanh sklearn Pipeline."""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from ..preprocessing.feature_pipeline import common_steps, scaling_steps

MODEL_NAMES = ("logreg", "random_forest")


def build_pipeline(model_name: str, cfg: dict, seed: int | None = None) -> Pipeline:
    if model_name not in MODEL_NAMES:
        raise ValueError(f"Mo hinh khong biet: {model_name} (ho tro: {MODEL_NAMES})")
    seed = cfg["project"]["seed"] if seed is None else seed
    p = dict(cfg["models"][model_name])
    if model_name == "logreg":
        model = LogisticRegression(C=p["C"], max_iter=p["max_iter"],
                                   class_weight=p["class_weight"], random_state=seed)
        steps = common_steps() + scaling_steps() + [("model", model)]
    elif model_name == "random_forest":
        model = RandomForestClassifier(
            n_estimators=p["n_estimators"], max_depth=p["max_depth"],
            min_samples_leaf=p["min_samples_leaf"], max_samples=p["max_samples"],
            class_weight=p["class_weight"], n_jobs=p["n_jobs"], random_state=seed)
        steps = common_steps() + [("model", model)]
    else:
        raise ValueError(f"Mo hinh khong biet: {model_name} (ho tro: {MODEL_NAMES})")
    return Pipeline(steps)


def score(pipe: Pipeline, X) -> np.ndarray:
    """Diem tan cong P(attack) trong [0,1]."""
    return pipe.predict_proba(X)[:, 1]
