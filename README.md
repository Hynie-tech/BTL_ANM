# BTL_ANM - AI trong phát hiện an ninh mạng: huấn luyện - đánh giá - giám sát

Đồ án thực nghiệm cho đề tài **“Đánh giá vai trò và giới hạn của AI trong phát hiện an ninh; xây dựng quy trình huấn luyện - đánh giá - giám sát thay vì chỉ tập trung vào độ chính xác.”**

Dữ liệu: flow mạng có nhãn (`Benign`, `FTP-Patator`, `SSH-Patator`), 389.714 dòng × 77 đặc trưng.
Thông điệp chính: điểm cao trên tập test **không** chứng minh hệ thống phát hiện đáng tin cậy; cần quy trình giám sát drift, ngưỡng cảnh báo hợp lý và con người xác minh.

## 1. Cấu trúc thư mục
```
BTL_ANM/
├── configs/config.yaml          # mọi tham số thực nghiệm
├── data/
│   ├── input/                   # dataset đầu vào (đặt file .parquet vào đây)
│   └── output/
│       ├── checkpoints/         # mô hình theo phiên bản (registry)
│       ├── drift_data/          # các tập dữ liệu drift + manifest.json
│       ├── predictions/         # hàng đợi xác minh mẫu
│       └── processed/           # chỉ số chia train/val/test
├── docs/
│   ├── 01_project_management/   # kế hoạch, danh sách việc, hướng dẫn, tiến độ
│   ├── 02_requirements/         # yêu cầu đề tài + ma trận truy vết
│   ├── 03_research/             # báo cáo lý thuyết (7 chủ đề + tài liệu tham khảo)
│   ├── 04_design/               # kiến trúc, luồng xử lý, SOP HITL, model card, sơ đồ
│   ├── 05_testing/              # kế hoạch, ca kiểm thử, báo cáo kiểm thử
│   └── 06_results/              # kết quả, đánh giá, kết luận (tự sinh)
├── experiments/                 # chương trình thực nghiệm
│   ├── inspect_data.py          # 1. EDA + chia tập
│   ├── train_models.py          # 2. huấn luyện 2 mô hình, đăng ký v1
│   ├── compare_models.py        # 3. BT1: so sánh mô hình (P/R/F1/FP, base-rate)
│   ├── generate_drift_data.py   # 4. tạo tập dữ liệu drift
│   ├── monitor_drift.py         # 5. BT2: giám sát drift (không nhãn + có nhãn)
│   ├── tune_alert_policy.py     # 6. ngưỡng 3 vùng + hàng đợi người xác minh
│   ├── retrain_and_version.py   # 7. retrain, quality gate, promote, rollback
│   ├── label_noise_experiment.py# 8. nhiễu nhãn (poisoning mức khái niệm)
│   ├── build_report.py          # 9. sinh báo cáo/CSV
│   ├── run_all.py  registry_cli.py  make_diagrams.py
├── notebooks/                   # 01 khám phá, 02 huấn luyện/so sánh, 03 tổng hợp
├── results/{figures,tables,reports}/
├── src/
│   ├── config.py  utils.py
│   ├── preprocessing/           # data_loader, feature_pipeline
│   ├── models/                  # model_builder, model_inspector, model_registry, model_loader
│   ├── training/                # trainer (train, gate, retrain)
│   ├── evaluation/              # metrics, thresholds
│   ├── monitoring/              # drift_detector (PSI, KS)
│   ├── simulation/              # drift_scenarios
│   ├── hitl/                    # triage (hàng đợi, analyst, audit, khối lượng)
│   └── visualization/           # plot_results, save_results
├── tests/                       # 47 ca kiểm thử
├── CHANGELOG.md  LICENSE  README.md  requirements.txt  .gitignore
```

## 2. Đáp ứng yêu cầu đề bài
| Yêu cầu | Ở đâu |
|---|---|
| Dữ liệu flow có nhãn | `data/input/` |
| 2 mô hình cơ bản | Logistic Regression + Random Forest: `src/models/model_builder.py` |
| Precision / recall / F1 / false positive | `experiments/compare_models.py` → `results/tables/test_metrics.csv` |
| Tập dữ liệu có phân phối thay đổi | `data/output/drift_data/*.csv.gz` |
| Đề xuất ngưỡng cảnh báo | `experiments/tune_alert_policy.py`, `results/reports/ket_qua_thuc_nghiem.md` mục 5 |
| Quy trình con người xác minh | `docs/04_design/hitl_sop.md` |
| Lý thuyết (AI & ứng phó, dữ liệu, nhiễu/poisoning, drift, false positive, lifecycle/HITL) | `docs/03_research/` |

## 3. Cài đặt và chạy
```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Đặt Bruteforce-Tuesday-no-metadata.parquet vào data/input/

python experiments/run_all.py            # toàn bộ pipeline (thêm --skip-noise để bỏ bước chậm nhất)
python -m pytest tests -q                # hoặc: python -m unittest discover -s tests
```
Chạy từng bước: xem `docs/01_project_management/task_guide.md`. Mọi lệnh chạy từ **thư mục gốc**. Kết quả tái lập được nhờ `seed` trong `configs/config.yaml`.

Quản lý phiên bản mô hình:
```bash
python experiments/registry_cli.py list
python experiments/registry_cli.py rollback random_forest
python experiments/registry_cli.py promote random_forest v2
```

## 4. Lưu ý
- File dữ liệu gốc (47 MB) bị `.gitignore` bỏ qua; clone repo xong phải tự đặt vào `data/input/`.
- Các tập drift là **mô phỏng** từ tập test, không phải lưu lượng thật.
- Dữ liệu brute-force này rất dễ phân loại và không có timestamp/IP, nên số liệu lạc quan; xem `docs/04_design/experiment_design_and_limitations.md` trước khi diễn giải.
- Mọi con số trong `results/` và `docs/06_results/` được sinh từ lần chạy thực tế; các tài liệu còn lại cố ý không gõ cứng số liệu.
- Các bước 3, 5, 6, 7 luôn so với `models.baseline_version` (mặc định `v1`) nên chạy riêng lẻ vẫn đúng sau khi `v2` đã được promote.
