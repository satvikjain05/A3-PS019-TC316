# 03. System Architecture and Design
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Implementation:** Modular Python Architecture with Streamlit UI & SQLite Ingestion  

---

## 1. High-Level Architecture Overview

The **Privacy Intelligence Engine** employs a decoupled, multi-tier architecture designed around four primary layers:
1. **Presentation & Interaction Layer:** Streamlit-based web dashboard (`app.py`) providing modern light SaaS visual aesthetics, reactive controls, interactive Plotly visualizations, and tabular audit logs.
2. **Intelligence & Analysis Layer:** Domain modules covering heuristic detection, explainable risk scoring, data lineage mapping, automated remediation synthesis, and governance posture evaluation.
3. **Data Ingestion & Discovery Layer:** Safe, bounded-sampling connectors for Delimited CSV text files and relational SQLite databases.
4. **Persistence & Evidence Store Layer:** Local JSON governance configuration (`config/metadata.json`, `config/remediations.json`) and audit output files (`reports/`).

```mermaid
graph TD
    subgraph UI ["Presentation Layer (Streamlit Web App)"]
        Dashboard["Executive Dashboard"]
        IngestionUI["Data Sources & Ingestion"]
        ResultsUI["Scan Results & Evidence"]
        InventoryUI["Privacy Evidence Inventory"]
        RadarUI["Privacy Risk Radar"]
        ExposureUI["Privacy Exposure Map"]
        RemediationUI["Remediation Center"]
        SimulatorUI["What-If Simulator"]
        BenchmarkUI["Benchmark Evaluation"]
        ExportUI["Reports & Export"]
    end

    subgraph Core ["Privacy Intelligence Core (scanner/)"]
        Detector["PersonalDataDetector\n(detection.py)"]
        CSVScan["CSVScanner\n(csv_scanner.py)"]
        SQLScan["SQLiteScanner\n(sqlite_scanner.py)"]
        MetaMgr["MetadataManager\n(metadata_manager.py)"]
        RiskRadar["PrivacyRiskRadar\n(risk_radar.py)"]
        ExpoMap["PrivacyExposureMap\n(exposure_map.py)"]
        Remediation["RemediationEngine\n(remediation_engine.py)"]
        Posture["PrivacyPostureScorecard\n(posture_scorecard.py)"]
        Evaluator["Evaluator\n(evaluation.py)"]
        Reporter["ReportGenerator\n(report_generator.py)"]
    end

    subgraph Data ["Data Sources & Persistence"]
        CSVFiles[("CSV Files\ncustomers, employees,\nsupport_tickets")]
        SQLiteDB[("SQLite Database\nprivacy_demo.db\n(mode=ro)")]
        BenchData[("Benchmark Ground Truth\nlabelled_test_data.csv")]
        MetaStore[("config/metadata.json\nPolicies & Decisions")]
        RemeStore[("config/remediations.json\nActionable Tasks")]
        Reports[("reports/\nCSV, JSON, Markdown")]
    end

    UI --> Core
    CSVScan --> CSVFiles
    SQLScan --> SQLiteDB
    Evaluator --> BenchData
    MetaMgr --> MetaStore
    Remediation --> RemeStore
    Reporter --> Reports
    Detector --> CSVScan
    Detector --> SQLScan
    RiskRadar --> Detector
    RiskRadar --> MetaMgr
    Posture --> RiskRadar
    Posture --> MetaMgr
    ExpoMap --> MetaMgr
    Remediation --> RiskRadar
```

---

## 2. Component Responsibilities & Module Catalog

### 2.1 Application Entry Point (`app.py` & `src/app.py`)
- Coordinates Streamlit page state, routing between 10 navigation views.
- Handles reactive widget triggers (buttons, dropdowns, radio toggles).
- Applies modern light SaaS styling via injected custom CSS.
- Encapsulates error handling for file uploads and database browsing.

### 2.2 Personal Data Detector (`scanner/detection.py`)
- Implements `PersonalDataDetector`.
- Houses compiled regular expression patterns for 5 personal data classes:
  - `NAME`, `EMAIL`, `PHONE_NUMBER`, `ADDRESS`, `GOVERNMENT_ID`.
- Executes header keyword matching and negative-header exclusion filters.
- Computes heuristic confidence scores based on header (+0.4), value match ratio (+0.5), and value diversity (+0.1).
- Provides data masking routines for UI presentation and export sanitization.

### 2.3 Data Ingestion Connectors (`scanner/csv_scanner.py` & `scanner/sqlite_scanner.py`)
- **`CSVScanner`:**
  - Safely loads CSV files with delimiter sniffing (comma, semicolon, tab).
  - Implements bounded row sampling (first 100 non-null values per column) to prevent high memory usage.
  - Recovers gracefully from UTF-8 decode errors via fallback to ISO-8859-1.
- **`SQLiteScanner`:**
  - Connects to SQLite databases using read-only URI connection strings (`file:...mode=ro`).
  - Enumerates all tables via `sqlite_master` catalog queries.
  - Introspects column definitions with `PRAGMA table_info`.
  - Samples up to 100 rows per table with `LIMIT 100`.

