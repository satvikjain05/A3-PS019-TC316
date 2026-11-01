"""
tests/test_privacy_intelligence.py
Unit and integration tests for the Privacy Intelligence Layer:
- PrivacyRiskRadar (explainable factors, bounds, priority levels)
- RemediationEngine (deterministic triggers, status updates, persistence)
- PrivacyPostureScorecard (5 pillars, denominators, deficit rankings)
- PrivacyImpactSimulator (what-if scenarios, zero side-effects on disk)
- PrivacyExposureMap (Sankey structure, cross-source summary)
"""

import pytest
from pathlib import Path

from scanner.risk_radar import PrivacyRiskRadar, RiskEvaluation
from scanner.remediation_engine import RemediationEngine, RemediationTask
from scanner.posture_scorecard import PrivacyPostureScorecard
from scanner.exposure_map import PrivacyExposureMap


@pytest.fixture
def risk_radar():
    return PrivacyRiskRadar()


@pytest.fixture
def sample_inventory():
    return [
        {
            "field_key": "customers.csv::::synthetic_govt_id",
            "source_name": "customers.csv",
            "table_name": "",
            "column_name": "synthetic_govt_id",
            "detected_class": "GOVERNMENT_ID",
            "confirmed_class": "GOVERNMENT_ID",
            "is_personal": True,
            "confidence_score": 0.90,
            "declared_purpose": "Statutory KYC verification",
            "retention_days": 30,
            "retention_label": "30 days",
            "has_approved_purpose": False,
            "is_missing_purpose": False,
            "is_missing_retention": False,
            "review_status": "PENDING_REVIEW",
            "reviewer_notes": "",
            "masked_samples": "SYN-AAD-****-9012",
            "evidence_details": "Synthetic Aadhaar header and pattern match"
        },
        {
            "field_key": "employees.csv::::work_email",
            "source_name": "employees.csv",
            "table_name": "",
            "column_name": "work_email",
            "detected_class": "EMAIL",
            "confirmed_class": "EMAIL",
            "is_personal": True,
            "confidence_score": 0.95,
            "declared_purpose": "Corporate communication",
            "retention_days": 365,
            "retention_label": "365 days",
            "has_approved_purpose": True,
            "is_missing_purpose": False,
            "is_missing_retention": False,
            "review_status": "CONFIRMED",
            "reviewer_notes": "Approved by HR",
            "masked_samples": "a***v@corp.test",
            "evidence_details": "Corporate email match"
        },
        {
            "field_key": "support_tickets.csv::::callback_number",
            "source_name": "support_tickets.csv",
            "table_name": "",
            "column_name": "callback_number",
            "detected_class": "PHONE_NUMBER",
            "confirmed_class": "PHONE_NUMBER",
            "is_personal": True,
            "confidence_score": 0.85,
            "declared_purpose": "",
            "retention_days": 0,
            "retention_label": "Missing",
            "has_approved_purpose": False,
            "is_missing_purpose": True,
            "is_missing_retention": True,
            "review_status": "PENDING_REVIEW",
            "reviewer_notes": "",
            "masked_samples": "+91-98***-***45",
            "evidence_details": "Phone format match"
        },
        {
            "field_key": "customers.csv::::customer_id",
            "source_name": "customers.csv",
            "table_name": "",
            "column_name": "customer_id",
            "detected_class": "NOT_PERSONAL",
            "confirmed_class": "NOT_PERSONAL",
            "is_personal": False,
            "confidence_score": 0.0,
            "declared_purpose": "N/A",
            "retention_days": 0,
            "retention_label": "N/A",
            "has_approved_purpose": False,
            "is_missing_purpose": False,
            "is_missing_retention": False,
            "review_status": "NOT_APPLICABLE",
            "reviewer_notes": "",
            "masked_samples": "",
            "evidence_details": "No PII syntax"
        }
    ]


