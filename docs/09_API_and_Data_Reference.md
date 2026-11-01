# 09. API and Data Reference Specification
**Project:** PS-019 Privacy Intelligence Engine  
**Team ID:** Team A3-PS019-TC316  
**Interface Type:** Internal Modular Python Class Library & Structured File Schemas  

---

## 1. Interface Architecture Overview

> [!NOTE]
> **No Public REST / HTTP API:** The Privacy Intelligence Engine is designed as an interactive, local Streamlit web application. It does not expose external public HTTP/REST endpoints. All functional operations are driven via modular, decoupled Python class interfaces and structured local configuration files.

---

## 2. Internal Python Class APIs (`scanner/`)

### 2.1 `PersonalDataDetector` (`scanner/detection.py`)
Encapsulates regex pattern matching, header heuristics, sample diversity analysis, and sample masking.

```python
class PersonalDataDetector:
    HEADER_PATTERNS: Dict[str, Pattern]
    VALUE_PATTERNS: Dict[str, Pattern]
    NEGATIVE_NAME_HEADERS: Pattern

    @classmethod
    def evaluate_column(
        cls,
        column_name: str,
        sample_values: List[Any],
        source_name: str = "",
        table_name: str = ""
    ) -> DetectionResult:
        """
        Evaluates a column's name and sampled values.
        Returns a DetectionResult dataclass instance containing detected_class,
        confidence_score, sample match statistics, and masked samples.
        """

    @classmethod
    def mask_value(cls, value: str, pii_class: str) -> str:
        """
        Masks a raw sensitive string value based on its PII category.
        """
```

#### Dataclass: `DetectionResult`
| Field | Type | Description |
|:---|:---|:---|
| `source_name` | `str` | Name of the source file or database. |
| `table_name` | `str` | Database table name (empty string for CSV). |
| `column_name` | `str` | Physical column identifier. |
| `detected_class` | `Optional[str]` | Detected class (`NAME`, `EMAIL`, `PHONE_NUMBER`, `ADDRESS`, `GOVERNMENT_ID`, or `None`). |
| `is_personal` | `bool` | Boolean flag indicating whether personal data was detected. |
| `confidence_score` | `float` | Heuristic confidence metric in $[0.0, 1.0]$. |
| `sample_count` | `int` | Total rows evaluated. |
| `matching_sample_count`| `int` | Count of rows matching value regex. |
| `sample_match_rate` | `float` | Fraction of non-null samples matching pattern. |
| `masked_samples` | `List[str]` | Obfuscated sample tokens for safe display. |

---

### 2.2 `CSVScanner` (`scanner/csv_scanner.py`)
Handles safe, bounded-sampling ingestion of delimited CSV files.

```python
class CSVScanner:
    def __init__(self, data_dir: Optional[Path] = None, max_sample_rows: int = 100): ...
    
    def scan_file(self, file_path: Path) -> List[DetectionResult]:
        """Samples up to max_sample_rows per column and executes detection."""

    def scan_directory(self, dir_path: Optional[Path] = None) -> List[DetectionResult]:
        """Scans all CSV files discovered within target directory."""
```

---

### 2.3 `SQLiteScanner` (`scanner/sqlite_scanner.py`)
Handles safe, read-only introspection of SQLite database schemas.

```python
class SQLiteScanner:
    def __init__(self, db_path: Path, max_sample_rows: int = 100): ...

    def discover_tables(self) -> List[str]:
        """Queries sqlite_master to enumerate non-system tables."""

    def scan_database(self) -> List[DetectionResult]:
        """Samples tables with mode=ro and evaluates all columns."""

    def get_table_sample(self, table_name: str, limit: int = 10) -> pd.DataFrame:
        """Returns small preview DataFrame for UI display."""
```

---

### 2.4 `MetadataManager` (`scanner/metadata_manager.py`)
Manages organizational purpose policies, retention periods, and human verification records.

