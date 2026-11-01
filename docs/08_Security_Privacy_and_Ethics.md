# 08. Security, Privacy, and Ethical Considerations
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Guiding Framework:** India Digital Personal Data Protection (DPDP) Act 2023 & MeitY Guidelines  

---

## 1. Threat Modeling & Data Protection Principles

Privacy discovery tools operate in sensitive environments where they ingest, analyze, and catalog an organization's most critical data assets. If poorly architected, a privacy scanner can itself become a vector for data leakage.

The **Privacy Intelligence Engine** was engineered from inception around a zero-trust, local-only architecture designed to enforce three foundational privacy engineering tenets:
1. **Confidentiality by Local Isolation:** Zero cloud dependencies, zero external API calls, and zero external telemetry transmission.
2. **Integrity by Read-Only Access:** Ingestion connectors strictly enforce read-only connections, ensuring source databases and files remain immutable.
3. **Minimization by Masking & Bounded Sampling:** Only small bounded row samples (max 100 rows) are inspected in volatile memory, and all values are masked prior to display or persistence.

---

## 2. Personal Data Handling & Processing Profile

### 2.1 Types of Personal Data Encountered
The system is designed to identify five categories of personal data:
- **Direct Identifiers:** Full names (`NAME`), personal/work email addresses (`EMAIL`), and mobile numbers (`PHONE_NUMBER`).
- **Physical Identifiers:** Postal and residential home addresses (`ADDRESS`).
- **Statutory National Identifiers:** National identification numbers (`GOVERNMENT_ID`). In production, this includes Aadhaar, PAN, and Voter ID numbers.

### 2.2 Volatile In-Memory Processing
- Data files and database tables are read into transient Pandas DataFrames in local process memory.
- Column data is sampled (first 100 non-null values) to compute statistical metrics and pattern frequencies.
- Raw values are immediately discarded from memory once regex matching concludes; only masked strings (`j***@example.com`, `M*** M***`, `+91-*****-***10`) and aggregate metrics are retained.

---

## 3. Data Masking and Exposure Mitigation

### 3.1 Display Masking Architecture
Under no circumstances does raw, unmasked personal data appear in the Streamlit user interface, application error dialogs, or exported compliance reports.

```
[Raw Ingested Value] ──> [PersonalDataDetector.mask_value()] ──> [Masked Token]
                                                                        │
                         ┌──────────────────────────────────────────────┴──────────────────────────┐
                         ▼                                              ▼                          ▼
               [Streamlit Web UI]                           [reports/inventory.csv]     [reports/inventory.json]
```

- **Emails:** Truncated local parts retaining only the first and last characters and domain (`a***n@example.com`).
- **Phone Numbers:** Intermediate digits suppressed, retaining only country code and terminal 2 digits (`+91-*****-***10`).
- **Names:** First initials preserved, remaining alphabetic characters masked (`A*** S***`).
- **Addresses:** Street and locality obscured, retaining only numeric building prefixes (`42 P***... [Masked Address]`).
- **Government IDs:** Statutory prefixes and checksum digits preserved, core credential payload redacted (`SYN-***-****-****-7890`).

### 3.2 Audit Export Sanitization
Exported compliance files (`reports/privacy_evidence_inventory.csv`, `reports/privacy_evidence_inventory.json`, `reports/privacy_audit_report.md`) contain only:
1. Source repository identifier and column name.
2. Detected class and heuristic confidence score.
3. Masked sample representations.
4. Linked purpose and retention metadata.
5. Calculated risk score and priority tier.

Raw data samples are **never serialized** to disk.

---

## 4. Input Validation & Fault Injection Safeguards

### 4.1 Read-Only Database Connections
SQLite databases are opened exclusively using Python's URI protocol with read-only flags:
```python
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
```
- Write transactions, `DROP TABLE`, `UPDATE`, or `DELETE` statements are physically rejected by the SQLite engine at the C-library level.
- Table and column discovery utilizes standard catalog queries (`SELECT name FROM sqlite_master WHERE type='table'`) and `PRAGMA table_info()`, preventing SQL injection vulnerabilities.

### 4.2 Malicious / Malformed File Ingestion
- **Row-Count Bounding:** To prevent Denial-of-Service (DoS) via memory exhaustion when ingesting multi-gigabyte CSV files, `CSVScanner` utilizes chunked or row-limited ingestion (`nrows=100`).
- **Encoding Attacks:** Fallback mechanisms catch decoding traps (e.g., unexpected UTF-16, malformed byte sequences) and degrade gracefully to ISO-8859-1 without throwing unhandled exceptions.

---

## 5. Secret, Credential, and Access Management

- **Zero Hardcoded Secrets:** The application contains zero API keys, cloud secrets, AWS/Azure credentials, or hardcoded passwords.
- **Local Single-User Architecture:** In its current form, the application runs locally on the user's desktop (`localhost:8501`). There is no multi-tenant session isolation or external authentication gateway.
- **Role Differentiation:** While four operational roles (DPO, Privacy Engineer, DBA, Auditor) are defined in the governance model, role enforcement in the current release relies on desktop-level access controls.

---

## 6. Synthetic Data Boundaries & Ethical Guidelines

### 6.1 Strict Use of Synthetic Test Data
In accordance with ethical AI research practices and data protection laws:
- All datasets included in this repository (`customers.csv`, `employees.csv`, `support_tickets.csv`, `privacy_demo.db`, `labelled_test_data.csv`) were generated using pseudorandom algorithms with fixed seeds (`SEED=42`).
- Names, emails, and phone numbers are completely fictional.
- Government IDs feature explicit synthetic markers (`SYN-AAD-`, `SYNPA`, `SYNVOT`, `TEST-DL-`) to guarantee they cannot be confused with live statutory identity credentials.

### 6.2 Prohibited Use Cases
- **No Deanonymization:** The system must not be used to cross-reference anonymized datasets with intent to re-identify living individuals.
- **No Unconsented Surveillance:** The scanner is intended for enterprise data governance and internal security auditing; it must not be deployed for unauthorized surveillance of employee communications.

---

## 7. Recommended Production Hardening Roadmap

Before deploying the Privacy Intelligence Engine into a high-assurance production environment, the following enterprise hardening measures are recommended:

1. **Role-Based Access Control (RBAC):** Integrate Streamlit with an enterprise OpenID Connect (OIDC) or SAML 2.0 provider (e.g., Azure AD, Okta) to authenticate DPO and DBA personas.
2. **Transport Layer Security (TLS):** Place the Streamlit web application behind an enterprise reverse proxy (Nginx, Traefik) terminating TLS 1.3 with valid institutional certificates.
3. **Database Audit Logging:** Configure cryptographic append-only audit logging for all human review decisions and remediation status updates.
4. **Hardware Security Module (HSM) / KMS Integration:** If encrypted databases or files are scanned, cryptographic keys should be retrieved from an enterprise Key Management Service (AWS KMS, HashiCorp Vault) rather than local config files.
5. **Human-in-the-Loop Safeguards:** Ensure organizational policy mandates human DPO sign-off for any data purge or masking action recommended by the Remediation Center.
