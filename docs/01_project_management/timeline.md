# Tiến độ (theo giai đoạn)

Chưa gắn ngày cụ thể; hãy điền ngày theo lịch của môn học.

| Giai đoạn | Nội dung | Đầu ra | Phụ thuộc |
|---|---|---|---|
| 1. Chuẩn bị | Đọc yêu cầu, nghiên cứu lý thuyết cơ bản | `docs/02_requirements/`, bản nháp `docs/03_research/` | - |
| 2. Dữ liệu | EDA, kiểm tra chất lượng, chia tập | `inspect_data.py` | 1 |
| 3. Mô hình | Huấn luyện, đánh giá 2 mô hình | `train_models.py`, `compare_models.py` | 2 |
| 4. Drift | Tạo dữ liệu drift, giám sát | `generate_drift_data.py`, `monitor_drift.py` | 3 |
| 5. Cảnh báo & HITL | Ngưỡng 3 vùng, hàng đợi, SOP | `tune_alert_policy.py`, `hitl_sop.md` | 3, 4 |
| 6. Vòng đời | Retrain, versioning, rollback; nhiễu nhãn | `retrain_and_version.py`, `label_noise_experiment.py` | 4, 5 |
| 7. Báo cáo | Sinh kết quả, viết kết luận, rà soát | `build_report.py`, `docs/06_results/` | 3-6 |
| 8. Kiểm thử & nộp | Chạy test, đóng gói, đẩy lên GitHub | `tests/`, `docs/05_testing/` | 7 |
