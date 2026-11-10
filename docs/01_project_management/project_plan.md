# Kế hoạch dự án

## 1. Đề tài
**Đánh giá vai trò và giới hạn của AI trong phát hiện an ninh; xây dựng quy trình huấn luyện - đánh giá - giám sát thay vì chỉ tập trung vào độ chính xác.**

## 2. Mục tiêu
1. Đánh giá AI làm được gì và *không* làm được gì trong phát hiện tấn công mạng.
2. Xây dựng quy trình **huấn luyện → đánh giá → giám sát → xác minh bởi con người → cập nhật**.
3. Chứng minh bằng thực nghiệm rằng độ chính xác cao trên tập kiểm thử không bảo đảm độ tin cậy khi phân phối dữ liệu thay đổi.

## 3. Phạm vi
| Trong phạm vi | Ngoài phạm vi |
|---|---|
| Dữ liệu flow có nhãn (brute-force FTP/SSH) | Phân tích payload, mã độc, tấn công mã hoá |
| 2 mô hình cơ bản (Logistic Regression, Random Forest) | Học sâu, mô hình chuỗi thời gian |
| Drift mô phỏng có kiểm soát | Thu thập lưu lượng thật |
| Ngưỡng cảnh báo + quy trình người xác minh (mô phỏng) | Triển khai SOC thật, tích hợp SIEM/SOAR |
| Poisoning ở mức khái niệm (nhiễu nhãn) | Phát triển kỹ thuật tấn công poisoning |

## 4. Sản phẩm bàn giao
| Sản phẩm | Vị trí |
|---|---|
| Mã nguồn thư viện | `src/` |
| Chương trình thực nghiệm | `experiments/` |
| Tập dữ liệu drift | `data/output/drift_data/` |
| Mô hình có phiên bản | `data/output/checkpoints/` |
| Báo cáo lý thuyết | `docs/03_research/` |
| Quy trình HITL (SOP) | `docs/04_design/hitl_sop.md` |
| Kết quả thực nghiệm | `results/`, `docs/06_results/` |
| Kiểm thử | `tests/`, `docs/05_testing/` |

## 5. Rủi ro và hạn chế
| Rủi ro / hạn chế | Ảnh hưởng | Giảm thiểu |
|---|---|---|
| Dữ liệu dễ, hẹp (một testbed, một ngày) | Điểm cao quá lạc quan | Nêu rõ trong báo cáo; chỉ coi là demo quy trình |
| Không có timestamp/IP | Không chia theo thời gian/nguồn; rò rỉ giữa các flow cùng chiến dịch | Ghi nhận hạn chế; đề xuất mở rộng |
| Drift là mô phỏng | Không đại diện drift thật | Tham số trong config, ghi rõ trong manifest |
| FPR ước lượng từ rất ít FP | Ngoại suy precision bất định | Báo cáo cận trên 95% (kịch bản bi quan) |
| Giả định gộp cảnh báo chưa đo | Khối lượng analyst chỉ mang tính minh hoạ | Đưa vào config, ghi rõ giả định |
| Một seed duy nhất | Chưa có khoảng tin cậy | Đề xuất chạy nhiều seed |

Chi tiết: `docs/04_design/experiment_design_and_limitations.md`.

## 6. Tiêu chí hoàn thành
- [x] 2 mô hình, báo cáo precision/recall/F1/FP trên tập test.
- [x] Có tập dữ liệu drift và giám sát drift (có/không nhãn).
- [x] Đề xuất ngưỡng cảnh báo và quy trình người xác minh.
- [x] Vòng đời: versioning, quality gate, retrain, rollback.
- [x] Báo cáo lý thuyết đủ các mục theo đề bài.
- [x] Kiểm thử tự động chạy qua.
