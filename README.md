# Cấu trúc dự án BTL_ANM

**AI trong phát hiện an ninh mạng: huấn luyện - đánh giá - giám sát - human-in-the-loop.**
Tài liệu này liệt kê **toàn bộ 142 file** trong project và vai trò của từng file. Cập nhật theo lần đóng gói gần nhất.

## 1. Tổng quan nhanh
| Thành phần | Thư mục | Vai trò |
|---|---|---|
| Cấu hình | `configs/` | Mọi tham số thực nghiệm trong một file YAML |
| Dữ liệu | `data/input/`, `data/output/` | Dataset vào; mô hình, tập drift, dự đoán, chỉ số chia tập ra |
| Thư viện | `src/` | Toàn bộ logic: tiền xử lý, mô hình, huấn luyện, đánh giá, giám sát, mô phỏng drift, HITL, vẽ hình |
| Thực nghiệm | `experiments/` | 9 chương trình chạy theo thứ tự, gọi thư viện trong `src/` |
| Notebook | `notebooks/` | 3 notebook đã chạy sẵn (khám phá, so sánh mô hình, drift + HITL) |
| Kết quả | `results/` | Hình PNG, bảng JSON/CSV, báo cáo thực nghiệm |
| Tài liệu | `docs/` | Quản lý dự án, yêu cầu, lý thuyết, thiết kế, kiểm thử, kết quả |
| Kiểm thử | `tests/` | 47 ca kiểm thử tự động |

