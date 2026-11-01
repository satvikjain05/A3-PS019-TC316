# 01. Project Overview & Problem Statement
**Problem Statement:** PS-019 — Personal-Data Discovery & Privacy Evidence Inventory  
**Project Name:** Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Target Platform:** Windows 11 / Local Python Environment (Offline Capable)  

---

## 1. Problem Statement Addressed

Modern enterprises collect and process unprecedented volumes of customer, employee, and business data. In fast-paced software environments, sensitive Personal Data (PII) frequently sprawls across departmental file shares, legacy CSV spreadsheets, development exports, and uncataloged SQLite databases.

Under major data protection statutes—such as India's **Digital Personal Data Protection (DPDP) Act 2023**, the **MeitY Data Protection Framework**, and the **EU General Data Protection Regulation (GDPR)**—enterprises acting as *Data Fiduciaries* face stringent statutory duties:
1. **Purpose Limitation:** Personal data must only be collected and processed for explicitly stated, lawful purposes.
2. **Storage Limitation / Data Minimization:** Personal data must not be retained indefinitely; retention schedules must align strictly with active business necessity.
3. **Accountability & Demonstrable Evidence:** Data fiduciaries must maintain a comprehensive, up-to-date inventory of personal data repositories, showing technical evidence of purpose and retention compliance.

Failure to maintain an accurate personal data inventory leads to severe regulatory sanctions, increased vulnerability to credential stuffing and identity theft during breach events, and audit failures.

---

## 2. Gap Analysis: Limitations of Existing Approaches

Existing data discovery approaches generally fall into two extremes, leaving a dangerous operational gap:

| Dimension | Legacy Manual Surveys | Heavyweight Enterprise Cloud DLP | PS-019 Privacy Intelligence Engine |
|:---|:---|:---|:---|
| **Discovery Mechanism** | Static spreadsheets and annual interviews with engineering teams. | Proprietary ML agents scanning cloud object stores. | Deterministic, local multi-factor regex & header heuristics. |
| **Operational Friction** | High: prone to human memory lapses, quickly obsolete. | High: requires complex cloud infrastructure, external network access, and recurring cloud licensing costs. | Minimal: single-command local run, zero cloud dependencies, lightweight execution. |
| **Governance Linking** | Disconnected from actual database schemas; no automated linking. | Flags "sensitive strings" without linking to declared business purpose or retention policy. | Natively links detected fields to declared purpose, retention schedules, and review status. |
| **Risk Explainability** | Subjective, ad-hoc qualitative rankings. | Opaque "black-box" risk numbers without formula breakdown. | Transparent 0–100 mathematical risk score factoring 6 explainable weights. |
| **Data Privacy Threat** | Moderate: manual data handling across spreadsheets. | High: transmits schema samples or data extracts to third-party cloud APIs. | Zero external risk: strictly local processing, read-only database connections, automated sample masking. |

---

## 3. Proposed Solution

The **Privacy Intelligence Engine** is a modular, transparent, and completely local privacy engineering platform designed to bridge discovery and compliance evidence. 

Rather than merely generating a list of matching regex strings, the system transforms raw discovery into an active privacy governance evidence store:
1. **Multi-Source Discovery Scanner:** Ingests CSV files and structured SQLite databases, sampling records safely to detect 5 distinct personal-data classes (`NAME`, `EMAIL`, `PHONE_NUMBER`, `ADDRESS`, `GOVERNMENT_ID`).
2. **Dynamic Metadata Inventory:** Automatically links discovered candidate columns to organizational metadata, checking whether the data has a declared business purpose and a defined retention schedule.
3. **Explainable Privacy Risk Radar (0–100):** Evaluates every detected field against an explicit mathematical formula, scoring sensitivity, detection confidence, missing purpose penalties, retention overages, and cross-source proliferation.
4. **Visual Privacy Exposure Map:** Renders interactive Plotly Sankey lineage diagrams, tracing data flows from physical storage sources through data categories into organizational purposes.
5. **Intelligent Remediation Center:** Automatically generates prioritized, actionable remediation tasks (e.g., purpose formalization, retention policy enforcement) and persists reviewer actions across sessions.
6. **Privacy Posture Scorecard & What-If Simulator:** Calculates a composite 0–100 institutional posture score across 5 governance pillars, allowing privacy officers to simulate compliance actions before committing engineering resources.
7. **Empirical Benchmark Evaluator:** Formally tests detection accuracy against a curated ground-truth dataset, reporting per-class Precision, Recall, F1-score, and confusion matrices.

---

## 4. Main Objectives

- **Objective 1 (Detection Accuracy):** Achieve high precision and recall (>90%) across 5 core personal data classes in semi-structured CSV and relational SQLite formats without using paid APIs or cloud dependencies.
- **Objective 2 (Evidence Inventory):** Maintain a persistent, structured inventory linking physical storage locations to data fiduciary metadata (purpose, retention period, human verification status).
- **Objective 3 (Explainable Prioritization):** Provide security and compliance teams with a deterministic risk scoring model that eliminates guesswork and highlights urgent data liabilities.
- **Objective 4 (Safe Operation):** Enforce strict read-only guarantees on discovered data sources and automatically mask all sensitive sample values displayed in the UI or exported in audit reports.
- **Objective 5 (Empirical Accountability):** Provide automated verification through a dedicated test suite (33 automated pytest tests) and reproducible ground-truth benchmark reporting.

