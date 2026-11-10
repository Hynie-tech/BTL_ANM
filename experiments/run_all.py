"""Chay toan bo pipeline theo thu tu:  python experiments/run_all.py  [--skip-noise]"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    ("inspect_data.py", []),
    ("train_models.py", ["--fresh"]),
    ("compare_models.py", []),
    ("generate_drift_data.py", []),
    ("monitor_drift.py", []),
    ("tune_alert_policy.py", []),
    ("retrain_and_version.py", []),
    ("label_noise_experiment.py", []),
    ("build_report.py", []),
]

if __name__ == "__main__":
    skip_noise = "--skip-noise" in sys.argv
    t0 = time.time()
    for script, args in STEPS:
        if skip_noise and script.startswith("label_noise"):
            continue
        print(f"\n=== {script} ===", flush=True)
        r = subprocess.run([sys.executable, str(HERE / script), *args])
        if r.returncode != 0:
            sys.exit(f"Loi o buoc {script}")
    print(f"\nHoan tat sau {time.time() - t0:.0f}s. Xem reports/ket_qua_thuc_nghiem.md")
