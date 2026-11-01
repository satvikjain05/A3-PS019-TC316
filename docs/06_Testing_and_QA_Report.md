# 06. Testing and Quality Assurance Report
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Test Framework:** Pytest 9.0.3 / Python 3.12.6  
**Execution Date:** 2026-10-31  

---

## 1. Quality Assurance Strategy & Test Philosophy

The testing architecture for **PS-019: Privacy Intelligence Engine** emphasizes automated, deterministic validation of privacy engineering rules. Given the sensitive nature of privacy compliance, test suites are structured to enforce four critical safety properties:
1. **Detection Correctness:** Verifying that regex patterns, negative header exclusions, and diversity filters accurately detect personal data without generating spurious alerts on metadata or system metrics.
2. **Ingestion Robustness:** Verifying that CSV and SQLite connectors handle corrupt encodings, empty tables, missing files, and non-PII tables safely without crashing.
3. **Data Protection Safety:** Verifying that data masking routines obfuscate sensitive patterns and that database connections enforce strict read-only constraints (`mode=ro`).
4. **Governance Mathematical Integrity:** Verifying that risk formulas, posture pillar calculations, and What-If simulations produce exact, reproducible values without state mutations.

---

## 2. Test Environment Specifications

| Parameter | Specification |
|:---|:---|
| **Host Operating System** | Microsoft Windows 11 Enterprise (64-bit) |
| **Python Runtime** | Python 3.12.6 (CPython standard distribution) |
| **Test Runner** | `pytest 9.0.3` with `pluggy 1.6.0`, `anyio 4.11.0` |
| **Execution Command** | `python -m pytest -v` |
| **Working Directory** | `C:\Users\krary\OneDrive\Desktop\A3-PS019-TC316` |
| **Execution Duration** | 10.90 seconds |

---

## 3. Test Suite Execution Summary Table

| Test Category | Source Test File | Tests Run | Passed | Failed | Skipped | Pass Rate |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Pattern Detection & Heuristics** | `tests/test_detection.py` | 9 | 9 | 0 | 0 | 100% |
| **Data Ingestion & Scanners** | `tests/test_scanner.py` | 7 | 7 | 0 | 0 | 100% |
| **Metadata & Persistence** | `tests/test_metadata.py` | 3 | 3 | 0 | 0 | 100% |
| **Evaluation & Metrics** | `tests/test_evaluation.py` | 4 | 4 | 0 | 0 | 100% |
| **Compliance Exporting** | `tests/test_export.py` | 4 | 4 | 0 | 0 | 100% |
| **Privacy Intelligence & Risk Radar**| `tests/test_privacy_intelligence.py` | 6 | 6 | 0 | 0 | 100% |
| **TOTAL VERIFIED SUITE** | **6 Test Suites** | **33** | **33** | **0** | **0** | **100%** |

---

## 4. Itemized Test Results Breakdown

### 4.1 Detection & Heuristics (`tests/test_detection.py`)
- `test_email_detection_valid_and_invalid`: Validates RFC-5322 compliance and rejects malformed strings (`test@`, `@domain.com`, `plainaddress`).
- `test_phone_detection_indian_formats`: Tests standard Indian 10-digit mobile formats, `+91` prefixes, and hyphen/space separators.
- `test_address_detection`: Verifies address keyword detection and 6-digit Indian PIN code matching.
- `test_government_id_synthetic_markers`: Validates synthetic Aadhaar (`SYN-AAD-`), PAN (`SYNPA`), and Voter ID regexes while ensuring non-synthetic patterns do not leak.
- `test_name_detection`: Verifies 2-to-4 token capitalized human names while filtering numeric or single-character values.
- `test_evaluate_column_email_header_and_values`: Verifies end-to-end column evaluation awarding header (+0.4) and value (+0.5) weights.
- `test_evaluate_column_negative_header_exclusions`: Confirms negative headers (`company_name`, `task_status`, `log_level`, `latency_ms`) are suppressed to `NOT_PERSONAL`.
- `test_evaluate_column_ambiguous_mixed_tokens`: Tests handling of columns with low diversity ratios or ambiguous alphanumeric data.
- `test_masking_utility`: Verifies masking output formats across all 5 classes (`j***@example.com`, `+91-*****-***10`, `A*** S***`).

