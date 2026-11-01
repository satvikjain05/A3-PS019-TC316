# 10. Hackathon Demonstration Guide & Presentation Script
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Presentation Target:** 3–5 Minute Live Demonstration & Pitch  
**Audience:** Technical Judges, Privacy Architects & Hackathon Evaluators  

---

## 1. Pre-Demo Setup & Verification Checklist

Complete these verification steps **5 minutes before** presenting to judges:

- [ ] **Terminal Open:** Windows PowerShell open in repository root: `C:\Users\krary\OneDrive\Desktop\A3-PS019-TC316`.
- [ ] **Virtual Environment Active:** Terminal prompt shows `(.venv)`.
- [ ] **Pre-Run Test Suite:** Run `python -m pytest -q` to confirm all 33 tests pass in ~10 seconds.
- [ ] **Streamlit App Running:** Run `streamlit run app.py` and open `http://localhost:8501` in your browser.
- [ ] **Browser Window Prepared:** Maximize browser window (press `F11` for full-screen clean view or `Ctrl + 0` to reset zoom to 100%).
- [ ] **Reset Demo State:** In the sidebar, click **"Reset Demo State"** to ensure clean baseline scores and unreviewed findings.

---

## 2. Timed 3–5 Minute Demonstration Script

### Act 1: The Regulatory Problem & Context (0:00 – 0:45)
- **Presenter Narration:**
  > *"Respected judges, under India’s Digital Personal Data Protection (DPDP) Act 2023 and the MeitY Framework, enterprises face two strict statutory principles: **Purpose Limitation** and **Storage Limitation**. In practice, sensitive personal data inevitably sprawls across legacy CSV spreadsheets and unindexed SQLite databases without documentation. 
  > Current solutions are either manual, error-prone surveys or heavyweight cloud tools that risk data leaks. 
  > We present **PS-019: Privacy Intelligence Engine**—a 100% local, explainable privacy discovery and evidence governance platform."*

---

### Act 2: Multi-Source Discovery & Safe Sampling (0:45 – 1:30)
- **Action:**
  1. Click **"Data Sources & Ingestion"** in the sidebar.
  2. Point out the CSV and SQLite data sources (`customers.csv`, `employees.csv`, `privacy_demo.db`).
  3. Click **"Scan Results & Evidence"** in the sidebar, then click the prominent lime-green button: **"Run Full Discovery Scan"**.
- **Presenter Narration:**
  > *"Our scanner connects to delimited files and SQLite databases using strict read-only connections. It analyzes column nomenclature, evaluates regex patterns, and checks token diversity across 5 statutory classes: Name, Email, Phone, Address, and Government ID. 
  > Notice that values are sampled in bounded memory and immediately masked—protecting employee and customer confidentiality during discovery."*
- **Visible Output on Screen:**
  - Progress spinner resolves in < 2 seconds.
  - Candidate table displays 15 discovered PII fields with heuristic confidence scores (1.00) and masked tokens like `j***@example.com` and `+91-*****-***10`.

---

### Act 3: Privacy Evidence Inventory & Human Review (1:30 – 2:15)
- **Action:**
  1. Click **"Privacy Evidence Inventory"** in the sidebar.
  2. Show how discovered fields automatically link to declared purposes and retention days.
  3. Under "Human Review & Decision Recording", select `customers.csv::phone_number`, set status to **"Confirmed PII"**, and click **"Save Review Decision"**.
- **Presenter Narration:**
  > *"Discovery alone is insufficient for compliance; evidence must link to organizational governance. Our engine correlates physical columns with our metadata store, immediately flagging unapproved purposes or retention overages greater than 365 days. 
  > Furthermore, the DPO can record human verification decisions, which persist across application restarts in our local governance store."*
- **Visible Output on Screen:**
  - Success alert: `"Decision recorded for customers.csv::phone_number"`.
  - Review status immediately updates in the inventory table.

---

