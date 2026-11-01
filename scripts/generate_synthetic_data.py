#!/usr/bin/env python3
"""
scripts/generate_synthetic_data.py
Deterministic Synthetic Data Generator for PS-019 Privacy Evidence Inventory.

Generates realistic but entirely fictional datasets:
- 3 CSV files (customers.csv, employees.csv, support_tickets.csv)
- 1 SQLite database (privacy_demo.db) with 4 tables (customers, employees, support_tickets, system_logs)
- 1 Labelled ground truth test dataset (labelled_test_data.csv)
- 1 Comprehensive Data Dictionary (data_dictionary.md)

All personal-data fields use synthetic placeholders, example domains, and fictional IDs.
No real personal records are generated or used.
Seed is fixed (42) for 100% deterministic reproducibility.
"""

import os
import csv
import random
import sqlite3
from pathlib import Path

# Fix random seed for determinism
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Fictional name parts
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Shaurya", "Diya", "Saanvi", "Ananya", "Aadhya",
    "Pari", "Chiara", "Riya", "Anvi", "Sneha", "Kavya", "Pooja", "Rohan",
    "Vikram", "Neha", "Rahul", "Priya", "Amit", "Deepak", "Sunita"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Mehta", "Iyer",
    "Reddy", "Nair", "Chopra", "Joshi", "Bose", "Das", "Rao", "Mishra",
    "Kulkarni", "Deshmukh", "Pillai", "Menon", "Bhat", "Saxena", "Agarwal"
]

DOMAINS = ["example.com", "example.org", "example.net", "privacy-test.corp", "sample-mail.test"]

STREETS = [
    "MG Road", "Brigade Road", "Park Street", "Connaught Place", "Marine Drive",
    "Anna Salai", "FC Road", "Gariahat Road", "Banjara Hills Road 12", "Indiranagar 100ft Road"
]

LOCALITIES = [
    "Koramangala", "Bandra West", "Connaught Circus", "Alwarpet", "Salt Lake Sector V",
    "Jubilee Hills", "Shivajinagar", "Viman Nagar", "Indiranagar", "Whitefield"
]

CITIES = [
    ("Bengaluru", "Karnataka", "560001"),
    ("Mumbai", "Maharashtra", "400001"),
    ("New Delhi", "Delhi", "110001"),
    ("Chennai", "Tamil Nadu", "600001"),
    ("Kolkata", "West Bengal", "700001"),
    ("Hyderabad", "Telangana", "500001"),
    ("Pune", "Maharashtra", "411001"),
    ("Ahmedabad", "Gujarat", "380001")
]

DEPARTMENTS = ["Engineering", "Product", "Human Resources", "Finance", "Legal & Compliance", "Operations", "Customer Success"]
JOB_TITLES = ["Software Engineer", "Product Manager", "Data Analyst", "HR Specialist", "Accountant", "Legal Counsel", "Operations Lead"]
TICKET_ISSUES = ["Password Reset", "Billing Discrepancy", "Delivery Delay", "Feature Request", "Account Locked", "Refund Request"]
TICKET_PRIORITIES = ["Low", "Medium", "High", "Critical"]
SYSTEM_MODULES = ["auth_service", "billing_engine", "notification_gateway", "catalog_api", "session_manager"]


def generate_phone(seed_val: int) -> str:
    """Generates synthetic Indian phone numbers in standard formats."""
    fmt = seed_val % 4
    # Fictional Indian 10-digit number starting with 98, 97, 96, 91, or 88
    prefix = random.choice(["98200", "98450", "98100", "97110", "88260", "77380"])
    suffix = f"{random.randint(10000, 99999)}"
    if fmt == 0:
        return f"+91-{prefix[:2]}{prefix[2:]}-{suffix}"
    elif fmt == 1:
        return f"+91 {prefix} {suffix}"
    elif fmt == 2:
        return f"0{prefix}{suffix}"
    else:
        return f"{prefix}{suffix}"


def generate_address(seed_val: int) -> str:
    """Generates synthetic residential / postal addresses."""
    apt_num = random.randint(101, 999)
    bldg = random.choice(["Lotus Enclave", "Green Meadows", "Silver Oak Apartments", "Shanti Heights", "Sai Residency", "Orchid Towers"])
    street = random.choice(STREETS)
    locality = random.choice(LOCALITIES)
    city, state, pin_prefix = random.choice(CITIES)
    pin = f"{pin_prefix[:3]}{random.randint(100, 999)}"
    return f"Flat {apt_num}, {bldg}, {street}, {locality}, {city}, {state} - {pin}"


