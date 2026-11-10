# Dữ liệu huấn luyện

**Dữ liệu dùng:** flow mạng có nhãn (kiểu CICFlowMeter, 77 đặc trưng số: thời lượng, số gói, kích thước gói, IAT, cờ TCP...), nhãn Benign / FTP-Patator / SSH-Patator (brute-force). Dữ liệu này có dạng giống phiên bản làm sạch của CIC-IDS2017, ngày thứ Ba; hãy xác nhận nguồn gốc chính xác trước khi trích dẫn trong báo cáo cuối.

Các vấn đề chất lượng dữ liệu cần kiểm soát:
- **Mất cân bằng lớp** (~2,3% tấn công): accuracy vô nghĩa (bộ “luôn Benign” đạt ~97,7%). Dùng precision/recall/F1, PR-curve, số FP.
- **Rò rỉ dữ liệu (leakage).** Mọi bước tiền xử lý (loại cột hằng, chuẩn hoá, điền thiếu) nằm *trong pipeline* và chỉ học từ tập train. Ngưỡng chọn trên *validation*, test chỉ dùng để báo cáo.
- **Flow tương quan mạnh.** Một chiến dịch brute-force sinh hàng nghìn flow gần giống nhau. Chia ngẫu nhiên đặt flow “anh em” vào cả train lẫn test → **lạc quan quá mức**. Cách đúng: chia theo thời gian hoặc theo chiến dịch/nguồn (cần timestamp/IP, file này không có).
- **Tính đại diện.** Dữ liệu từ một testbed trong một ngày không đại diện cho mạng thật (xem Engelen và cs., 2021 về các lỗi nhãn/đặc trưng của CIC-IDS2017).
- **Đặc trưng thời gian dễ vỡ** (IAT, duration): thay đổi theo độ trễ mạng/hạ tầng - xem mục 5.