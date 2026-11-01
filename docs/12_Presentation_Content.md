# 12. Project Presentation Content (Pitch Deck)
**Project Title:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Format:** 10-Slide Structured Pitch Deck for Hackathon Judges & Evaluators  

---

## Slide 1: Title & Team Identification

### Header: PS-019: Privacy Intelligence Engine
#### Subtitle: Personal-Data Discovery & Privacy Evidence Inventory with Explainable Governance
- **Hackathon Track:** AIORI Hackathon 3 — Problem Statement PS-019
- **Team ID:** Team A3-PS019-TC316
- **Team Members:** `[Insert Presenter 1 Name]` | `[Insert Presenter 2 Name]` | `[Insert Presenter 3 Name]`
- **Technology Stack:** Python 3.12, Streamlit, Pandas, SQLite, Scikit-learn, Plotly
- **Core Value Proposition:** 100% offline, explainable privacy discovery transforming raw database schemas into audit-ready regulatory evidence under India’s DPDP Act.

---

## Slide 2: The Regulatory Problem

### Header: The Challenge of Unregulated Personal Data Sprawl
- **The Modern Enterprise Reality:** Personal Data (PII) inevitably sprawls across legacy CSV exports, staging spreadsheets, and uncataloged SQLite databases.
- **Statutory Mandate (DPDP Act 2023 & MeitY Framework):**
  - **Purpose Limitation:** Processing is permitted only for explicitly declared, lawful purposes.
  - **Storage Limitation:** Personal data must not be retained indefinitely once the purpose is satisfied.
- **The Core Dilemma:** You cannot govern, retain, or delete data you do not know you possess.

---

## Slide 3: Why This Problem Matters

### Header: The Cost of Inaction: Penalties, Breaches, and Audit Failures
- **Severe Financial Penalties:** India's DPDP Act imposes statutory penalties up to ₹250 Crores for significant data protection failures.
- **Expanded Attack Surface:** Unmanaged, unindexed database columns containing emails, phone numbers, and government IDs create attractive targets for credential stuffing and identity fraud.
- **The Operational Gap:**
  - *Manual surveys* are instantly obsolete and subjective.
  - *Cloud enterprise DLP* is expensive, complex, and ironically introduces privacy risks by transmitting schema extracts outside the corporate firewall.

---

## Slide 4: Our Proposed Solution

### Header: The Privacy Intelligence Engine
- **From Raw Discovery to Active Governance:** We bridge the chasm between raw regex matching and demonstrable compliance evidence.
- **Five Core Capabilities:**
  1. **Multi-Source Discovery:** Samples CSV files and SQLite databases with zero data alteration.
  2. **Evidence Linking:** Correlates candidate fields with declared business purposes and retention limits.
  3. **Privacy Risk Radar:** Calculates an explainable 0–100 risk score based on 6 transparent factors.
  4. **Privacy Exposure Map:** Visualizes data lineage and cross-source proliferation using interactive Sankey diagrams.
  5. **Remediation & Simulation:** Deterministically generates remediation tasks and models policy impact via an interactive What-If Simulator.

---

## Slide 5: System Architecture & Design

### Header: Modular, Local-First, and Resilient Architecture
- **Presentation Layer:** Modern clean light-theme Streamlit web interface with 10 structured workflow pages.
- **Intelligence Core (`scanner/`):** Decoupled Python classes for detection heuristics, risk scoring, remediation management, and posture calculation.
- **Safety Guarantees:**
  - Strict read-only database connections (`mode=ro`).
  - Bounded memory sampling (max 100 non-null rows per column).
  - Automated data masking (`M*** M***`, `j***@example.com`, `+91-*****-***10`).
- **Persistence Store:** Zero external database engines; local JSON governance stores (`config/metadata.json`, `config/remediations.json`).

---

## Slide 6: Key Features & The Governance Workflow

