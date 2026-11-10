# Nhiễu nhãn và poisoning (mức khái niệm)

**Label noise** - nhãn sai không chủ ý: analyst gán nhầm, công cụ gán nhãn tự động sai, nhãn trễ.

**Data poisoning** - ai đó *chủ ý* làm bẩn dữ liệu huấn luyện. Ở mức khái niệm có ba mục tiêu:
| Loại | Mục tiêu của kẻ tấn công | Ví dụ khái niệm |
|---|---|---|
| Availability | Làm mô hình kém đi nói chung | Chèn nhiều mẫu nhiễu → nhiều cảnh báo giả/bỏ sót |
| Integrity | Làm mô hình bỏ sót loại tấn công cụ thể | Tấn công “lẫn” vào dữ liệu được gán nhãn Benign |
| Backdoor | Một mẫu kích hoạt riêng khiến mô hình bỏ qua | Chỉ hiệu lực khi có “dấu hiệu” do kẻ tấn công kiểm soát |

Poisoning khả thi khi mô hình **học liên tục từ dữ liệu mà đối thủ có thể ảnh hưởng** (log do mạng sinh ra, phản hồi analyst, dữ liệu từ nguồn bên ngoài). Tổng quan: Biggio & Roli (2018).

**Phòng vệ ở mức quy trình:** kiểm soát nguồn gốc dữ liệu (provenance), tách quyền ghi vào kho dữ liệu huấn luyện, kiểm định dữ liệu trước khi train (phân phối, nhãn bất thường, trùng lặp), giữ **tập kiểm thử vàng** do con người duyệt và không để mô hình/đối thủ chạm tới, so sánh phiên bản mới với phiên bản cũ trước khi promote, lưu hash dữ liệu và mô hình.

**Thực nghiệm (`experiments/label_noise_experiment.py`):** đảo nhãn ngẫu nhiên và gán nhầm một tỉ lệ tấn công thành Benign trong tập *của chính chúng ta*, rồi đo mô hình trên test sạch. Đây là đo độ bền với nhiễu nhãn, không phải hướng dẫn tấn công. Kết quả trên bộ dữ liệu *dễ* này chỉ cho thấy mô hình dư thừa thông tin có thể chịu nhiễu vừa phải; không suy rộng sang kẻ tấn công thông minh nhắm vào các điểm yếu của mô hình.