def test_risk_radar_scoring_and_explanation(risk_radar, sample_inventory):
    # Field 1: Govt ID (High sensitivity, unapproved purpose, pending review)
    govt_field = sample_inventory[0]
    res_govt = risk_radar.calculate_field_risk(govt_field)
    assert res_govt.risk_score >= 60
    assert res_govt.priority_level in ["High", "Critical"]
    assert "data_sensitivity" in res_govt.factor_breakdown
    assert res_govt.factor_breakdown["data_sensitivity"] == 35.0
    assert "Engineering prioritization score" in res_govt.explanation

    # Field 4: Non-personal field must have risk score 0
    non_pii_field = sample_inventory[3]
    res_non_pii = risk_radar.calculate_field_risk(non_pii_field)
    assert res_non_pii.risk_score == 0
    assert res_non_pii.priority_level == "Low"


def test_missing_metadata_increases_risk_score(risk_radar, sample_inventory):
    # Field 3 has missing purpose AND missing retention
    missing_meta_field = sample_inventory[2]
    res = risk_radar.calculate_field_risk(missing_meta_field)
    assert res.factor_breakdown["purpose_compliance"] == 20.0
    assert res.factor_breakdown["retention_compliance"] == 15.0
    assert res.risk_score >= 70
    assert res.priority_level in ["High", "Critical"]


def test_remediation_engine_generates_tasks(tmp_path, sample_inventory, risk_radar):
    store = tmp_path / "rem_test.json"
    engine = RemediationEngine(store_path=store)

    evals = risk_radar.evaluate_inventory(sample_inventory)
    tasks = engine.generate_recommendations(sample_inventory, evals)

    assert len(tasks) >= 2
    task_titles = [t.title for t in tasks]
    assert any("Document & Formally Declare Lawful Business Purpose" in t for t in task_titles)
    assert any("Define and Enforce Storage Retention Schedule" in t for t in task_titles)

    # Test status update and persistence
    target_task = tasks[0]
    engine.update_task_status(target_task.recommendation_id, "In Progress", "Assigned to DPO team")

    # Reload from disk
    engine2 = RemediationEngine(store_path=store)
    tasks2 = engine2.generate_recommendations(sample_inventory, evals)
    reloaded_task = next(t for t in tasks2 if t.recommendation_id == target_task.recommendation_id)
    assert reloaded_task.status == "In Progress"
    assert "Assigned to DPO" in reloaded_task.reviewer_notes


def test_posture_scorecard_calculation(sample_inventory, risk_radar):
    evals = risk_radar.evaluate_inventory(sample_inventory)
    scorecard = PrivacyPostureScorecard.calculate_scorecard(sample_inventory, evals)

    assert "overall_score" in scorecard
    assert 0.0 <= scorecard["overall_score"] <= 100.0
    assert "tier" in scorecard
    assert "components" in scorecard
    assert "top_improvement_areas" in scorecard

    # Verify pillar weights
    assert "review_coverage" in scorecard["components"]
    assert "purpose_approval" in scorecard["components"]
    assert "retention_coverage" in scorecard["components"]
    assert "high_risk_resolution" in scorecard["components"]
    assert "evidence_readiness" in scorecard["components"]


def test_what_if_simulation_zero_side_effects(sample_inventory, risk_radar):
    # Initial scorecard
    init_scorecard = PrivacyPostureScorecard.calculate_scorecard(sample_inventory)
    init_score = init_scorecard["overall_score"]

    # Run simulation with improvements
    sim_res = PrivacyPostureScorecard.run_simulation(
        enriched_inventory=sample_inventory,
        risk_radar=risk_radar,
        simulate_all_purpose_approved=True,
        simulate_all_retention_configured=True,
        simulate_all_high_risk_reviewed=True
    )

    assert sim_res["simulated_score"] > init_score
    assert sim_res["score_delta"] > 0
    assert sim_res["risk_delta"] <= 0  # Simulated risk should decrease or stay same

    # Ensure baseline sample_inventory was NOT modified
    assert sample_inventory[0]["has_approved_purpose"] is False
    assert sample_inventory[2]["is_missing_purpose"] is True


def test_exposure_map_generation(sample_inventory):
    fig = PrivacyExposureMap.build_sankey_diagram(sample_inventory)
    assert fig is not None
    assert len(fig.data) > 0

    cross_summary = PrivacyExposureMap.get_cross_source_summary(sample_inventory)
    assert isinstance(cross_summary, list)
