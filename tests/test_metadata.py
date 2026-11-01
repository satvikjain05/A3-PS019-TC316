"""
tests/test_metadata.py
Unit tests for MetadataManager, compliance linking, and reviewer persistence.
"""

import pytest
from pathlib import Path
from scanner.metadata_manager import MetadataManager
from scanner.detection import DetectionResult


@pytest.fixture
def temp_metadata(tmp_path):
    cfg_file = tmp_path / "metadata_test.json"
    mgr = MetadataManager(config_path=cfg_file)
    return mgr


def test_default_policies_exist(temp_metadata):
    pol_email = temp_metadata.get_default_policy_for_class("EMAIL")
    assert pol_email["retention_days"] == 365
    assert "Account communication" in pol_email["purpose"]
    assert pol_email["is_approved"] is False  # Never assume approved by default

    pol_govt = temp_metadata.get_default_policy_for_class("GOVERNMENT_ID")
    assert pol_govt["retention_days"] == 30
    assert "KYC" in pol_govt["purpose"]


def test_enrich_detection_flags_missing_approval(temp_metadata):
    detection = DetectionResult(
        source_name="customers.csv",
        table_name="",
        column_name="email_address",
        detected_class="EMAIL",
        is_personal=True,
        confidence_score=0.95,
        header_matched="email_address",
        sample_count=50,
        non_null_count=50,
        matching_sample_count=50,
        sample_match_rate=1.0,
        masked_samples=["a***n@example.com"],
        evidence_details="Header and value match"
    )

    enriched = temp_metadata.enrich_detection(detection)
    assert enriched["has_approved_purpose"] is False
    assert enriched["review_status"] == "PENDING_REVIEW"
    assert enriched["retention_days"] == 365
    assert enriched["is_missing_purpose"] is False
    assert enriched["is_missing_retention"] is False


def test_record_reviewer_decision_persistence(tmp_path):
    cfg_file = tmp_path / "metadata_persist.json"
    mgr1 = MetadataManager(config_path=cfg_file)

    field_key = "customers.csv::::email_address"
    mgr1.record_review_decision(
        field_key=field_key,
        confirmed_class="EMAIL",
        review_status="CONFIRMED",
        declared_purpose="Newsletter dispatch and transactional alerts",
        retention_days=180,
        has_approved_purpose=True,
        is_missing_purpose=False,
        is_missing_retention=False,
        reviewer_notes="Approved per Privacy Committee Review #104",
        reviewer_name="Data Protection Officer"
    )

    # Re-instantiate from disk to verify persistence
    mgr2 = MetadataManager(config_path=cfg_file)
    decisions = mgr2.get_all_decisions()
    assert field_key in decisions
    d = decisions[field_key]
    assert d["confirmed_class"] == "EMAIL"
    assert d["review_status"] == "CONFIRMED"
    assert d["has_approved_purpose"] is True
    assert d["retention_days"] == 180
    assert d["reviewer_name"] == "Data Protection Officer"