```python
class MetadataManager:
    def __init__(self, config_path: Optional[Path] = None): ...

    def enrich_inventory(self, raw_detections: List[DetectionResult]) -> List[Dict[str, Any]]:
        """Links detected fields to declared purpose, retention days, and review status."""

    def record_reviewer_decision(
        self,
        source_name: str,
        column_name: str,
        table_name: str,
        review_status: str,
        confirmed_class: Optional[str] = None,
        notes: str = ""
    ) -> bool:
        """Updates review status and persists atomically to config/metadata.json."""
```

---

### 2.5 `PrivacyRiskRadar` (`scanner/risk_radar.py`)
Calculates explainable 0–100 risk scores across 6 weighted factors.

```python
class PrivacyRiskRadar:
    CLASS_SENSITIVITY_WEIGHTS: Dict[str, float]
    PRIORITY_THRESHOLDS: List[Tuple[int, str]]

    def calculate_field_risk(
        self,
        field_data: Dict[str, Any],
        cross_source_class_counts: Optional[Dict[str, int]] = None
    ) -> RiskEvaluation:
        """Calculates bounded score [0, 100], priority tier, and factor breakdown."""

    def evaluate_inventory(self, enriched_inventory: List[Dict[str, Any]]) -> List[RiskEvaluation]:
        """Evaluates all fields in inventory and sorts descending by risk score."""
```

---

### 2.6 `PrivacyPostureScorecard` (`scanner/posture_scorecard.py`)
Calculates the 5-pillar composite governance score and runs What-If simulations.

```python
class PrivacyPostureScorecard:
    WEIGHTS: Dict[str, float]

    @classmethod
    def calculate_scorecard(
        cls,
        enriched_inventory: List[Dict[str, Any]],
        risk_evaluations: Optional[List[RiskEvaluation]] = None
    ) -> Dict[str, Any]:
        """Returns overall score (0-100), tier, pillar details, and top improvement areas."""

    @classmethod
    def simulate_what_if(
        cls,
        enriched_inventory: List[Dict[str, Any]],
        scenario_flags: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Simulates compliance improvements in volatile memory."""
```

---

### 2.7 `RemediationEngine` (`scanner/remediation_engine.py`)
Generates actionable remediation tasks and manages lifecycle states.

```python
class RemediationEngine:
    def generate_recommendations(
        self,
        enriched_inventory: List[Dict[str, Any]],
        risk_evaluations: Optional[List[RiskEvaluation]] = None
    ) -> List[RemediationTask]:
        """Generates prioritized tasks matching compliance deficits."""

    def update_task_status(
        self,
        task_id: str,
        status: str,
        reviewer_notes: str = ""
    ) -> bool:
        """Updates task state (Open, In Progress, Resolved) and persists to disk."""
```

---

## 3. Database Schema Reference (`data/privacy_demo.db`)

The SQLite database `privacy_demo.db` contains three tables representing enterprise workloads:

### Table 1: `customer_accounts`
| Column Name | SQLite Data Type | Primary Key | Description & Classification |
|:---|:---|:---:|:---|
| `account_id` | `INTEGER` | YES | Auto-increment internal account identifier (`NOT_PERSONAL`). |
| `full_name` | `TEXT` | NO | Customer full name (`NAME`). |
| `primary_email` | `TEXT` | NO | Primary contact email address (`EMAIL`). |
| `mobile_number` | `TEXT` | NO | Contact telephone number (`PHONE_NUMBER`). |
| `kyc_synthetic_ref` | `TEXT` | NO | Synthetic Aadhaar/KYC identity marker (`GOVERNMENT_ID`). |

### Table 2: `internal_staff`
| Column Name | SQLite Data Type | Primary Key | Description & Classification |
|:---|:---|:---:|:---|
| `employee_id` | `INTEGER` | YES | Internal staff identifier (`NOT_PERSONAL`). |
| `employee_name`| `TEXT` | NO | Staff member legal name (`NAME`). |
| `work_email` | `TEXT` | NO | Enterprise corporate email (`EMAIL`). |
| `department_name` | `TEXT` | NO | Department assignment (`NOT_PERSONAL`). |
| `monthly_salary`| `REAL` | NO | Financial compensation figure (`NOT_PERSONAL`). |

