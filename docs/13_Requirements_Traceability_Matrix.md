# 13. Requirements Traceability Matrix (RTM)
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Baseline Specification:** `docs/02_Software_Requirements_Specification.md`  
**Test Suite Verification:** 33 Passing Tests in `tests/`  

---

## 1. Traceability Overview

This Requirements Traceability Matrix (RTM) maps each Functional Requirement (FR) and Non-Functional Requirement (NFR) specified in the formal SRS to:
1. The exact source code module, class, and method implementing the behavior.
2. The specific automated unit, integration, or property test in `tests/` validating the requirement.
3. The verified implementation status.

---

## 2. Functional Requirements Traceability Matrix

| Req ID | Requirement Description | Source Implementation | Automated Test Function | Verification Status |
|:---|:---|:---|:---|:---:|
| **FR-DISC-01** | Multi-Format Delimited CSV Ingestion | `scanner/csv_scanner.py`<br>`CSVScanner.scan_file()` | `tests/test_scanner.py`<br>`test_csv_scan_customers()` | **Verified (Pass)** |
| **FR-DISC-02** | SQLite Catalog & Schema Discovery | `scanner/sqlite_scanner.py`<br>`SQLiteScanner.discover_tables()` | `tests/test_scanner.py`<br>`test_sqlite_table_discovery()` | **Verified (Pass)** |
| **FR-DISC-03** | Read-Only SQLite Access (`mode=ro`) | `scanner/sqlite_scanner.py`<br>`sqlite3.connect(?mode=ro)` | `tests/test_scanner.py`<br>`test_sqlite_scan_database_read_only()` | **Verified (Pass)** |
| **FR-DISC-04** | Bounded Memory Sampling (Max 100 Rows) | `scanner/csv_scanner.py`<br>`scanner/sqlite_scanner.py` | `tests/test_detection.py`<br>`test_sample_limits()` | **Verified (Pass)** |
| **FR-DISC-05** | Encoding Fault Tolerance (UTF-8 / ISO-8859-1) | `scanner/csv_scanner.py`<br>`CSVScanner._read_with_fallback()` | `tests/test_scanner.py`<br>`test_csv_scan_malformed_file()` | **Verified (Pass)** |
| **FR-DETC-01** | Detection of 5 Predefined Classes | `scanner/detection.py`<br>`PersonalDataDetector.evaluate_column()` | `tests/test_detection.py`<br>`test_email_detection_valid_and_invalid()`, `test_phone_detection_indian_formats()` | **Verified (Pass)** |
| **FR-DETC-02** | Header Semantic Keyword Matching | `scanner/detection.py`<br>`HEADER_PATTERNS` | `tests/test_detection.py`<br>`test_evaluate_column_email_header_and_values()` | **Verified (Pass)** |
| **FR-DETC-03** | Value Regular Expression Matching | `scanner/detection.py`<br>`VALUE_PATTERNS` | `tests/test_detection.py`<br>`test_address_detection()`, `test_government_id_synthetic_markers()` | **Verified (Pass)** |
| **FR-DETC-04** | Negative Header Exclusion Filtering | `scanner/detection.py`<br>`NEGATIVE_NAME_HEADERS` | `tests/test_detection.py`<br>`test_evaluate_column_negative_header_exclusions()` | **Verified (Pass)** |
| **FR-DETC-05** | Value Diversity Ratio Metric | `scanner/detection.py`<br>`PersonalDataDetector._calculate_diversity()` | `tests/test_detection.py`<br>`test_evaluate_column_ambiguous_mixed_tokens()` | **Verified (Pass)** |
| **FR-DETC-06** | Heuristic Confidence Score Formulation | `scanner/detection.py`<br>`evaluate_column() (weights: 0.4, 0.5, 0.1)` | `tests/test_detection.py`<br>`test_evaluate_column_email_header_and_values()` | **Verified (Pass)** |
| **FR-DETC-07** | Automated Sample Value Masking | `scanner/detection.py`<br>`PersonalDataDetector.mask_value()` | `tests/test_detection.py`<br>`test_masking_utility()` | **Verified (Pass)** |
| **FR-META-01** | Purpose Policy Linking | `scanner/metadata_manager.py`<br>`MetadataManager.enrich_inventory()` | `tests/test_metadata.py`<br>`test_default_policies_exist()` | **Verified (Pass)** |
| **FR-META-02** | Retention Schedule Tracking | `scanner/metadata_manager.py`<br>`enrich_inventory()` | `tests/test_metadata.py`<br>`test_enrich_detection_flags_missing_approval()` | **Verified (Pass)** |
| **FR-META-03** | DPO Human Verification Recording | `scanner/metadata_manager.py`<br>`record_reviewer_decision()` | `tests/test_metadata.py`<br>`test_record_reviewer_decision_persistence()` | **Verified (Pass)** |
| **FR-META-04** | Metadata Persistence to Disk | `scanner/metadata_manager.py`<br>`save_policies() -> config/metadata.json` | `tests/test_metadata.py`<br>`test_record_reviewer_decision_persistence()` | **Verified (Pass)** |
| **FR-RISK-01** | Transparent 0–100 Scoring Formula | `scanner/risk_radar.py`<br>`PrivacyRiskRadar.calculate_field_risk()` | `tests/test_privacy_intelligence.py`<br>`test_risk_radar_scoring_and_explanation()` | **Verified (Pass)** |
| **FR-RISK-02** | Priority Tier Classification | `scanner/risk_radar.py`<br>`get_priority_level()` | `tests/test_privacy_intelligence.py`<br>`test_risk_radar_scoring_and_explanation()` | **Verified (Pass)** |
| **FR-RISK-03** | Factor Breakdown Output | `scanner/risk_radar.py`<br>`RiskEvaluation.factor_breakdown` | `tests/test_privacy_intelligence.py`<br>`test_missing_metadata_increases_risk_score()` | **Verified (Pass)** |
| **FR-RISK-04** | Inventory Risk Sorting | `scanner/risk_radar.py`<br>`evaluate_inventory(reverse=True)` | `tests/test_privacy_intelligence.py`<br>`test_risk_radar_scoring_and_explanation()` | **Verified (Pass)** |
| **FR-EXPO-01** | Plotly Sankey Lineage Diagram | `scanner/exposure_map.py`<br>`create_sankey_diagram()` | `tests/test_privacy_intelligence.py`<br>`test_exposure_map_generation()` | **Verified (Pass)** |
| **FR-EXPO-02** | Cross-Source Proliferation Detection | `scanner/exposure_map.py`<br>`get_cross_source_summary()` | `tests/test_privacy_intelligence.py`<br>`test_exposure_map_generation()` | **Verified (Pass)** |
| **FR-EXPO-03** | Compliance Status Color Styling | `scanner/exposure_map.py`<br>`_get_node_color()` | `tests/test_privacy_intelligence.py`<br>`test_exposure_map_generation()` | **Verified (Pass)** |
| **FR-REME-01** | Deterministic Remediation Task Generation | `scanner/remediation_engine.py`<br>`generate_recommendations()` | `tests/test_privacy_intelligence.py`<br>`test_remediation_engine_generates_tasks()` | **Verified (Pass)** |
| **FR-REME-02** | Task Lifecycle State Tracking | `scanner/remediation_engine.py`<br>`update_task_status()` | `tests/test_privacy_intelligence.py`<br>`test_remediation_engine_generates_tasks()` | **Verified (Pass)** |
| **FR-REME-03** | Read-Only Advisory Boundary | `scanner/remediation_engine.py`<br>(Zero DB mutation calls) | `tests/test_scanner.py`<br>`test_sqlite_scan_database_read_only()` | **Verified (Pass)** |
| **FR-POST-01** | 5-Pillar Privacy Posture Calculation | `scanner/posture_scorecard.py`<br>`calculate_scorecard()` | `tests/test_privacy_intelligence.py`<br>`test_posture_scorecard_calculation()` | **Verified (Pass)** |
| **FR-POST-02** | Algorithmic Priority Gap Identification | `scanner/posture_scorecard.py`<br>`get_priority_gaps()` | `tests/test_privacy_intelligence.py`<br>`test_posture_scorecard_calculation()` | **Verified (Pass)** |
| **FR-POST-03** | What-If Simulation Scenarios | `scanner/posture_scorecard.py`<br>`simulate_what_if()` | `tests/test_privacy_intelligence.py`<br>`test_what_if_simulation_zero_side_effects()` | **Verified (Pass)** |
| **FR-POST-04** | In-Memory Simulation Safety (No Side Effects) | `scanner/posture_scorecard.py`<br>(Isolated dictionary mutations) | `tests/test_privacy_intelligence.py`<br>`test_what_if_simulation_zero_side_effects()` | **Verified (Pass)** |
| **FR-EVAL-01** | Ground-Truth Benchmark Evaluation | `scanner/evaluation.py`<br>`Evaluator.evaluate()` | `tests/test_evaluation.py`<br>`test_evaluator_metrics_calculation()` | **Verified (Pass)** |
| **FR-EVAL-02** | Scikit-learn Precision/Recall/F1 Computation | `scanner/evaluation.py`<br>`precision_recall_fscore_support()` | `tests/test_evaluation.py`<br>`test_evaluator_metrics_calculation()` | **Verified (Pass)** |
| **FR-EVAL-03** | Confusion Matrix Heatmap Visualization | `scanner/evaluation.py`<br>`plot_confusion_matrix()` | `tests/test_evaluation.py`<br>`test_confusion_matrix_structure()`, `test_confusion_matrix_plot()` | **Verified (Pass)** |
| **FR-EVAL-04** | Diagnostic Error Itemization | `scanner/evaluation.py`<br>`res['detailed_records']` | `tests/test_evaluation.py`<br>`test_evaluator_metrics_calculation()` | **Verified (Pass)** |
| **FR-REPT-01** | CSV Inventory Export with Masking | `scanner/report_generator.py`<br>`export_inventory_csv()` | `tests/test_export.py`<br>`test_export_inventory_csv()` | **Verified (Pass)** |
| **FR-REPT-02** | Structured JSON Inventory Export | `scanner/report_generator.py`<br>`export_inventory_json()` | `tests/test_export.py`<br>`test_export_inventory_json()` | **Verified (Pass)** |
| **FR-REPT-03** | Benchmark Metrics CSV Export | `scanner/report_generator.py`<br>`export_evaluation_metrics_csv()` | `tests/test_export.py`<br>`test_export_evaluation_metrics_csv()` | **Verified (Pass)** |
| **FR-REPT-04** | Executive Markdown Audit Report Export | `scanner/report_generator.py`<br>`generate_audit_report_markdown()` | `tests/test_export.py`<br>`test_generate_audit_report_markdown()` | **Verified (Pass)** |