---

## 5. Scope and Boundaries

### In Scope
- File formats: Delimited CSV text files (comma, semicolon, tab) and SQLite 3 relational database files (`.db`, `.sqlite`).
- Personal data classes: 5 predefined classes:
  - `NAME`: Individual customer/employee names.
  - `EMAIL`: RFC-5322 compliant email addresses.
  - `PHONE_NUMBER`: Formatted telephone numbers (specialized support for Indian mobile formats: `+91`, 10-digit formats).
  - `ADDRESS`: Postal and physical residential addresses.
  - `GOVERNMENT_ID`: Synthetic national identification markers (Aadhaar, PAN, SSN-style alphanumeric structures).
- Storage: Local JSON configuration files (`config/metadata.json`, `config/remediations.json`).
- Visualization & UI: Streamlit-based web interface with Plotly and Matplotlib visualizations.
- Export formats: CSV, JSON, and Markdown audit reports.

### Out of Scope
- Unstructured text scanning (e.g., scanning raw PDF documents, Word documents, or audio transcripts).
- Cloud database connectors (e.g., live connectors for AWS RDS, Snowflake, or Google BigQuery).
- Heavyweight Machine Learning or LLM models (regex and heuristic algorithms are intentionally prioritized for determinism, zero inference latency, and offline compliance).
- Automated database modifications (the system strictly acts as an auditor; it never deletes, alters, or masks records in the source databases).

---

## 6. Intended User Personas

1. **Data Protection Officer (DPO) / Chief Privacy Officer:**
   - Evaluates overall organizational compliance against DPDP / GDPR requirements.
   - Monitors the Privacy Posture Scorecard and reviews high-risk unapproved data stores.
   - Exports authoritative Markdown/JSON audit evidence reports for statutory authorities.
2. **Privacy Engineer / AppSec Specialist:**
   - Runs discovery scans across staging databases and batch exports.
   - Investigates data proliferation in the Privacy Exposure Map.
   - Evaluates detection performance and fine-tunes regex patterns via the Benchmark Evaluator.
3. **Database Administrator (DBA) / Data Steward:**
   - Receives prioritized remediation tasks from the Remediation Center.
   - Configures retention policies and purges stale personal data based on inventory findings.
4. **Internal Compliance Auditor:**
   - Inspects human-review decision logs and confirms that personal data fields have valid declared purposes.

---

## 7. Key Operational Workflows

```
┌─────────────────┐     ┌───────────────────────┐     ┌──────────────────────┐
│  Data Sources   │ ──> │ Multi-Factor Detector │ ──> │  Evidence Inventory  │
│ (CSV & SQLite)  │     │ (Header + Regex + Div)│     │(Link Purpose/Retain) │
└─────────────────┘     └───────────────────────┘     └──────────────────────┘
                                                                 │
                                                                 ▼
┌─────────────────┐     ┌───────────────────────┐     ┌──────────────────────┐
│ Audit Evidence  │ <── │ Remediation Center &  │ <── │ Explainable Radar &  │
│(CSV/JSON/Report)│     │  What-If Simulations  │     │ Posture Scorecard    │
└─────────────────┘     └───────────────────────┘     └──────────────────────┘
```

1. **Ingestion & Discovery:** The user points the scanner to local CSV datasets or SQLite databases. The engine samples up to 100 rows per column without loading entire massive datasets into memory.
2. **Multi-Factor Classification:** Columns are analyzed using regex pattern matching, header semantics, negative-header exclusion filters, and value diversity metrics.
3. **Metadata Enrichment:** Discovered fields are correlated with `config/metadata.json` to verify purpose alignment, retention schedules, and review status.
4. **Risk Quantification:** Each field receives an explainable 0–100 risk score and tier assignment (Critical, High, Medium, Low).
5. **Review & Remediation:** The privacy officer records review decisions (`Approved`, `Flagged`, `Under Review`) and resolves remediation tasks.
6. **Audit Export:** The final verified evidence inventory is exported as CSV, JSON, or Markdown for compliance reporting.

---

## 8. Expected Impact & Utility

- **Audit Readiness:** Replaces manual spreadsheet tracking with a live, reproducible inventory verified against actual database schemas.
- **Regulatory Penalty Mitigation:** Highlights unapproved purposes and overdue retention schedules before official regulatory inspections.
- **Resource Prioritization:** Pinpoints the highest-risk fields across disparate systems so privacy engineering teams focus effort where legal exposure is highest.
- **Zero Privacy Leakage:** Built from the ground up for strict local operation, ensuring that sensitive enterprise data never leaves the local perimeter.

---

## 9. Explicit Assumptions & Unvalidated Claims

To ensure rigorous honesty and academic integrity:
- **Heuristic Confidence vs. Probability:** The detection confidence metric (0.0 to 1.0) is a deterministic heuristic ratio based on pattern matches and header keywords. It is **not** a calibrated Bayesian probability.
- **Synthetic Ground Truth:** The reported 100% precision and recall scores were calculated on our synthetic benchmark dataset (`data/labelled_test_data.csv`, 39 columns). In real-world enterprise databases containing ambiguous free-text fields or inconsistent formatting, performance will be subject to edge cases and false positives/negatives.
- **Statutory Legal Guarantee:** The Risk Radar score and Posture Scorecard provide engineering prioritization metrics; they do not constitute formal legal counsel or guarantee immunity from regulatory enforcement under the DPDP Act.
