# Model card - bộ phát hiện brute-force trên flow (demo học thuật)

| Mục | Nội dung |
|---|---|
| Mục đích | Minh hoạ quy trình huấn luyện - đánh giá - giám sát - xác minh. **Không** dùng làm hệ thống phát hiện sản xuất. |
| Mô hình | `random_forest` (chính), `logreg` (phụ, tín hiệu đồng thuận). Mỗi phiên bản ở `data/output/checkpoints/<tên>/<vN>/` |
| Đầu vào | 77 đặc trưng số kiểu CICFlowMeter; cột hằng bị loại trong pipeline |
| Đầu ra | Điểm P(attack) ∈ [0,1] → vùng ALERT / REVIEW / IGNORE theo ngưỡng trong `metadata.json` |
| Dữ liệu huấn luyện | 60% của `Bruteforce-Tuesday-no-metadata.parquet` (hash lưu ở `data_fingerprint`) |
| Loại tấn công | FTP-Patator, SSH-Patator (brute-force). Không bao phủ loại khác |
| Chỉ số | Precision/recall/F1/FP/FPR/AP - xem `results/reports/ket_qua_thuc_nghiem.md` |
| Vùng hoạt động an toàn | Phân phối thời gian/tốc độ flow gần với dữ liệu huấn luyện. Random Forest **nhạy với dịch chuyển thang thời gian** (xem kịch bản drift) |
| Hạn chế đã biết | Dữ liệu dễ, một testbed, không có timestamp/IP; chia ngẫu nhiên; không kiểm chứng với đối thủ thích nghi; xem `docs/04_design/experiment_design_and_limitations.md` |
| Giám sát bắt buộc | PSI đặc trưng, PSI theo dải điểm, tỉ lệ dự đoán tấn công, tỉ lệ bất đồng 2 mô hình, F1 trên mẫu đã xác minh |
| Điều kiện retrain | Tín hiệu drift **và** F1 trên mẫu có nhãn giảm > `f1_drop_trigger`, hoặc quá tải analyst kéo dài |
| Quản trị | Quality gate trước khi promote; giữ bản cũ để rollback; ghi `parent_version`, hash mô hình/dữ liệu |
| Con người | Xác minh vùng REVIEW và P2/P3; phê duyệt hành động chặn; xem `docs/04_design/hitl_sop.md` |