## 2. Cây thư mục đầy đủ
```text
BTL_ANM/
├── configs/                                         # Cấu hình trung tâm
│   └── config.yaml                                  # Mọi tham số thực nghiệm (đường dẫn, mô hình, ngưỡng, drift, giả định analyst...)
├── data/                                            # Dữ liệu vào/ra
│   ├── input/                                       # Dataset đầu vào (đặt file .parquet vào đây)
│   │   ├── Bruteforce-Tuesday-no-metadata.parquet   # Dataset gốc: 389.714 flow × 77 đặc trưng + nhãn (không đưa lên Git)
│   │   └── .gitkeep                                 # Giữ thư mục rỗng trong Git
│   ├── output/                                      # Dữ liệu do chương trình sinh ra
│   │   ├── checkpoints/                             # Registry mô hình theo phiên bản
│   │   │   ├── logreg/                              # Logistic Regression
│   │   │   │   ├── v1/                              # Phiên bản gốc (baseline)
│   │   │   │   │   ├── metadata.json                # Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường
│   │   │   │   │   └── model.joblib                 # Pipeline đầy đủ (tiền xử lý + mô hình)
│   │   │   │   └── v2/                              # Phiên bản retrain sau drift
│   │   │   │       ├── metadata.json                # Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường
│   │   │   │       └── model.joblib                 # Pipeline đầy đủ (tiền xử lý + mô hình)
│   │   │   ├── random_forest/                       # Random Forest
│   │   │   │   ├── v1/                              # Phiên bản gốc (baseline)
│   │   │   │   │   ├── metadata.json                # Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường
│   │   │   │   │   └── model.joblib                 # Pipeline đầy đủ (tiền xử lý + mô hình)
│   │   │   │   └── v2/                              # Phiên bản retrain sau drift
│   │   │   │       ├── metadata.json                # Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường
│   │   │   │       └── model.joblib                 # Pipeline đầy đủ (tiền xử lý + mô hình)
│   │   │   └── registry.json                        # Chỉ mục các phiên bản mô hình + stage (staging/production/archived)
│   │   ├── drift_data/                              # Các tập dữ liệu có phân phối thay đổi (mô phỏng)
│   │   │   ├── combined.csv.gz                      # Drift: kết hợp ba kịch bản
│   │   │   ├── covariate_network.csv.gz             # Drift: mọi flow bị kéo giãn thời gian (mạng chậm hơn)
│   │   │   ├── evasion_low_slow.csv.gz              # Drift: tấn công làm chậm để né tránh
│   │   │   ├── manifest.json                        # Mô tả các tập drift: tham số, số dòng, tỷ lệ tấn công, cảnh báo mô phỏng
│   │   │   └── prevalence_low.csv.gz                # Drift: tỷ lệ tấn công giảm còn 0,5%
│   │   ├── predictions/                             # Kết quả dự đoán / hàng đợi xác minh
│   │   │   └── review_queue_sample.csv              # Ví dụ hàng đợi người xác minh (flow, điểm số, vùng, độ ưu tiên)
│   │   └── processed/                               # Dữ liệu trung gian (chỉ số chia tập)
│   │       └── splits.npz                           # Chỉ số chia train/val/test (stratified, seed cố định)
│   └── README.md                                    # Dữ liệu vào/ra
├── docs/                                            # Tài liệu dự án
│   ├── 01_project_management/                       # Quản lý dự án
│   │   ├── project_plan.md                          # Kế hoạch dự án
│   │   ├── task_guide.md                            # Hướng dẫn thực hiện từng công việc
│   │   ├── task_list.md                             # Danh sách công việc
│   │   └── timeline.md                              # Tiến độ (theo giai đoạn)
│   ├── 02_requirements/                             # Yêu cầu đề tài
│   │   ├── experiment_requirements.md               # Yêu cầu thực nghiệm (demo)
│   │   └── lab_requirements.md                      # Yêu cầu đề tài (mục tiêu và lý thuyết)
│   ├── 03_research/                                 # Nghiên cứu lý thuyết
│   │   ├── ai_in_detection.md                       # AI trong phát hiện và ứng phó
│   │   ├── evaluation_methods.md                    # Phương pháp đánh giá
│   │   ├── false_positive.md                        # Cảnh báo giả (false positive)
│   │   ├── lifecycle_monitoring_hitl.md             # Vòng đời mô hình, versioning, giám sát, human-in-the-loop
│   │   ├── model_drift.md                           # Model drift
│   │   ├── noise_poisoning.md                       # Nhiễu nhãn và poisoning (mức khái niệm)
│   │   ├── README.md                                # Tổng hợp nghiên cứu lý thuyết
│   │   ├── references.md                            # Tài liệu tham khảo
│   │   └── training_data.md                         # Dữ liệu huấn luyện
│   ├── 04_design/                                   # Thiết kế hệ thống
│   │   ├── diagrams/                                # Sơ đồ
│   │   │   ├── hitl_triage_flow.png                 # Sơ đồ phân luồng cảnh báo 3 vùng
│   │   │   └── system_flow.png                      # Sơ đồ quy trình huấn luyện - đánh giá - giám sát - xác minh
│   │   ├── experiment_design_and_limitations.md     # Thiết kế thực nghiệm, giả định và hạn chế
│   │   ├── hitl_sop.md                              # Quy trình con người xác minh cảnh báo (Human-in-the-loop SOP)
│   │   ├── model_card.md                            # Model card - bộ phát hiện brute-force trên flow (demo học thuật)
│   │   ├── processing_pipeline.md                   # Luồng xử lý dữ liệu và thực nghiệm
│   │   └── system_architecture.md                   # Kiến trúc hệ thống
│   ├── 05_testing/                                  # Kiểm thử
│   │   ├── test_cases.md                            # Danh sách ca kiểm thử
│   │   ├── test_plan.md                             # Kế hoạch kiểm thử
│   │   └── test_report.md                           # Báo cáo kiểm thử
│   └── 06_results/                                  # Tổng hợp kết quả (tự sinh)
│       ├── conclusion.md                            # Kết luận (sinh tự động từ kết quả lần chạy gần nhất)
│       ├── evaluation_results.md                    # Kết quả đánh giá mô hình (sinh tự động)
│       └── experiment_results.md                    # Kết quả thực nghiệm (sinh tự động)
├── experiments/                                     # Chương trình thực nghiệm
│   ├── __init__.py                                  # Package Python
│   ├── _common.py                                   # Hàm dùng chung cho các chương trình thực nghiệm (nạp cấu hình, dữ liệu, registry, đường dẫn)
│   ├── build_report.py                              # Bước 9: tự động sinh báo cáo, CSV và kết luận từ các file JSON kết quả
│   ├── compare_models.py                            # Bước 3 (BT1): so sánh 2 mô hình trên tập test (P/R/F1/FP, recall theo loại, base-rate)
│   ├── generate_drift_data.py                       # Bước 4: tạo các tập dữ liệu có phân phối thay đổi (drift mô phỏng) từ tập test
│   ├── inspect_data.py                              # Bước 1: khám phá dữ liệu (EDA), kiểm tra chất lượng, chia train/val/test
│   ├── label_noise_experiment.py                    # Bước 8: thí nghiệm nhiễu nhãn (poisoning ở mức khái niệm)
│   ├── make_diagrams.py                             # Vẽ sơ đồ hệ thống và sơ đồ phân luồng cảnh báo vào docs/04_design/diagrams/
│   ├── monitor_drift.py                             # Bước 5 (BT2): giám sát drift (không nhãn + có nhãn), phát hiện "drift im lặng"
│   ├── README.md                                    # `experiments/` - Chương trình thực nghiệm
│   ├── registry_cli.py                              # Dòng lệnh quản lý phiên bản mô hình: list | promote | rollback
│   ├── retrain_and_version.py                       # Bước 7: retrain v2, quality gate, promote, rollback drill
│   ├── run_all.py                                   # Chạy toàn bộ pipeline theo thứ tự (thêm --skip-noise để bỏ bước chậm nhất)
│   ├── train_models.py                              # Bước 2: huấn luyện 2 mô hình, chọn ngưỡng trên validation, đăng ký v1
│   └── tune_alert_policy.py                         # Bước 6: ngưỡng cảnh báo 3 vùng + hàng đợi người xác minh + khối lượng analyst
├── notebooks/                                       # Jupyter Notebooks (đã chạy sẵn)
│   ├── 01_explore_data.ipynb                        # Khám phá dữ liệu: mất cân bằng lớp, chất lượng, phân phối, chia tập
│   ├── 02_train_and_compare_models.ipynb            # Huấn luyện và so sánh 2 mô hình (P/R/F1/FP, PR-curve, base-rate)
│   ├── 03_drift_hitl_full.ipynb                     # Drift, giám sát, hàng đợi người, khối lượng analyst, retrain/versioning
│   └── README.md                                    # `notebooks/` - Jupyter Notebooks
├── results/                                         # Kết quả thực nghiệm
│   ├── figures/                                     # Biểu đồ PNG
│   │   ├── 01_class_distribution.png                # Số flow theo nhãn (tuyến tính và log)
│   │   ├── 03_confusion_matrices.png                # Ma trận nhầm lẫn 2 mô hình
│   │   ├── 03_feature_importance_logreg.png         # Đặc trưng quan trọng - Logistic Regression
│   │   ├── 03_feature_importance_random_forest.png  # Đặc trưng quan trọng - Random Forest
│   │   ├── 03_pr_curves.png                         # Đường Precision-Recall
│   │   ├── 05_performance_under_drift.png           # P/R/F1 theo kịch bản drift
│   │   ├── 05_psi_heatmap.png                       # PSI các đặc trưng theo kịch bản
│   │   ├── 05_score_distribution.png                # Phân phối điểm số baseline và drift
│   │   ├── 06_precision_vs_prevalence.png           # Precision theo tỷ lệ tấn công (base-rate)
│   │   ├── 06_threshold_tradeoff.png                # P/R/F1 và FP theo ngưỡng
│   │   ├── 06_workload_projection.png               # Khối lượng analyst theo tỷ lệ tấn công
│   │   └── 08_label_noise.png                       # Ảnh hưởng của nhiễu nhãn
│   ├── reports/                                     # Báo cáo thực nghiệm
│   │   └── ket_qua_thuc_nghiem.md                   # Báo cáo kết quả thực nghiệm đầy đủ (tự sinh)
│   └── tables/                                      # Bảng kết quả (JSON, CSV)
│       ├── alert_policy_hitl.json                   # Ngưỡng 3 vùng, hàng đợi người, khối lượng analyst, ngưỡng vừa sức
│       ├── drift_monitoring.json                    # Giám sát drift: PSI, tỉ lệ dự đoán, hiệu năng, drift im lặng
│       ├── drift_summary.csv                        # Tóm tắt drift (CSV)
│       ├── eda.json                                 # Thống kê dữ liệu, chia tập, fingerprint
│       ├── label_noise.csv                          # Thí nghiệm nhiễu nhãn (CSV)
│       ├── label_noise.json                         # Thí nghiệm nhiễu nhãn
│       ├── retrain_comparison.csv                   # So sánh retrain (CSV)
│       ├── retrain_comparison.json                  # So sánh v1 / v1+chỉnh ngưỡng / v2 retrain, quyết định promote
│       ├── test_evaluation.json                     # Đánh giá trên test: nhiều điểm vận hành, recall theo loại, base-rate
│       ├── test_metrics.csv                         # Bảng metric trên test (CSV)
│       └── training_summary.json                    # Kết quả huấn luyện, ngưỡng, quality gate
├── src/                                             # Mã nguồn chính (thư viện)
│   ├── evaluation/                                  # Metric và ngưỡng
│   │   ├── __init__.py                              # Package Python
│   │   ├── metrics.py                               # Metric: precision, recall, F1, false positive, công thức Bayes theo tỷ lệ tấn công
│   │   ├── README.md                                # `src/evaluation/` - Metric và ngưỡng cảnh báo
│   │   └── thresholds.py                            # Chọn ngưỡng cảnh báo trên validation; chính sách 3 vùng (alert/review/ignore)
│   ├── hitl/                                        # Human-in-the-loop
│   │   ├── __init__.py                              # Package Python
│   │   ├── README.md                                # `src/hitl/` - Human-in-the-loop
│   │   └── triage.py                                # Hàng đợi người xác minh, mô phỏng analyst, audit, khối lượng công việc
│   ├── models/                                      # Mô hình, registry
│   │   ├── __init__.py                              # Package Python
│   │   ├── model_builder.py                         # Xây dựng 2 mô hình (Logistic Regression, Random Forest) thành sklearn Pipeline
│   │   ├── model_inspector.py                       # Khám phá mô hình: cột được giữ, đặc trưng quan trọng
│   │   ├── model_loader.py                          # Nạp mô hình từ registry theo phiên bản hoặc stage
│   │   ├── model_registry.py                        # Model registry file-based: versioning, stage, rollback
│   │   └── README.md                                # `src/models/` - Mô hình và registry
│   ├── monitoring/                                  # Giám sát drift
│   │   ├── __init__.py                              # Package Python
│   │   ├── drift_detector.py                        # Đo drift: PSI, KS, PSI theo dải điểm, tổng hợp trạng thái
│   │   └── README.md                                # `src/monitoring/` - Phát hiện drift
│   ├── preprocessing/                               # Đọc dữ liệu, tiền xử lý
│   │   ├── __init__.py                              # Package Python
│   │   ├── data_loader.py                           # Đọc dữ liệu flow, chuẩn hoá nhãn, chia train/val/test phân tầng
│   │   ├── feature_pipeline.py                      # Các bước tiền xử lý đặc trưng (nằm trong Pipeline để tránh rò rỉ dữ liệu)
│   │   └── README.md                                # `src/preprocessing/` - Dữ liệu và tiền xử lý
│   ├── simulation/                                  # Sinh dữ liệu drift
│   │   ├── __init__.py                              # Package Python
│   │   ├── drift_scenarios.py                       # Sinh 4 kịch bản drift: covariate, prevalence, evasion, combined
│   │   └── README.md                                # `src/simulation/` - Sinh dữ liệu có phân phối thay đổi
│   ├── training/                                    # Huấn luyện, quality gate, retrain
│   │   ├── __init__.py                              # Package Python
│   │   ├── README.md                                # `src/training/` - Huấn luyện, quality gate, retrain
│   │   └── trainer.py                               # Huấn luyện, chọn ngưỡng, đăng ký registry, quality gate, retrain
│   ├── visualization/                               # Vẽ hình, lưu kết quả
│   │   ├── __init__.py                              # Package Python
│   │   ├── plot_results.py                          # Vẽ hình cho báo cáo (matplotlib, chạy được khi không có màn hình)
│   │   ├── README.md                                # `src/visualization/` - Vẽ hình và lưu kết quả
│   │   └── save_results.py                          # Lưu kết quả: JSON, CSV (results/tables), markdown (results/reports)
│   ├── __init__.py                                  # BTL_ANM - Vong doi AI trong phat hien an ninh mang: huan luyen - danh gia - giam sat - human-in-the-loop
│   ├── config.py                                    # Đọc cấu hình YAML và đổi đường dẫn tương đối thành tuyệt đối
│   ├── README.md                                    # `src/` - Thư viện dùng chung
│   └── utils.py                                     # Tiện ích chung: seed, logging, JSON, hash dữ liệu, bảng markdown
├── tests/                                           # Kiểm thử mã nguồn
│   ├── conftest.py                                  # Cấu hình chung cho kiểm thử: đưa thư mục gốc vào sys.path, dữ liệu tổng hợp dùng chung
│   ├── README.md                                    # `tests/` - Kiểm thử
│   ├── test_drift.py                                # Kiểm thử PSI, giám sát drift và mô phỏng drift
│   ├── test_metrics.py                              # Kiểm thử metric precision/recall/F1/FP và công thức Bayes
│   ├── test_model_registry.py                       # Kiểm thử registry (versioning, promote, rollback) và inspector
│   ├── test_pipeline.py                             # Kiểm thử tích hợp end-to-end trên dữ liệu tổng hợp
│   ├── test_preprocessing.py                        # Kiểm thử tiền xử lý, pipeline và chia tập
│   ├── test_save_results.py                         # Kiểm thử lưu JSON/CSV/Markdown và vẽ hình
│   ├── test_thresholds.py                           # Kiểm thử ngưỡng cảnh báo và chính sách 3 vùng
│   ├── test_trainer.py                              # Kiểm thử huấn luyện, quality gate và retrain
│   └── test_triage.py                               # Kiểm thử phân luồng, analyst sai, audit và khối lượng công việc
├── CHANGELOG.md                                     # Lịch sử thay đổi
├── LICENSE                                          # Giấy phép MIT
├── PROJECT_STRUCTURE.md                             # File này: cấu trúc đầy đủ của dự án
├── README.md                                        # Tài liệu chính của dự án
├── requirements.txt                                 # Thư viện cần thiết
└── .gitignore                                       # Các file loại trừ khỏi Git
```