### Table 3: `system_logs`
| Column Name | SQLite Data Type | Primary Key | Description & Classification |
|:---|:---|:---:|:---|
| `log_id` | `INTEGER` | YES | Sequential log transaction ID (`NOT_PERSONAL`). |
| `timestamp` | `TEXT` | NO | ISO-8601 transaction event timestamp (`NOT_PERSONAL`). |
| `log_level` | `TEXT` | NO | Severity level: `INFO`, `WARN`, `ERROR` (`NOT_PERSONAL`). |
| `service_name` | `TEXT` | NO | Microservice origin identifier (`NOT_PERSONAL`). |
| `status_code` | `INTEGER` | NO | HTTP response status code (`NOT_PERSONAL`). |
| `latency_ms` | `REAL` | NO | Endpoint round-trip latency in milliseconds (`NOT_PERSONAL`). |
| `request_path` | `TEXT` | NO | Internal API endpoint route (`NOT_PERSONAL`). |

---

## 4. Configuration File Schemas (`config/`)

### 4.1 Metadata Policy Store: `config/metadata.json`
```json
{
  "declared_purposes": {
    "customers.csv::email_address": {
      "purpose_code": "PURP_COMM",
      "purpose_name": "Customer Communication & Support",
      "is_approved": true,
      "approved_by": "DPO_OFFICE",
      "retention_days": 180
    }
  },
  "reviewer_decisions": {
    "customers.csv::phone_number": {
      "review_status": "CONFIRMED",
      "confirmed_class": "PHONE_NUMBER",
      "reviewer_notes": "Verified customer callback contact",
      "reviewed_at": "2026-10-31T15:30:00Z"
    }
  }
}
```

### 4.2 Remediation Task Store: `config/remediations.json`
```json
{
  "TASK-CUST-GOVT-001": {
    "recommendation_id": "TASK-CUST-GOVT-001",
    "finding_id": "customers.csv::synthetic_govt_id",
    "source_name": "customers.csv",
    "column_name": "synthetic_govt_id",
    "confirmed_class": "GOVERNMENT_ID",
    "risk_level": "Critical",
    "title": "Formalize Declared Purpose for Statutory Identifier",
    "reason": "Synthetic government ID detected without approved purpose policy.",
    "suggested_action": "Execute formal DPIA review and record lawful basis.",
    "expected_benefit": "Reduces field risk score by 20 points.",
    "status": "Open",
    "reviewer_notes": "",
    "created_at": "2026-10-31T12:00:00Z",
    "updated_at": "2026-10-31T12:00:00Z"
  }
}
```

---

## 5. Export Specifications (`reports/`)

| File Path | Format | Primary Headers / Structure | Purpose |
|:---|:---:|:---|:---|
| `reports/privacy_evidence_inventory.csv` | CSV | `source_name`, `table_name`, `column_name`, `detected_class`, `confidence_score`, `masked_samples`, `declared_purpose`, `retention_days`, `review_status`, `risk_score`, `priority_level` | Tabular compliance audit evidence. |
| `reports/privacy_evidence_inventory.json` | JSON | Root array of enriched field dictionaries with nested `factor_breakdown` and `evidence_details`. | System-to-system integration and ingestion into GRC platforms. |
| `reports/evaluation_benchmark.csv` | CSV | `class_name`, `precision`, `recall`, `f1_score`, `support`, `true_positives`, `false_positives`, `false_negatives` | Proof of algorithmic accuracy and benchmark performance. |
| `reports/privacy_audit_report.md` | Markdown | Formatted compliance document with Executive Summary, Posture Scorecard, Top Liabilities, and Recommendations. | Formal executive and statutory filing under DPDP Act. |
