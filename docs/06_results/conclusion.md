# Kết luận (sinh tự động từ kết quả lần chạy gần nhất)

## Điều rút ra

1. **Accuracy đánh lừa.** Bộ phân loại ‘luôn Benign’ có accuracy 0.9765 nhưng recall 0. Hai mô hình đều có accuracy > 0,99 nên chỉ phân biệt được qua precision/recall/F1/FP: random_forest F1=0.9986 (FP=1), logreg F1=0.9587 (FP=73).
2. **Điểm cao ≠ bền vững.** Khi phân phối đổi, F1 của random_forest giảm từ 0.998 xuống 0.284 (kịch bản `combined`) với ngưỡng đóng băng. Mô hình đơn giản hơn (logreg) không nhất thiết kém hơn khi drift: độ bền phụ thuộc vào đặc trưng mà mô hình dựa vào.
3. **Giám sát không nhãn không đủ.** Trong lần chạy này mọi trường hợp suy giảm đều bị giám sát không nhãn phát hiện, nhưng kịch bản `prevalence_low` cho thấy drift của tỉ lệ tấn công có thể báo động dù mô hình vẫn tốt, nên vẫn cần mẫu có nhãn.
4. **Con người trong vòng lặp có giá trị và có chi phí.** Vùng REVIEW cứu recall khi mô hình chính mất tự tin (recall chỉ-máy → máy+người ở các kịch bản drift: xem bảng mục 5 của kết quả). Nhưng sai sót của analyst (3%) làm recall hệ thống là 0.9727 thay vì 0.9995 khi analyst hoàn hảo, nên cần kiểm soát hai người khi bác bỏ cảnh báo điểm cao.
5. **Base-rate fallacy.** Ở tỉ lệ tấn công giả định 0.10%, hàng đợi cần ≈ 4.5 ca analyst/ngày và chỉ 0.8% ticket là tấn công thật (theo các giả định gộp cảnh báo trong config).
6. **Vòng đời khép kín.** Với random_forest: giữ v1 F1(drift)=0.375; chỉ chỉnh ngưỡng = 0.973; retrain v2 = 0.994, thoái lui trên dữ liệu gốc +0.001; quyết định: PROMOTE.
7. **Nhiễu nhãn (khái niệm).** Với 20% nhãn tấn công bị gán nhầm là Benign, random_forest có recall 0.988, F1 0.994 trên test sạch. Bộ dữ liệu này dễ và dư thừa nên không suy rộng cho kẻ tấn công chủ động.

## Giới hạn
Xem `docs/04_design/` và mục ‘Hạn chế’ trong `docs/01_project_management/project_plan.md`: dữ liệu dễ và hẹp, không có timestamp/IP, drift là mô phỏng, FPR ước lượng từ rất ít FP, giả định gộp cảnh báo chưa đo, một seed duy nhất.
