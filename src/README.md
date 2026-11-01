# PS-019: Personal-Data Discovery & Privacy Evidence Inventory
### Enhanced with Privacy Intelligence Layer & Hackathon Demo Mode

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework: Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://sqlite.org/)
[![Tests: Pytest (33 Passed)](https://img.shields.io/badge/Pytest-33%20Passed-brightgreen.svg)](https://pytest.org/)
[![Compliance Standard: MeitY DPDP](https://img.shields.io/badge/Standard-MeitY%20DPDP%20Framework-orange.svg)](https://www.meity.gov.in/)

A modular, explainable, and local privacy engineering platform built for **AIORI Hackathon 3 (Team A3-PS019-TC316)**. The scanner discovers Personally Identifiable Information (PII) across unstructured CSV files and structured SQLite databases, links detected fields to declared purpose and retention metadata, provides an explainable **Privacy Risk Radar (0–100)**, visualizes data lineage with an interactive **Privacy Exposure Map**, automates governance with an **Intelligent Remediation Engine**, and projects compliance gains using an interactive **What-If Impact Simulator**.

> 📚 **Complete Documentation Suite:** See [docs/INDEX.md](../docs/INDEX.md) for formal IEEE-style SRS, Architecture, Benchmark Reports, and Presentation Slides.

---

## 1. Project Overview & Problem Statement

### The Regulatory Challenge
Under modern data protection frameworks—such as the **Digital Personal Data Protection (DPDP) Act 2023** (India) and the **MeitY Data Protection Framework**—organizations act as *Data Fiduciaries*. They are legally bound by two non-negotiable principles:
1. **Purpose Limitation:** Collecting and processing personal data strictly for specified, declared, and lawful purposes.
2. **Storage Limitation:** Retaining personal data only for as long as necessary to satisfy those stated purposes.

In fast-moving enterprises, sensitive personal data fields inevitably proliferate across legacy CSV spreadsheets, departmental exports, and unindexed SQLite databases without active documentation. This creates significant compliance liability, untracked attack surfaces, and privacy audit failures.

### The Solution: Privacy Intelligence Layer
This application upgrades traditional data discovery into an active privacy governance system:
- **Heuristic Pattern Discovery:** Identifies 5 predefined personal-data classes (`NAME`, `EMAIL`, `PHONE_NUMBER`, `ADDRESS`, `GOVERNMENT_ID`) using an explainable combination of column nomenclature heuristics, regex pattern matching, and data diversity metrics.
- **Privacy Risk Radar (0–100):** Explainable, multi-factor risk scoring factoring in data sensitivity, detection confidence, missing purpose, missing retention, human-review state, and cross-source exposure.
- **Visual Privacy Exposure Map:** Interactive Plotly Sankey visualization mapping data lineage: `Data Source → Personal Data Class → Declared Purpose → Governance Status`.
- **Intelligent Remediation Center:** Deterministic recommendation engine that generates actionable tasks (e.g., formalize purpose, configure retention, verify statutory IDs) with persistent tracking.
- **Privacy Posture Scorecard & What-If Simulator:** A transparent 0–100 governance index with 5 documented pillars, plus an interactive simulator to project compliance gains before committing organizational resources.
- **Audit-Ready Evidence Reports:** One-click compliance exports (CSV, JSON, Markdown) with raw personal values masked or excluded.

---

## 2. Seven Core Privacy Intelligence Features

### Feature 1: Privacy Risk Radar
Calculates a transparent risk score (0 to 100) per detected field based on 6 documented factors:
1. **Data Sensitivity (0–35 pts):** `GOVERNMENT_ID` (35) > `PHONE_NUMBER` / `EMAIL` (25) > `ADDRESS` (20) > `NAME` (15).
2. **Detection Confidence (0–15 pts):** Scaled contribution based on empirical match ratios ($conf \times 15$).
3. **Purpose Compliance (0–20 pts):** Missing purpose (+20); Unapproved purpose (+10); Approved purpose (0).
4. **Retention Schedule (0–15 pts):** Missing retention (+15); Extended retention > 365d (+8); Standard (0).
5. **Review Workflow State (0–15 pts):** Unreviewed pending (+15); Secondary flag (+10); Confirmed (0).
6. **Cross-Source Exposure (0–15 pts):** Proliferation across $\ge 3$ sources (+15); across 2 sources (+10).
- **Priority Tiers:** Critical (75–100), High (55–74), Medium (35–54), Low (0–34).

### Feature 2: Visual Privacy Exposure Map
- Interactive Plotly Sankey diagram illustrating multi-tier data flow.
- Color-coded nodes highlighting compliance gaps (red/amber for missing purpose or high-risk identifiers).
- Cross-source proliferation table identifying classes stored across multiple independent systems.

### Feature 3: Intelligent Remediation Engine
- Generates actionable compliance tasks for every detected issue.
- Tasks include target field ID, risk level, title, justification, suggested action, expected benefit, and status (`Open`, `In Progress`, `Resolved`).
- Status updates and reviewer notes persist across app restarts in `config/remediations.json`.
- Strictly read-only: never modifies source databases or deletes raw data.

### Feature 4: Privacy Posture Scorecard
Transparent 0–100 score built on 5 documented governance pillars with explicit mathematical denominators:
1. `Review Coverage Rate` (25% weight): % of candidate fields reviewed by human DPO.
2. `Purpose Approval Rate` (25% weight): % of candidate fields with officially approved purposes.
3. `Retention Policy Coverage` (20% weight): % of candidate fields with configured retention schedules.
4. `High-Risk Resolution Rate` (20% weight): % of Critical/High findings reviewed and approved.
5. `Evidence & Audit Readiness` (10% weight): % of fields with technical evidence & masked samples logged.

### Feature 5: Privacy Impact What-If Simulator
- In-memory simulation of hypothetical governance improvements:
  - Scenario A: Formally document & approve all purpose metadata.
  - Scenario B: Define & enforce standard 180-day retention schedules.
  - Scenario C: Complete DPO human verification for Critical/High findings.
  - Scenario D: Implement data minimization (eliminate cross-source duplication).
- Displays real-time deltas for Posture Score, Average Risk, and Critical Findings Count.

### Feature 6: Audit-Ready Compliance Exports
- Export Enriched Inventory as CSV (with risk scores and masked values).
- Export Full Compliance Inventory as JSON (with lineage, risk evaluations, and remediation tasks).
- Export Evaluation Benchmark Metrics as CSV.
- Export Comprehensive Markdown Audit Report (`reports/privacy_audit_report.md`).
- Explicit distinction between: (1) Scanner observations, (2) Declared metadata, (3) Reviewer decisions, (4) Automated recommendations, and (5) Simulated results.

### Feature 7: Guided Hackathon Demo Mode
- A 7-step guided presentation mode built directly into the sidebar.
- Step-by-step progress tracking with "Next" / "Previous" navigation.
- Safe Demo State Reset with automatic timestamped backups in `config/backups/`.

---

## 3. Technology Stack

| Component | Technology | Version | Rationale |
|:---|:---|:---|:---|
| **Programming Language** | Python | 3.11+ (Tested on 3.12.6) | Cross-platform compatibility, clean standard library. |
| **User Interface** | Streamlit | >= 1.30.0 | Lightweight, reactive, no web-server boilerplate needed. |
| **Visual Charts** | Plotly & Matplotlib | >= 5.18.0 / >= 3.7.0 | Interactive Sankey diagrams & confusion matrix heatmaps. |
| **Data Processing** | Pandas | >= 2.0.0 | Efficient tabular ingestion and bounded sampling. |
| **Embedded Database** | SQLite3 | Python standard lib | Zero-configuration local database (read-only mode). |
| **Pattern Matching** | Python Regex (`re`) | Python standard lib | Fast, local, deterministic pattern matching. |
| **Evaluation Metrics** | Scikit-learn | >= 1.3.0 | Standardized calculations for precision, recall, F1. |
| **Test Automation** | Pytest | >= 7.4.0 | Unit, integration, and edge-case test verification (33 tests). |

---

## 4. Setup Instructions for Windows 11

### Step 1: Open PowerShell in the Project Directory
```powershell
cd C:\Users\krary\OneDrive\Desktop\A3-PS019-TC316
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Run Automated Tests (33 Tests)
```powershell
python -m pytest -v
```
*Expected Output: `33 passed in ~10.90s (100% pass rate)`.*

### Step 5: Launch the Streamlit Web Application
```powershell
streamlit run app.py
```
*Automatically opens in browser at `http://localhost:8501`.*

---
**AIORI Hackathon 3 | Team A3-PS019-TC316**