---

## 3. Non-Functional Requirements Traceability Matrix

| Req ID | Requirement Description | Implementation Mechanism | Verification Method | Status |
|:---|:---|:---|:---|:---:|
| **NFR-PERF-01** | Bounded Row Ingestion $\le 5$s | `max_sample_rows = 100` in `CSVScanner` and `SQLiteScanner` | Measured in `test_scanner.py` ($< 1.5$s total) | **Verified (Pass)** |
| **NFR-PERF-02** | Fast Benchmark Evaluation $\le 3$s | In-memory evaluation loop over 39 columns | Measured in `test_evaluation.py` ($< 0.8$s) | **Verified (Pass)** |
| **NFR-PRIV-01** | Zero Outbound Network Requests | No `requests`, `urllib`, `socket` network calls in `scanner/` | Offline execution verified on isolated network | **Verified (Pass)** |
| **NFR-PRIV-02** | Universal Data Masking | `mask_value()` applied before UI rendering and file export | `tests/test_detection.py::test_masking_utility` | **Verified (Pass)** |
| **NFR-PRIV-03** | Immutability of Scanned Repositories | Read-only mode `?mode=ro` enforced on SQLite connections | `tests/test_scanner.py::test_sqlite_scan_database_read_only` | **Verified (Pass)** |
| **NFR-PORT-01** | Windows 11 Native Compatibility | Standard library `pathlib.Path`, cross-platform path separators | Tested on Windows 11 PowerShell 5.1 & Core | **Verified (Pass)** |
| **NFR-RELI-01** | 100% Automated Test Pass Rate | 33 automated tests across 6 files in `tests/` | Pytest suite: 33 passed, 0 failed, 0 skipped | **Verified (Pass)** |
