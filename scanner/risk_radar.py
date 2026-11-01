"""
scanner/risk_radar.py
Explainable Privacy Risk Radar and Prioritization Engine for PS-019.

Calculates a deterministic risk score (0 to 100) for every detected personal-data field
based on 6 configurable factors:
1. Data sensitivity (GOVERNMENT_ID > PHONE_NUMBER / EMAIL > ADDRESS > NAME)
2. Detection confidence
3. Missing or unapproved purpose
4. Missing or overdue retention schedule
5. Human-review status
6. Multi-source exposure (cross-system proliferation)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RiskEvaluation:
    """Represents the explainable risk assessment for a detected field."""
    field_key: str
    source_name: str
    table_name: str
    column_name: str
    confirmed_class: str
    is_personal: bool
    risk_score: int             # 0 to 100
    priority_level: str         # Critical, High, Medium, Low
    factor_breakdown: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    is_multi_source: bool = False
    review_status: str = "PENDING_REVIEW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_key": self.field_key,
            "source_name": self.source_name,
            "table_name": self.table_name or "N/A",
            "column_name": self.column_name,
            "confirmed_class": self.confirmed_class,
            "is_personal": self.is_personal,
            "risk_score": self.risk_score,
            "priority_level": self.priority_level,
            "review_status": self.review_status,
            "is_multi_source": self.is_multi_source,
            "factor_breakdown": self.factor_breakdown,
            "explanation": self.explanation
        }


class PrivacyRiskRadar:
    """
    Explainable, rule-based risk prioritization engine.
    Produces risk scores and priority tiers with transparent mathematical factor contributions.
    """

    # Baseline sensitivity weights (0 - 35 points)
    CLASS_SENSITIVITY_WEIGHTS = {
        "GOVERNMENT_ID": 35.0,  # Statutory identifiers carry highest legal impact under DPDP/KYC
        "PHONE_NUMBER": 25.0,   # Direct contact channel, spam/fraud target, 2FA compromise
        "EMAIL": 25.0,          # Primary online identity and communication channel
        "ADDRESS": 20.0,        # Physical location / home residency exposure
        "NAME": 15.0,           # Basic personal identifier
        "NOT_PERSONAL": 0.0     # Non-personal fields have zero baseline sensitivity
    }

    # Priority thresholds
    PRIORITY_THRESHOLDS = [
        (75, "Critical"),
        (55, "High"),
        (35, "Medium"),
        (0, "Low")
    ]

    def __init__(self, sensitivity_weights: Optional[Dict[str, float]] = None):
        self.sensitivity_weights = sensitivity_weights or dict(self.CLASS_SENSITIVITY_WEIGHTS)

    @classmethod
    def get_priority_level(cls, score: int) -> str:
        for threshold, label in cls.PRIORITY_THRESHOLDS:
            if score >= threshold:
                return label
        return "Low"

    def calculate_field_risk(
        self,
        field_data: Dict[str, Any],
        cross_source_class_counts: Optional[Dict[str, int]] = None
    ) -> RiskEvaluation:
        """
        Calculates an explainable risk score (0 to 100) for a single enriched field record.
        """
        field_key = field_data.get("field_key", "")
        source_name = field_data.get("source_name", "")
        table_name = field_data.get("table_name", "")
        col_name = field_data.get("column_name", "")
        p_class = field_data.get("confirmed_class") or field_data.get("detected_class") or "NOT_PERSONAL"
        is_personal = bool(field_data.get("is_personal", False))
        review_status = field_data.get("review_status", "PENDING_REVIEW")
        conf_score = float(field_data.get("confidence_score", 0.0))

        # If confirmed as non-personal or human reviewer marked REJECTED, risk drops to 0
        if not is_personal or p_class == "NOT_PERSONAL" or review_status == "REJECTED":
            return RiskEvaluation(
                field_key=field_key,
                source_name=source_name,
                table_name=table_name,
                column_name=col_name,
                confirmed_class="NOT_PERSONAL" if review_status == "REJECTED" else p_class,
                is_personal=False,
                risk_score=0,
                priority_level="Low",
                factor_breakdown={"non_personal_override": 0.0},
                explanation="Field classified as non-personal or rejected during human review. Risk score zeroed.",
                is_multi_source=False,
                review_status=review_status
            )

        breakdown: Dict[str, float] = {}
        explanation_parts: List[str] = []

        # 1. Base Sensitivity Weight (up to 35 pts)
        base_sens = self.sensitivity_weights.get(p_class, 15.0)
        breakdown["data_sensitivity"] = base_sens
        explanation_parts.append(f"{p_class} sensitivity weight (+{base_sens:.0f})")

        # 2. Detection Confidence Factor (up to 15 pts)
        # Bounded between 0 and 15
        conf_pts = round(conf_score * 15.0, 1)
        breakdown["confidence_factor"] = conf_pts
        explanation_parts.append(f"Detection confidence ({conf_score:.2f}) scaled (+{conf_pts:.1f})")

        # 3. Purpose Compliance (up to 20 pts)
        # Missing purpose is critical under DPDP Act; unapproved purpose is elevated
        has_approved_purpose = bool(field_data.get("has_approved_purpose", False))
        is_missing_purpose = bool(field_data.get("is_missing_purpose", False))

        if is_missing_purpose:
            purpose_pts = 20.0
            explanation_parts.append("Missing declared business purpose (+20)")
        elif not has_approved_purpose:
            purpose_pts = 10.0
            explanation_parts.append("Purpose declared but lacks official DPO approval (+10)")
        else:
            purpose_pts = 0.0
            explanation_parts.append("Approved business purpose documented (0)")
        breakdown["purpose_compliance"] = purpose_pts

        # 4. Retention Schedule Compliance (up to 15 pts)
        is_missing_ret = bool(field_data.get("is_missing_retention", False))
        ret_days = int(field_data.get("retention_days", 0))

        if is_missing_ret:
            ret_pts = 15.0
            explanation_parts.append("Missing data retention schedule (+15)")
        elif ret_days > 365:
            # Extended retention adds storage limitation risk
            ret_pts = 8.0
            explanation_parts.append(f"Extended retention schedule ({ret_days} days) requires review (+8)")
        else:
            ret_pts = 0.0
            explanation_parts.append("Standard retention schedule configured (0)")
        breakdown["retention_compliance"] = ret_pts

        # 5. Review Workflow State (up to 15 pts)
        if review_status == "PENDING_REVIEW":
            review_pts = 15.0
            explanation_parts.append("Unreviewed candidate pending human confirmation (+15)")
        elif review_status == "FLAGGED":
            review_pts = 10.0
            explanation_parts.append("Flagged for secondary compliance verification (+10)")
        elif review_status == "CONFIRMED":
            # Human verified - review penalty eliminated
            review_pts = 0.0
            explanation_parts.append("Confirmed by human reviewer (review penalty removed)")
        else:
            review_pts = 5.0
        breakdown["review_status"] = review_pts

        # 6. Multi-Source Exposure (Cross-system proliferation) (up to 15 pts)
        source_count = (cross_source_class_counts or {}).get(p_class, 1)
        is_multi_source = source_count > 1
        if source_count >= 3:
            exposure_pts = 15.0
            explanation_parts.append(f"High multi-source exposure ({source_count} datasets hold {p_class}) (+15)")
        elif source_count == 2:
            exposure_pts = 10.0
            explanation_parts.append(f"Multi-source exposure ({source_count} datasets hold {p_class}) (+10)")
        else:
            exposure_pts = 0.0
            explanation_parts.append("Single dataset occurrence (0)")
        breakdown["multi_source_exposure"] = exposure_pts

        # Aggregate total score bounded in [0, 100]
        total_raw = sum(breakdown.values())
        final_score = int(round(min(max(total_raw, 0.0), 100.0)))
        priority = self.get_priority_level(final_score)

        explanation_str = (
            f"Risk Score: {final_score}/100 ({priority} Priority). Factors: "
            + "; ".join(explanation_parts)
            + ". [Note: Engineering prioritization score, not a legal compliance determination.]"
        )

        return RiskEvaluation(
            field_key=field_key,
            source_name=source_name,
            table_name=table_name,
            column_name=col_name,
            confirmed_class=p_class,
            is_personal=is_personal,
            risk_score=final_score,
            priority_level=priority,
            factor_breakdown=breakdown,
            explanation=explanation_str,
            is_multi_source=is_multi_source,
            review_status=review_status
        )

    def evaluate_inventory(self, enriched_inventory: List[Dict[str, Any]]) -> List[RiskEvaluation]:
        """
        Calculates cross-source exposure and produces risk assessments for all fields in inventory.
        """
        # Calculate cross-source proliferation for each personal class
        class_source_map: Dict[str, set] = {}
        for f in enriched_inventory:
            if f.get("is_personal") and f.get("review_status") != "REJECTED":
                cls = f.get("confirmed_class") or f.get("detected_class")
                src = f.get("source_name")
                if cls and src:
                    class_source_map.setdefault(cls, set()).add(src)

        cross_counts = {cls: len(sources) for cls, sources in class_source_map.items()}

        evaluations: List[RiskEvaluation] = []
        for field_data in enriched_inventory:
            ev = self.calculate_field_risk(field_data, cross_source_class_counts=cross_counts)
            evaluations.append(ev)

        # Sort descending by risk score
        evaluations.sort(key=lambda x: x.risk_score, reverse=True)
        return evaluations
