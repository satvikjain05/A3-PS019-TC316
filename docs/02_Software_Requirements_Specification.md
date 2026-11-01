# 02. Software Requirements Specification (SRS)
**Project Title:** PS-019 Privacy Intelligence Engine  
**Standard:** IEEE 830-1998 Adapted for Privacy Engineering Applications  
**Status:** Implemented & Verified (AIORI Hackathon 3)  
**Target Platform:** Windows 11 (Python 3.11+, tested on Python 3.12.6)  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) specifies the functional and non-functional requirements for the **PS-019: Privacy Intelligence Engine** (Team A3-PS019-TC316). It serves as the authoritative baseline against which implementation completeness, test suites, and benchmark performance are evaluated.

### 1.2 System Scope
The system is an offline, desktop-accessible web application designed to discover personal data across tabular CSV files and relational SQLite databases, link discovered data to statutory purpose and retention metadata, compute explainable risk scores, map data lineage, recommend remediations, and export audit-ready evidence.

---

## 2. Overall Description

### 2.1 User Roles and Personas

| Role ID | Persona | Primary Responsibilities | System Permissions |
|:---|:---|:---|:---|
| **ROL-01** | **Data Protection Officer (DPO)** | Compliance oversight, approving purposes, auditing posture scorecard. | Full read, record human reviews, export reports. |
| **ROL-02** | **Privacy Engineer** | Running scans, tuning heuristics, analyzing exposure lineage, managing remediations. | Ingest datasets, trigger scans, edit remediation states. |
| **ROL-03** | **Database Administrator (DBA)** | Verifying schema accuracy, configuring physical retention schedules. | Read-only scan view, review remediation suggestions. |
| **ROL-04** | **External Compliance Auditor** | Inspecting data inventories, evaluating Precision/Recall benchmark evidence. | Read-only access to reports and evaluation metrics. |

### 2.2 Operating Environment
- **Operating System:** Windows 11 (fully tested), Linux (Ubuntu 22.04+), macOS (12+).
- **Runtime:** Python 3.11 or Python 3.12 (standard CPython).
- **User Interface:** Web browser via local Streamlit server (`http://localhost:8501`).
- **Network Access:** Fully offline; zero external network access required or attempted.

---

## 3. Functional Requirements (FR)

### 3.1 Discovery & Data Ingestion (FR-DISC)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-DISC-01** | Multi-Format Ingestion | System shall ingest standard comma-separated, semicolon, or tab-delimited CSV files. | **Implemented** | `scanner/csv_scanner.py` (`CSVScanner.scan_file`) |
| **FR-DISC-02** | SQLite Discovery | System shall connect to SQLite databases, enumerate tables, and inspect column schemas. | **Implemented** | `scanner/sqlite_scanner.py` (`SQLiteScanner.scan_database`) |
| **FR-DISC-03** | Safe Read-Only Access | System shall open SQLite connections in strict read-only URI mode (`file:...mode=ro`). | **Implemented** | `scanner/sqlite_scanner.py` |
| **FR-DISC-04** | Bounded Memory Sampling | System shall limit value inspection to at most 100 non-null rows per column to prevent memory exhaustion. | **Implemented** | `scanner/csv_scanner.py`, `scanner/sqlite_scanner.py` |
| **FR-DISC-05** | Encoding Fault Tolerance | System shall attempt UTF-8 decoding with fallback to ISO-8859-1 (Latin-1) upon decode errors. | **Implemented** | `scanner/csv_scanner.py` |

