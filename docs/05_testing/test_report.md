# Báo cáo kiểm thử

| Mục | Giá trị |
|---|---|
| Ngày chạy | 2026-11-09 |
| Lệnh | `python -m unittest discover -s tests -v` (cũng chạy được bằng `python -m pytest tests`) |
| Python / scikit-learn / numpy / pandas | 3.12.3 / 1.9.1 / 2.5.4 / 3.0.6 |
| Tổng số ca | 47 |
| Đạt | 47 |
| Không đạt | 0 |

## Kết quả theo file
| File | Số ca | Đạt |
|---|---|---|
| `tests/test_drift.py` | 11 | 11 |
| `tests/test_metrics.py` | 5 | 5 |
| `tests/test_model_registry.py` | 4 | 4 |
| `tests/test_pipeline.py` | 1 | 1 |
| `tests/test_preprocessing.py` | 6 | 6 |
| `tests/test_save_results.py` | 4 | 4 |
| `tests/test_thresholds.py` | 6 | 6 |
| `tests/test_trainer.py` | 4 | 4 |
| `tests/test_triage.py` | 6 | 6 |

## Ghi chú
- Kiểm thử đơn vị dùng dữ liệu tổng hợp nhỏ, không phụ thuộc file dữ liệu thật hay `pyarrow`.
- Kiểm thử tích hợp (`test_pipeline.py`) chạy toàn vòng: train → ngưỡng → hàng đợi người → drift trên dữ liệu tổng hợp.
- Trong quá trình phát triển, kiểm thử đã phát hiện và giúp sửa: (1) `replace_inf` ghi đè mảng chỉ đọc; (2) PSI không phân biệt được đặc trưng gần-hằng-số khi bin bao gồm cả cận; (3) tên mô hình không hợp lệ báo lỗi `KeyError` khó hiểu thay vì `ValueError`.
- Chưa có kiểm thử hiệu năng/tải và chưa kiểm thử trên dữ liệu thật ngoài bộ dữ liệu đã dùng.
