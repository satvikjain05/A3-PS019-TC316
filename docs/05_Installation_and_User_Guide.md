# 05. Installation and User Guide
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Target Environment:** Windows 11 (PowerShell) / Linux / macOS  

---

## 1. Prerequisites & System Requirements

Before setting up the project, ensure your workstation meets the following requirements:
- **Operating System:** Windows 11 (64-bit) recommended; compatible with Windows 10, Ubuntu 22.04+, and macOS Monterey+.
- **Python Version:** Python 3.11 or Python 3.12 (Checked and verified on Python 3.12.6).
- **RAM:** Minimum 4 GB (8 GB recommended).
- **Disk Space:** ~200 MB free space for repository, virtual environment, and synthetic datasets.
- **Network Requirement:** Internet access is required ONLY during initial dependency installation (`pip install`). The application runs 100% offline once dependencies are cached.

> [!IMPORTANT]
> **Safety Notice:** Always use the provided synthetic sample datasets for testing and demonstrations. **Never upload real, live, or sensitive personal data** to hackathon testing environments.

---

## 2. Windows 11 Setup: Step-by-Step

### Step 1: Open Windows PowerShell
Press `Win + X` and select **Terminal** or **PowerShell** (Standard User, no Admin rights needed). Navigate to your project directory:

```powershell
cd C:\Users\krary\OneDrive\Desktop\A3-PS019-TC316
```

### Step 2: Create a Dedicated Virtual Environment
Isolate project dependencies to avoid conflicts with other system packages:

```powershell
python -m venv .venv
```

### Step 3: Configure PowerShell Execution Policy & Activate Virtual Environment
If PowerShell restricts script execution, set the policy for the current session and activate:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

*(Your terminal prompt should now be prefixed with `(.venv)`).*

### Step 4: Install Required Dependencies
Install the pinned libraries specified in `requirements.txt`:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Verify key package installations:
```powershell
python -c "import streamlit, pandas, sklearn, plotly, matplotlib, pytest; print('Environment Ready!')"
```

### Step 5: (Optional) Regenerate Deterministic Synthetic Datasets
The project comes preloaded with synthetic CSV datasets and a SQLite database. You can deterministically regenerate them at any time:

```powershell
python scripts/generate_synthetic_data.py
```
*(Generated files: `data/customers.csv`, `data/employees.csv`, `data/support_tickets.csv`, `data/privacy_demo.db`, `data/labelled_test_data.csv`).*

---

## 3. Launching the Application

Start the local Streamlit dashboard server:

```powershell
streamlit run app.py
```

Streamlit will start and display local access URLs:
```
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```
Open your web browser (Chrome, Edge, Firefox) and navigate to `http://localhost:8501`.

---

## 4. Comprehensive User Interface Walkthrough

The navigation sidebar organizes the Privacy Intelligence Engine into 10 structured views:

### View 1: Executive Dashboard
- **Visual Posture Scorecard:** Displays your composite institutional compliance score (0–100), governance tier (e.g., *Defined Baseline*), and individual pillar point allocations.
- **KPI Summary Cards:** Quick view of Total Discovered Fields, Candidate PII Fields, High/Critical Liabilities, and Pending Human Reviews.
- **Top 3 Priority Improvements:** Algorithmic gap detection pinpointing the biggest opportunities for compliance score enhancement.

### View 2: Data Sources & Ingestion
- **Source Inspection:** Review local tabular assets:
  - `customers.csv` (100 rows, 7 columns: customer demographics, contacts, synthetic IDs)
  - `employees.csv` (100 rows, 7 columns: internal staff contacts, salaries, government IDs)
  - `support_tickets.csv` (100 rows, 8 columns: helpdesk tickets, customer emails, callback numbers)
  - `privacy_demo.db` (SQLite database: `customer_accounts`, `internal_staff`, `system_logs`)
- **Read-Only Verification:** Demonstrates safe, bounded row previewing (up to 10 rows shown).

### View 3: Scan Results & Evidence
- **Discovery Execution:** Click **"Run Full Discovery Scan"** to sample all columns and evaluate regex patterns.
- **Candidate Evidence Table:** Review detected personal data classes, heuristic confidence scores, header patterns matched, and sample match percentages.
- **Sample Masking:** Verify that sample values are safely masked (`j***@example.com`, `M*** M***`, `+91-98765-XXXXX`).