### 3.2 Detection & Classification (FR-DETC)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-DETC-01** | Five Predefined Classes | System shall detect: `NAME`, `EMAIL`, `PHONE_NUMBER`, `ADDRESS`, and `GOVERNMENT_ID`. | **Implemented** | `scanner/detection.py` (`PersonalDataDetector`) |
| **FR-DETC-02** | Header Semantic Matching | System shall evaluate column names against known PII regex synonyms and aliases. | **Implemented** | `scanner/detection.py` (`HEADER_PATTERNS`) |
| **FR-DETC-03** | Value Pattern Matching | System shall evaluate cell values against compiled regex patterns for each data class. | **Implemented** | `scanner/detection.py` (`VALUE_PATTERNS`) |
| **FR-DETC-04** | Negative Header Filtering | System shall suppress false positives by filtering non-PII headers (`id`, `uuid`, `hash`, `count`, `priority`, etc.). | **Implemented** | `scanner/detection.py` (`NEGATIVE_HEADER_PATTERNS`) |
| **FR-DETC-05** | Value Diversity Metric | System shall evaluate unique token ratios to prevent repetitive categorical codes from triggering PII detection. | **Implemented** | `scanner/detection.py` (`_calculate_diversity`) |
| **FR-DETC-06** | Heuristic Confidence Score | System shall calculate an explainable confidence score (0.0 to 1.0) based on header match (+0.4), value match ratio (+0.5), and diversity (+0.1). | **Implemented** | `scanner/detection.py` (`evaluate_column`) |
| **FR-DETC-07** | Automated Sample Masking | System shall mask sample values before UI presentation (e.g., `j***@example.com`, `M*** M***`, `+91-98765-XXXXX`). | **Implemented** | `scanner/detection.py` (`mask_value`) |

### 3.3 Metadata Management & Evidence Inventory (FR-META)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-META-01** | Purpose Linking | Discovered fields shall link to declared purpose policies defined in `config/metadata.json`. | **Implemented** | `scanner/metadata_manager.py` (`MetadataManager`) |
| **FR-META-02** | Retention Tracking | Discovered fields shall link to declared retention periods and highlight overages > 365 days. | **Implemented** | `scanner/metadata_manager.py` (`enrich_inventory`) |
| **FR-META-03** | Human Review Workflow | DPO users shall record human verification decisions: `Pending Review`, `Confirmed PII`, `False Positive`, `Excluded`. | **Implemented** | `scanner/metadata_manager.py` (`record_reviewer_decision`) |
| **FR-META-04** | State Persistence | Reviewer decisions, purposes, and retention limits shall persist to disk across restarts. | **Implemented** | `config/metadata.json` |

### 3.4 Privacy Risk Radar (FR-RISK)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-RISK-01** | Transparent Scoring Formula | Calculate field risk (0–100) using 6 weighted components: Sensitivity, Confidence, Purpose, Retention, Review, and Exposure. | **Implemented** | `scanner/risk_radar.py` (`PrivacyRiskRadar.calculate_field_risk`) |
| **FR-RISK-02** | Risk Tier Assignment | Categorize fields into `Critical` (75–100), `High` (55–74), `Medium` (35–54), and `Low` (0–34). | **Implemented** | `scanner/risk_radar.py` |
| **FR-RISK-03** | Factor Breakdown Output | Provide an itemized, human-readable justification detailing exact points contributed by each risk factor. | **Implemented** | `scanner/risk_radar.py` (`breakdown` dict) |
| **FR-RISK-04** | Priority Sorting | Support sorting inventory by descending risk score to highlight high-liability exposures. | **Implemented** | `app.py` (Risk Radar View) |

### 3.5 Privacy Exposure Map (FR-EXPO)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-EXPO-01** | Interactive Sankey Diagram | Render a multi-level Plotly Sankey diagram: `Data Source → Personal Data Class → Declared Purpose → Governance Status`. | **Implemented** | `scanner/exposure_map.py` (`create_sankey_diagram`) |
| **FR-EXPO-02** | Cross-Source Proliferation | Detect and tabularize PII classes that appear across multiple independent data repositories. | **Implemented** | `scanner/exposure_map.py` (`get_cross_source_summary`) |
| **FR-EXPO-03** | Compliance Status Styling | Visual nodes shall highlight unapproved purposes in amber/red and approved purposes in green. | **Implemented** | `scanner/exposure_map.py` |

