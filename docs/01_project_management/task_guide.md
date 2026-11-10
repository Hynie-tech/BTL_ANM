# Hướng dẫn thực hiện từng công việc

Chạy mọi lệnh từ **thư mục gốc** của project (nơi có `README.md`).

## 0. Cài đặt
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Đặt file `Bruteforce-Tuesday-no-metadata.parquet` vào `data/input/`.

## 1. Chạy từng bước
| Bước | Lệnh | Đầu ra chính |
|---|---|---|
| 1 | `python experiments/inspect_data.py` | `results/tables/eda.json`, `data/output/processed/splits.npz` |
| 2 | `python experiments/train_models.py --fresh` | `data/output/checkpoints/` (v1) |
| 3 | `python experiments/compare_models.py` | `results/tables/test_evaluation.json`, hình PR/confusion |
| 4 | `python experiments/generate_drift_data.py` | `data/output/drift_data/*.csv.gz` |
| 5 | `python experiments/monitor_drift.py` | `results/tables/drift_monitoring.json`, hình PSI |
| 6 | `python experiments/tune_alert_policy.py` | `results/tables/alert_policy_hitl.json`, `data/output/predictions/review_queue_sample.csv` |
| 7 | `python experiments/retrain_and_version.py` | phiên bản v2 trong checkpoints |
| 8 | `python experiments/label_noise_experiment.py` | `results/tables/label_noise.json` (chậm nhất) |
| 9 | `python experiments/build_report.py` | `results/reports/`, `docs/06_results/`, CSV |

Hoặc chạy tất cả: `python experiments/run_all.py` (thêm `--skip-noise` để bỏ bước 8).

## 2. Thay đổi tham số
Sửa `configs/config.yaml` (mức drift, mục tiêu precision/recall, chi phí, giả định analyst...) rồi chạy lại.

## 3. Quản lý phiên bản mô hình
```bash
python experiments/registry_cli.py list
python experiments/registry_cli.py rollback random_forest
python experiments/registry_cli.py promote random_forest v2
```

## 4. Kiểm thử
```bash
python -m pytest tests -q          # hoặc: python -m unittest discover -s tests
```

## 5. Lưu ý
- Bước 4 trở đi cần bước 2 đã chạy. Bước 7 đăng ký thêm v2 mỗi lần chạy; để làm lại từ đầu hãy chạy `train_models.py --fresh` trước.
- Các bước 3, 5, 6, 7 luôn so với `models.baseline_version` (mặc định `v1`) nên chạy riêng lẻ vẫn ổn sau khi v2 đã được promote.