## 3. Luồng dữ liệu giữa các thư mục
```text
data/input/*.parquet
      │  experiments/inspect_data.py
      ▼
data/output/processed/splits.npz ──► experiments/train_models.py ──► data/output/checkpoints/ (v1)
                                                │
      ┌─────────────────────────────────────────┤
      ▼                                         ▼
experiments/compare_models.py          experiments/generate_drift_data.py ──► data/output/drift_data/
      │                                         │
      │                                         ▼
      │                          experiments/monitor_drift.py ──► experiments/tune_alert_policy.py
      │                                                                   │ (hàng đợi → data/output/predictions/)
      │                                                                   ▼
      │                                         experiments/retrain_and_version.py ──► checkpoints (v2)
      ▼                                                                   │
results/tables/*.json ◄───────────────────────────────────────────────────┘
      │  experiments/build_report.py
      ▼
results/reports/ + docs/06_results/ + results/tables/*.csv
```
`src/` được gọi bởi mọi chương trình trong `experiments/`, mọi notebook và mọi test; `configs/config.yaml` được đọc qua `src/config.py`.

## 4. Chi tiết theo nhóm

### 4.1. Gốc project
| File | Mô tả |
|---|---|
| `.gitignore` | Các file loại trừ khỏi Git |
| `CHANGELOG.md` | Lịch sử thay đổi |
| `PROJECT_STRUCTURE.md` | File này: cấu trúc đầy đủ của dự án |
| `LICENSE` | Giấy phép MIT |
| `README.md` | Tài liệu chính của dự án |
| `requirements.txt` | Thư viện cần thiết |

