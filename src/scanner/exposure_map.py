"""
scanner/exposure_map.py
Visual Privacy Exposure Map Generator for PS-019.

Builds interactive relationship mappings using Plotly:
Data Source -> Table/File -> Detected Field -> Data Class -> Declared Purpose -> Retention Policy -> Review Status.

Highlights:
- Cross-source proliferation (PII classes occurring in multiple databases/CSVs)
- Missing purpose or retention metadata (color-coded red/amber)
- Confirmed findings vs unreviewed candidate detections
Strictly excludes raw sensitive personal-data values from graph nodes and labels.
"""

from typing import List, Dict, Any, Tuple
import plotly.graph_objects as go
from .risk_radar import RiskEvaluation


class PrivacyExposureMap:
    """
    Constructs multi-dimensional exposure maps and Sankey relationship diagrams
    from actual scanner findings and metadata.
    """

    @classmethod
    def build_sankey_diagram(cls, enriched_inventory: List[Dict[str, Any]]) -> go.Figure:
        """
        Builds a Plotly Sankey diagram illustrating data lineage:
        [Data Source] -> [Data Class] -> [Declared Purpose] -> [Review Status]
        """
        # Filter personal data fields
        pii_fields = [
            f for f in enriched_inventory
            if f.get("is_personal") and f.get("review_status") != "REJECTED"
        ]

        if not pii_fields:
            # Empty state figure
            fig = go.Figure()
            fig.add_annotation(
                text="No active personal data fields discovered to map.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#6B7280")
            )
            fig.update_layout(height=400)
            return fig

        # Unique node identifiers
        sources = sorted(list(set(f["source_name"] for f in pii_fields)))
        classes = sorted(list(set(f["confirmed_class"] for f in pii_fields)))
        purposes = sorted(list(set(
            "Missing Purpose" if f.get("is_missing_purpose") else (f.get("declared_purpose") or "Default Purpose")
            for f in pii_fields
        )))
        statuses = sorted(list(set(
            "Approved & Confirmed" if (f.get("has_approved_purpose") and f.get("review_status") == "CONFIRMED")
            else ("Pending Review" if f.get("review_status") == "PENDING_REVIEW" else f.get("review_status", "Active"))
            for f in pii_fields
        )))

        # Build node index map
        all_nodes = []
        node_colors = []

        # 1. Sources (Blue)
        source_offset = len(all_nodes)
        for s in sources:
            all_nodes.append(f"📁 {s}")
            node_colors.append("#2563EB")

        # 2. Classes (Purple / Amber)
        class_offset = len(all_nodes)
        for c in classes:
            all_nodes.append(f"🏷️ {c}")
            if c == "GOVERNMENT_ID":
                node_colors.append("#DC2626")  # Red for high sensitivity
            elif c in ["EMAIL", "PHONE_NUMBER"]:
                node_colors.append("#D97706")  # Amber
            else:
                node_colors.append("#7C3AED")  # Purple

        # 3. Purposes (Green / Red)
        purpose_offset = len(all_nodes)
        for p in purposes:
            if "Missing" in p:
                all_nodes.append(f"⚠️ {p}")
                node_colors.append("#EF4444")  # Red for compliance gap
            else:
                # Truncate long purpose labels for readability
                short_p = (p[:30] + "...") if len(p) > 30 else p
                all_nodes.append(f"⚖️ {short_p}")
                node_colors.append("#059669")  # Green

        # 4. Statuses (Teal / Gray)
        status_offset = len(all_nodes)
        for st in statuses:
            if "Approved" in st:
                all_nodes.append(f"✅ {st}")
                node_colors.append("#10B981")
            elif "Pending" in st:
                all_nodes.append(f"⏳ {st}")
                node_colors.append("#F59E0B")
            else:
                all_nodes.append(f"📋 {st}")
                node_colors.append("#6B7280")

        # Build links between layers
        links_dict: Dict[Tuple[int, int], int] = {}

        for f in pii_fields:
            src = f["source_name"]
            cls_name = f["confirmed_class"]
            p_val = "Missing Purpose" if f.get("is_missing_purpose") else (f.get("declared_purpose") or "Default Purpose")
            st_val = (
                "Approved & Confirmed" if (f.get("has_approved_purpose") and f.get("review_status") == "CONFIRMED")
                else ("Pending Review" if f.get("review_status") == "PENDING_REVIEW" else f.get("review_status", "Active"))
            )

            src_idx = source_offset + sources.index(src)
            cls_idx = class_offset + classes.index(cls_name)
            purp_idx = purpose_offset + purposes.index(p_val)
            stat_idx = status_offset + statuses.index(st_val)

            # Link 1: Source -> Class
            pair1 = (src_idx, cls_idx)
            links_dict[pair1] = links_dict.get(pair1, 0) + 1

            # Link 2: Class -> Purpose
            pair2 = (cls_idx, purp_idx)
            links_dict[pair2] = links_dict.get(pair2, 0) + 1

            # Link 3: Purpose -> Status
            pair3 = (purp_idx, stat_idx)
            links_dict[pair3] = links_dict.get(pair3, 0) + 1

        link_sources = [k[0] for k in links_dict.keys()]
        link_targets = [k[1] for k in links_dict.keys()]
        link_values = list(links_dict.values())

        # Link colors: subtle transparent flows
        link_colors = ["rgba(156, 163, 175, 0.45)" for _ in link_values]

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=18,
                thickness=22,
                line=dict(color="#1F2937", width=0.5),
                label=all_nodes,
                color=node_colors,
                hovertemplate="Node: %{label}<br>Associated Fields: %{value}<extra></extra>"
            ),
            link=dict(
                source=link_sources,
                target=link_targets,
                value=link_values,
                color=link_colors,
                hovertemplate="Lineage Flow: %{source.label} → %{target.label}<br>Field Count: %{value}<extra></extra>"
            )
        )])

        fig.update_layout(
            title_text="<b>Data Lineage & Privacy Exposure Flow</b> (Source → Class → Purpose → Governance Status)",
            font_size=11,
            height=520,
            margin=dict(l=15, r=15, t=45, b=15)
        )
        return fig

    @classmethod
    def get_cross_source_summary(cls, enriched_inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarizes personal data classes that proliferate across multiple sources.
        """
        class_sources: Dict[str, set] = {}
        class_fields: Dict[str, List[str]] = {}

        for f in enriched_inventory:
            if f.get("is_personal") and f.get("review_status") != "REJECTED":
                c = f.get("confirmed_class") or f.get("detected_class")
                src = f.get("source_name")
                col = f.get("column_name")
                if c and src:
                    class_sources.setdefault(c, set()).add(src)
                    class_fields.setdefault(c, []).append(f"{src}:{col}")

        summary = []
        for c, srcs in sorted(class_sources.items(), key=lambda x: len(x[1]), reverse=True):
            summary.append({
                "personal_class": c,
                "source_count": len(srcs),
                "sources_involved": ", ".join(sorted(srcs)),
                "field_occurrences": len(class_fields.get(c, [])),
                "exposure_level": "High (3+ Sources)" if len(srcs) >= 3 else ("Moderate (2 Sources)" if len(srcs) == 2 else "Isolated (1 Source)"),
                "minimization_recommendation": "High priority data minimization review" if len(srcs) >= 3 else "Standard cross-system audit"
            })
        return summary