### View 4: Privacy Evidence Inventory
- **Metadata Association:** View candidate columns linked to declared business purposes and retention periods.
- **Human Verification Workflow:**
  1. Select a discovered field from the dropdown.
  2. Choose a review decision: `Pending Review`, `Confirmed PII`, `False Positive`, or `Excluded`.
  3. Enter reviewer notes and click **"Save Review Decision"**.
  4. Changes are immediately saved to `config/metadata.json` and persist across restarts.

### View 5: Privacy Risk Radar
- **Explainable Prioritization:** View fields ranked by descending risk score (0 to 100).
- **Filter by Risk Tier:** Filter by `Critical (75–100)`, `High (55–74)`, `Medium (35–54)`, or `Low (0–34)`.
- **Explainability Drawer:** Expand any field to inspect the exact point contribution across all 6 factors (Sensitivity, Confidence, Purpose, Retention, Review, and Exposure).

### View 6: Visual Privacy Exposure Map
- **Interactive Sankey Lineage Diagram:** Hover over nodes and links to trace the flow:
  $$\text{Storage Repository} \longrightarrow \text{Personal Data Class} \longrightarrow \text{Business Purpose} \longrightarrow \text{Governance Status}$$
- **Cross-Source Proliferation Table:** Review personal data classes stored across multiple disparate files (e.g., finding `EMAIL` duplicated across 3 systems).

### View 7: Remediation Center
- **Actionable Task List:** Review auto-generated remediation tickets (e.g., *Document Purpose for Customer Govt ID*, *Configure Retention for Helpdesk Phone Numbers*).
- **Status Lifecycle:** Update ticket statuses (`Open`, `In Progress`, `Resolved`) with compliance notes. Changes persist to `config/remediations.json`.

### View 8: What-If Impact Simulator
- **Interactive Policy Toggles:** Toggle hypothetical governance interventions:
  - ☑ Document and approve all declared business purposes
  - ☑ Enforce standard 180-day retention policies
  - ☑ Complete DPO review for all Critical/High risk fields
  - ☑ Eliminate redundant cross-source proliferation
- **Real-Time Projection:** Observe instant score delta metrics ($+\Delta$ Posture Score, $-\Delta$ Mean Risk, $-\Delta$ Critical Findings) without modifying actual data or configs.

### View 9: Benchmark Evaluation
- **Ground-Truth Verification:** Run automated evaluation against `data/labelled_test_data.csv`.
- **Standardized Metrics:** Review Macro Precision, Recall, and F1-score tables.
- **Confusion Matrix:** Inspect the 6x6 graphical confusion matrix heatmap comparing predicted vs. ground-truth labels.

### View 10: Reports & Export
- **One-Click Audit Deliverables:**
  - `Export CSV Inventory`: Generates `reports/privacy_evidence_inventory.csv` with masked samples.
  - `Export JSON Inventory`: Generates structured `reports/privacy_evidence_inventory.json` for API/data pipelines.
  - `Export Benchmark CSV`: Generates `reports/evaluation_benchmark.csv`.
  - `Export Markdown Audit Report`: Generates `reports/privacy_audit_report.md` formatted for formal executive filing.

---

## 5. Troubleshooting Common Issues

### Issue 1: PowerShell Script Execution Restricted
- **Error:** `File Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
- **Solution:** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell, then re-run `.\.venv\Scripts\Activate.ps1`.

### Issue 2: Streamlit Port Conflict (Port 8501 in use)
- **Error:** `Port 8501 is already in use.`
- **Solution:** Specify an alternate port when starting the app:
  ```powershell
  streamlit run app.py --server.port 8502
  ```

### Issue 3: SQLite File Locked or Access Denied
- **Error:** `sqlite3.OperationalError: database is locked`
- **Solution:** The application opens SQLite databases using read-only URI mode (`?mode=ro`). Ensure no external DB browser (e.g., DB Browser for SQLite) has an uncommitted write transaction open on `privacy_demo.db`.

### Issue 4: Pytest Command Fails to Locate Modules
- **Error:** `ModuleNotFoundError: No module named 'scanner'`
- **Solution:** Always run pytest using Python's module flag from the repository root:
  ```powershell
  python -m pytest -v
  ```