### 4.2. Mã nguồn `src/`
| File | Mô tả |
|---|---|
| `src/README.md` | `src/` - Thư viện dùng chung |
| `src/config.py` | Đọc cấu hình YAML và đổi đường dẫn tương đối thành tuyệt đối |
| `src/utils.py` | Tiện ích chung: seed, logging, JSON, hash dữ liệu, bảng markdown |
| `src/evaluation/README.md` | `src/evaluation/` - Metric và ngưỡng cảnh báo |
| `src/evaluation/metrics.py` | Metric: precision, recall, F1, false positive, công thức Bayes theo tỷ lệ tấn công |
| `src/evaluation/thresholds.py` | Chọn ngưỡng cảnh báo trên validation; chính sách 3 vùng (alert/review/ignore) |
| `src/hitl/README.md` | `src/hitl/` - Human-in-the-loop |
| `src/hitl/triage.py` | Hàng đợi người xác minh, mô phỏng analyst, audit, khối lượng công việc |
| `src/models/README.md` | `src/models/` - Mô hình và registry |
| `src/models/model_builder.py` | Xây dựng 2 mô hình (Logistic Regression, Random Forest) thành sklearn Pipeline |
| `src/models/model_inspector.py` | Khám phá mô hình: cột được giữ, đặc trưng quan trọng |
| `src/models/model_loader.py` | Nạp mô hình từ registry theo phiên bản hoặc stage |
| `src/models/model_registry.py` | Model registry file-based: versioning, stage, rollback |
| `src/monitoring/README.md` | `src/monitoring/` - Phát hiện drift |
| `src/monitoring/drift_detector.py` | Đo drift: PSI, KS, PSI theo dải điểm, tổng hợp trạng thái |
| `src/preprocessing/README.md` | `src/preprocessing/` - Dữ liệu và tiền xử lý |
| `src/preprocessing/data_loader.py` | Đọc dữ liệu flow, chuẩn hoá nhãn, chia train/val/test phân tầng |
| `src/preprocessing/feature_pipeline.py` | Các bước tiền xử lý đặc trưng (nằm trong Pipeline để tránh rò rỉ dữ liệu) |
| `src/simulation/README.md` | `src/simulation/` - Sinh dữ liệu có phân phối thay đổi |
| `src/simulation/drift_scenarios.py` | Sinh 4 kịch bản drift: covariate, prevalence, evasion, combined |
| `src/training/README.md` | `src/training/` - Huấn luyện, quality gate, retrain |
| `src/training/trainer.py` | Huấn luyện, chọn ngưỡng, đăng ký registry, quality gate, retrain |
| `src/visualization/README.md` | `src/visualization/` - Vẽ hình và lưu kết quả |
| `src/visualization/plot_results.py` | Vẽ hình cho báo cáo (matplotlib, chạy được khi không có màn hình) |
| `src/visualization/save_results.py` | Lưu kết quả: JSON, CSV (results/tables), markdown (results/reports) |

