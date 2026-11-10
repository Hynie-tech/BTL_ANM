"""Doc cau hinh YAML va quy doi duong dan tuong doi -> tuyet doi (goc = thu muc project)."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "config.yaml"


def load_config(path: str | Path | None = None) -> dict:
    path = Path(path) if path else DEFAULT_CONFIG
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def path_of(cfg: dict, key: str, *parts: str, create: bool = False) -> Path:
    """Lay duong dan tuyet doi tu muc `paths` trong config."""
    p = ROOT / cfg["paths"][key]
    p = p.joinpath(*parts)
    if create:
        (p if not p.suffix else p.parent).mkdir(parents=True, exist_ok=True)
    return p
