# Data Dictionary: Synthetic Datasets for PS-019 Privacy Evidence Inventory

This data dictionary outlines the schema, synthetic design rationale, and ground-truth personal-data classifications for all test files generated for **PS-019 (Personal-Data Discovery and Privacy Evidence Inventory)**.

> **Safety Notice:** All datasets are synthetically generated using deterministic seeds. All email domains use IETF reserved test domains (`example.com`, `example.org`, `corp.test`), phone numbers are synthetic, physical addresses are fictitious, and government IDs use explicitly labelled prefixes (`SYN-AAD-`, `SYNPA-`, `SYNVOT-`). No real personal records exist in this repository.

---

## 1. Datasets Overview

| Dataset / Table Name | Source Type | Row Count | Personal Fields | Non-Personal Fields |
|:---|:---|:---:|:---:|:---:|
| `customers.csv` | CSV File | 120 | 5 | 5 |
| `employees.csv` | CSV File | 80 | 5 | 6 |
| `support_tickets.csv` | CSV File | 100 | 5 | 6 |
| `privacy_demo.db` (`customers`) | SQLite Table | 120 | 5 | 5 |
| `privacy_demo.db` (`employees`) | SQLite Table | 80 | 5 | 6 |
| `privacy_demo.db` (`support_tickets`) | SQLite Table | 100 | 5 | 6 |
| `privacy_demo.db` (`system_logs`) | SQLite Table | 150 | 0 | 7 |
| `labelled_test_data.csv` | Ground Truth Benchmark | 38 columns | 15 PII | 23 Non-PII |

---

## 2. Five Predefined Personal-Data Classes

1. **`NAME`**: Individual legal or common names (e.g. `full_name`, `employee_name`, `requester_name`).
2. **`EMAIL`**: Electronic mail addresses conforming to RFC standards (e.g. `email_address`, `work_email`, `support_email`).
3. **`PHONE_NUMBER`**: Fixed-line or mobile telephony numbers in Indian telephone format (e.g. `phone_number`, `contact_mobile`, `callback_number`).
4. **`ADDRESS`**: Residential, office, or dispatch physical postal addresses containing street, locality, city, state, and pin code.
5. **`GOVERNMENT_ID`**: Synthetic identity tokens representing statutory identifiers (Aadhaar, PAN, Voter ID, Driving License) prefixed with synthetic markers.

---

## 3. Detailed Column Specification

### 3.1 `customers.csv` / `customers` table
- `customer_id` (`NOT_PERSONAL`): Unique customer identifier token (`CUST-1001`).
- `full_name` (`NAME`): Customer's full name.
- `email_address` (`EMAIL`): Electronic mail address.
- `phone_number` (`PHONE_NUMBER`): Contact mobile number in Indian formats.
- `residential_address` (`ADDRESS`): Street and postal residential address.
- `synthetic_govt_id` (`GOVERNMENT_ID`): Synthetic statutory ID marker (`SYN-AAD-xxxx` or `SYNPAxxxx`).
- `contact_pref_token` (`NOT_PERSONAL` - Ambiguous): Mixed column containing either system notification tokens or email strings to test scanner discrimination.
- `account_status` (`NOT_PERSONAL`): Categorical status (`ACTIVE`, `DORMANT`, etc.).
- `loyalty_points` (`NOT_PERSONAL`): Numeric reward balance.
- `created_date` (`NOT_PERSONAL`): Date of customer record creation.

### 3.2 `employees.csv` / `employees` table
- `emp_id` (`NOT_PERSONAL`): Enterprise worker ID (`EMP-2001`).
- `employee_name` (`NAME`): Staff full name.
- `work_email` (`EMAIL`): Corporate email address.
- `contact_mobile` (`PHONE_NUMBER`): Official mobile contact.
- `office_postal_address` (`ADDRESS`): Facility location postal address.
- `national_id_synthetic` (`GOVERNMENT_ID`): Synthetic national identification document.
- `internal_workstation_tag` (`NOT_PERSONAL`): IT asset tag (`WS-IND-xxx-X`).
- `department` (`NOT_PERSONAL`): Business unit name.
- `job_title` (`NOT_PERSONAL`): Role designation.
- `salary_band` (`NOT_PERSONAL`): Internal compensation level.
- `joining_date` (`NOT_PERSONAL`): Date of employment inception.

### 3.3 `support_tickets.csv` / `support_tickets` table
- `ticket_id` (`NOT_PERSONAL`): Customer service ticket number (`TCK-2026xxxx`).
- `requester_name` (`NAME`): Requester's name.
- `support_email` (`EMAIL`): Contact email associated with the inquiry.
- `callback_number` (`PHONE_NUMBER`): Customer telephone for voice follow-up.
- `dispatch_address` (`ADDRESS`): Physical dispatch location for hardware replacements.
- `kyc_synthetic_ref` (`GOVERNMENT_ID`): Synthetic verification proof identifier.
- `device_fingerprint` (`NOT_PERSONAL`): SHA-256 cryptographic device hash.
- `issue_category` (`NOT_PERSONAL`): Classification of ticket subject.
- `ticket_priority` (`NOT_PERSONAL`): Urgency classification (`Low`, `Medium`, `High`, `Critical`).
- `resolution_time_hrs` (`NOT_PERSONAL`): Floating-point number of hours to resolution.
- `is_escalated` (`NOT_PERSONAL`): Binary escalation flag (`0` or `1`).

### 3.4 `system_logs` table (SQLite Control)
- `log_id` (`NOT_PERSONAL`): Diagnostic record key (`LOG-50001`).
- `timestamp` (`NOT_PERSONAL`): ISO UTC event timestamp.
- `log_level` (`NOT_PERSONAL`): Log severity level (`INFO`, `WARN`, `ERROR`, `DEBUG`).
- `service_name` (`NOT_PERSONAL`): Backend microservice name.
- `status_code` (`NOT_PERSONAL`): HTTP status code (200, 404, 500).
- `latency_ms` (`NOT_PERSONAL`): Server processing latency in milliseconds.
- `request_path` (`NOT_PERSONAL`): HTTP endpoint URI.
