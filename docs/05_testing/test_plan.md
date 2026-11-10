# Kế hoạch kiểm thử

## 1. Mục tiêu
Bảo đảm các thành phần của quy trình (tiền xử lý, metric, ngưỡng, giám sát drift, mô phỏng drift, registry, hàng đợi người, lưu kết quả) hoạt động đúng và có thể tái lập; phát hiện sớm lỗi hồi quy khi sửa mã.

## 2. Phạm vi
| Lớp kiểm thử | Đối tượng | Công cụ |
|---|---|---|
| Đơn vị | Hàm trong `src/` | `unittest` / `pytest` |
| Tích hợp | Vòng đời đầy đủ trên dữ liệu tổng hợp | `tests/test_pipeline.py` |
| Hệ thống (thủ công) | Chạy `experiments/run_all.py` trên dữ liệu thật, đối chiếu số liệu trong báo cáo | `docs/06_results/` |

## 3. Chiến lược
1. **Tính đúng đắn toán học:** metric trên ví dụ có đáp án tính tay; công thức Bayes theo prevalence; PSI trên phân phối biết trước.
2. **Tính bất biến (invariants):** chính sách ngưỡng `t_review ≤ t_alert`; tích thời gian × tốc độ không đổi sau khi kéo giãn; tập chia không giao nhau và phủ đủ dữ liệu.
3. **Hành vi biên:** chia cho 0 (không có tấn công), cột hằng/Inf/NaN, tên mô hình sai, rollback khi không có bản archived.
4. **Hành vi nghiệp vụ:** quality gate, quy tắc phân luồng P1/P2/P3, sai sót analyst làm giảm recall, audit hiệu chỉnh sai sót analyst.
5. **Dữ liệu tổng hợp nhỏ** để chạy nhanh (vài giây) và không cần dữ liệu thật.

## 4. Tiêu chí đạt
- 100% ca kiểm thử đạt.
- Mọi lỗi tìm thấy được ghi vào `CHANGELOG.md` khi sửa.

## 5. Rủi ro kiểm thử
Dữ liệu tổng hợp dễ hơn dữ liệu thật; kiểm thử không thay thế việc đối chiếu số liệu báo cáo với lần chạy thật.

## 6. Cách chạy
```bash
python -m pytest tests -q
# hoặc không cần pytest:
python -m unittest discover -s tests -v
```