### Act 4: Explainable Privacy Risk Radar & Exposure Lineage (2:15 – 3:15)
- **Action:**
  1. Click **"Privacy Risk Radar"** in the sidebar.
  2. Highlight the Critical tier (fields scoring $\ge 75/100$, such as `customers.csv::synthetic_govt_id`).
  3. Expand the explanation accordion to show the factor breakdown.
  4. Click **"Privacy Exposure Map"** in the sidebar to reveal the Plotly Sankey diagram.
- **Presenter Narration:**
  > *"Rather than opaque risk scores, our Privacy Risk Radar provides an explainable 0–100 score factoring 6 explicit weights: data sensitivity, detection confidence, missing purpose (+20), missing retention (+15), review state, and cross-source proliferation. 
  > Here, our Government ID scored 85/100 because it lacks an approved purpose. 
  > Switching to our Exposure Map, our interactive Sankey diagram traces data lineage from physical storage into business purposes, alerting us where customer emails and phone numbers proliferate across multiple systems."*
- **Visible Output on Screen:**
  - Interactive multi-color Sankey diagram with interactive hover tooltips.
  - Proliferation table showing `EMAIL` and `PHONE_NUMBER` appearing in 3 distinct repositories.

---

### Act 5: Remediation Center & What-If Impact Simulator (3:15 – 4:15)
- **Action:**
  1. Click **"What-If Simulator"** in the sidebar.
  2. Show the baseline Posture Score (~58/100).
  3. Toggle the simulation checkboxes:
     - ☑ *Document and approve all declared business purposes*
     - ☑ *Enforce standard 180-day retention policies*
     - ☑ *Complete DPO review for high-risk fields*
  4. Point to the real-time positive delta cards ($+\Delta$ Posture Score, $-\Delta$ Critical Findings).
- **Presenter Narration:**
  > *"Governance requires actionable follow-through. Our Remediation Center generates deterministic task tickets with persistent lifecycle tracking. 
  > Even more powerfully, our What-If Simulator allows DPOs to model policy interventions before committing engineering resources. By simulating purpose approvals and retention enforcement, our projected institutional posture jumps from 58 to 86—achieving a 'Proactive & Governed' tier entirely in-memory with zero side effects."*
- **Visible Output on Screen:**
  - Posture Score metric dynamically animates upwards with green delta tags (`+28.0 pts`).
  - Critical Findings counter drops to 0.

---

### Act 6: Empirical Benchmark, Export & Conclusion (4:15 – 5:00)
- **Action:**
  1. Click **"Benchmark Evaluation"** in the sidebar.
  2. Point to the 100% Precision, Recall, and F1 metrics and the 6x6 confusion matrix.
  3. Click **"Reports & Export"** in the sidebar, then click **"Export Markdown Audit Report"**.
- **Presenter Narration:**
  > *"To validate our engineering claims, our benchmark suite evaluates 39 ground-truth columns, achieving 100% Precision, Recall, and F1 across all 5 classes with zero false positives on non-PII metrics. 
  > With a single click, we generate audit-ready CSV, JSON, and formal Markdown reports formatted for regulatory submission. 
  > All of this runs 100% locally on standard Windows 11 hardware with zero cloud costs and zero privacy exposure. Thank you, and we welcome your questions!"*
- **Visible Output on Screen:**
  - Evaluator confusion matrix heatmap.
  - Generated audit report saved in `reports/privacy_audit_report.md`.

---

## 3. Demo Contingency & Fallback Plans

| Potential Issue | Immediate Action / Fallback |
|:---|:---|
| **Streamlit Page Hangs or Browser Glitch** | Refresh the browser tab (`Ctrl + R`). Streamlit session state preserves active scan results. |
| **Accidental Button Double-Click** | The scanner handles repeated invocations idempotently; allow the spinner 2 seconds to complete. |
| **Port Conflict on Launch** | Launch on fallback port: `streamlit run app.py --server.port 8502`. |
| **Judge Asks for Proof of Code Quality** | Switch to PowerShell terminal and run `python -m pytest -v`. Point to 33 passing automated tests running in ~10 seconds. |
| **Judge Inquires About Real Data Uploads** | Reiterate our ethical and security posture: for compliance and security safety, the scanner strictly utilizes deterministic synthetic datasets (`scripts/generate_synthetic_data.py`, seed=42) to prevent accidental data leaks. |