### 3.6 Intelligent Remediation Center (FR-REME)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-REME-01** | Rule-Based Task Generation | Generate deterministic compliance remediation tasks based on missing metadata, high sensitivity, and excessive retention. | **Implemented** | `scanner/remediation_engine.py` (`generate_tasks`) |
| **FR-REME-02** | Remediation Lifecycle Tracking | Support task state transitions: `Open`, `In Progress`, `Resolved` with persistent notes. | **Implemented** | `scanner/remediation_engine.py` (`update_task_status`) |
| **FR-REME-03** | Zero Source Alteration | Remediation actions shall remain strictly advisory; engine shall never alter source data or schemas. | **Implemented** | `scanner/remediation_engine.py` |

### 3.7 Privacy Posture Scorecard & What-If Simulator (FR-POST)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-POST-01** | 5-Pillar Posture Score | Calculate 0–100 governance index: Review Coverage (25%), Purpose Approval (25%), Retention (20%), High-Risk Resolution (20%), Evidence Logging (10%). | **Implemented** | `scanner/posture_scorecard.py` (`calculate_posture`) |
| **FR-POST-02** | Priority Gap Identification | Identify top 3 institutional weaknesses based on largest point deficits against max pillar weight. | **Implemented** | `scanner/posture_scorecard.py` (`get_priority_gaps`) |
| **FR-POST-03** | What-If Simulation Scenarios | Simulate compliance impact of: (A) Approving all purposes, (B) Defining all retention limits, (C) Reviewing critical fields, (D) Data minimization. | **Implemented** | `scanner/posture_scorecard.py` (`simulate_what_if`) |
| **FR-POST-04** | In-Memory Simulation Safety | Simulation shall execute in isolated memory without mutating actual configuration or persistence stores. | **Implemented** | `scanner/posture_scorecard.py` |

### 3.8 Benchmark Evaluation (FR-EVAL)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-EVAL-01** | Ground-Truth Evaluation | Ingest pre-labelled benchmark dataset (`data/labelled_test_data.csv`) and compare predictions against ground truth. | **Implemented** | `scanner/evaluation.py` (`Evaluator.evaluate`) |
| **FR-EVAL-02** | Standardized Metrics | Compute Macro Precision, Macro Recall, Macro F1-score, and Per-Class breakdown via Scikit-learn. | **Implemented** | `scanner/evaluation.py` |
| **FR-EVAL-03** | Confusion Matrix Heatmap | Render 6x6 confusion matrix (5 PII classes + NOT_PERSONAL) using Matplotlib / Seaborn / Plotly. | **Implemented** | `scanner/evaluation.py` (`plot_confusion_matrix`) |
| **FR-EVAL-04** | Error Diagnostics | Display detailed diagnostics table for any False Positives or False Negatives encountered. | **Implemented** | `scanner/evaluation.py` |

### 3.9 Compliance Reporting & Exports (FR-REPT)

| Req ID | Title | Description | Implementation Status | Verified Source |
|:---|:---|:---|:---:|:---|
| **FR-REPT-01** | CSV Inventory Export | Export inventory with masked samples, metadata links, and risk scores to `reports/privacy_evidence_inventory.csv`. | **Implemented** | `scanner/report_generator.py` (`export_inventory_csv`) |
| **FR-REPT-02** | JSON Inventory Export | Export complete hierarchical inventory with remediation tasks to `reports/privacy_evidence_inventory.json`. | **Implemented** | `scanner/report_generator.py` (`export_inventory_json`) |
| **FR-REPT-03** | Benchmark Metrics Export | Export benchmark evaluation metrics table to `reports/evaluation_benchmark.csv`. | **Implemented** | `scanner/report_generator.py` (`export_evaluation_metrics_csv`) |
| **FR-REPT-04** | Comprehensive Markdown Audit | Generate formatted Markdown audit report detailing findings, risk tiers, and scorecard to `reports/privacy_audit_report.md`. | **Implemented** | `scanner/report_generator.py` (`generate_audit_report_markdown`) |

