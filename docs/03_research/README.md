# Tổng hợp nghiên cứu lý thuyết

Nội dung lý thuyết theo yêu cầu đề tài, mỗi chủ đề một file:

| File | Chủ đề |
|---|---|
| [ai_in_detection.md](ai_in_detection.md) | AI trong phát hiện và ứng phó |
| [training_data.md](training_data.md) | Dữ liệu huấn luyện |
| [noise_poisoning.md](noise_poisoning.md) | Nhiễu nhãn / poisoning (mức khái niệm) |
| [evaluation_methods.md](evaluation_methods.md) | Phương pháp đánh giá (precision/recall/F1/FP) |
| [model_drift.md](model_drift.md) | Model drift |
| [false_positive.md](false_positive.md) | Cảnh báo giả, base-rate fallacy, chọn ngưỡng |
| [lifecycle_monitoring_hitl.md](lifecycle_monitoring_hitl.md) | Lifecycle, versioning, monitoring, human-in-the-loop |
| [references.md](references.md) | Tài liệu tham khảo |

**Tư tưởng xuyên suốt:** một mô hình đạt điểm cao trên tập kiểm thử không đồng nghĩa với một hệ thống phát hiện đáng tin cậy. Giá trị thật nằm ở quy trình bao quanh mô hình: dữ liệu → huấn luyện → đánh giá → triển khai → giám sát → con người xác minh → cập nhật.
