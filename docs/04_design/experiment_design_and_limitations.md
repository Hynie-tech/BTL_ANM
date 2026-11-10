# Thiết kế thực nghiệm, giả định và hạn chế

## 1. Thiết kế
1. **Dữ liệu:** `data/input/Bruteforce-Tuesday-no-metadata.parquet` (389.714 flow × 77 đặc trưng; nhãn Benign/FTP-Patator/SSH-Patator). Nhị phân hoá: Benign=0, tấn công=1; giữ loại tấn công để phân tích recall theo loại.
2. **Chia tập:** train 60% / validation 20% / test 20%, phân tầng theo nhãn, `seed=42`; chỉ lưu *chỉ số* chia (`data/output/processed/splits.npz`) và fingerprint từng tập.
3. **Hai mô hình cơ bản:** Logistic Regression (log-signed + chuẩn hoá, tuyến tính, dễ giải thích) và Random Forest (phi tuyến, không cần chuẩn hoá). Cả hai nằm trong một `sklearn.Pipeline` gồm xử lý Inf/NaN, loại cột hằng.
4. **Chọn ngưỡng chỉ trên validation**; test chỉ dùng để báo cáo.
5. **Drift:** tạo từ *mẫu 40.000 flow của tập test* (mô hình chưa thấy) → so sánh “có/không drift” trên *cùng* các flow (thiết kế ghép cặp) và có nhóm **control** (không đổi) để kiểm tra giám sát không báo động sai.
6. **Retrain:** dữ liệu drift chia 30% feedback (nhãn trễ) / 15% validation mới / 55% đánh giá; so sánh v1 giữ nguyên, v1 chỉnh ngưỡng, và v2 retrain; có quality gate và rollback drill.
7. **Nhiễu nhãn:** đảo nhãn trong train, đánh giá trên test sạch với ngưỡng cố định 0,5 và AP.

## 2. Giả định có thể chỉnh trong `configs/config.yaml`
Mức drift (hệ số kéo giãn thời gian, tỉ lệ tấn công), mục tiêu precision/recall cho ngưỡng, chi phí FN/FP, tỉ lệ tấn công triển khai (`deploy_prevalence`), lưu lượng flow/ngày, mức gộp cảnh báo, thời gian xử lý mỗi ticket, số ca analyst, tỉ lệ sai của analyst.

## 3. Hạn chế (cần nêu khi bảo vệ)
1. **Dữ liệu dễ và hẹp.** Brute-force trong testbed một ngày gần như tách được hoàn toàn; điểm cao không chứng minh khả năng phát hiện trong mạng thật.
2. **Không có timestamp/IP** → không chia theo thời gian hoặc theo nguồn; flow cùng chiến dịch nằm ở cả train và test → số liệu lạc quan. Cùng lý do, retrain demo có feedback và đánh giá lấy từ cùng một mẫu drift nên mức “hồi phục” cũng lạc quan.
3. **Drift là mô phỏng.** Chỉ kéo giãn thời gian và đổi tỉ lệ tấn công; kẻ tấn công thật có thể thay đổi nhiều đặc trưng khác. Các tham số được chọn để minh hoạ cơ chế, không đại diện cho tần suất hay mức độ drift trong thực tế.
4. **FPR ước lượng từ rất ít FP** (RF có thể chỉ 1 FP trên ~76.000 benign) → ngoại suy precision ở prevalence thấp rất bất định (báo cáo kèm kịch bản bi quan bằng cận trên 95%).
5. **Khối lượng analyst** phụ thuộc hai giả định gộp cảnh báo chưa được đo.
6. **Analyst mô phỏng** chỉ có một tham số sai ngẫu nhiên; thực tế còn thiên lệch, mệt mỏi, bất đồng giữa người.
7. **Nhiễu nhãn** chỉ là đảo nhãn ngẫu nhiên; không đại diện cho tấn công poisoning có chủ đích.
8. **Chưa xét đối kháng thích nghi** (kẻ tấn công biết mô hình). `evasion_low_slow` chỉ là một biến đổi cố định.
9. **Một lần chạy, một seed** - chưa có khoảng tin cậy qua nhiều seed/chia tập.

## 4. Cách mở rộng
Chia theo thời gian/nguồn; thêm mô hình (gradient boosting, isolation forest cho phát hiện bất thường); thêm drift thật từ ngày khác của CIC-IDS2017; calibration xác suất; audit phân tầng; nhiều seed + khoảng tin cậy; dashboard giám sát.
