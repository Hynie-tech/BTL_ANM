# Phương pháp đánh giá

- **Precision** = trong số cảnh báo, bao nhiêu là thật. **Recall** = trong số tấn công thật, bắt được bao nhiêu. **F1** = trung bình điều hoà.
- **FPR / số FP trên 100.000 flow** quyết định tải công việc của analyst.
- Báo cáo ở **nhiều điểm vận hành** (ngưỡng mặc định 0,5; tối đa F1 trên validation; theo chi phí; theo mục tiêu precision/recall), kèm khoảng bất định khi số FP rất nhỏ (cận Clopper-Pearson).
- **Baseline tầm thường** (luôn Benign) để thấy accuracy đánh lừa.