### 4.3. Chương trình thực nghiệm `experiments/`
| File | Mô tả |
|---|---|
| `experiments/README.md` | `experiments/` - Chương trình thực nghiệm |
| `experiments/_common.py` | Hàm dùng chung cho các chương trình thực nghiệm (nạp cấu hình, dữ liệu, registry, đường dẫn) |
| `experiments/build_report.py` | Bước 9: tự động sinh báo cáo, CSV và kết luận từ các file JSON kết quả |
| `experiments/compare_models.py` | Bước 3 (BT1): so sánh 2 mô hình trên tập test (P/R/F1/FP, recall theo loại, base-rate) |
| `experiments/generate_drift_data.py` | Bước 4: tạo các tập dữ liệu có phân phối thay đổi (drift mô phỏng) từ tập test |
| `experiments/inspect_data.py` | Bước 1: khám phá dữ liệu (EDA), kiểm tra chất lượng, chia train/val/test |
| `experiments/label_noise_experiment.py` | Bước 8: thí nghiệm nhiễu nhãn (poisoning ở mức khái niệm) |
| `experiments/make_diagrams.py` | Vẽ sơ đồ hệ thống và sơ đồ phân luồng cảnh báo vào docs/04_design/diagrams/ |
| `experiments/monitor_drift.py` | Bước 5 (BT2): giám sát drift (không nhãn + có nhãn), phát hiện "drift im lặng" |
| `experiments/registry_cli.py` | Dòng lệnh quản lý phiên bản mô hình: list | promote | rollback |
| `experiments/retrain_and_version.py` | Bước 7: retrain v2, quality gate, promote, rollback drill |
| `experiments/run_all.py` | Chạy toàn bộ pipeline theo thứ tự (thêm --skip-noise để bỏ bước chậm nhất) |
| `experiments/train_models.py` | Bước 2: huấn luyện 2 mô hình, chọn ngưỡng trên validation, đăng ký v1 |
| `experiments/tune_alert_policy.py` | Bước 6: ngưỡng cảnh báo 3 vùng + hàng đợi người xác minh + khối lượng analyst |

