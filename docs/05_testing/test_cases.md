# Danh sách ca kiểm thử

Sinh từ `python -m unittest discover -s tests -v`. Mỗi ca là một hàm `test_*` trong `tests/`.

| File | Mục đích | Số ca |
|---|---|---|
| `tests/test_drift.py` | PSI, giám sát drift, mô phỏng drift | 11 |
| `tests/test_metrics.py` | Metric precision/recall/F1/FP, Bayes | 5 |
| `tests/test_model_registry.py` | Registry (versioning/rollback), inspector | 4 |
| `tests/test_pipeline.py` | Tích hợp end-to-end trên dữ liệu tổng hợp | 1 |
| `tests/test_preprocessing.py` | Tiền xử lý, pipeline, chia tập | 6 |
| `tests/test_save_results.py` | Lưu JSON/CSV/Markdown, vẽ hình | 4 |
| `tests/test_thresholds.py` | Ngưỡng và chính sách 3 vùng | 6 |
| `tests/test_trainer.py` | Huấn luyện, quality gate, retrain | 4 |
| `tests/test_triage.py` | Hàng đợi người, mô phỏng analyst, audit, khối lượng | 6 |

## `tests/test_drift.py` - PSI, giám sát drift, mô phỏng drift

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestPSI | `test_band_psi_detects_mass_moving_between_bands` | OK |
| TestPSI | `test_constant_reference_detects_change` | OK |
| TestPSI | `test_feature_table_flags_shifted_feature` | OK |
| TestPSI | `test_same_distribution_small` | OK |
| TestPSI | `test_shift_large` | OK |
| TestPSI | `test_summary_flags_alert_rate_drop` | OK |
| TestScenarios | `test_column_detection` | OK |
| TestScenarios | `test_covariate_changes_all_flows` | OK |
| TestScenarios | `test_evasion_only_changes_attacks_and_keeps_consistency` | OK |
| TestScenarios | `test_prevalence_resample` | OK |
| TestScenarios | `test_unknown_scenario` | OK |

## `tests/test_metrics.py` - Metric precision/recall/F1/FP, Bayes

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestMetrics | `test_at_threshold_and_table` | OK |
| TestMetrics | `test_binary_report_counts` | OK |
| TestMetrics | `test_majority_baseline_accuracy_trap` | OK |
| TestMetrics | `test_precision_at_prevalence_bayes` | OK |
| TestMetrics | `test_zero_division_safe` | OK |

## `tests/test_model_registry.py` - Registry (versioning/rollback), inspector

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestInspector | `test_top_features_and_kept` | OK |
| TestRegistry | `test_rollback_without_archived_raises` | OK |
| TestRegistry | `test_unknown_model_raises` | OK |
| TestRegistry | `test_version_promote_rollback_load` | OK |

## `tests/test_pipeline.py` - Tích hợp end-to-end trên dữ liệu tổng hợp

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestEndToEnd | `test_full_lifecycle_on_synthetic_data` | OK |

## `tests/test_preprocessing.py` - Tiền xử lý, pipeline, chia tập

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestFeaturePipeline | `test_pipelines_handle_inf_nan_constant` | OK |
| TestFeaturePipeline | `test_replace_inf` | OK |
| TestFeaturePipeline | `test_replace_inf_does_not_mutate_input` | OK |
| TestFeaturePipeline | `test_signed_log1p_keeps_sign_and_order` | OK |
| TestFeaturePipeline | `test_unknown_model` | OK |
| TestSplits | `test_splits_disjoint_cover_and_stratified` | OK |

## `tests/test_save_results.py` - Lưu JSON/CSV/Markdown, vẽ hình

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestSaveResults | `test_figure_is_written` | OK |
| TestSaveResults | `test_md_table` | OK |
| TestSaveResults | `test_save_metrics_numpy_safe` | OK |
| TestSaveResults | `test_save_table_and_markdown` | OK |

## `tests/test_thresholds.py` - Ngưỡng và chính sách 3 vùng

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestThresholds | `test_build_policy_review_not_above_alert` | OK |
| TestThresholds | `test_cost_threshold_prefers_recall_when_fn_expensive` | OK |
| TestThresholds | `test_max_f1_in_range` | OK |
| TestThresholds | `test_policy_zones` | OK |
| TestThresholds | `test_precision_target_met` | OK |
| TestThresholds | `test_recall_target_met` | OK |

## `tests/test_trainer.py` - Huấn luyện, quality gate, retrain

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestTrainer | `test_decide_promotion` | OK |
| TestTrainer | `test_gate` | OK |
| TestTrainer | `test_retrain_candidate_returns_thresholds` | OK |
| TestTrainer | `test_train_and_register_promotes_good_model` | OK |

## `tests/test_triage.py` - Hàng đợi người, mô phỏng analyst, audit, khối lượng

| Lớp | Ca kiểm thử | Kết quả |
|---|---|---|
| TestTriage | `test_analyst_error_lowers_recall` | OK |
| TestTriage | `test_audit_estimate_corrects_analyst_error` | OK |
| TestTriage | `test_capacity_thresholds_fewer_shifts_at_higher_threshold` | OK |
| TestTriage | `test_queue_rules` | OK |
| TestTriage | `test_summary_recall_with_perfect_analyst` | OK |
| TestTriage | `test_workload_monotonic` | OK |