def generate_synthetic_govt_id(seed_val: int) -> str:
    """Generates clearly synthetic government identification identifiers with explicit test prefixes."""
    id_type = seed_val % 4
    if id_type == 0:
        # Synthetic Aadhaar placeholder (clearly non-real with SYN- prefix)
        return f"SYN-AAD-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    elif id_type == 1:
        # Synthetic PAN placeholder (clearly non-real with SYNPA prefix)
        return f"SYNPA{random.randint(1000, 9999)}{random.choice(['A','B','C','D'])}"
    elif id_type == 2:
        # Synthetic Voter ID placeholder
        return f"SYNVOT{random.randint(1000000, 9999999)}"
    else:
        # Synthetic Driving License / Passport placeholder
        return f"SYN-DL-TEST-{random.randint(10000, 99999)}"


def build_customers_data(n: int = 120):
    rows = []
    for i in range(1, n + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        full_name = f"{fn} {ln}"
        clean_email_name = f"{fn.lower()}.{ln.lower()}{random.randint(10, 99)}"
        email = f"{clean_email_name}@{random.choice(DOMAINS)}"
        phone = generate_phone(i)
        address = generate_address(i)
        govt_id = generate_synthetic_govt_id(i)
        
        # Inject realistic missing values (5-10%)
        if random.random() < 0.08:
            phone = ""
        if random.random() < 0.05:
            address = ""
        if random.random() < 0.12:
            govt_id = ""

        # Ambiguous column: contact_pref_value (either email or a numeric token)
        if random.random() < 0.5:
            contact_ref = f"REF-NOTIFY-{random.randint(1000, 9999)}"
        else:
            contact_ref = email

        rows.append({
            "customer_id": f"CUST-{1000 + i}",
            "full_name": full_name,
            "email_address": email,
            "phone_number": phone,
            "residential_address": address,
            "synthetic_govt_id": govt_id,
            "contact_pref_token": contact_ref,  # Ambiguous / mixed
            "account_status": random.choice(["ACTIVE", "DORMANT", "PENDING_VERIFICATION", "SUSPENDED"]),
            "loyalty_points": random.randint(0, 5000),
            "created_date": f"2025-0{random.randint(1, 9)}-{random.randint(10, 28)}"
        })
    return rows


def build_employees_data(n: int = 80):
    rows = []
    for i in range(1, n + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        employee_name = f"{fn} {ln}"
        work_email = f"{fn.lower()}.{ln.lower()}@privacy-test.corp"
        contact_mobile = generate_phone(i + 500)
        office_postal_address = generate_address(i + 300)
        national_id_synthetic = generate_synthetic_govt_id(i + 200)

        # Ambiguous column: internal_workstation_tag (non-PII machine ID)
        ws_tag = f"WS-IND-{random.randint(100, 999)}-X"

        rows.append({
            "emp_id": f"EMP-{2000 + i}",
            "employee_name": employee_name,
            "work_email": work_email,
            "contact_mobile": contact_mobile,
            "office_postal_address": office_postal_address,
            "national_id_synthetic": national_id_synthetic,
            "internal_workstation_tag": ws_tag,  # Non-PII
            "department": random.choice(DEPARTMENTS),
            "job_title": random.choice(JOB_TITLES),
            "salary_band": f"BAND-{random.choice(['L1', 'L2', 'L3', 'L4', 'L5'])}",
            "joining_date": f"2024-{random.randint(10, 12):02d}-{random.randint(10, 28):02d}"
        })
    return rows


def build_support_tickets_data(n: int = 100):
    rows = []
    for i in range(1, n + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        requester_name = f"{fn} {ln}"
        support_email = f"{fn.lower()}{random.randint(1, 99)}@{random.choice(DOMAINS)}"
        callback_number = generate_phone(i + 800)
        dispatch_address = generate_address(i + 600)
        kyc_synthetic_ref = generate_synthetic_govt_id(i + 700) if random.random() > 0.4 else ""

        # Non-personal columns & edge cases
        ticket_id = f"TCK-{20260000 + i}"
        device_fingerprint = f"sha256:{random.randint(10000000, 99999999):x}{random.randint(10000000, 99999999):x}"
        issue = random.choice(TICKET_ISSUES)
        priority = random.choice(TICKET_PRIORITIES)
        res_hours = random.choice([2.5, 4.0, 12.0, 24.5, 48.0])

        rows.append({
            "ticket_id": ticket_id,
            "requester_name": requester_name,
            "support_email": support_email,
            "callback_number": callback_number,
            "dispatch_address": dispatch_address,
            "kyc_synthetic_ref": kyc_synthetic_ref,
            "device_fingerprint": device_fingerprint,  # Non-PII hash
            "issue_category": issue,
            "ticket_priority": priority,
            "resolution_time_hrs": res_hours,
            "is_escalated": random.choice([0, 1])
        })
    return rows


def build_system_logs_data(n: int = 150):
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "log_id": f"LOG-{50000 + i}",
            "timestamp": f"2026-10-31T{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z",
            "log_level": random.choice(["INFO", "WARN", "DEBUG", "ERROR"]),
            "service_name": random.choice(SYSTEM_MODULES),
            "status_code": random.choice([200, 200, 200, 201, 400, 401, 404, 500]),
            "latency_ms": random.randint(15, 850),
            "request_path": random.choice(["/api/v1/auth", "/api/v1/status", "/healthz", "/metrics", "/api/v1/checkout"])
        })
    return rows


def write_csv(filepath: Path, rows: list):
    """Safely writes rows to CSV with standard header."""
    if not rows:
        return
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def write_sqlite(db_path: Path, tables_dict: dict):
    """Safely creates SQLite database with multiple structured tables."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for table_name, rows in tables_dict.items():
        if not rows:
            continue
        cols = list(rows[0].keys())
        col_defs = ", ".join([f'"{col}" TEXT' for col in cols])
        cur.execute(f'CREATE TABLE "{table_name}" ({col_defs});')

        placeholders = ", ".join(["?"] * len(cols))
        insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders});'
        values_list = [[row[c] for c in cols] for row in rows]
        cur.executemany(insert_sql, values_list)

    conn.commit()
    conn.close()


def generate_labelled_test_dataset(data_dir: Path):
    """
    Creates labelled_test_data.csv for evaluation.
    Each row represents a specific column from a source (CSV or SQLite table),
    giving the ground truth class (NAME, EMAIL, PHONE_NUMBER, ADDRESS, GOVERNMENT_ID, or NOT_PERSONAL).
    """
    ground_truth = [
        # customers.csv
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "customer_id", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Customer primary key identifier"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "full_name", "true_class": "NAME", "is_personal": 1, "description": "Full customer legal/display name"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "email_address", "true_class": "EMAIL", "is_personal": 1, "description": "Primary email contact address"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "phone_number", "true_class": "PHONE_NUMBER", "is_personal": 1, "description": "Customer mobile phone number"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "residential_address", "true_class": "ADDRESS", "is_personal": 1, "description": "Customer residential mailing address"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "synthetic_govt_id", "true_class": "GOVERNMENT_ID", "is_personal": 1, "description": "Synthetic government identity proof placeholder"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "contact_pref_token", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Ambiguous mixed column containing system tokens or partial strings"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "account_status", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Account status flag"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "loyalty_points", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Numeric loyalty rewards balance"},
        {"source_type": "csv", "source_name": "customers.csv", "table_name": "", "column_name": "created_date", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Account registration timestamp"},

        # employees.csv
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "emp_id", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Employee organizational ID"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "employee_name", "true_class": "NAME", "is_personal": 1, "description": "Employee full name"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "work_email", "true_class": "EMAIL", "is_personal": 1, "description": "Corporate email address"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "contact_mobile", "true_class": "PHONE_NUMBER", "is_personal": 1, "description": "Official employee telephone contact"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "office_postal_address", "true_class": "ADDRESS", "is_personal": 1, "description": "Assigned office physical address"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "national_id_synthetic", "true_class": "GOVERNMENT_ID", "is_personal": 1, "description": "Synthetic national ID placeholder for HR file"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "internal_workstation_tag", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Hardware inventory asset tag"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "department", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Corporate department"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "job_title", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Job designation"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "salary_band", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Compensation grade band"},
        {"source_type": "csv", "source_name": "employees.csv", "table_name": "", "column_name": "joining_date", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Date of joining"},

        # support_tickets.csv
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "ticket_id", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Helpdesk ticket identifier"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "requester_name", "true_class": "NAME", "is_personal": 1, "description": "Customer requester full name"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "support_email", "true_class": "EMAIL", "is_personal": 1, "description": "Contact email provided in support ticket"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "callback_number", "true_class": "PHONE_NUMBER", "is_personal": 1, "description": "Phone number for escalation callbacks"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "dispatch_address", "true_class": "ADDRESS", "is_personal": 1, "description": "Physical dispatch or replacement address"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "kyc_synthetic_ref", "true_class": "GOVERNMENT_ID", "is_personal": 1, "description": "Synthetic verification document ID reference"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "device_fingerprint", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Cryptographic hash of client device"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "issue_category", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Support category classification"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "ticket_priority", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Support priority tier"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "resolution_time_hrs", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Duration to resolve issue in hours"},
        {"source_type": "csv", "source_name": "support_tickets.csv", "table_name": "", "column_name": "is_escalated", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Escalation status flag"},

        # privacy_demo.db -> system_logs (pure non-PII control table)
        {"source_type": "sqlite", "source_name": "privacy_demo.db", "table_name": "system_logs", "column_name": "log_id", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Log entry identifier"},
        {"source_type": "sqlite", "source_name": "privacy_demo.db", "table_name": "system_logs", "column_name": "timestamp", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Log timestamp"},
        {"source_type": "sqlite", "source_name": "privacy_demo.db", "table_name": "system_logs", "column_name": "log_level", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Severity level"},
        {"source_type": "sqlite", "source_name": "privacy_demo.db", "table_name": "system_logs", "column_name": "service_name", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Microservice identifier"},
        {"source_type": "sqlite", "source_name": "privacy_demo.db", "table_name": "system_logs", "column_name": "status_code", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "HTTP response code"},
        {"source_type": "sqlite", "source_name": "privacy_demo.db", "table_name": "system_logs", "column_name": "latency_ms", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "Roundtrip execution latency in ms"},
        {"source_type": "sqlite", "source_name": "privacy_demo.db", "table_name": "system_logs", "column_name": "request_path", "true_class": "NOT_PERSONAL", "is_personal": 0, "description": "API route path"}
    ]

    out_file = data_dir / "labelled_test_data.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ground_truth[0].keys())
        writer.writeheader()
        writer.writerows(ground_truth)
    print(f"Generated ground truth labelled test dataset: {out_file} ({len(ground_truth)} columns)")


def generate_data_dictionary(data_dir: Path):
    """Writes a comprehensive Data Dictionary documentation file."""
    dict_content = """# Data Dictionary: Synthetic Datasets for PS-019 Privacy Evidence Inventory

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
"""
    out_file = data_dir / "data_dictionary.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(dict_content)
    print(f"Generated Data Dictionary: {out_file}")


def main():
    print(f"Initializing synthetic data generation with seed={RANDOM_SEED}...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate data rows
    customers = build_customers_data(120)
    employees = build_employees_data(80)
    tickets = build_support_tickets_data(100)
    logs = build_system_logs_data(150)

    # 2. Write CSV files
    write_csv(DATA_DIR / "customers.csv", customers)
    write_csv(DATA_DIR / "employees.csv", employees)
    write_csv(DATA_DIR / "support_tickets.csv", tickets)
    print(f"Generated CSV files in {DATA_DIR}: customers.csv (120 rows), employees.csv (80 rows), support_tickets.csv (100 rows)")

    # 3. Write SQLite database
    sqlite_db_path = DATA_DIR / "privacy_demo.db"
    write_sqlite(sqlite_db_path, {
        "customers": customers,
        "employees": employees,
        "support_tickets": tickets,
        "system_logs": logs
    })
    print(f"Generated SQLite database at {sqlite_db_path} with 4 tables.")

    # 4. Generate labelled test dataset
    generate_labelled_test_dataset(DATA_DIR)

    # 5. Generate data dictionary
    generate_data_dictionary(DATA_DIR)

    print("Synthetic data generation completed successfully!")


if __name__ == "__main__":
    main()
