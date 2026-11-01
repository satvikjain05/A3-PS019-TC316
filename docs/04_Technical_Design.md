# 04. Technical Design and Algorithmic Specifications
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Implementation Baseline:** Python 3.12, Deterministic Heuristics, Explainable Scoring Models  

---

## 1. Algorithmic Overview & Design Philosophy

The **Privacy Intelligence Engine** relies on explainable, deterministic algorithms rather than opaque black-box machine learning models. In compliance and privacy auditing, auditability, explainability, and reproducibility are paramount:
- Every detection decision provides human-readable evidence strings.
- Every risk score provides an itemized mathematical point breakdown.
- Every governance pillar in the posture scorecard has an explicit numerator and denominator.

---

## 2. Personal Data Discovery & Classification Engine

### 2.1 Multi-Factor Detection Heuristics
The classification of a column into one of the 5 predefined classes (`NAME`, `EMAIL`, `PHONE_NUMBER`, `ADDRESS`, `GOVERNMENT_ID`) or `NOT_PERSONAL` is determined through a four-stage pipeline:

```
[Column Input] ──> [1. Negative Header Exclusion]
                          │ (passes)
                          ▼
                   [2. Semantic Header Matching (+0.40 pts)]
                          │
                          ▼
                   [3. Sample Value Pattern Evaluation (+0.50 pts)]
                          │
                          ▼
                   [4. Value Diversity Analysis (+0.10 pts)]
                          │
                          ▼
                   [Composite Confidence Score (0.00 – 1.00)]
```

### 2.2 Stage 1: Negative Header Exclusion Filtering
To eliminate obvious false positives before value evaluation, column names matching system metadata, keys, status flags, and categorical fields are filtered out:
- **Exclusion Pattern:** `(?:company|org|organization|file|table|column|col|database|host|server|service|event|app|tag|project|schema|issue|category|status|type|dept|department|role|priority)_?`
- **Identifier Exclusion:** Columns ending in `_id`, `_uuid`, `_hash`, `_key`, `_count`, `_index` are disqualified from personal identifier classification unless explicitly prefixed with personal markers (e.g., `user_id` vs `customer_id`).

### 2.3 Stage 2: Semantic Header Regex Patterns
When a column header matches known semantic aliases, it contributes a baseline **+0.40** to detection confidence:

| Class | Compiled Regex Pattern | Examples Matched |
|:---|:---|:---|
| **EMAIL** | `(?:^\|[_\-])(?:e?mail\|email_addr\|contact_email\|work_email\|support_email)(?:[_\-]\|$)$` | `email`, `email_address`, `work_email` |
| **PHONE_NUMBER** | `(?:^\|[_\-])(?:phone\|mobile\|cell\|contact_no\|contact_mobile\|callback_number\|tel(?:ephone)?)(?:[_\-]\|$)$` | `phone_number`, `contact_mobile`, `cell` |
| **NAME** | `(?:^\|[_\-])(?:full_name\|first_name\|last_name\|employee_name\|customer_name\|requester_name\|client_name\|user_name\|patient_name)(?:[_\-]\|$)\|^name$` | `full_name`, `employee_name`, `customer_name` |
| **ADDRESS** | `(?:^\|[_\-])(?:address\|residential_address\|office_postal_address\|dispatch_address\|street_address\|postal_address\|shipping_address\|billing_address)(?:[_\-]\|$)$` | `residential_address`, `postal_address` |
| **GOVERNMENT_ID**| `(?:^\|[_\-])(?:synthetic_govt_id\|national_id\|national_id_synthetic\|kyc_synthetic_ref\|synthetic_tax_id\|govt_id\|aadhaar\|pan_card\|voter_id)(?:[_\-]\|$)$` | `synthetic_govt_id`, `kyc_synthetic_ref` |

### 2.4 Stage 3: Sample Value Regex Validation
Sample values (up to 100 non-null rows) are evaluated against syntactic rules. The fraction of matching samples scales up to **+0.50** points:

- **`EMAIL`:** Standard RFC-5322 compliant regex: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`
- **`PHONE_NUMBER`:** Indian and international telecommunication formats: `^(?:\+91[\-\s]?)?[0]?[6-9]\d{4}[\-\s]?\d{5}$|^(?:\+91[\-\s]?)?[0]?[6-9]\d{9}$`
- **`ADDRESS`:** Keyword dictionary matching (e.g., `street`, `road`, `avenue`, `nagar`, `colony`, `sector`, `pune`, `mumbai`, `delhi`, `bengaluru`) combined with 6-digit PIN code verification (`\b[1-9][0-9]{5}\b`).
- **`GOVERNMENT_ID`:** Synthetic marker formats strictly isolating test data from live statutory credentials:
  - Synthetic Aadhaar: `^SYN-AAD-\d{4}-\d{4}-\d{4}$`
  - Synthetic PAN: `^SYNPA\d{4}[A-Z]$|^TESTP\d{4}[A-Z]$`
  - Synthetic Voter ID: `^SYNVOT\d{6,8}$`
  - Generic Synthetic ID: `^(?:SYN|TEST|DUMMY)-(?:ID|DL|SSN|UID|PASSPORT)-[A-Z0-9\-]+$`
- **`NAME`:** Multi-word alphabetic heuristic: 2–4 capitalized alphabetic tokens with length between 2 and 35 characters, validating against honorific titles (`Mr.`, `Ms.`, `Dr.`) and non-name stop words.

### 2.5 Stage 4: Value Diversity Metric
To distinguish true personal data (which exhibits high cardinality) from repetitive status enumerations or binary codes, the system calculates token diversity:

$$\text{Diversity Ratio} = \frac{\text{Count of Unique Non-Null Values}}{\text{Total Non-Null Sampled Values}}$$

- If $\text{Diversity Ratio} \ge 0.60$, the system awards the full **+0.10** diversity bonus.
- If $\text{Diversity Ratio} < 0.20$, the score is heavily discounted and flagged as `is_ambiguous = True`, preventing low-cardinality repetitive strings from triggering false alarms.

### 2.6 Confidence Score Formulation
The final heuristic confidence score $C \in [0.0, 1.0]$ is computed as:

$$C = W_{\text{header}} \cdot \mathbb{I}_{\text{header}} + W_{\text{val}} \cdot \left(\frac{N_{\text{matched}}}{N_{\text{samples}}}\right) + W_{\text{div}} \cdot \mathbb{I}_{\text{diversity} \ge 0.6}$$

Where $W_{\text{header}} = 0.40$, $W_{\text{val}} = 0.50$, and $W_{\text{div}} = 0.10$.

---

## 3. Data Masking and Display Sanitization

Before any sampled value is presented in the Streamlit UI, rendered in logs, or written to exported reports, it passes through `PersonalDataDetector.mask_value()`:

| Class | Original Synthetic Value | Masked Output for Presentation / Reports | Masking Logic Applied |
|:---|:---|:---|:---|
| **EMAIL** | `john.doe@enterprise.com` | `j***e@enterprise.com` | First & last character of user; full domain preserved. |
| **PHONE_NUMBER** | `+91-98765-43210` | `+91-*****-***10` | Mask all intermediate digits; retain country code & last 2 digits. |
| **NAME** | `Arjun Sharma` | `A*** S***` | First initial retained; trailing characters replaced with asterisks. |
| **ADDRESS** | `42 Park Avenue, Pune 411001` | `42 P***... [Masked Address]` | Leading building number retained; location details obfuscated. |
| **GOVERNMENT_ID**| `SYN-AAD-9012-3456-7890` | `SYN-***-****-****-7890` | Prefix and last 4 characters preserved; inner payload masked. |

---

## 4. Privacy Risk Radar: Mathematical Formulation

### 4.1 Objective
The **Privacy Risk Radar** transforms static discovery into a dynamic risk-prioritization index $R \in [0, 100]$.

### 4.2 Scoring Formula
For each personal data field $i$, the total risk score is the bounded sum of six orthogonal risk components:

$$R_i = \min\left(100, \max\left(0, S(c_i) + K(conf_i) + P(purp_i) + T(ret_i) + V(rev_i) + E(exp_i)\right)\right)$$

### 4.3 Factor Weight Breakdown

| Factor | Notation | Range (pts) | Mathematical Condition & Valuation |
|:---|:---:|:---:|:---|
| **1. Data Sensitivity** | $S(c)$ | 0 – 35 | • `GOVERNMENT_ID`: **35.0 pts** (Statutory identity/KYC risk)<br>• `PHONE_NUMBER`: **25.0 pts** (Direct communication/2FA risk)<br>• `EMAIL`: **25.0 pts** (Primary digital account identifier)<br>• `ADDRESS`: **20.0 pts** (Physical home residency exposure)<br>• `NAME`: **15.0 pts** (Standard identity attribute)<br>• `NOT_PERSONAL`: **0.0 pts** (Non-sensitive) |
| **2. Detection Confidence**| $K(conf)$ | 0 – 15 | Scaled linearly by confidence score: $K = \text{round}(conf \times 15.0, 1)$ |
| **3. Purpose Compliance** | $P(purp)$ | 0 – 20 | • Missing declared purpose: **+20.0 pts** (Violation of Purpose Limitation)<br>• Purpose declared but unapproved: **+10.0 pts** (Pending DPO review)<br>• Approved purpose documented: **0.0 pts** |
| **4. Retention Schedule** | $T(ret)$ | 0 – 15 | • Missing retention schedule: **+15.0 pts** (Storage Limitation risk)<br>• Extended retention schedule ($>365$ days): **+8.0 pts**<br>• Standard retention scheduled ($\le 365$ days): **0.0 pts** |
| **5. Human Review State** | $V(rev)$ | 0 – 15 | • `PENDING_REVIEW`: **+15.0 pts** (Unverified candidate)<br>• `FLAGGED`: **+10.0 pts** (Secondary compliance scrutiny)<br>• `CONFIRMED`: **0.0 pts** (Human verification completed) |
| **6. Multi-Source Exposure**| $E(exp)$ | 0 – 15 | • Class resides across $\ge 3$ independent data sources: **+15.0 pts**<br>• Class resides across $2$ independent data sources: **+10.0 pts**<br>• Single source occurrence: **0.0 pts** |

### 4.4 Priority Tiers
- **Critical Priority (75 – 100):** High-sensitivity fields lacking purpose approval, unreviewed, or showing multi-source exposure.
- **High Priority (55 – 74):** Sensitive identifiers with partial documentation or unverified review status.
- **Medium Priority (35 – 54):** Moderately sensitive fields with documented purposes but extended retention.
- **Low Priority (0 – 34):** Confirmed, purpose-approved fields with compliant retention policies.

---

## 5. Privacy Posture Scorecard: Five-Pillar Governance Index

### 5.1 Institutional Score Formulation
The Privacy Posture Score $S_{\text{posture}} \in [0, 100]$ evaluates institutional compliance maturity across five weighted pillars:

$$S_{\text{posture}} = \sum_{j=1}^{5} W_j \cdot \left(\frac{\text{Numerator}_j}{\text{Denominator}_j}\right)$$

Where $\sum_{j=1}^{5} W_j = 100.0$.

### 5.2 Pillar Breakdown Table

| Pillar Name | Weight ($W_j$) | Denominator | Numerator Definition | Regulatory Rationale |
|:---|:---:|:---|:---|:---|
| **Human Review Coverage** | **25%** | Total Candidate PII Fields | Fields with status `CONFIRMED`, `MODIFIED`, or `REVIEWED` | Eliminates algorithmic uncertainty through verified DPO sign-off. |
| **Purpose Approval Rate** | **25%** | Total Candidate PII Fields | Fields where `has_approved_purpose == True` | Enforces DPDP Section 6 Purpose Limitation principles. |
| **Retention Schedule Coverage** | **20%** | Total Candidate PII Fields | Fields with `is_missing_retention == False` and `days > 0` | Enforces Storage Limitation and timely data disposal. |
| **High-Risk Resolution Rate** | **20%** | Fields categorized as `Critical` or `High` | High/Critical fields reviewed and approved | Measures rapid mitigation of highest legal liabilities. |
| **Evidence & Audit Readiness** | **10%** | Total Candidate PII Fields | Fields with masked samples and regex proof captured | Demonstrable accountability for statutory audits. |

---

## 6. What-If Impact Simulation Engine

The What-If Simulator allows privacy officers to model four proactive governance interventions in isolated memory without touching disk state:
- **Scenario A (Universal Purpose Documentation):** Sets `has_approved_purpose = True` across all unapproved fields.
- **Scenario B (Universal Retention Enforcement):** Enforces a standard 180-day retention schedule across all missing-retention fields.
- **Scenario C (High-Risk DPO Review Clearance):** Simulates completing human verification for all fields in `Critical` and `High` tiers.
- **Scenario D (Data Minimization / Proliferation Elimination):** Clamps cross-source class occurrences to 1 (simulating consolidation).

The engine recalculates $S_{\text{posture}}$, mean risk score, and count of critical findings, displaying positive deltas (e.g., $+24.5\text{ pts}$ Posture Improvement).

---

## 7. Critical Technical Distinctions for Reviewers & Judges

To avoid conflating engineering automation with legal certainty:
1. **Candidate Detection vs. Confirmed PII:** A detected candidate is an algorithmic observation showing syntactic and lexical similarities to personal data. It requires human DPO confirmation to become an officially verified personal data field.
2. **Prioritization Score vs. Legal Risk Assessment:** The Risk Radar score (0–100) is an internal engineering tool to prioritize technical remediation. It does not replace a statutory Data Protection Impact Assessment (DPIA).
3. **Record Match vs. Individual Identity:** Finding a valid email or phone pattern confirms the presence of personal data in that column; it does not deanonymize or authenticate the identity of the specific human subject.
4. **Simulated State vs. Production State:** Outcomes in the What-If Simulator represent mathematical projections. They do not alter metadata, database tables, or remediation states until formally committed by an administrator.