---

## 4. Non-Functional Requirements (NFR)

### 4.1 Performance & Scalability (NFR-PERF)
- **NFR-PERF-01 (Sampling Ingestion):** Data loading shall complete in under 5.0 seconds for standard files by sampling at most 100 rows per column rather than reading million-row files into memory.
- **NFR-PERF-02 (Evaluation Latency):** Full benchmark evaluation over 39 columns shall execute in under 3.0 seconds.
- **NFR-PERF-03 (UI Responsiveness):** Dashboard page switching in Streamlit shall render within 1.5 seconds.

### 4.2 Privacy & Security (NFR-PRIV)
- **NFR-PRIV-01 (Local Execution):** System shall not establish any outbound network connections. No data, telemetry, or metadata shall leave the host machine.
- **NFR-PRIV-02 (Data Masking):** No unmasked raw PII values shall appear in the Streamlit UI, CSV exports, JSON exports, or Markdown audit reports.
- **NFR-PRIV-03 (Immutability of Scanned Assets):** Scanners shall open SQLite databases in strict read-only mode (`?mode=ro`) and open CSV files with read-only file descriptors (`'r'`).

### 4.3 Portability & Compatibility (NFR-PORT)
- **NFR-PORT-01 (Windows 11 Native):** System shall install and run cleanly on Windows 11 using PowerShell without requiring WSL (Windows Subsystem for Linux) or administrative privileges.
- **NFR-PORT-02 (Cross-Platform Fallback):** Codebase shall run seamlessly on standard Linux and macOS environments with identical behavior.

### 4.4 Reliability & Maintainability (NFR-RELI)
- **NFR-RELI-01 (Test Suite Verification):** 100% of automated tests (33 tests) must pass consistently with zero flakiness.
- **NFR-RELI-02 (Graceful Degradation):** Empty CSV files, missing database tables, or corrupt records shall be handled with informative error messages without crashing the Streamlit session.

---

## 5. System Constraints and Dependencies

1. **Python Version:** Python 3.11 or Python 3.12 (standard library `re`, `sqlite3`, `pathlib`, `json`).
2. **Key Dependencies:**
   - `streamlit >= 1.30.0` (Web UI)
   - `pandas >= 2.0.0` (Dataframe processing)
   - `scikit-learn >= 1.3.0` (Metrics calculation)
   - `plotly >= 5.18.0` (Interactive Sankey and charts)
   - `matplotlib >= 3.7.0` (Confusion matrix plotting)
   - `pytest >= 7.4.0` (Test execution)
3. **No External Infrastructure:** No requirement for PostgreSQL, Redis, Docker, or paid cloud APIs.

---

## 6. Acceptance Criteria

| Criteria ID | Condition for Acceptance | Verified Evidence |
|:---|:---|:---|
| **AC-01** | Application launches locally via `streamlit run app.py` without unhandled startup exceptions. | Verified (tested clean import and execution). |
| **AC-02** | 5 personal data classes detected accurately in synthetic datasets (`customers.csv`, `employees.csv`, `support_tickets.csv`, `privacy_demo.db`). | Verified (39 columns evaluated; 15 PII columns identified). |
| **AC-03** | Benchmark evaluation reports Precision, Recall, and F1 >= 0.90 for all 5 classes. | Verified (Macro Precision 1.0, Macro Recall 1.0, Macro F1 1.0). |
| **AC-04** | All automated tests pass via `pytest`. | Verified (33 passed in 10.90s). |
| **AC-05** | Reports are generated in `reports/` in CSV, JSON, and Markdown formats with masked PII. | Verified (`reports/` contains valid exports). |