### 4.2 Data Ingestion & Scanners (`tests/test_scanner.py`)
- `test_csv_scan_customers`: Ingests `customers.csv`, samples rows, and detects personal fields accurately.
- `test_csv_scan_empty_file`: Asserts graceful handling of zero-byte or header-only CSV files.
- `test_csv_scan_missing_file`: Asserts `FileNotFoundError` or safe handled exit when target path does not exist.
- `test_csv_scan_malformed_file`: Asserts fallback decoding when encountering corrupt or non-UTF8 encodings.
- `test_sqlite_table_discovery`: Introspects `privacy_demo.db` and enumerates tables (`customer_accounts`, `internal_staff`, `system_logs`).
- `test_sqlite_column_discovery`: Extracts schema metadata and PRAGMA table info accurately.
- `test_sqlite_scan_database_read_only`: Validates that database connections are strictly established with `mode=ro` preventing any write or lock attempts.

### 4.3 Metadata Management & Persistence (`tests/test_metadata.py`)
- `test_default_policies_exist`: Verifies that `config/metadata.json` loads default purposes and retention policies.
- `test_enrich_detection_flags_missing_approval`: Asserts that detected fields lacking official DPO approval are flagged with `has_approved_purpose = False`.
- `test_record_reviewer_decision_persistence`: Tests recording DPO review states (`CONFIRMED`, `REJECTED`) and verifies persistence to disk across instances.

### 4.4 Benchmark Evaluation (`tests/test_evaluation.py`)
- `test_ground_truth_loads_correctly`: Verifies loading of `data/labelled_test_data.csv` with 39 annotated columns.
- `test_evaluator_metrics_calculation`: Calculates precision, recall, and F1 scores using Scikit-learn and validates expected outputs.
- `test_confusion_matrix_structure`: Verifies the 6x6 confusion matrix shape (5 PII classes + NOT_PERSONAL).
- `test_confusion_matrix_plot`: Asserts graphical figure generation without display server dependencies (Matplotlib headless `Agg` backend).

### 4.5 Compliance Exporting (`tests/test_export.py`)
- `test_export_inventory_csv`: Exports enriched inventory to CSV, verifying column headers, risk scores, and masked values.
- `test_export_inventory_json`: Exports inventory to structured JSON and validates schema conformity.
- `test_export_evaluation_metrics_csv`: Generates benchmark evaluation metrics CSV in `reports/`.
- `test_generate_audit_report_markdown`: Generates formal Markdown compliance report and verifies header structure and risk summaries.

### 4.6 Privacy Intelligence & Risk Radar (`tests/test_privacy_intelligence.py`)
- `test_risk_radar_scoring_and_explanation`: Asserts 0–100 score bounds, priority tier mapping, and human-readable factor breakdowns.
- `test_missing_metadata_increases_risk_score`: Verifies that stripping purpose or retention metadata immediately increases calculated risk.
- `test_remediation_engine_generates_tasks`: Verifies automated generation of actionable tickets for missing purposes and high-sensitivity identifiers.
- `test_posture_scorecard_calculation`: Computes 5-pillar posture score and verifies exact mathematical numerator/denominator adherence.
- `test_what_if_simulation_zero_side_effects`: Runs What-If simulation and verifies that in-memory transformations do not alter persistent state.
- `test_exposure_map_generation`: Generates Plotly Sankey data lineage payloads and cross-source proliferation dictionaries.

---

## 5. Application Launch & UI Sanity Verification

In addition to headless automated unit tests, the application startup lifecycle was verified:
- **Clean Python Compilation:** `python -m py_compile app.py src/app.py scanner/*.py` completed with zero syntax or indentation errors.
- **Import Verification:** Verified that `from app import *` executes without missing dependencies or circular imports.
- **Port Binding:** Verified that Streamlit initializes its Tornado web server and binds cleanly to `http://localhost:8501`.
- **Navigation Stress Test:** All 10 navigation views render without unhandled exceptions or session state corruption.

---

## 6. Known Defects, Skipped Tests, and Limitations

- **Failed or Skipped Tests:** **0 failed, 0 skipped.** 100% of the 33 defined test cases passed cleanly.
- **Headless Plotting Note:** In automated environments without a graphical display manager, Matplotlib defaults to the non-interactive `Agg` backend, which functions correctly and produces valid PNG outputs.
