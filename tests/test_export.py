"""
tests/test_export.py
Unit tests for ReportGenerator, exports, and masking verification.
"""

import json
import pytest
from scanner.report_generator import ReportGenerator


@pytest.fixture
def sample_inventory():
    return [
        {
            "field_key": "customers.csv::::email_address",
            "source_name": "customers.csv",
            "table_name": "",
            "column_name": "email_address",
            "detected_class": "EMAIL",
            "confirmed_class": "EMAIL",
            "is_personal": True,
            "confidence_score": 0.95,
            "declared_purpose": "Account notifications",
            "retention_days": 365,
            "retention_label": "365 days",
            "has_approved_purpose": True,
            "is_missing_purpose": False,
            "is_missing_retention": False,
            "review_status": "CONFIRMED",
            "reviewer_notes": "Approved for DPDP compliance",
            "reviewed_by": "Compliance Officer",
            "reviewed_at": "2026-10-31T12:00:00Z",
            "masked_samples": "a***n@example.com",
            "evidence_details": "Header match and 100% regex match"
        }
    ]


def test_export_inventory_csv(sample_inventory):
    csv_str = ReportGenerator.export_inventory_csv(sample_inventory)
    assert "email_address" in csv_str
    assert "Account notifications" in csv_str
    assert "CONFIRMED" in csv_str
    # Verify header row exists
    assert "field_key,source_name" in csv_str


def test_export_inventory_json(sample_inventory):
    json_str = ReportGenerator.export_inventory_json(sample_inventory)
    data = json.loads(json_str)
    assert data["total_inventory_fields"] == 1
    assert data["inventory"][0]["column_name"] == "email_address"


def test_export_evaluation_metrics_csv():
    mock_eval = {
        "macro_precision": 0.98,
        "macro_recall": 0.95,
        "macro_f1": 0.96,
        "per_class_metrics": {
            "EMAIL": {
                "precision": 1.0,
                "recall": 1.0,
                "f1_score": 1.0,
                "support": 3,
                "predicted_count": 3,
                "true_positives": 3,
                "false_positives": 0,
                "false_negatives": 0,
                "status_note": ""
            }
        }
    }
    csv_str = ReportGenerator.export_evaluation_metrics_csv(mock_eval)
    assert "EMAIL" in csv_str
    assert "MACRO_AVERAGE" in csv_str


def test_generate_audit_report_markdown(sample_inventory):
    md = ReportGenerator.generate_audit_report_markdown(sample_inventory)
    assert "# Personal-Data Discovery & Privacy Evidence Inventory" in md
    assert "Executive Summary" in md
    assert "customers.csv" in md
