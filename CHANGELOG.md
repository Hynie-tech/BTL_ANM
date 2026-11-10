# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/).

## [1.0.0]
### Thêm
- Quy trình đầy đủ: EDA → huấn luyện 2 mô hình (Logistic Regression, Random Forest) → đánh giá (precision/recall/F1/FP) → tạo dữ liệu drift → giám sát drift → ngưỡng 3 vùng + hàng đợi người xác minh → retrain/versioning/rollback → thí nghiệm nhiễu nhãn → báo cáo tự sinh.
- Model registry file-based với stage (staging/production/archived), hash mô hình/dữ liệu, rollback.
- 4 kịch bản drift mô phỏng: `covariate_network`, `prevalence_low`, `evasion_low_slow`, `combined`.
- Tài liệu `docs/01…06`, 3 notebook, sơ đồ hệ thống, 47 ca kiểm thử.

### Đã sửa
- `replace_inf` ghi đè mảng chỉ đọc (lỗi với DataFrame float32).
- PSI không tách được tham chiếu hằng số (bin đóng bên phải).
- Tên mô hình sai báo `KeyError` thay vì `ValueError` rõ ràng.
- Audit ngẫu nhiên trước đây ước lượng tỉ lệ bỏ sót sai do không hiệu chỉnh sai sót analyst; nay dùng hiệu chỉnh Rogan-Gladen và nêu giới hạn phát hiện.
- Khối lượng analyst tính theo từng flow cho số phi thực tế; nay có tham số gộp cảnh báo.

### Thay đổi cấu trúc
- Chuyển sang cấu trúc `data/{input,output}`, `docs/01…06`, `experiments/`, `notebooks/`, `results/`, `src/{models,preprocessing,training,evaluation,monitoring,simulation,hitl,visualization}`, `tests/`.
