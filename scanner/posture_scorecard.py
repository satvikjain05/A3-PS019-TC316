"""
scanner/posture_scorecard.py
Privacy Posture Scorecard and What-If Impact Simulator for PS-019.

Calculates an objective, transparent Privacy Posture Score (0 to 100)
using 5 documented governance pillars with explicit mathematical denominators.
Provides interactive simulation of hypothetical remediation scenarios without
altering actual records.
"""

from typing import List, Dict, Any, Tuple, Optional
from .risk_radar import RiskEvaluation, PrivacyRiskRadar


class PrivacyPostureScorecard:
    """
    Transparent governance scorecard engine and hypothetical impact simulator.
    """

    # Pillar Weights (Sum to 100%)
    WEIGHTS = {
        "review_coverage": 25.0,        # Human verification of discovered candidates
        "purpose_approval": 25.0,       # Official DPO/Legal purpose approvals
        "retention_coverage": 20.0,     # Storage limitation schedule coverage
        "high_risk_resolution": 20.0,   # Resolution of Critical & High risk findings
        "evidence_readiness": 10.0      # Audit trail & technical evidence completeness
    }

    @classmethod
    def calculate_scorecard(
        cls,
        enriched_inventory: List[Dict[str, Any]],
        risk_evaluations: Optional[List[RiskEvaluation]] = None
    ) -> Dict[str, Any]:
        """
        Calculates project-defined Privacy Posture Score and sub-metric contributions.
        """
        # Filter personal data candidate fields
        personal_fields = [
            f for f in enriched_inventory
            if f.get("is_personal") and f.get("review_status") != "REJECTED"
        ]
        total_pii = len(personal_fields)

        # Edge case: If no personal data detected, posture is 100
        if total_pii == 0:
            return {
                "overall_score": 100.0,
                "tier": "Exemplary",
                "total_pii_fields": 0,
                "components": {},
                "top_improvement_areas": [],
                "disclaimer": "No personal data fields detected in analyzed sources."
            }

        # 1. Review Coverage Rate (Weight: 25%)
        # Denominator: Total Candidate PII Fields
        # Numerator: Fields where review_status is CONFIRMED or MODIFIED
        reviewed_count = sum(1 for f in personal_fields if f.get("review_status") in ["CONFIRMED", "MODIFIED", "REVIEWED"])
        review_coverage_pct = (reviewed_count / total_pii) * 100.0
        review_contrib = (review_coverage_pct / 100.0) * cls.WEIGHTS["review_coverage"]

        # 2. Purpose Approval Rate (Weight: 25%)
        # Denominator: Total Candidate PII Fields
        # Numerator: Fields with has_approved_purpose == True
        approved_count = sum(1 for f in personal_fields if f.get("has_approved_purpose"))
        purpose_approval_pct = (approved_count / total_pii) * 100.0
        purpose_contrib = (purpose_approval_pct / 100.0) * cls.WEIGHTS["purpose_approval"]

        # 3. Retention Schedule Coverage (Weight: 20%)
        # Denominator: Total Candidate PII Fields
        # Numerator: Fields where is_missing_retention is False and retention_days > 0
        retention_count = sum(1 for f in personal_fields if not f.get("is_missing_retention") and f.get("retention_days", 0) > 0)
        retention_coverage_pct = (retention_count / total_pii) * 100.0
        retention_contrib = (retention_coverage_pct / 100.0) * cls.WEIGHTS["retention_coverage"]

        # 4. Critical & High Risk Resolution Rate (Weight: 20%)
        # Denominator: Total Critical & High Risk Fields
        # Numerator: Critical & High Risk Fields that have been reviewed/approved
        risk_map = {r.field_key: r for r in (risk_evaluations or [])}
        high_critical_fields = [
            f for f in personal_fields
            if risk_map.get(f.get("field_key", ""), None) and risk_map[f["field_key"]].priority_level in ["Critical", "High"]
        ]
        total_high_critical = len(high_critical_fields)

        if total_high_critical > 0:
            resolved_high_critical = sum(
                1 for f in high_critical_fields
                if f.get("review_status") == "CONFIRMED" and f.get("has_approved_purpose")
            )
            risk_resolution_pct = (resolved_high_critical / total_high_critical) * 100.0
        else:
            # If zero high-critical findings, full marks awarded
            risk_resolution_pct = 100.0
            resolved_high_critical = 0

        risk_contrib = (risk_resolution_pct / 100.0) * cls.WEIGHTS["high_risk_resolution"]

        # 5. Evidence & Audit Readiness (Weight: 10%)
        # Denominator: Total Candidate PII Fields
        # Numerator: Fields with technical evidence and masked samples captured
        evidence_count = sum(1 for f in personal_fields if f.get("evidence_details") and f.get("masked_samples"))
        evidence_pct = (evidence_count / total_pii) * 100.0
        evidence_contrib = (evidence_pct / 100.0) * cls.WEIGHTS["evidence_readiness"]

        # Overall Score
        overall_score = round(review_contrib + purpose_contrib + retention_contrib + risk_contrib + evidence_contrib, 1)

        # Tier assignment
        if overall_score >= 85:
            tier = "Proactive & Governed"
        elif overall_score >= 65:
            tier = "Defined Baseline"
        elif overall_score >= 45:
            tier = "Emerging / Needs Attention"
        else:
            tier = "Elevated Compliance Risk"

        components = {
            "review_coverage": {
                "name": "Human Review Coverage",
                "percentage": round(review_coverage_pct, 1),
                "numerator": reviewed_count,
                "denominator": total_pii,
                "weight": cls.WEIGHTS["review_coverage"],
                "earned_points": round(review_contrib, 1),
                "deficit_points": round(cls.WEIGHTS["review_coverage"] - review_contrib, 1),
                "description": f"{reviewed_count} of {total_pii} candidate PII fields reviewed by DPO."
            },
            "purpose_approval": {
                "name": "Purpose Approval Rate",
                "percentage": round(purpose_approval_pct, 1),
                "numerator": approved_count,
                "denominator": total_pii,
                "weight": cls.WEIGHTS["purpose_approval"],
                "earned_points": round(purpose_contrib, 1),
                "deficit_points": round(cls.WEIGHTS["purpose_approval"] - purpose_contrib, 1),
                "description": f"{approved_count} of {total_pii} fields have approved lawful purposes."
            },
            "retention_coverage": {
                "name": "Retention Policy Coverage",
                "percentage": round(retention_coverage_pct, 1),
                "numerator": retention_count,
                "denominator": total_pii,
                "weight": cls.WEIGHTS["retention_coverage"],
                "earned_points": round(retention_contrib, 1),
                "deficit_points": round(cls.WEIGHTS["retention_coverage"] - retention_contrib, 1),
                "description": f"{retention_count} of {total_pii} fields have declared retention schedules."
            },
            "high_risk_resolution": {
                "name": "High-Risk Finding Resolution",
                "percentage": round(risk_resolution_pct, 1),
                "numerator": resolved_high_critical,
                "denominator": total_high_critical,
                "weight": cls.WEIGHTS["high_risk_resolution"],
                "earned_points": round(risk_contrib, 1),
                "deficit_points": round(cls.WEIGHTS["high_risk_resolution"] - risk_contrib, 1),
                "description": f"{resolved_high_critical} of {total_high_critical} Critical/High findings confirmed & approved."
            },
            "evidence_readiness": {
                "name": "Evidence & Audit Readiness",
                "percentage": round(evidence_pct, 1),
                "numerator": evidence_count,
                "denominator": total_pii,
                "weight": cls.WEIGHTS["evidence_readiness"],
                "earned_points": round(evidence_contrib, 1),
                "deficit_points": round(cls.WEIGHTS["evidence_readiness"] - evidence_contrib, 1),
                "description": f"{evidence_count} of {total_pii} fields have complete technical evidence logs."
            }
        }

        # Identify Top 3 Improvement Areas sorted by highest point deficit
        sorted_deficits = sorted(components.items(), key=lambda item: item[1]["deficit_points"], reverse=True)
        top_improvements = [
            {
                "pillar": item[1]["name"],
                "deficit": item[1]["deficit_points"],
                "current_pct": item[1]["percentage"],
                "action": f"Elevate {item[1]['name']} from {item[1]['percentage']}% to 100% to regain up to +{item[1]['deficit_points']} points."
            }
            for item in sorted_deficits[:3] if item[1]["deficit_points"] > 0
        ]

        return {
            "overall_score": overall_score,
            "tier": tier,
            "total_pii_fields": total_pii,
            "components": components,
            "top_improvement_areas": top_improvements,
            "disclaimer": "Internal technical privacy posture index based on explicit governance criteria; not a legal compliance certification."
        }

    @classmethod
    def run_simulation(
        cls,
        enriched_inventory: List[Dict[str, Any]],
        risk_radar: PrivacyRiskRadar,
        simulate_all_purpose_approved: bool = False,
        simulate_all_retention_configured: bool = False,
        simulate_all_high_risk_reviewed: bool = False,
        simulate_duplicate_reduction: bool = False
    ) -> Dict[str, Any]:
        """
        Runs an in-memory hypothetical improvement simulation.
        Does NOT alter source data or actual review records on disk.
        """
        # Create an isolated in-memory copy of inventory
        simulated_inventory = [dict(f) for f in enriched_inventory]

        for f in simulated_inventory:
            if not f.get("is_personal"):
                continue

            if simulate_all_purpose_approved:
                f["has_approved_purpose"] = True
                f["is_missing_purpose"] = False
                if not f.get("declared_purpose") or f.get("declared_purpose") == "N/A (Non-Personal Field)":
                    f["declared_purpose"] = f"Simulated Lawful Basis for {f.get('confirmed_class')}"

            if simulate_all_retention_configured:
                f["is_missing_retention"] = False
                if f.get("retention_days", 0) <= 0 or f.get("retention_days", 0) > 365:
                    f["retention_days"] = 180
                    f["retention_label"] = "180 days (Simulated)"

            if simulate_all_high_risk_reviewed:
                # Mark high-risk candidate as reviewed and confirmed
                if f.get("confirmed_class") in ["GOVERNMENT_ID", "PHONE_NUMBER", "EMAIL"]:
                    f["review_status"] = "CONFIRMED"
                    f["has_approved_purpose"] = True

        # Re-evaluate simulated risk radar
        # If duplicate reduction simulated, cross_source counts are normalized to 1
        simulated_evals = risk_radar.evaluate_inventory(simulated_inventory)
        if simulate_duplicate_reduction:
            # Overwrite multi_source risk contribution
            for ev in simulated_evals:
                if ev.is_multi_source:
                    ev.factor_breakdown["multi_source_exposure"] = 0.0
                    ev.is_multi_source = False
                    ev.risk_score = int(round(min(max(sum(ev.factor_breakdown.values()), 0.0), 100.0)))
                    ev.priority_level = PrivacyRiskRadar.get_priority_level(ev.risk_score)

        # Baseline calculations
        baseline_evals = risk_radar.evaluate_inventory(enriched_inventory)
        baseline_scorecard = cls.calculate_scorecard(enriched_inventory, baseline_evals)
        simulated_scorecard = cls.calculate_scorecard(simulated_inventory, simulated_evals)

        baseline_pii_evals = [e for e in baseline_evals if e.is_personal]
        sim_pii_evals = [e for e in simulated_evals if e.is_personal]

        baseline_avg_risk = round(sum(e.risk_score for e in baseline_pii_evals) / len(baseline_pii_evals), 1) if baseline_pii_evals else 0.0
        sim_avg_risk = round(sum(e.risk_score for e in sim_pii_evals) / len(sim_pii_evals), 1) if sim_pii_evals else 0.0

        baseline_critical_count = sum(1 for e in baseline_pii_evals if e.priority_level == "Critical")
        sim_critical_count = sum(1 for e in sim_pii_evals if e.priority_level == "Critical")

        return {
            "baseline_score": baseline_scorecard["overall_score"],
            "simulated_score": simulated_scorecard["overall_score"],
            "score_delta": round(simulated_scorecard["overall_score"] - baseline_scorecard["overall_score"], 1),
            "baseline_avg_risk": baseline_avg_risk,
            "simulated_avg_risk": sim_avg_risk,
            "risk_delta": round(sim_avg_risk - baseline_avg_risk, 1),
            "baseline_critical_count": baseline_critical_count,
            "simulated_critical_count": sim_critical_count,
            "critical_delta": sim_critical_count - baseline_critical_count,
            "simulated_components": simulated_scorecard["components"],
            "simulation_flags": {
                "simulate_all_purpose_approved": simulate_all_purpose_approved,
                "simulate_all_retention_configured": simulate_all_retention_configured,
                "simulate_all_high_risk_reviewed": simulate_all_high_risk_reviewed,
                "simulate_duplicate_reduction": simulate_duplicate_reduction
            },
            "disclaimer": "Hypothetical projection only. Does not alter source tables, live databases, or official DPO review records."
        }
