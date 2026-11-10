# AI trong phát hiện và ứng phó

### 1.1 Ba cách tiếp cận
| Cách tiếp cận | Ý tưởng | Điểm mạnh | Giới hạn chính |
|---|---|---|---|
| Luật / chữ ký (signature) | So khớp mẫu đã biết | Chính xác, dễ giải thích | Không thấy tấn công mới; phải bảo trì liên tục |
| Phát hiện bất thường (unsupervised) | Học “bình thường”, cảnh báo cái “lạ” | Không cần nhãn; có thể thấy cái chưa biết | “Lạ” ≠ “độc hại” → nhiều cảnh báo giả |
| Học có giám sát (supervised) | Học ranh giới Benign/Attack từ dữ liệu có nhãn | Độ chính xác cao với tấn công đã có nhãn | Phụ thuộc nhãn; mong manh khi phân phối đổi |

Đồ án này dùng **học có giám sát** (Logistic Regression và Random Forest) trên đặc trưng flow, vì có dữ liệu có nhãn.

### 1.2 AI làm tốt gì trong SOC
- **Phân loại và xếp hạng ưu tiên** hàng triệu sự kiện/ngày để analyst chỉ nhìn phần đáng chú ý.
- **Làm giàu ngữ cảnh** (gộp flow theo nguồn, gắn điểm rủi ro).
- **Hỗ trợ ứng phó**: gợi ý hành động; tự động hoá bước ít rủi ro (mở ticket, gắn cờ) và để con người phê duyệt bước rủi ro cao (chặn IP, cô lập máy).

### 1.3 Giới hạn nền tảng
1. **Thế giới đóng và thế giới mở.** Học máy giả định dữ liệu tương lai giống quá khứ; an ninh mạng là môi trường mở và có đối thủ thích nghi (Sommer & Paxson, 2010).
2. **Khoảng cách ngữ nghĩa.** Mô hình nói “giống tấn công”, không nói “tấn công này có thật, ảnh hưởng gì”. Cần ngữ cảnh con người.
3. **Đối thủ thích nghi.** Kẻ tấn công thay đổi hành vi (chậm lại, phân tán) để lọt qua. Điều này tạo ra *concept drift có chủ đích*.
4. **Base-rate fallacy.** Tấn công rất hiếm nên dù tỉ lệ cảnh báo giả thấp, phần lớn cảnh báo vẫn là giả (Axelsson, 2000) - xem mục 6.
5. **Nhãn là sản phẩm của quy trình**, không phải sự thật tuyệt đối: nhãn có thể sai, trễ, hoặc thiên lệch theo công cụ phát hiện cũ.