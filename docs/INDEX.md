# Privacy Intelligence Engine — Documentation Index & Submission Package
**Project Identification:** PS-019 | Personal-Data Discovery & Privacy Evidence Inventory  
**Hackathon:** AIORI Hackathon 3  
**Team ID:** Team A3-PS019-TC316  
**Repository Branch:** main / local workspace  
**Platform Compatibility:** Windows 11 / Linux / macOS (Python 3.11+, tested on Python 3.12.6)  

---

## Welcome Reviewers & Judges

Welcome to the official technical documentation suite for **PS-019: Privacy Intelligence Engine**. This documentation provides a comprehensive, empirically verified reference for the system's architecture, regulatory alignment (India DPDP Act & MeitY Framework), algorithmic design, benchmark performance, and testing validation.

Every metric, formula, test count, and architectural component documented across these files has been verified against the actual source code and executed test suite in this repository.

---

## Suggested Reviewer Reading Order

For an efficient evaluation, we recommend reviewing this package in the following sequence:

| Step | Document | Purpose & Key Takeaways | Est. Reading Time |
|:---:|:---|:---|:---:|
| **1** | [Project Overview](01_Project_Overview.md) | Problem statement, regulatory gap analysis, proposed solution, objectives, and scope. | 5 min |
| **2** | [Software Requirements Specification](02_Software_Requirements_Specification.md) | Functional Requirements (FR-01 to FR-10) with IDs, Non-Functional Requirements, and constraints. | 7 min |
| **3** | [System Architecture](03_System_Architecture.md) | High-level system architecture, ingestion pipeline, state persistence, and 4 Mermaid diagrams. | 6 min |
| **4** | [Technical Design & Algorithms](04_Technical_Design.md) | Algorithmic heuristics, regex patterns, Risk Radar scoring formula, and Posture Scorecard math. | 8 min |
| **5** | [Benchmark & Evaluation Report](07_Benchmark_and_Evaluation.md) | Ground-truth benchmark on 39 fields, confusion matrix, precision/recall/F1 metrics. | 5 min |
| **6** | [Testing & QA Report](06_Testing_and_QA_Report.md) | Automated test suite breakdown (33 passed tests, 0 failures), coverage, and edge cases. | 5 min |
| **7** | [Hackathon Demo Guide](10_Hackathon_Demo_Guide.md) | Step-by-step 3–5 minute pitch and demonstration walkthrough with expected outputs and fallback plans. | 4 min |
| **8** | [Traceability Matrix](13_Requirements_Traceability_Matrix.md) | Full mapping from SRS requirements to code implementations and automated pytest tests. | 4 min |

---

## Complete Document Directory

```
docs/
├── INDEX.md                                  # This master navigation index
├── 01_Project_Overview.md                    # Problem context, gap, solution, and scope
├── 02_Software_Requirements_Specification.md # Formal SRS (FRs, NFRs, acceptance criteria)
├── 03_System_Architecture.md                 # Architecture, pipelines, and Mermaid diagrams
├── 04_Technical_Design.md                    # Heuristics, formulas, scoring, and normalization
├── 05_Installation_and_User_Guide.md         # Windows 11 setup, launch, UI guide, troubleshooting
├── 06_Testing_and_QA_Report.md               # QA suite report (33 tests, environment, categories)
├── 07_Benchmark_and_Evaluation.md            # Empirical benchmark results (P/R/F1, confusion matrix)
├── 08_Security_Privacy_and_Ethics.md         # Masking, DPDP principles, threats, and hardening
├── 09_API_and_Data_Reference.md              # Python class APIs, schemas, and export formats
├── 10_Hackathon_Demo_Guide.md                # 3–5 minute presentation script and narration
├── 11_Final_Submission_Checklist.md          # Complete verification matrix (Verified vs Manual)
├── 12_Presentation_Content.md                # 10-slide pitch presentation content
├── 13_Requirements_Traceability_Matrix.md   # SRS-to-Code-to-Test traceability matrix
└── screenshots/
    └── README.md                             # Screenshot capture checklist and visual guide
```

---

## Quick Command Reference

```powershell
# 1. Activate Virtual Environment (Windows 11 PowerShell)
.\.venv\Scripts\Activate.ps1

# 2. Install Project Dependencies
pip install -r requirements.txt

# 3. Regenerate Synthetic Datasets (Deterministic Seed = 42)
python scripts/generate_synthetic_data.py

# 4. Run Complete Automated Test Suite (33 Tests)
python -m pytest -v

# 5. Launch Privacy Intelligence Engine Dashboard
streamlit run app.py
```

---

## Verified Implementation Factsheet

- **Total Test Cases:** 33 passing automated tests across 6 test suites (`pytest`).
- **Benchmark Evaluation:** Evaluated across 39 ground-truth fields across 3 CSV datasets and 1 SQLite database.
  - **Macro Precision:** 1.0 (100%)
  - **Macro Recall:** 1.0 (100%)
  - **Macro F1-Score:** 1.0 (100%)
  - **Binary PII F1-Score:** 1.0 (100%)
- **Data Privacy Standard:** Strict local execution; zero cloud calls; read-only SQLite ingestion; automatic data masking (`M*** M***`, `j***@example.com`, `+91-98765-XXXXX`).
- **User Interface:** Streamlit modern light SaaS interface with responsive navigation, Plotly Sankey visualizations, and real-time What-If simulation.