### 2.4 Metadata & Evidence Manager (`scanner/metadata_manager.py`)
- Implements `MetadataManager`.
- Interfaces with `config/metadata.json` for organizational data policies.
- Enriches scanner candidate fields with declared business purposes and retention periods.
- Records and persists DPO human verification decisions (`Pending Review`, `Confirmed PII`, `False Positive`, `Excluded`).

### 2.5 Explainable Privacy Risk Radar (`scanner/risk_radar.py`)
- Implements `PrivacyRiskRadar`.
- Calculates an explainable 0–100 risk score for each detected personal data column.
- Factors: Data sensitivity (35 pts), detection confidence (15 pts), missing purpose (20 pts), retention overages (15 pts), review status (15 pts), cross-source proliferation (15 pts).
- Assigns priority tiers (`Critical`, `High`, `Medium`, `Low`) and generates human-readable factor contribution breakdowns.

### 2.6 Privacy Exposure Lineage Map (`scanner/exposure_map.py`)
- Implements `PrivacyExposureMap`.
- Generates 4-tier Sankey data flow models: `Source → Class → Purpose → Governance Status`.
- Detects cross-source proliferation where identical personal data classes reside across multiple physical databases.
- Highlights unapproved or orphan data flows in visual alert colors.

### 2.7 Intelligent Remediation Engine (`scanner/remediation_engine.py`)
- Implements `RemediationEngine`.
- Generates structured, prioritized remediation tickets for compliance deficits.
- Manages ticket lifecycles (`Open`, `In Progress`, `Resolved`) with persistent JSON storage in `config/remediations.json`.
- Strictly maintains read-only boundaries: never modifies underlying data assets.

### 2.8 Posture Scorecard & What-If Simulator (`scanner/posture_scorecard.py`)
- Implements `PrivacyPostureScorecard`.
- Synthesizes institutional compliance into a composite 0–100 index across 5 pillars:
  - Human Review Coverage (25%), Purpose Approval (25%), Retention Schedule (20%), High-Risk Resolution (20%), Evidence Logging (10%).
- Provides in-memory What-If scenario projections without altering persistent governance state.

### 2.9 Empirical Evaluator (`scanner/evaluation.py`)
- Implements `Evaluator`.
- Ingests ground-truth labeled benchmark data (`data/labelled_test_data.csv`).
- Calculates standardized performance metrics via `scikit-learn`: Macro Precision, Recall, F1-score, per-class breakdown, and confusion matrices.
- Renders confusion matrix visualization heatmaps using Matplotlib/Seaborn.

### 2.10 Compliance Report Generator (`scanner/report_generator.py`)
- Implements `ReportGenerator`.
- Generates audit deliverables in `reports/`:
  - `privacy_evidence_inventory.csv`: Tabular inventory with masked samples and risk ratings.
  - `privacy_evidence_inventory.json`: Full nested schema with lineage and remediation metadata.
  - `evaluation_benchmark.csv`: Metric table for precision/recall validation.
  - `privacy_audit_report.md`: Formal Markdown compliance document for regulatory filing.

---

## 3. Data Processing Pipeline (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor User as DPO / Privacy Engineer
    participant App as Streamlit UI (app.py)
    participant Scanner as Ingestion (CSV / SQLite)
    participant Detector as PersonalDataDetector
    participant MetaMgr as MetadataManager
    participant Risk as PrivacyRiskRadar
    participant Store as Local Storage (JSON/Reports)

    User->>App: Trigger Scan (Select Directory or DB)
    App->>Scanner: Request Ingestion (Sample max 100 rows)
    Scanner->>App: Return Dataframe & Schema Metadata
    loop For Each Discovered Column
        App->>Detector: evaluate_column(name, sample_values)
        Detector->>Detector: Check Header Regex & Negative Filters
        Detector->>Detector: Evaluate Value Patterns & Calculate Diversity
        Detector-->>App: Return (Class, Confidence, Masked Sample, Evidence)
    end
    App->>MetaMgr: enrich_inventory(detections)
    MetaMgr->>Store: Read config/metadata.json
    MetaMgr-->>App: Return Enriched Items (Purpose, Retention, Review Status)
    loop For Each Enriched Field
        App->>Risk: calculate_field_risk(field_metadata)
        Risk-->>App: Return (Score 0-100, Tier, Breakdown)
    end
    App->>User: Render Interactive Dashboard & Visualizations
    User->>App: Record Review Decision / Resolve Task
    App->>MetaMgr: record_reviewer_decision(...)
    MetaMgr->>Store: Persist to config/metadata.json
