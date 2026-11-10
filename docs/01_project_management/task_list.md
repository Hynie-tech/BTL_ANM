# Danh sách công việc

Trạng thái: ✅ xong · 🔄 đang làm · ⬜ chưa làm

## A. Chuẩn bị và dữ liệu
| # | Công việc | Chương trình / tài liệu | Trạng thái |
|---|---|---|---|
| A1 | Xác nhận yêu cầu đề tài | `docs/02_requirements/` | ✅ |
| A2 | Khám phá dữ liệu, kiểm tra chất lượng, chia train/val/test | `experiments/inspect_data.py` | ✅ |

## B. Mô hình và đánh giá
| # | Công việc | Chương trình | Trạng thái |
|---|---|---|---|
| B1 | Huấn luyện 2 mô hình, chọn ngưỡng trên validation, đăng ký phiên bản | `experiments/train_models.py` | ✅ |
| B2 | So sánh mô hình: precision/recall/F1/FP, base-rate | `experiments/compare_models.py` | ✅ |

## C. Drift và giám sát
| # | Công việc | Chương trình | Trạng thái |
|---|---|---|---|
| C1 | Tạo tập dữ liệu có phân phối thay đổi | `experiments/generate_drift_data.py` | ✅ |
| C2 | Giám sát drift (không nhãn + có nhãn) | `experiments/monitor_drift.py` | ✅ |

## D. Cảnh báo và con người xác minh
| # | Công việc | Chương trình / tài liệu | Trạng thái |
|---|---|---|---|
| D1 | Ngưỡng 3 vùng, chi phí, năng lực analyst | `experiments/tune_alert_policy.py` | ✅ |
| D2 | Quy trình xác minh (SOP) | `docs/04_design/hitl_sop.md` | ✅ |

## E. Vòng đời
| # | Công việc | Chương trình | Trạng thái |
|---|---|---|---|
| E1 | Retrain, quality gate, promote, rollback | `experiments/retrain_and_version.py` | ✅ |
| E2 | Thí nghiệm nhiễu nhãn (poisoning mức khái niệm) | `experiments/label_noise_experiment.py` | ✅ |

## F. Báo cáo và kiểm thử
| # | Công việc | Tài liệu | Trạng thái |
|---|---|---|---|
| F1 | Báo cáo lý thuyết | `docs/03_research/` | ✅ |
| F2 | Sinh báo cáo kết quả | `experiments/build_report.py` → `docs/06_results/` | ✅ |
| F3 | Kiểm thử tự động | `tests/`, `docs/05_testing/` | ✅ |

## G. Việc nên làm tiếp (ngoài phạm vi nộp bài)
| # | Công việc |
|---|---|
| G1 | Chạy nhiều seed và báo cáo khoảng tin cậy |
| G2 | Chia theo thời gian/nguồn khi có timestamp/IP |
| G3 | Thêm drift thật từ ngày khác của bộ dữ liệu gốc |
| G4 | Thêm mô hình phát hiện bất thường (Isolation Forest) |
