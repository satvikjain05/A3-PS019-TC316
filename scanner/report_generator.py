"""
scanner/report_generator.py
Enhanced Audit-Ready Compliance and Privacy Evidence Report Generator for PS-019.

Generates:
- Comprehensive Markdown Privacy Audit & Evidence Report
- Complete CSV / JSON exports of enriched inventory with risk and remediation data
- Evaluation metrics exports

Strictly distinguishes:
1. Scanner Observations
2. Declared Metadata
3. Reviewer-Confirmed Findings
4. Automated Recommendations
5. Simulated Results
Strictly masks or excludes raw sensitive personal data.
"""

import json
import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from .risk_radar import RiskEvaluation
from .remediation_engine import RemediationTask


class ReportGenerator:
    """
    Handles privacy-safe compliance exports and audit summaries.
    """

    @staticmethod
    def export_inventory_csv(
        enriched_inventory: List[Dict[str, Any]],
        risk_evaluations: Optional[List[RiskEvaluation]] = None
    ) -> str:
        """
        Exports the enriched inventory with risk assessment scores to CSV.
        Omits unmasked raw sample values.
        """
        risk_map = {r.field_key: r for r in (risk_evaluations or [])}

        output = io.StringIO()
        fieldnames = [
            "field_key",
            "source_name",
            "table_name",
            "column_name",
            "detected_class",
            "confirmed_class",
            "is_personal",
            "confidence_score",
            "risk_score",
            "priority_level",
            "declared_purpose",
            "retention_days",
            "retention_label",
            "has_approved_purpose",
            "is_missing_purpose",
            "is_missing_retention",
            "review_status",
            "reviewer_notes",
            "reviewed_by",
            "reviewed_at",
            "masked_samples",
            "evidence_details",
            "risk_explanation"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for row in enriched_inventory:
            row_copy = dict(row)
            key = row_copy.get("field_key", "")
            r_eval = risk_map.get(key)
            if r_eval:
                row_copy["risk_score"] = r_eval.risk_score
                row_copy["priority_level"] = r_eval.priority_level
                row_copy["risk_explanation"] = r_eval.explanation
            else:
                row_copy["risk_score"] = 0
                row_copy["priority_level"] = "Low"
                row_copy["risk_explanation"] = "Non-personal or unrated"
            writer.writerow(row_copy)

        return output.getvalue()

    @staticmethod
    def export_inventory_json(
        enriched_inventory: List[Dict[str, Any]],
        risk_evaluations: Optional[List[RiskEvaluation]] = None,
        remediation_tasks: Optional[List[RemediationTask]] = None,
        posture_scorecard: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Exports the comprehensive compliance inventory to structured JSON.
        """
        risk_map = {r.field_key: r.to_dict() for r in (risk_evaluations or [])}

        inventory_records = []
        for row in enriched_inventory:
            rec = dict(row)
            key = rec.get("field_key", "")
            if key in risk_map:
                rec["risk_evaluation"] = risk_map[key]
            inventory_records.append(rec)

        remediation_dicts = [t.to_dict() for t in (remediation_tasks or [])]

        payload = {
            "total_inventory_fields": len(inventory_records),
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "regulatory_standard": "MeitY Data Protection Framework (DPDP Act) Reference",
                "framework_principles": ["Purpose Limitation", "Storage Limitation", "Data Minimization"],
                "total_inventory_fields": len(inventory_records),
                "active_pii_fields": sum(1 for r in inventory_records if r.get("is_personal")),
                "disclaimer": "Technical privacy-review aid and evidence inventory, not a formal legal opinion or compliance certification."
            },
            "governance_posture": posture_scorecard or {},
            "inventory": inventory_records,
            "remediation_tasks": remediation_dicts
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    @staticmethod
    def export_evaluation_metrics_csv(eval_results: Dict[str, Any]) -> str:
        """
        Exports per-class precision, recall, and F1 metrics to CSV string.
        """
        output = io.StringIO()
        fieldnames = [
            "class_name",
            "precision",
            "recall",
            "f1_score",
            "support",
            "predicted_count",
            "true_positives",
            "false_positives",
            "false_negatives",
            "status_note"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        per_class = eval_results.get("per_class_metrics", {})
        for cls_name, m in per_class.items():
            row = {"class_name": cls_name, **m}
            writer.writerow(row)

        # Macro average row
        writer.writerow({
            "class_name": "MACRO_AVERAGE",
            "precision": eval_results.get("macro_precision", 0.0),
            "recall": eval_results.get("macro_recall", 0.0),
            "f1_score": eval_results.get("macro_f1", 0.0),
            "support": sum(m.get("support", 0) for m in per_class.values()),
            "predicted_count": sum(m.get("predicted_count", 0) for m in per_class.values()),
            "true_positives": sum(m.get("true_positives", 0) for m in per_class.values()),
            "false_positives": sum(m.get("false_positives", 0) for m in per_class.values()),
            "false_negatives": sum(m.get("false_negatives", 0) for m in per_class.values()),
            "status_note": "Averaged across 5 predefined personal-data classes"
        })

        return output.getvalue()

    @staticmethod
    def generate_audit_report_markdown(
        enriched_inventory: List[Dict[str, Any]],
        eval_results: Optional[Dict[str, Any]] = None,
        risk_evaluations: Optional[List[RiskEvaluation]] = None,
        remediation_tasks: Optional[List[RemediationTask]] = None,
        posture_scorecard: Optional[Dict[str, Any]] = None,
        simulation_results: Optional[Dict[str, Any]] = None,
        audit_title: str = "Personal-Data Discovery & Privacy Evidence Inventory Audit Report"
    ) -> str:
        """
        Generates an extensive, publication-ready Markdown compliance audit report.
        Strictly categorizes and distinguishes:
        1. Scanner Observations
        2. Declared Metadata
        3. Reviewer-Confirmed Findings
        4. Automated Recommendations
        5. Simulated Results
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        total_fields = len(enriched_inventory)
        personal_fields = [f for f in enriched_inventory if f.get("is_personal") and f.get("review_status") != "REJECTED"]
        num_personal = len(personal_fields)
        num_pending = sum(1 for f in personal_fields if f.get("review_status") == "PENDING_REVIEW")
        num_confirmed = sum(1 for f in personal_fields if f.get("review_status") == "CONFIRMED")
        num_approved = sum(1 for f in personal_fields if f.get("has_approved_purpose"))
        num_missing_purpose = sum(1 for f in personal_fields if f.get("is_missing_purpose"))
        num_missing_retention = sum(1 for f in personal_fields if f.get("is_missing_retention"))

        # Risk breakdown
        risk_map = {r.field_key: r for r in (risk_evaluations or [])}
        critical_count = sum(1 for r in (risk_evaluations or []) if r.is_personal and r.priority_level == "Critical")
        high_count = sum(1 for r in (risk_evaluations or []) if r.is_personal and r.priority_level == "High")
        med_count = sum(1 for r in (risk_evaluations or []) if r.is_personal and r.priority_level == "Medium")
        low_count = sum(1 for r in (risk_evaluations or []) if r.is_personal and r.priority_level == "Low")

        # Class counts
        class_counts: Dict[str, int] = {}
        for f in personal_fields:
            c = f.get("confirmed_class") or f.get("detected_class") or "UNKNOWN"
            class_counts[c] = class_counts.get(c, 0) + 1

        md = []
        md.append(f"# {audit_title}")
        md.append(f"*Generated on: {now}* | *Project: PS-019 (AIORI Hackathon 3 / Team A3-PS019-TC316)*")
        md.append("")
        md.append("> **Formal Regulatory Disclaimer:** This document is generated as a technical evidence aid for Data Protection Officers (DPOs) and internal compliance audits. It is based on deterministic pattern heuristics and declared repository metadata. It does not constitute a formal legal opinion or binding certification under the Digital Personal Data Protection (DPDP) Act.")
        md.append("")

        # Section 1: Executive Governance Summary
        md.append("## 1. Executive Summary & Privacy Governance")
        md.append("")
        if posture_scorecard:
            md.append(f"### **Overall Privacy Posture Score: {posture_scorecard.get('overall_score', 0.0)} / 100** (`{posture_scorecard.get('tier', 'Standard')}`)")
            md.append("")

        md.append("| Governance Metric | Count / Status | Regulatory Context |")
        md.append("|:---|:---:|:---|")
        md.append(f"| **Total Fields Scanned** | `{total_fields}` | Evaluated across CSV files and SQLite database tables |")
        md.append(f"| **Active Personal Data Candidates** | `{num_personal}` | Fields exhibiting PII characteristics across 5 classes |")
        md.append(f"| **Reviewer-Confirmed Findings** | `{num_confirmed}` | Formally verified by human reviewer |")
        md.append(f"| **Pending Human Review** | `{num_pending}` | Candidate discoveries awaiting manual sign-off |")
        md.append(f"| **Approved Business Purposes** | `{num_approved}` | Compliance sign-off completed for Purpose Limitation |")
        md.append(f"| **Missing Purpose Alerts** | `{num_missing_purpose}` | Fields lacking documented legal justification |")
        md.append(f"| **Missing Retention Alerts** | `{num_missing_retention}` | Fields lacking storage limitation schedules |")
        md.append(f"| **Critical / High Priority Findings** | `{critical_count + high_count}` | Prioritized for immediate remediation |")
        md.append("")

        # Section 2: Distinction Framework
        md.append("## 2. Information Architecture & Evidence Distinctions")
        md.append("")
        md.append("To maintain compliance rigor, this report enforces explicit boundaries between information categories:")
        md.append("- **1. Scanner Observations:** Empirical facts detected during sampling (column name, regex matches, match rate %, sample diversity).")
        md.append("- **2. Declared Metadata:** Policy expectations mapped from the configurable registry (stated purpose, statutory retention window).")
        md.append("- **3. Reviewer-Confirmed Findings:** Decisions confirmed by an authorized human reviewer with timestamps and justification.")
        md.append("- **4. Automated Recommendations:** Deterministic remediation actions generated by rule triggers to guide governance tasks.")
        md.append("- **5. Simulated Results:** Hypothetical projection models clearly separated from production audit records.")
        md.append("")

        # Section 3: Risk Radar Prioritization
        md.append("## 3. Privacy Risk Radar & Prioritization Rationale")
        md.append("")
        md.append("Risk scores (0–100) are computed using 6 weighted, explainable factors: Data Sensitivity, Confidence, Purpose Status, Retention Schedule, Human Review State, and Cross-System Proliferation.")
        md.append("")
        md.append(f"- **Critical Priority (75–100):** `{critical_count}` fields")
        md.append(f"- **High Priority (55–74):** `{high_count}` fields")
        md.append(f"- **Medium Priority (35–54):** `{med_count}` fields")
        md.append(f"- **Low Priority (0–34):** `{low_count}` fields")
        md.append("")
        md.append("### Top High & Critical Findings Requiring Action")
        md.append("")
        md.append("| Field Key | Class | Confidence | Risk Score | Priority | Factor Rationale |")
        md.append("|:---|:---:|:---:|:---:|:---:|:---|")
        high_critical_evals = [r for r in (risk_evaluations or []) if r.is_personal and r.priority_level in ["Critical", "High"]]
        for r in high_critical_evals[:8]:
            md.append(f"| `{r.field_key}` | **{r.confirmed_class}** | {r.factor_breakdown.get('confidence_factor', 0):.1f}pts | **{r.risk_score}** | `{r.priority_level}` | {r.explanation} |")
        md.append("")

        # Section 4: Privacy Evidence Inventory
        md.append("## 4. Privacy Evidence Inventory")
        md.append("")
        md.append("| Field Identifier | Data Class | Declared Purpose | Retention | Approved? | Review Status | Masked Example |")
        md.append("|:---|:---:|:---|:---:|:---:|:---:|:---|")
        for f in personal_fields:
            appr = "✅ Yes" if f.get("has_approved_purpose") else "❌ No"
            masked = f.get("masked_samples") or "N/A"
            md.append(f"| `{f.get('field_key')}` | **{f.get('confirmed_class')}** | {f.get('declared_purpose')} | {f.get('retention_label')} | {appr} | `{f.get('review_status')}` | `{masked}` |")
        md.append("")

        # Section 5: Automated Remediation Tasks
        if remediation_tasks:
            md.append("## 5. Automated Remediation Recommendations")
            md.append("")
            md.append("| Task ID | Finding Target | Risk Level | Recommended Action | Expected Compliance Benefit | Status |")
            md.append("|:---|:---|:---:|:---|:---|:---:|")
            for t in remediation_tasks[:10]:
                md.append(f"| `{t.recommendation_id}` | `{t.finding_id}` | `{t.risk_level}` | **{t.title}**: {t.suggested_action} | {t.expected_benefit} | `{t.status}` |")
            md.append("")

        # Section 6: Ground Truth Evaluation Benchmark
        if eval_results:
            md.append("## 6. Detection Performance & Ground Truth Benchmark")
            md.append("")
            md.append(f"- **Macro-Averaged Precision:** `{eval_results.get('macro_precision', 0.0):.4f}`")
            md.append(f"- **Macro-Averaged Recall:** `{eval_results.get('macro_recall', 0.0):.4f}`")
            md.append(f"- **Macro-Averaged F1-Score:** `{eval_results.get('macro_f1', 0.0):.4f}`")
            md.append(f"- **Binary PII F1-Score:** `{eval_results.get('overall_pii_f1', 0.0):.4f}`")
            md.append("")
            md.append("| Personal Data Class | Precision | Recall | F1-Score | Support | TP | FP | FN |")
            md.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
            per_class = eval_results.get("per_class_metrics", {})
            for c_name, m in per_class.items():
                md.append(
                    f"| **{c_name}** | {m['precision']:.2f} | {m['recall']:.2f} | {m['f1_score']:.2f} | "
                    f"{m['support']} | {m['true_positives']} | {m['false_positives']} | {m['false_negatives']} |"
                )
            md.append("")

        # Section 7: Simulated Impact Projection (if provided)
        if simulation_results:
            md.append("## 7. Hypothetical Privacy Improvement Simulation")
            md.append("")
            md.append("> **Notice:** The following metrics represent a hypothetical what-if scenario. They do not alter actual review records.")
            md.append("")
            md.append(f"- **Baseline Posture Score:** `{simulation_results.get('baseline_score', 0)}` → **Simulated Posture Score:** `{simulation_results.get('simulated_score', 0)}` (Δ: `+{simulation_results.get('score_delta', 0)}`)")
            md.append(f"- **Baseline Average Risk:** `{simulation_results.get('baseline_avg_risk', 0)}` → **Simulated Average Risk:** `{simulation_results.get('simulated_avg_risk', 0)}` (Δ: `{simulation_results.get('risk_delta', 0)}`)")
            md.append(f"- **Critical Findings Count:** `{simulation_results.get('baseline_critical_count', 0)}` → **Simulated Critical Count:** `{simulation_results.get('simulated_critical_count', 0)}` (Δ: `{simulation_results.get('critical_delta', 0)}`)")
            md.append("")

        # Section 8: Technical Limitations & False Positives/Negatives
        md.append("## 8. Technical Limitations & Error Considerations")
        md.append("")
        md.append("1. **Heuristic Scope:** Regex patterns are calibrated against synthetic Indian mobile numbers (+91), RFC emails, and synthetic statutory ID markers. Non-standard or foreign formats require pattern configuration.")
        md.append("2. **Ambiguous Columns:** Columns featuring mixed categorical and personal strings (such as `contact_pref_token`) are flagged for human review but not automatically asserted as PII.")
        md.append("3. **Free-Text Blobs:** Deeply nested narrative text blocks require complementary NLP/NER models for fine-grained entity extraction.")
        md.append("")

        return "\n".join(md)
