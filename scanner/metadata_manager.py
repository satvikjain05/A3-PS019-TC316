"""
scanner/metadata_manager.py
Configurable Metadata Registry and Review Decision Store.

Links detected personal-data fields to declared purpose and retention policies,
tracks missing compliance metadata, and persists human review decisions.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from .detection import DetectionResult


class MetadataManager:
    """
    Manages declared purpose, retention schedules, and reviewer overrides.
    Persists review decisions across application runs.
    """

    DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "metadata.json"

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Loads configuration and persisted reviewer decisions from disk."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to load metadata from {self.config_path}: {e}. Initializing defaults.")
                self._init_defaults()
        else:
            self._init_defaults()
            self.save()

    def _init_defaults(self):
        """Initializes baseline structure if configuration file does not exist."""
        self.data = {
            "version": "1.0.0",
            "default_class_policies": {
                "NAME": {
                    "default_purpose": "Account management & record keeping",
                    "default_retention_days": 365,
                    "legal_basis_recommendation": "Contractual Necessity / Consent",
                    "default_approved": False
                },
                "EMAIL": {
                    "default_purpose": "Account communication & service notifications",
                    "default_retention_days": 365,
                    "legal_basis_recommendation": "Contractual Necessity / Legitimate Interest",
                    "default_approved": False
                },
                "PHONE_NUMBER": {
                    "default_purpose": "Customer support & two-factor authentication (2FA)",
                    "default_retention_days": 180,
                    "legal_basis_recommendation": "Security / Contractual Necessity",
                    "default_approved": False
                },
                "ADDRESS": {
                    "default_purpose": "Order delivery & billing fulfillment",
                    "default_retention_days": 90,
                    "legal_basis_recommendation": "Contractual Necessity",
                    "default_approved": False
                },
                "GOVERNMENT_ID": {
                    "default_purpose": "Statutory identity verification (KYC compliance)",
                    "default_retention_days": 30,
                    "legal_basis_recommendation": "Legal Obligation (MeitY DPDP / RBI KYC)",
                    "default_approved": False
                }
            },
            "field_overrides": {},
            "reviewer_decisions": {}
        }

    def save(self):
        """Atomically saves metadata and reviewer decisions to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.config_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        temp_path.replace(self.config_path)

    @staticmethod
    def make_field_key(source_name: str, table_name: str, column_name: str) -> str:
        """Constructs a deterministic unique identifier for a field."""
        return f"{source_name}::{table_name}::{column_name}".strip()

    def get_default_policy_for_class(self, pii_class: Optional[str]) -> Dict[str, Any]:
        """Returns baseline policy mapping for a detected PII class."""
        if not pii_class or pii_class == "NOT_PERSONAL":
            return {
                "purpose": "N/A (Non-Personal Field)",
                "retention_days": 0,
                "retention_label": "N/A",
                "is_approved": False,
                "is_missing_purpose": False,
                "is_missing_retention": False
            }
        policies = self.data.get("default_class_policies", {})
        policy = policies.get(pii_class, {})
        purpose = policy.get("default_purpose", "")
        ret_days = policy.get("default_retention_days", 0)
        return {
            "purpose": purpose,
            "retention_days": ret_days,
            "retention_label": f"{ret_days} days" if ret_days > 0 else "Unspecified",
            "is_approved": False,  # Never assume approved by default!
            "is_missing_purpose": not bool(purpose),
            "is_missing_retention": ret_days <= 0
        }

    def enrich_detection(self, detection: DetectionResult) -> Dict[str, Any]:
        """
        Combines detection findings with declared metadata and stored human review decisions.
        """
        key = self.make_field_key(detection.source_name, detection.table_name, detection.column_name)
        base = detection.to_dict()
        base["field_key"] = key

        # Get class default
        default_pol = self.get_default_policy_for_class(detection.detected_class)

        # Check for persisted human review decisions
        decisions = self.data.setdefault("reviewer_decisions", {})
        decision = decisions.get(key, {})

        # Merge declared / override values
        final_class = decision.get("confirmed_class", detection.detected_class or "NOT_PERSONAL")
        base["confirmed_class"] = final_class

        # Purpose & Retention
        declared_purpose = decision.get("declared_purpose", default_pol["purpose"])
        declared_retention_days = decision.get("retention_days", default_pol["retention_days"])
        base["declared_purpose"] = declared_purpose
        base["retention_days"] = declared_retention_days
        base["retention_label"] = f"{declared_retention_days} days" if declared_retention_days > 0 else "Missing / Undefined"

        # Compliance Flags
        # Personal data MUST have an approved purpose and declared retention
        if final_class != "NOT_PERSONAL":
            has_approved_purpose = decision.get("has_approved_purpose", False)
            is_missing_purpose = decision.get("is_missing_purpose", not bool(declared_purpose) or declared_purpose == "N/A (Non-Personal Field)")
            is_missing_retention = decision.get("is_missing_retention", declared_retention_days <= 0)
        else:
            has_approved_purpose = False
            is_missing_purpose = False
            is_missing_retention = False

        base["has_approved_purpose"] = has_approved_purpose
        base["is_missing_purpose"] = is_missing_purpose
        base["is_missing_retention"] = is_missing_retention

        # Review Workflow State
        # If human reviewed: "CONFIRMED", "REJECTED", or "MODIFIED"
        # Otherwise: "PENDING_REVIEW" if candidate personal, else "NOT_APPLICABLE"
        if key in decisions:
            base["review_status"] = decision.get("review_status", "REVIEWED")
        else:
            base["review_status"] = "PENDING_REVIEW" if detection.is_personal else "NOT_APPLICABLE"

        base["reviewer_notes"] = decision.get("reviewer_notes", "")
        base["reviewed_by"] = decision.get("reviewed_by", "")
        base["reviewed_at"] = decision.get("reviewed_at", "")

        return base

    def record_review_decision(
        self,
        field_key: str,
        confirmed_class: str,
        review_status: str,
        declared_purpose: str,
        retention_days: int,
        has_approved_purpose: bool,
        is_missing_purpose: bool,
        is_missing_retention: bool,
        reviewer_notes: str = "",
        reviewer_name: str = "Compliance Reviewer"
    ):
        """
        Records and persists a human review decision for a specific field.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        decisions = self.data.setdefault("reviewer_decisions", {})

        decisions[field_key] = {
            "confirmed_class": confirmed_class,
            "review_status": review_status,
            "declared_purpose": declared_purpose,
            "retention_days": retention_days,
            "has_approved_purpose": has_approved_purpose,
            "is_missing_purpose": is_missing_purpose,
            "is_missing_retention": is_missing_retention,
            "reviewer_notes": reviewer_notes,
            "reviewed_by": reviewer_name,
            "reviewer_name": reviewer_name,
            "reviewed_at": now_str
        }

        self.save()

    def get_all_decisions(self) -> Dict[str, Any]:
        return self.data.get("reviewer_decisions", {})

    def clear_all_decisions(self):
        """Utility to reset review store if requested."""
        self.data["reviewer_decisions"] = {}
        self.save()