### Header: End-to-End Privacy Discovery Workflow
```
[1. Ingest & Sample] ──> [2. Multi-Factor Detection] ──> [3. Evidence Enrichment]
  CSV & SQLite (mode=ro)    Header + Regex + Diversity      Link Purpose & Retention
                                                                    │
                                                                    ▼
[6. Compliance Export] <── [5. Simulate & Remediate] <── [4. Quantify & Map Risk]
  CSV, JSON, Audit Markdown   What-If Engine & Tasks        Risk Radar & Sankey Map
```
- **Transparent Risk Scoring:** Factors sensitivity (35 pts), confidence (15 pts), missing purpose (+20 pts), missing retention (+15 pts), review status (15 pts), and proliferation (+15 pts).
- **Human-in-the-Loop:** DPO can record verified review decisions (`Confirmed`, `Rejected`, `Flagged`) that persist across application sessions.

---

## Slide 7: Demonstration Results & Empirical Benchmark

### Header: Verified Accuracy: 100% Precision, Recall, and F1
- **Empirical Ground-Truth Evaluation (`scanner/evaluation.py`):**
  - Evaluated on **39 columns** across 3 CSV datasets and 1 SQLite database.
  - 15 True PII Columns (3 per class: Name, Email, Phone, Address, Government ID).
  - 24 Non-PII Technical & Metric Columns (latency, logs, status codes).
- **Benchmark Performance Metrics:**
  - **Macro Precision:** **1.00 (100.0%)** | **Macro Recall:** **1.00 (100.0%)** | **Macro F1:** **1.00 (100.0%)**
  - **False Positives:** **0** | **False Negatives:** **0**
- **Automated Test Suite:** **33 automated pytest tests** covering unit, integration, and security assertions (100% pass rate in ~10 seconds).

---

## Slide 8: Privacy, Security & Ethical Safeguards

### Header: Engineered for Privacy: Zero Leakage, Zero Risk
- **100% Offline Processing:** Never makes outbound HTTP requests; no telemetry, no cloud API dependencies.
- **Strict Data Masking:** Sample values displayed in the dashboard or exported to audit reports are cryptographically masked before presentation.
- **Deterministic Synthetic Data:** Preloaded with realistic synthetic datasets generated with `SEED=42`. Synthetic government IDs feature explicit markers (`SYN-AAD-`, `SYNPA`) to ensure test safety.
- **Non-Destructive Assurance:** The application never deletes, alters, or masks records in source databases—guaranteeing zero accidental data loss.

---

## Slide 9: Limitations & Future Roadmap

### Header: Transparency & Engineering Evolution
- **Current System Boundaries:**
  - Evaluates structured and tabular columns; does not currently perform Named Entity Recognition (NER) on free-text narrative paragraphs.
  - Risk Radar scores and Posture Scorecard provide technical prioritization metrics; they do not replace formal legal counsel or statutory DPIA reviews.
- **Production Roadmap:**
  - **Phase 1:** Enterprise Single Sign-On (SSO / OIDC) for DPO and DBA role separation.
  - **Phase 2:** Connectors for distributed databases (PostgreSQL, Snowflake, Amazon S3).
  - **Phase 3:** Local transformer-based small language models (SLMs) for multi-language unstructured text redaction.

---

## Slide 10: Conclusion & Impact

### Header: Transforming Compliance from an Annual Headache into Live Evidence
- **Immediate Value:** Turns hidden personal data liabilities into an organized, prioritized compliance inventory.
- **Audit-Ready Evidence:** Generates comprehensive CSV, JSON, and Markdown audit reports with a single click.
- **Cost & Simplicity:** Zero licensing cost, zero cloud infrastructure, runs on any standard Windows 11 workstation.
- **Closing Statement:**
  > *"PS-019 Privacy Intelligence Engine delivers demonstrable, explainable, and accessible privacy governance—empowering every enterprise to fulfill the spirit of the DPDP Act."*
- **Q&A:** We welcome questions from the jury!
