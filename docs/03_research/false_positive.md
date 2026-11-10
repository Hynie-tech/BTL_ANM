# Cảnh báo giả (false positive)

**Base-rate fallacy.** Gọi *TPR* là recall, *FPR* là tỉ lệ cảnh báo giả trên benign, *p* là tỉ lệ tấn công:

`precision = TPR·p / (TPR·p + FPR·(1−p))`

Với p nhỏ, mẫu số bị chi phối bởi FPR·(1−p): ngay cả FPR = 0,1% cũng đủ làm phần lớn cảnh báo là giả khi p = 0,01%. Hệ quả:
- **Alert fatigue**: analyst quá tải nên bỏ qua cả cảnh báo thật.
- **Chi phí bất đối xứng**: bỏ sót (FN) thường đắt hơn FP nhưng FP lặp lại làm hỏng quy trình.
- Phải **ngoại suy precision ở tỉ lệ tấn công thực tế**, không báo cáo precision của tập test cân bằng giả tạo.
- Gộp cảnh báo (alert aggregation) theo nguồn/chiến dịch giảm mạnh số ticket - thông số này phải đo trên hệ thống thật.

Chiến lược ngưỡng (`experiments/tune_alert_policy.py`): chọn **trên validation** theo (i) precision mục tiêu cho vùng ALERT, (ii) recall mục tiêu cho vùng REVIEW, (iii) chi phí kỳ vọng, (iv) **năng lực analyst** (capacity-aware).