# Screenshot Catalog & Manual Capture Instructions
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**UI Aesthetic:** Clean Light SaaS Dashboard (`#F8FAFC`, `#FFFFFF`, `#2563EB`)  
**Resolution Standard:** 1920 × 1080 (1080p Full HD)  

---

## 1. Ethical Screenshot Policy

> [!IMPORTANT]
> In strict accordance with the hackathon submission rules:
> - **Zero Mockups or Fabricated Screens:** We never fabricate screenshots or insert external SaaS templates as proof of implementation.
> - **Authentic UI Evidence:** All screenshots must be captured directly from the live running application (`http://localhost:8501`) executing on synthetic datasets.

---

## 2. Screenshot Capture Checklist (Manual Execution Guide)

Follow this step-by-step checklist to capture high-resolution screenshots for your hackathon pitch deck and repository submission:

### Prerequisites:
1. Start the Streamlit application:
   ```powershell
   streamlit run app.py
   ```
2. Open `http://localhost:8501` in Google Chrome or Microsoft Edge.
3. Maximize your browser and press **`F11`** for full-screen mode to eliminate browser address bars.
4. Ensure the display zoom is set to **`100%`** (`Ctrl + 0`).
5. Use Windows Snipping Tool (`Win + Shift + S`) or a full-window screen capture tool. Save PNG images in `docs/screenshots/`.

---

### Step-by-Step Screen Inventory

| File Name | Navigation View in Sidebar | Key Elements That MUST Be Visible |
|:---|:---|:---|
| `01_executive_dashboard.png` | **Executive Dashboard** | • Top Hero Banner with Posture Score (e.g., 58.0/100) & Tier Badge.<br>• 4 Metric KPI Cards (Total Discovered, Candidate PII, High-Risk, Pending Review).<br>• Top 3 Priority Improvement Opportunities cards. |
| `02_data_sources_ingestion.png` | **Data Sources & Ingestion** | • Data source summary metrics.<br>• Tabs for `customers.csv`, `employees.csv`, `support_tickets.csv`, and `privacy_demo.db`.<br>• Read-only data sample preview table with bounded 10 rows. |
| `03_scan_results_evidence.png` | **Scan Results & Evidence** | • "Run Full Discovery Scan" action button.<br>• Discovered candidate columns table.<br>• Heuristic confidence scores (1.00), sample match rates, and masked values (`j***@example.com`). |
| `04_privacy_evidence_inventory.png`| **Privacy Evidence Inventory** | • Enriched inventory table linking physical columns to declared purposes and retention days.<br>• Human Review & Decision form (dropdown selector, radio review status, notes input). |
| `05_privacy_risk_radar.png` | **Privacy Risk Radar** | • Critical / High / Medium / Low priority filter pills.<br>• Risk-ranked inventory cards sorted descending by score (e.g., 85/100).<br>• Expanded accordion showing 6-factor mathematical point breakdown. |
| `06_privacy_exposure_map.png` | **Privacy Exposure Map** | • Full interactive Plotly Sankey diagram (`Source → Class → Purpose → Governance Status`).<br>• Cross-Source Proliferation Table highlighting duplicate PII categories across databases. |
| `07_remediation_center.png` | **Remediation Center** | • Open / In Progress / Resolved task summary metric pills.<br>• Actionable remediation cards with title, suggested action, expected benefit, and status selector. |
| `08_what_if_simulator.png` | **What-If Simulator** | • Interactive policy scenario checkboxes.<br>• Dynamic delta cards showing Posture Score increase ($+\Delta$) and Critical Findings reduction ($-\Delta$). |
| `09_benchmark_evaluation.png` | **Benchmark Evaluation** | • Macro Precision (1.0), Macro Recall (1.0), Macro F1 (1.0) metric cards.<br>• 6x6 Graphical Confusion Matrix Heatmap.<br>• Per-class support and accuracy breakdown table. |
| `10_reports_export.png` | **Reports & Export** | • 4 Export cards (CSV Inventory, JSON Inventory, Benchmark CSV, Markdown Audit Report).<br>• Success download confirmation badges and file paths in `reports/`. |

---

## 3. Recommended Directory Structure

Once captured, place your screen captures in this folder:

```
docs/screenshots/
├── README.md                          # This capture guide
├── 01_executive_dashboard.png         # Main dashboard & posture score
├── 02_data_sources_ingestion.png      # Tabular & SQLite sources
├── 03_scan_results_evidence.png       # Discovery candidate evidence & masking
├── 04_privacy_evidence_inventory.png  # Linked purpose/retention & DPO reviews
├── 05_privacy_risk_radar.png          # Explainable 0-100 risk scoring
├── 06_privacy_exposure_map.png        # Plotly Sankey data lineage
├── 07_remediation_center.png          # Deterministic task management
├── 08_what_if_simulator.png           # Policy simulation & projected deltas
├── 09_benchmark_evaluation.png        # Confusion matrix & 100% F1 benchmark
└── 10_reports_export.png              # Audit report download center
```