### 4.4. Notebook `notebooks/`
| File | Mô tả |
|---|---|
| `notebooks/01_explore_data.ipynb` | Khám phá dữ liệu: mất cân bằng lớp, chất lượng, phân phối, chia tập |
| `notebooks/02_train_and_compare_models.ipynb` | Huấn luyện và so sánh 2 mô hình (P/R/F1/FP, PR-curve, base-rate) |
| `notebooks/03_drift_hitl_full.ipynb` | Drift, giám sát, hàng đợi người, khối lượng analyst, retrain/versioning |
| `notebooks/README.md` | `notebooks/` - Jupyter Notebooks |

### 4.5. Kiểm thử `tests/`
| File | Mô tả |
|---|---|
| `tests/README.md` | `tests/` - Kiểm thử |
| `tests/conftest.py` | Cấu hình chung cho kiểm thử: đưa thư mục gốc vào sys.path, dữ liệu tổng hợp dùng chung |
| `tests/test_drift.py` | Kiểm thử PSI, giám sát drift và mô phỏng drift |
| `tests/test_metrics.py` | Kiểm thử metric precision/recall/F1/FP và công thức Bayes |
| `tests/test_model_registry.py` | Kiểm thử registry (versioning, promote, rollback) và inspector |
| `tests/test_pipeline.py` | Kiểm thử tích hợp end-to-end trên dữ liệu tổng hợp |
| `tests/test_preprocessing.py` | Kiểm thử tiền xử lý, pipeline và chia tập |
| `tests/test_save_results.py` | Kiểm thử lưu JSON/CSV/Markdown và vẽ hình |
| `tests/test_thresholds.py` | Kiểm thử ngưỡng cảnh báo và chính sách 3 vùng |
| `tests/test_trainer.py` | Kiểm thử huấn luyện, quality gate và retrain |
| `tests/test_triage.py` | Kiểm thử phân luồng, analyst sai, audit và khối lượng công việc |

### 4.6. Cấu hình và dữ liệu
| File | Mô tả |
|---|---|
| `configs/config.yaml` | Mọi tham số thực nghiệm (đường dẫn, mô hình, ngưỡng, drift, giả định analyst...) |