```

---

## 4. User Workflow Diagram (Mermaid)

```mermaid
flowchart TD
    Start([Launch Application]) --> Nav{Select Navigation Page}
    
    Nav -->|1. Overview| ExecDash["View Executive Dashboard\nPosture Score, KPI Cards & Gaps"]
    Nav -->|2. Ingestion| Ingest["Inspect Data Sources\n(CSV Files & SQLite DB)"]
    Nav -->|3. Discovery| RunScan["Trigger Discovery Scan\nSample columns & evaluate regex"]
    Nav -->|4. Evidence| ReviewInv["Examine Evidence Inventory\nLink Purpose & Retention Metadata"]
    Nav -->|5. Risk Radar| CheckRadar["Analyze Privacy Risk Radar\nFilter by Critical/High Tiers"]
    Nav -->|6. Exposure| ViewSankey["Explore Exposure Map\nInspect Data Lineage & Proliferation"]
    Nav -->|7. Remediation| FixTasks["Review Remediation Center\nUpdate Task Status (Open/Resolved)"]
    Nav -->|8. Simulator| RunWhatIf["Run What-If Simulator\nTest hypothetical policy impacts"]
    Nav -->|9. Evaluation| RunBench["Execute Benchmark Evaluation\nInspect Precision, Recall, F1"]
    Nav -->|10. Export| GenReports["Generate Compliance Reports\nExport CSV, JSON, Markdown"]

    RunScan --> ReviewInv
    ReviewInv --> CheckRadar
    CheckRadar --> ViewSankey
    ViewSankey --> FixTasks
    FixTasks --> RunWhatIf
    RunWhatIf --> GenReports
    RunBench --> GenReports
```

---

## 5. Component Interaction & Class Diagram (Mermaid)

```mermaid
classDiagram
    class PersonalDataDetector {
        +dict HEADER_PATTERNS
        +dict VALUE_PATTERNS
        +list NEGATIVE_HEADER_PATTERNS
        +evaluate_column(col_name, values) tuple
        +mask_value(val, class_name) str
        -_calculate_diversity(values) float
    }

    class CSVScanner {
        +Path data_dir
        +scan_file(file_path) list
        +scan_directory(dir_path) list
    }

    class SQLiteScanner {
        +Path db_path
        +discover_tables() list
        +scan_database() list
        +get_table_sample(table_name, limit) DataFrame
    }

    class MetadataManager {
        +Path config_path
        +dict policies
        +enrich_inventory(detections) list
        +record_reviewer_decision(source, column, status, notes) bool
        +save_policies() void
    }

    class PrivacyRiskRadar {
        +dict SENSITIVITY_WEIGHTS
        +calculate_field_risk(field) dict
        +get_risk_summary(inventory) dict
    }

    class PrivacyPostureScorecard {
        +calculate_posture(inventory) dict
        +get_priority_gaps(pillar_scores) list
        +simulate_what_if(inventory, scenario_flags) dict
    }

    class RemediationEngine {
        +Path remediations_path
        +generate_tasks(inventory) list
        +update_task_status(task_id, status, notes) bool
    }

    class ReportGenerator {
        +Path output_dir
        +export_inventory_csv(inventory) str
        +export_inventory_json(inventory) str
        +export_evaluation_metrics_csv(metrics) str
        +generate_audit_report_markdown(inventory, posture) str
    }

    CSVScanner --> PersonalDataDetector : uses
    SQLiteScanner --> PersonalDataDetector : uses
    MetadataManager --> PersonalDataDetector : references
    PrivacyRiskRadar --> MetadataManager : enriches from
    PrivacyPostureScorecard --> PrivacyRiskRadar : aggregates
    RemediationEngine --> PrivacyRiskRadar : triggers on
    ReportGenerator --> MetadataManager : reads
    ReportGenerator --> PrivacyRiskRadar : reads
```

---

## 6. State Management and Persistence

The application maintains state across three distinct mechanisms:
1. **Streamlit Session State (`st.session_state`):**
   - Active scan results (`scanned_inventory`).
   - Current navigation page and demo mode steps.
   - Dynamic simulation slider parameters.
2. **Local Governance Metadata (`config/metadata.json`):**
   - Stores declared purposes for specific column paths (`customers.csv::email_address`).
   - Stores official retention limits (e.g., 180 days, 365 days).
   - Stores human review verification audit stamps and reviewer notes.
3. **Remediation Task Store (`config/remediations.json`):**
   - Stores generated compliance tickets.
   - Tracks resolution lifecycle states (`Open`, `In Progress`, `Resolved`) and timestamps.

---

## 7. Error Handling & Fault Isolation Flow

- **Corrupted / Empty Files:** `CSVScanner` validates row counts; files with zero non-null values return empty detection sets without unhandled exceptions.
- **Encoding Anomalies:** When standard UTF-8 parsing fails, the reader automatically falls back to ISO-8859-1 (Latin-1), preventing ingestion crashes.
- **Database Locks / Concurrency:** SQLite connections are strictly opened with `uri=True` and `mode=ro`. No exclusive write locks are requested, guaranteeing zero risk of corruption to target databases.
- **Missing Configuration Files:** If `config/metadata.json` or `config/remediations.json` is missing or unparseable, default fallback policies are automatically populated in memory.
