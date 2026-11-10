# Quy trình con người xác minh cảnh báo (Human-in-the-loop SOP)

Quy trình đề xuất cho hệ thống phát hiện brute-force dựa trên hai mô hình (chính: Random Forest; phụ: Logistic Regression).
Các con số ngưỡng cụ thể nằm trong `results/reports/ket_qua_thuc_nghiem.md` và `data/output/checkpoints/*/*/metadata.json`; không hard-code ở đây.

## 1. Ba vùng điểm số (mô hình chính)
| Vùng | Điều kiện | Ý nghĩa |
|---|---|---|
| ALERT | `score ≥ t_alert` (precision mục tiêu trên validation) | Độ tin cậy cao |
| REVIEW | `t_review ≤ score < t_alert` | Không chắc chắn: **bắt buộc người xem** |
| IGNORE | `score < t_review` | Chỉ ghi log + lấy mẫu audit |

`t_review` khuyến nghị = max(ngưỡng theo mục tiêu recall, ngưỡng “vừa sức analyst”) - xem `experiments/tune_alert_policy.py`.

## 2. Hàng đợi và mức ưu tiên
| Hàng đợi | Điều kiện | SLA gợi ý | Hành động |
|---|---|---|---|
| **P1_alert** | ALERT và mô hình phụ đồng ý | 15 phút | Tạo ticket tự động; analyst *xác nhận tác động* rồi ứng phó; hành động chặn cần phê duyệt |
| **P2_review** | ALERT nhưng mô hình phụ không đồng ý, hoặc vùng REVIEW | 4 giờ | Analyst xác minh theo checklist (mục 3) |
| **P3_spotcheck** | Mô hình chính IGNORE, mô hình phụ báo tấn công | Lô trong ngày | Kiểm tra mẫu (`p3_review_fraction`); phần còn lại ghi log; **tỉ lệ bất đồng là tín hiệu drift** |
| **AUDIT** | Mẫu ngẫu nhiên nhỏ từ vùng IGNORE | Hằng tuần | Ước lượng tỉ lệ bỏ sót (xem hạn chế ở mục 6) |

## 3. Checklist xác minh một cảnh báo
1. Gộp các flow cùng nguồn/đích/cổng/khung thời gian thành **một sự cố** (tránh xử lý từng flow).
2. Kiểm tra nhật ký xác thực của dịch vụ đích (SSH/FTP): số lần đăng nhập thất bại, có thành công sau chuỗi thất bại không.
3. Nguồn có thuộc danh sách tin cậy/quét nội bộ/công cụ giám sát không? Có trong threat intel không?
4. Tốc độ và nhịp thử (đều đặn như máy, hay thưa/low-and-slow)?
5. Có tài khoản bị khoá/xâm phạm hoặc hành vi sau đăng nhập bất thường?
6. Kết luận một trong: **Tấn công thật / Cảnh báo giả / Không xác định** + ghi lý do ngắn.

## 4. Quyết định và leo thang
- **Tấn công thật:** theo playbook ứng phó (chặn nguồn, khoá/đổi mật khẩu, bật MFA...). Hành động chặn trên hệ thống sản xuất cần người phê duyệt.
- **Cảnh báo giả:** gắn nhãn, ghi nguyên nhân (nếu lặp lại → xem xét danh sách cho phép có kiểm soát, *không* tự nới ngưỡng).
- **Không xác định:** leo thang cấp 2 trong thời hạn SLA.
- **Kiểm soát sai sót con người:** việc *bác bỏ* cảnh báo điểm rất cao (P1) cần người thứ hai duyệt; đo định kỳ độ đồng thuận giữa các analyst; rút mẫu kiểm tra chất lượng nhãn.

## 5. Vòng phản hồi
1. Mọi kết luận được lưu: `flow_id/sự cố, điểm số hai mô hình, vùng, kết luận, analyst, thời gian, phiên bản mô hình`.
2. Nhãn đã xác minh vào **kho dữ liệu huấn luyện có kiểm soát**: chỉ vai trò được duyệt mới ghi; kiểm tra phân phối/nhãn bất thường trước khi dùng (phòng nhiễu và poisoning).
3. Hằng tuần (hoặc khi có cảnh báo drift): tính precision của từng hàng đợi, tỉ lệ bất đồng giữa hai mô hình, tỉ lệ dự đoán tấn công, tải analyst.
4. **Kích hoạt retrain** khi: (a) tín hiệu drift không nhãn *và* F1/recall trên mẫu đã xác minh giảm > ngưỡng (`f1_drop_trigger`), hoặc (b) precision hàng đợi giảm kéo dài làm quá tải analyst.
5. Mô hình mới qua **quality gate**, chạy shadow, rồi mới promote; luôn giữ bản cũ để rollback (`python experiments/registry_cli.py rollback <model>`).

## 6. Giới hạn cần biết
- **Tải analyst phụ thuộc mạnh vào tỉ lệ tấn công thực tế và mức gộp cảnh báo** - cả hai là giả định trong `config.yaml`; hãy đo trên hệ thống thật.
- **Audit ngẫu nhiên khó ước lượng tỉ lệ bỏ sót rất nhỏ** (giới hạn phát hiện ≈ 3/n). Bổ sung audit phân tầng theo điểm số, săn mối đe dọa chủ động, và bộ “tấn công tái hiện” (red-team replay) để kiểm tra độ nhạy.
- **Analyst sai** (mô phỏng 3%) làm giảm recall của hệ thống người-máy; cần kiểm soát hai người cho quyết định bác bỏ.