| File | Mô tả |
|---|---|
| `data/README.md` | `data/` - Dữ liệu |
| `data/input/.gitkeep` | Giữ thư mục rỗng trong Git |
| `data/input/Bruteforce-Tuesday-no-metadata.parquet` | Dataset gốc: 389.714 flow × 77 đặc trưng + nhãn (không đưa lên Git) |
| `data/output/checkpoints/registry.json` | Chỉ mục các phiên bản mô hình + stage (staging/production/archived) |
| `data/output/checkpoints/logreg/v1/metadata.json` | Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường |
| `data/output/checkpoints/logreg/v1/model.joblib` | Pipeline đầy đủ (tiền xử lý + mô hình) |
| `data/output/checkpoints/logreg/v2/metadata.json` | Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường |
| `data/output/checkpoints/logreg/v2/model.joblib` | Pipeline đầy đủ (tiền xử lý + mô hình) |
| `data/output/checkpoints/random_forest/v1/metadata.json` | Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường |
| `data/output/checkpoints/random_forest/v1/model.joblib` | Pipeline đầy đủ (tiền xử lý + mô hình) |
| `data/output/checkpoints/random_forest/v2/metadata.json` | Metric, ngưỡng, hash dữ liệu/mô hình, phiên bản cha, môi trường |
| `data/output/checkpoints/random_forest/v2/model.joblib` | Pipeline đầy đủ (tiền xử lý + mô hình) |
| `data/output/drift_data/combined.csv.gz` | Drift: kết hợp ba kịch bản |
| `data/output/drift_data/covariate_network.csv.gz` | Drift: mọi flow bị kéo giãn thời gian (mạng chậm hơn) |
| `data/output/drift_data/evasion_low_slow.csv.gz` | Drift: tấn công làm chậm để né tránh |
| `data/output/drift_data/manifest.json` | Mô tả các tập drift: tham số, số dòng, tỷ lệ tấn công, cảnh báo mô phỏng |
| `data/output/drift_data/prevalence_low.csv.gz` | Drift: tỷ lệ tấn công giảm còn 0,5% |
| `data/output/predictions/review_queue_sample.csv` | Ví dụ hàng đợi người xác minh (flow, điểm số, vùng, độ ưu tiên) |
| `data/output/processed/splits.npz` | Chỉ số chia train/val/test (stratified, seed cố định) |

### 4.7. Kết quả `results/`
| File | Mô tả |
|---|---|
| `results/figures/01_class_distribution.png` | Số flow theo nhãn (tuyến tính và log) |
| `results/figures/03_confusion_matrices.png` | Ma trận nhầm lẫn 2 mô hình |
| `results/figures/03_feature_importance_logreg.png` | Đặc trưng quan trọng - Logistic Regression |
| `results/figures/03_feature_importance_random_forest.png` | Đặc trưng quan trọng - Random Forest |
| `results/figures/03_pr_curves.png` | Đường Precision-Recall |
| `results/figures/05_performance_under_drift.png` | P/R/F1 theo kịch bản drift |
| `results/figures/05_psi_heatmap.png` | PSI các đặc trưng theo kịch bản |
| `results/figures/05_score_distribution.png` | Phân phối điểm số baseline và drift |
| `results/figures/06_precision_vs_prevalence.png` | Precision theo tỷ lệ tấn công (base-rate) |
| `results/figures/06_threshold_tradeoff.png` | P/R/F1 và FP theo ngưỡng |
| `results/figures/06_workload_projection.png` | Khối lượng analyst theo tỷ lệ tấn công |
| `results/figures/08_label_noise.png` | Ảnh hưởng của nhiễu nhãn |
| `results/reports/ket_qua_thuc_nghiem.md` | Báo cáo kết quả thực nghiệm đầy đủ (tự sinh) |
| `results/tables/alert_policy_hitl.json` | Ngưỡng 3 vùng, hàng đợi người, khối lượng analyst, ngưỡng vừa sức |
| `results/tables/drift_monitoring.json` | Giám sát drift: PSI, tỉ lệ dự đoán, hiệu năng, drift im lặng |
| `results/tables/drift_summary.csv` | Tóm tắt drift (CSV) |
| `results/tables/eda.json` | Thống kê dữ liệu, chia tập, fingerprint |
| `results/tables/label_noise.csv` | Thí nghiệm nhiễu nhãn (CSV) |
| `results/tables/label_noise.json` | Thí nghiệm nhiễu nhãn |
| `results/tables/retrain_comparison.csv` | So sánh retrain (CSV) |
| `results/tables/retrain_comparison.json` | So sánh v1 / v1+chỉnh ngưỡng / v2 retrain, quyết định promote |
| `results/tables/test_evaluation.json` | Đánh giá trên test: nhiều điểm vận hành, recall theo loại, base-rate |
| `results/tables/test_metrics.csv` | Bảng metric trên test (CSV) |
| `results/tables/training_summary.json` | Kết quả huấn luyện, ngưỡng, quality gate |

