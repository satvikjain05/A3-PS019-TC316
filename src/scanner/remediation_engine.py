"""
scanner/remediation_engine.py
Intelligent Privacy Remediation Engine for PS-019.

Generates deterministic, actionable compliance remediation tasks for detected PII fields:
- Missing purpose documentation
- Missing or excessive retention schedules
- Unreviewed high-sensitivity statutory IDs
- Low-confidence detections requiring deeper inspection
- Redundant multi-source data proliferation

Persists remediation workflow statuses (Open, In Progress, Resolved) across application restarts.
Guarantees zero automated deletion or alteration of source data.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from .risk_radar import RiskEvaluation


@dataclass
class RemediationTask:
    recommendation_id: str
    finding_id: str
    source_name: str
    column_name: str
    confirmed_class: str
    risk_level: str
    title: str
    reason: str
    suggested_action: str
    expected_benefit: str
    status: str            # Open, In Progress, Resolved
    reviewer_notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RemediationEngine:
    """
    Analyzes enriched inventory findings and risk evaluations to generate
    targeted remediation actions with status tracking and disk persistence.
    """

    DEFAULT_STORE_PATH = Path(__file__).resolve().parent.parent / "config" / "remediations.json"

    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = Path(store_path) if store_path else self.DEFAULT_STORE_PATH
        self.persisted_tasks: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        """Loads persisted remediation decisions from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.persisted_tasks = json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to load remediations from {self.store_path}: {e}")
                self.persisted_tasks = {}
        else:
            self.persisted_tasks = {}

    def save(self):
        """Atomically saves tasks to disk."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.store_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.persisted_tasks, f, indent=2, ensure_ascii=False)
        tmp.replace(self.store_path)

    def generate_recommendations(
        self,
        enriched_inventory: List[Dict[str, Any]],
        risk_evaluations: Optional[List[RiskEvaluation]] = None
    ) -> List[RemediationTask]:
        """
        Deterministically evaluates all personal data findings to surface actionable tasks.
        Preserves previously updated statuses and notes from disk.
        """
        # Map risk evaluations by field key for fast lookup
        risk_map = {r.field_key: r for r in (risk_evaluations or [])}

        tasks: List[RemediationTask] = []
        now_str = datetime.now(timezone.utc).isoformat()

        for f in enriched_inventory:
            if not f.get("is_personal") or f.get("review_status") == "REJECTED":
                continue

            field_key = f.get("field_key", "")
            source = f.get("source_name", "")
            col = f.get("column_name", "")
            p_class = f.get("confirmed_class") or f.get("detected_class") or "UNKNOWN"
            review_status = f.get("review_status", "PENDING_REVIEW")
            risk_eval = risk_map.get(field_key)
            risk_level = risk_eval.priority_level if risk_eval else "Medium"
            conf_score = float(f.get("confidence_score", 0.0))
            is_missing_purpose = bool(f.get("is_missing_purpose", False))
            has_approved_purpose = bool(f.get("has_approved_purpose", False))
            is_missing_ret = bool(f.get("is_missing_retention", False))
            ret_days = int(f.get("retention_days", 0))

            # Trigger 1: Missing Purpose
            if is_missing_purpose:
                rec_id = f"REC-PURP-{field_key}"
                tasks.append(self._create_or_merge_task(
                    rec_id=rec_id,
                    finding_id=field_key,
                    source_name=source,
                    column_name=col,
                    confirmed_class=p_class,
                    risk_level="Critical" if p_class in ["GOVERNMENT_ID", "PHONE_NUMBER"] else "High",
                    title="Document & Formally Declare Lawful Business Purpose",
                    reason=f"Field '{col}' holds personal data ({p_class}) without a declared business purpose, violating DPDP purpose limitation mandates.",
                    suggested_action="Consult business stakeholder to establish a lawful basis (e.g., Contractual Necessity, Statutory KYC, or Consent) and document in registry.",
                    expected_benefit="Mitigates unauthorized data processing risk and fulfills regulatory audit expectations.",
                    now_str=now_str
                ))

            # Trigger 2: Unapproved Purpose
            elif not has_approved_purpose and review_status != "CONFIRMED":
                rec_id = f"REC-APPR-{field_key}"
                tasks.append(self._create_or_merge_task(
                    rec_id=rec_id,
                    finding_id=field_key,
                    source_name=source,
                    column_name=col,
                    confirmed_class=p_class,
                    risk_level="Medium",
                    title="Obtain DPO / Compliance Approval for Declared Purpose",
                    reason=f"Purpose is documented ('{f.get('declared_purpose')}') but lacks formal compliance approval.",
                    suggested_action="Review declared purpose against privacy policy and obtain Data Protection Officer sign-off in the Inventory workspace.",
                    expected_benefit="Confirms legal alignment between technical collection and corporate privacy commitments.",
                    now_str=now_str
                ))

            # Trigger 3: Missing Retention Schedule
            if is_missing_ret:
                rec_id = f"REC-RET-{field_key}"
                tasks.append(self._create_or_merge_task(
                    rec_id=rec_id,
                    finding_id=field_key,
                    source_name=source,
                    column_name=col,
                    confirmed_class=p_class,
                    risk_level="High",
                    title="Define and Enforce Storage Retention Schedule",
                    reason=f"Field '{col}' has no defined retention period. Unbounded retention violates storage limitation principles.",
                    suggested_action="Define maximum permissible retention duration (e.g., 30 days for KYC, 180 days for support logs) and record schedule.",
                    expected_benefit="Enforces data lifecycle discipline and prevents indefinite risk accumulation.",
                    now_str=now_str
                ))
            elif ret_days > 365:
                rec_id = f"REC-EXCRET-{field_key}"
                tasks.append(self._create_or_merge_task(
                    rec_id=rec_id,
                    finding_id=field_key,
                    source_name=source,
                    column_name=col,
                    confirmed_class=p_class,
                    risk_level="Medium",
                    title="Review Extended Data Retention Schedule",
                    reason=f"Field '{col}' is retained for {ret_days} days (> 1 year). Extended retention requires annual necessity review.",
                    suggested_action="Verify if business necessity justifies maintaining live personal records beyond standard 365-day boundary.",
                    expected_benefit="Ensures compliance with storage limitation reviews without breaking ongoing business operations.",
                    now_str=now_str
                ))

            # Trigger 4: Unreviewed High-Sensitivity Government ID
            if p_class == "GOVERNMENT_ID" and review_status == "PENDING_REVIEW":
                rec_id = f"REC-GOVT-{field_key}"
                tasks.append(self._create_or_merge_task(
                    rec_id=rec_id,
                    finding_id=field_key,
                    source_name=source,
                    column_name=col,
                    confirmed_class=p_class,
                    risk_level="Critical",
                    title="Prioritize Human Verification for Statutory ID Candidate",
                    reason=f"Column '{col}' was flagged as synthetic Government ID with confidence {conf_score:.2f}. Statutory identifiers require strict human oversight.",
                    suggested_action="Perform manual spot-check to confirm whether field contains real or test identifiers; verify encryption at rest.",
                    expected_benefit="Prevents accidental exposure or mishandling of sensitive national identity proofs.",
                    now_str=now_str
                ))

            # Trigger 5: Low-Confidence Candidate Requiring Inspection
            if conf_score < 0.60 and review_status == "PENDING_REVIEW":
                rec_id = f"REC-CONF-{field_key}"
                tasks.append(self._create_or_merge_task(
                    rec_id=rec_id,
                    finding_id=field_key,
                    source_name=source,
                    column_name=col,
                    confirmed_class=p_class,
                    risk_level="Low",
                    title="Inspect Ambiguous Field Pattern / Expand Sampling",
                    reason=f"Candidate detection confidence ({conf_score:.2f}) is marginal. Risk of false alarm or unindexed mixed data.",
                    suggested_action="Increase sample limit or inspect column values manually in Evidence Explorer to confirm classification.",
                    expected_benefit="Improves discovery accuracy and eliminates false positive noise from governance inventory.",
                    now_str=now_str
                ))

            # Trigger 6: Cross-Source Duplication
            if risk_eval and risk_eval.is_multi_source:
                rec_id = f"REC-DUP-{field_key}"
                tasks.append(self._create_or_merge_task(
                    rec_id=rec_id,
                    finding_id=field_key,
                    source_name=source,
                    column_name=col,
                    confirmed_class=p_class,
                    risk_level="Medium",
                    title="Assess Cross-System Data Duplication & Minimization",
                    reason=f"Data class '{p_class}' is duplicated across multiple datasets. Redundant data stores expand potential attack surface.",
                    suggested_action="Conduct data minimization audit to evaluate if centralized reference tokenization can replace duplicate column storage.",
                    expected_benefit="Reduces compliance footprint and limits blast radius during potential data security incidents.",
                    now_str=now_str
                ))

        # Sort tasks by risk priority: Critical -> High -> Medium -> Low
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        tasks.sort(key=lambda t: (priority_order.get(t.risk_level, 4), t.status != "Open"))
        return tasks

    def _create_or_merge_task(
        self,
        rec_id: str,
        finding_id: str,
        source_name: str,
        column_name: str,
        confirmed_class: str,
        risk_level: str,
        title: str,
        reason: str,
        suggested_action: str,
        expected_benefit: str,
        now_str: str
    ) -> RemediationTask:
        """Merges with persisted reviewer decision if previously modified."""
        persisted = self.persisted_tasks.get(rec_id)
        if persisted:
            return RemediationTask(
                recommendation_id=rec_id,
                finding_id=finding_id,
                source_name=source_name,
                column_name=column_name,
                confirmed_class=confirmed_class,
                risk_level=risk_level,
                title=title,
                reason=reason,
                suggested_action=suggested_action,
                expected_benefit=expected_benefit,
                status=persisted.get("status", "Open"),
                reviewer_notes=persisted.get("reviewer_notes", ""),
                created_at=persisted.get("created_at", now_str),
                updated_at=persisted.get("updated_at", now_str)
            )
        else:
            new_task = RemediationTask(
                recommendation_id=rec_id,
                finding_id=finding_id,
                source_name=source_name,
                column_name=column_name,
                confirmed_class=confirmed_class,
                risk_level=risk_level,
                title=title,
                reason=reason,
                suggested_action=suggested_action,
                expected_benefit=expected_benefit,
                status="Open",
                reviewer_notes="",
                created_at=now_str,
                updated_at=now_str
            )
            # Store initial
            self.persisted_tasks[rec_id] = new_task.to_dict()
            self.save()
            return new_task

    def update_task_status(self, recommendation_id: str, new_status: str, notes: str = ""):
        """Updates and persists recommendation status and reviewer notes."""
        if recommendation_id in self.persisted_tasks:
            task_dict = self.persisted_tasks[recommendation_id]
            task_dict["status"] = new_status
            if notes:
                task_dict["reviewer_notes"] = notes
            task_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.save()

    def reset_remediations(self):
        """Clears stored remediation tasks."""
        self.persisted_tasks = {}
        self.save()
