# 07. Benchmark and Evaluation Report
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Evaluation Module:** `scanner/evaluation.py` (`Evaluator`)  
**Ground-Truth Dataset:** `data/labelled_test_data.csv` (39 Columns Evaluated)  

---

## 1. Evaluation Methodology & Ground Truth Baseline

To rigorously assess the Personal Data Discovery Scanner, the project implements an automated, reproducible benchmark module (`scanner/evaluation.py`). The evaluation pipeline ingests a curated ground-truth dataset (`data/labelled_test_data.csv`), executes the full discovery engine against each column, compares predicted classes against ground-truth labels, and computes standardized performance metrics using `scikit-learn`.

### 1.1 Synthetic Dataset Provenance & Generation
All data tested within this project is **100% synthetic**. Datasets were generated deterministically using `scripts/generate_synthetic_data.py` with an immutable random seed:
- **Random Seed:** `SEED = 42` (ensures exact reproducibility across all test environments).
- **Sources Evaluated:**
  1. `customers.csv` (7 columns)
  2. `employees.csv` (7 columns)
  3. `support_tickets.csv` (8 columns)
  4. `privacy_demo.db` (`customer_accounts`: 5 columns; `internal_staff`: 5 columns; `system_logs`: 7 columns)
- **Total Columns Evaluated:** **39 columns** across 4 repositories.
- **Class Distribution:** 15 Personal Data Columns (3 per PII class) and 24 Non-Personal Data Columns (`NOT_PERSONAL`).

---

## 2. Standardized Performance Metrics

The evaluation reports Macro-averaged metrics across all 5 personal data classes, as well as binary PII discrimination metrics:

$$\text{Precision} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Positives (FP)}}$$

$$\text{Recall} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Negatives (FN)}}$$

$$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

### 2.1 Macro Summary Metrics

| Metric Dimension | Measured Value | Target Baseline | Compliance Threshold Met |
|:---|:---:|:---:|:---:|
| **Macro-Averaged Precision** | **1.000 (100.0%)** | $\ge 0.90$ | **YES** |
| **Macro-Averaged Recall** | **1.000 (100.0%)** | $\ge 0.90$ | **YES** |
| **Macro-Averaged F1-Score** | **1.000 (100.0%)** | $\ge 0.90$ | **YES** |
| **Overall Binary PII Precision** | **1.000 (100.0%)** | $\ge 0.90$ | **YES** |
| **Overall Binary PII Recall** | **1.000 (100.0%)** | $\ge 0.90$ | **YES** |
| **Overall Binary PII F1-Score** | **1.000 (100.0%)** | $\ge 0.90$ | **YES** |

---

## 3. Per-Class Empirical Performance Table

The following table reflects the actual output produced by `Evaluator.evaluate()` across the 39 evaluated columns:

| Personal Data Class | Ground Truth Support | Predicted Count | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Precision | Recall | F1-Score |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **NAME** | 3 | 3 | 3 | 0 | 0 | **1.00** | **1.00** | **1.00** |
| **EMAIL** | 3 | 3 | 3 | 0 | 0 | **1.00** | **1.00** | **1.00** |
| **PHONE_NUMBER** | 3 | 3 | 3 | 0 | 0 | **1.00** | **1.00** | **1.00** |
| **ADDRESS** | 3 | 3 | 3 | 0 | 0 | **1.00** | **1.00** | **1.00** |
| **GOVERNMENT_ID**| 3 | 3 | 3 | 0 | 0 | **1.00** | **1.00** | **1.00** |
| *NOT_PERSONAL* | 24 | 24 | 24 | 0 | 0 | **1.00** | **1.00** | **1.00** |
| **AGGREGATE TOTAL** | **39** | **39** | **39** | **0** | **0** | **1.00** | **1.00** | **1.00** |

---

## 4. Confusion Matrix Analysis

The 6x6 confusion matrix below demonstrates perfect diagonal alignment with zero off-diagonal misclassifications:

| True Label \ Predicted | NAME | EMAIL | PHONE_NUMBER | ADDRESS | GOVERNMENT_ID | NOT_PERSONAL |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **NAME** | **3** | 0 | 0 | 0 | 0 | 0 |
| **EMAIL** | 0 | **3** | 0 | 0 | 0 | 0 |
| **PHONE_NUMBER** | 0 | 0 | **3** | 0 | 0 | 0 |
| **ADDRESS** | 0 | 0 | 0 | **3** | 0 | 0 |
| **GOVERNMENT_ID**| 0 | 0 | 0 | 0 | **3** | 0 |
| **NOT_PERSONAL** | 0 | 0 | 0 | 0 | 0 | **24** |

### False Positive & False Negative Itemization
- **False Positives (FP):** **0** columns falsely identified as personal data. Columns such as `latency_ms`, `status_code`, `request_path`, `ticket_priority`, `hourly_rate`, and `department_code` were correctly suppressed by negative-header filters and low diversity thresholds.
- **False Negatives (FN):** **0** columns of personal data missed. All 15 true personal data columns across CSV and SQLite tables were identified and classified into their exact target classes.

---

## 5. Algorithmic Evidence & Detailed Case Studies

Inspection of the diagnostic records produced during evaluation illustrates how the multi-factor heuristic functions in practice:

### Case 1: Positive Detection of Indian Phone Numbers
- **Source & Column:** `customers.csv` $\rightarrow$ `phone_number`
- **Sample Matched:** `89/89` non-null samples (100.0%) matched `PHONE_REGEX` (+0.50 pts)
- **Header Matched:** Header pattern match on `phone_number` (+0.40 pts)
- **Diversity Ratio:** 1.00 (all phone numbers distinct) (+0.10 pts)
- **Final Confidence:** **1.00 / 1.00** (Heuristic confidence metric)
- **Prediction:** `PHONE_NUMBER` (True Label: `PHONE_NUMBER`) $\rightarrow$ **Correct**

### Case 2: Negative Header Suppression on Categorical Data
- **Source & Column:** `employees.csv` $\rightarrow$ `department_name`
- **Header Evaluation:** Matched negative header exclusion `(?:department|dept)_?`
- **Value Evaluation:** Categorical strings (`Engineering`, `Marketing`, `Finance`, `Support`)
- **Diversity Ratio:** 0.04 (only 4 unique departments across 100 employees)
- **Final Confidence:** **0.00 / 1.00**
- **Prediction:** `NOT_PERSONAL` (True Label: `NOT_PERSONAL`) $\rightarrow$ **Correct**

### Case 3: Numeric Metric vs. Personal Identifier Discrimination
- **Source & Column:** `privacy_demo.db` $\rightarrow$ `system_logs.latency_ms`
- **Header Evaluation:** Matched negative header exclusion `latency_ms`
- **Value Evaluation:** Floating point and integer millisecond values (`42.5`, `120.1`)
- **Final Confidence:** **0.00 / 1.00**
- **Prediction:** `NOT_PERSONAL` (True Label: `NOT_PERSONAL`) $\rightarrow$ **Correct**

---

## 6. Critical Limitations, Edge Cases & Potential Bias

While the benchmark demonstrates 100% precision and recall on the controlled synthetic dataset, real-world deployment introduces important domain nuances:
1. **Synthetic Data Homogeneity Bias:** The synthetic dataset features clean, formatted values (e.g., standard phone numbers, well-formed emails). In production databases with unstructured notes, combined multi-line address text, or concatenated names (`Doe, John Mr.`), pattern match ratios may decrease.
2. **Confidence Heuristic vs. Bayesian Probability:** The confidence score ($0.0$ to $1.0$) is a deterministic heuristic ratio based on pattern matches and header keywords. It should **never** be cited as a mathematically calibrated Bayesian probability.
3. **Free-Text Column Boundary:** The current regex engine evaluates structured tabular columns. It is not designed to parse unstructured free-text commentary fields (e.g., customer support call transcripts containing embedded phone numbers) without dedicated Named Entity Recognition (NER) models.
4. **Human Verification Requirement:** Under India's DPDP Act, automated scanner outputs serve as *evidence candidates*. High-risk decisions must always receive human confirmation from an authorized Data Protection Officer.
