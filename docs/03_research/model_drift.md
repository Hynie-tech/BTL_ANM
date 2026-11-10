# Model drift

| Loại | Thay đổi | Ví dụ trong đồ án (`experiments/generate_drift_data.py`) |
|---|---|---|
| Covariate shift | P(X) đổi, quan hệ X→Y giữ nguyên | `covariate_network`: hạ tầng chậm hơn, mọi flow bị kéo giãn thời gian |
| Prior (label) shift | P(Y) đổi | `prevalence_low`: tỉ lệ tấn công giảm còn 0,5% |
| Concept drift | P(X\|Y) đổi | `evasion_low_slow`: kẻ tấn công làm chậm (low-and-slow) |

Cách phát hiện:
1. **Không cần nhãn (tín hiệu sớm):** PSI/KS theo từng đặc trưng; PSI của điểm số theo dải vận hành; **tỉ lệ dự đoán “tấn công”** so với baseline; tỉ lệ bất đồng giữa hai mô hình.
2. **Có nhãn (nhãn đến trễ):** F1/recall trên mẫu đã xác minh. Đây là bằng chứng quyết định retrain.

Cảnh báo quan trọng: **PSI từng đặc trưng có thể không thấy drift tập trung ở lớp thiểu số** (tấn công chiếm 2%), và drift ở prior shift có thể “báo động” dù mô hình vẫn tốt. Vì vậy cần kết hợp nhiều tín hiệu cùng mẫu nhãn có kiểm soát. Ngưỡng PSI 0,1/0,25 là quy ước kinh nghiệm, không phải định luật.

Phản ứng: (a) chỉnh lại ngưỡng (rẻ, nhanh); (b) retrain với dữ liệu mới + quality gate; (c) rollback nếu bản mới tệ hơn; (d) điều tra nguyên nhân (đổi hạ tầng? kẻ tấn công đổi chiến thuật?). Xem `experiments/retrain_and_version.py`.

Tài liệu nền: Gama và cs. (2014) về thích nghi với concept drift.