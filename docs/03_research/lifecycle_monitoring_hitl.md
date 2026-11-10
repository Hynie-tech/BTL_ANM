# Vòng đời mô hình, versioning, giám sát, human-in-the-loop

```
Dữ liệu ─► Kiểm định ─► Huấn luyện ─► Đánh giá (validation) ─► Quality gate ─► Registry (staging)
   ▲                                                                             │ promote
   │                                                                             ▼
Nhãn mới ◄── Analyst xác minh ◄── Hàng đợi 3 vùng ◄── Dự đoán ◄── Production (shadow/canary)
   │                                                                             │
   └──────────── Retrain ◄── Kích hoạt (drift + F1 giảm) ◄── Giám sát ◄─────────┘
```

- **Versioning:** mỗi phiên bản lưu mô hình, ngưỡng, metric, hash dữ liệu huấn luyện, phiên bản thư viện, hash file mô hình (toàn vẹn), phiên bản cha. Có **stage** (staging/production/archived) và **rollback**.
- **Quality gate:** chỉ promote khi đạt ngưỡng tối thiểu *và* không thoái lui trên dữ liệu gốc (tránh “quên” tấn công cũ).
- **Triển khai an toàn:** shadow mode (chạy song song, chưa hành động) → canary → toàn bộ.
- **Giám sát:** dữ liệu (drift), mô hình (phân phối điểm, tỉ lệ cảnh báo), vận hành (độ trễ, lỗi), kết quả (precision/recall từ mẫu xác minh).
- **Human-in-the-loop:** con người (1) xác minh cảnh báo mức không chắc chắn, (2) phê duyệt hành động ứng phó rủi ro cao, (3) cung cấp nhãn để học lại, (4) audit phần bị bỏ qua. Con người cũng sai - phải thiết kế kiểm soát (duyệt hai người khi bác bỏ cảnh báo điểm cao, đo độ đồng thuận giữa các analyst). Quy trình chi tiết: `docs/04_design/hitl_sop.md`.
- **Quản trị:** model card (`docs/04_design/model_card.md`), nhật ký quyết định, khung NIST AI RMF (Govern–Map–Measure–Manage).