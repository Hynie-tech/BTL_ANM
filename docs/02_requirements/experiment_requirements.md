# Yêu cầu thực nghiệm (demo)

Dùng dữ liệu flow có nhãn hoặc dữ liệu tổng hợp; xây dựng 2 mô hình cơ bản; đánh giá precision/recall/F1 và false positive; tạo một tập dữ liệu có phân phối thay đổi để minh hoạ drift; đề xuất ngưỡng cảnh báo và quy trình con người xác minh cảnh báo.

## Ma trận truy vết yêu cầu → hiện thực
| # | Yêu cầu | Hiện thực | Bằng chứng |
|---|---|---|---|
| R1 | Dữ liệu flow có nhãn | `data/input/Bruteforce-Tuesday-no-metadata.parquet` (389.714 flow, nhãn Benign/FTP-Patator/SSH-Patator) | `results/tables/eda.json` |
| R2 | 2 mô hình cơ bản | Logistic Regression, Random Forest (`src/models/model_builder.py`) | `results/tables/training_summary.json` |
| R3 | precision / recall / F1 / false positive | `src/evaluation/metrics.py`, `experiments/compare_models.py` | `results/tables/test_metrics.csv` |
| R4 | Tập dữ liệu có phân phối thay đổi | 4 kịch bản trong `data/output/drift_data/` (`generate_drift_data.py`) | `data/output/drift_data/manifest.json` |
| R5 | Minh hoạ drift | Giám sát không nhãn + có nhãn (`monitor_drift.py`) | `results/tables/drift_summary.csv`, `results/figures/05_*.png` |
| R6 | Đề xuất ngưỡng cảnh báo | Chính sách 3 vùng + chi phí + năng lực analyst (`tune_alert_policy.py`) | `results/tables/alert_policy_hitl.json` |
| R7 | Quy trình con người xác minh | `docs/04_design/hitl_sop.md` + mô phỏng hàng đợi | `data/output/predictions/review_queue_sample.csv` |
| R8 | Lifecycle, versioning | Registry, quality gate, retrain, rollback (`retrain_and_version.py`) | `results/tables/retrain_comparison.json` |
| R9 | Nhiễu / poisoning (khái niệm) | Thí nghiệm nhiễu nhãn (`label_noise_experiment.py`) | `results/tables/label_noise.csv` |