### 4.8. Tài liệu `docs/`
| File | Mô tả |
|---|---|
| `docs/01_project_management/project_plan.md` | Kế hoạch dự án |
| `docs/01_project_management/task_guide.md` | Hướng dẫn thực hiện từng công việc |
| `docs/01_project_management/task_list.md` | Danh sách công việc |
| `docs/01_project_management/timeline.md` | Tiến độ (theo giai đoạn) |
| `docs/02_requirements/experiment_requirements.md` | Yêu cầu thực nghiệm (demo) |
| `docs/02_requirements/lab_requirements.md` | Yêu cầu đề tài (mục tiêu và lý thuyết) |
| `docs/03_research/README.md` | Tổng hợp nghiên cứu lý thuyết |
| `docs/03_research/ai_in_detection.md` | AI trong phát hiện và ứng phó |
| `docs/03_research/evaluation_methods.md` | Phương pháp đánh giá |
| `docs/03_research/false_positive.md` | Cảnh báo giả (false positive) |
| `docs/03_research/lifecycle_monitoring_hitl.md` | Vòng đời mô hình, versioning, giám sát, human-in-the-loop |
| `docs/03_research/model_drift.md` | Model drift |
| `docs/03_research/noise_poisoning.md` | Nhiễu nhãn và poisoning (mức khái niệm) |
| `docs/03_research/references.md` | Tài liệu tham khảo |
| `docs/03_research/training_data.md` | Dữ liệu huấn luyện |
| `docs/04_design/experiment_design_and_limitations.md` | Thiết kế thực nghiệm, giả định và hạn chế |
| `docs/04_design/hitl_sop.md` | Quy trình con người xác minh cảnh báo (Human-in-the-loop SOP) |
| `docs/04_design/model_card.md` | Model card - bộ phát hiện brute-force trên flow (demo học thuật) |
| `docs/04_design/processing_pipeline.md` | Luồng xử lý dữ liệu và thực nghiệm |
| `docs/04_design/system_architecture.md` | Kiến trúc hệ thống |
| `docs/04_design/diagrams/hitl_triage_flow.png` | Sơ đồ phân luồng cảnh báo 3 vùng |
| `docs/04_design/diagrams/system_flow.png` | Sơ đồ quy trình huấn luyện - đánh giá - giám sát - xác minh |
| `docs/05_testing/test_cases.md` | Danh sách ca kiểm thử |
| `docs/05_testing/test_plan.md` | Kế hoạch kiểm thử |
| `docs/05_testing/test_report.md` | Báo cáo kiểm thử |
| `docs/06_results/conclusion.md` | Kết luận (sinh tự động từ kết quả lần chạy gần nhất) |
| `docs/06_results/evaluation_results.md` | Kết quả đánh giá mô hình (sinh tự động) |
| `docs/06_results/experiment_results.md` | Kết quả thực nghiệm (sinh tự động) |

## 5. Thứ tự chạy
```bash
pip install -r requirements.txt
# đặt Bruteforce-Tuesday-no-metadata.parquet vào data/input/
python experiments/run_all.py              # chạy bước 1 → 9 (thêm --skip-noise để bỏ bước chậm nhất)
python -m pytest tests -q                  # hoặc: python -m unittest discover -s tests
```
Chi tiết từng bước: `experiments/README.md`, `docs/01_project_management/task_guide.md`. Chạy notebook: `notebooks/README.md`.

## 6. Quy ước đặt tên
| Quy ước | Ví dụ |
|---|---|
| Thư mục `docs/` đánh số theo giai đoạn | `01_project_management` … `06_results` |
| Thư mục con của `src/` là một nhóm chức năng | `src/models/`, `src/hitl/` |
| File mô hình theo `<model>/<vN>/` | `data/output/checkpoints/random_forest/v1/` |
| Hình trong `results/figures/` đánh số theo chương trình sinh ra nó | `05_*` do `monitor_drift.py` tạo |
| File tự sinh (đừng sửa tay) | `results/**`, `docs/06_results/**`, `data/output/**` |

## 7. File được `.gitignore` bỏ qua
- `data/input/*.parquet` (dataset gốc, 47 MB): tự đặt vào khi clone.
- `data/output/processed/*.npz`, `__pycache__/`, `.venv/`, `.ipynb_checkpoints/`.
