"""Nap mo hinh tu registry (checkpoints) theo phien ban hoac stage."""
from __future__ import annotations

from ..config import path_of
from .model_registry import ModelRegistry


def get_registry(cfg: dict) -> ModelRegistry:
    return ModelRegistry(path_of(cfg, "registry_dir"))


def load_model(cfg: dict, name: str, version: str | None = None, stage: str | None = None):
    """Tra ve (pipeline, metadata). Mac dinh nap `models.baseline_version` (v1)
    de danh gia/giam sat luon so sanh voi cung mot baseline, bat ke production hien tai."""
    reg = get_registry(cfg)
    if version is None and stage is None:
        version = cfg["models"]["baseline_version"]
    return reg.load(name, version=version, stage=stage)
