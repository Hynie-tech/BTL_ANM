"""Model registry toi gian (file-based): versioning + stage + rollback.
Moi phien ban gom model.joblib + metadata.json (metric, nguong, hash du lieu, phien ban thu vien)."""
from __future__ import annotations

import datetime as dt
import platform
from pathlib import Path

import joblib
import sklearn

from ..utils import file_sha256, load_json, save_json

STAGES = ("staging", "production", "archived")


class ModelRegistry:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "registry.json"

    # ---------- index ----------
    def _read(self) -> dict:
        return load_json(self.index_path) if self.index_path.exists() else {"models": {}}

    def _write(self, idx: dict) -> None:
        save_json(idx, self.index_path)

    def versions(self, name: str) -> list[dict]:
        return self._read()["models"].get(name, [])

    # ---------- ghi ----------
    def register(self, name: str, estimator, *, metrics: dict, thresholds: dict,
                 params: dict, data_fingerprint: str, feature_names: list[str],
                 notes: str = "", parent_version: str | None = None,
                 stage: str = "staging") -> str:
        idx = self._read()
        entries = idx["models"].setdefault(name, [])
        version = f"v{len(entries) + 1}"
        vdir = self.root / name / version
        vdir.mkdir(parents=True, exist_ok=True)
        model_path = vdir / "model.joblib"
        joblib.dump(estimator, model_path, compress=3)
        meta = {
            "name": name, "version": version, "stage": stage,
            "created_at": dt.datetime.now().isoformat(timespec="seconds"),
            "parent_version": parent_version, "notes": notes,
            "metrics": metrics, "thresholds": thresholds, "params": params,
            "data_fingerprint": data_fingerprint, "n_features_in": len(feature_names),
            "feature_names": feature_names,
            "model_sha256": file_sha256(model_path),
            "env": {"python": platform.python_version(), "sklearn": sklearn.__version__},
        }
        save_json(meta, vdir / "metadata.json")
        entries.append({"version": version, "stage": stage, "created_at": meta["created_at"],
                        "parent_version": parent_version, "notes": notes,
                        "metrics": {k: metrics[k] for k in metrics if k in ("f1", "precision", "recall", "fpr")}})
        self._write(idx)
        return version

    def set_stage(self, name: str, version: str, stage: str) -> None:
        assert stage in STAGES
        idx = self._read()
        for e in idx["models"][name]:
            if e["version"] == version:
                e["stage"] = stage
        self._write(idx)
        meta_p = self.root / name / version / "metadata.json"
        meta = load_json(meta_p)
        meta["stage"] = stage
        save_json(meta, meta_p)

    def promote(self, name: str, version: str) -> None:
        """Dua `version` len production; phien ban production cu -> archived (de rollback)."""
        for e in self.versions(name):
            if e["stage"] == "production" and e["version"] != version:
                self.set_stage(name, e["version"], "archived")
        self.set_stage(name, version, "production")

    def rollback(self, name: str) -> str:
        """Quay lai phien ban archived gan nhat (version cao nhat < production hien tai)."""
        vs = self.versions(name)
        prod = [e for e in vs if e["stage"] == "production"]
        cur = int(prod[0]["version"][1:]) if prod else 10**9
        cands = [e for e in vs if e["stage"] == "archived" and int(e["version"][1:]) < cur]
        if not cands:
            raise RuntimeError("Khong co phien ban archived de rollback")
        target = max(cands, key=lambda e: int(e["version"][1:]))["version"]
        self.promote(name, target)
        return target

    # ---------- doc ----------
    def get_version(self, name: str, version: str | None = None, stage: str | None = None) -> str:
        vs = self.versions(name)
        if version:
            return version
        if stage:
            m = [e for e in vs if e["stage"] == stage]
            if m:
                return m[-1]["version"]
        if not vs:
            raise KeyError(f"Chua co mo hinh '{name}' trong registry")
        return vs[-1]["version"]

    def load(self, name: str, version: str | None = None, stage: str | None = None):
        v = self.get_version(name, version, stage)
        vdir = self.root / name / v
        meta = load_json(vdir / "metadata.json")
        est = joblib.load(vdir / "model.joblib")
        return est, meta
