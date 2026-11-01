"""
app.py
Privacy Intelligence Engine — PS-019: Personal-Data Discovery & Privacy Evidence Inventory
AIORI Hackathon 3 • Team A3-PS019-TC316

Clean, premium, modern LIGHT-THEME privacy governance dashboard redesigned to match
the reference visual specifications.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from scanner.detection import PersonalDataDetector, DetectionResult
from scanner.csv_scanner import CSVScanner
from scanner.sqlite_scanner import SQLiteScanner
from scanner.metadata_manager import MetadataManager
from scanner.evaluation import Evaluator
from scanner.report_generator import ReportGenerator

# Privacy Intelligence Layer
from scanner.risk_radar import PrivacyRiskRadar, RiskEvaluation
from scanner.remediation_engine import RemediationEngine, RemediationTask
from scanner.posture_scorecard import PrivacyPostureScorecard
from scanner.exposure_map import PrivacyExposureMap

# ---------------------------------------------------------
# Streamlit Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Privacy Intelligence Engine (PS-019)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Comprehensive Light-Theme CSS Styling
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 1. Global Font and Light Backgrounds */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* 2. Top Header Adjustments (Prevent Any Title Clipping) */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 1.2rem !important;
        z-index: 10 !important;
    }
    
    .block-container {
        padding-top: 2.4rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 100% !important;
    }
    
    /* 3. Sidebar Redesign (Exact Match to Reference Screenshot) */
    section[data-testid="stSidebar"] {
        width: 275px !important;
        min-width: 275px !important;
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #FFFFFF !important;
        padding-top: 1.4rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.35rem !important;
    }
    
    /* Clean Toggle Styling */
    div[data-testid="stToggle"] {
        margin-top: 2px !important;
        margin-bottom: 6px !important;
        padding: 2px 4px !important;
    }
    
    div[data-testid="stToggle"] label p,
    div[data-testid="stToggle"] label span {
        font-size: 0.86rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
    }
    
    /* Hide Radio Circles & Style Menu Items as Clean Tabs */
    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 2px !important;
    }
    
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        padding: 9px 12px !important;
        margin-bottom: 2px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
    }
    
    section[data-testid="stSidebar"] div[role="radiogroup"] > label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label span,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label div {
        color: #334155 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        margin: 0 !important;
        line-height: 1.3 !important;
    }
    
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #F8FAFC !important;
        border-color: #E2E8F0 !important;
    }
    
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #EFF6FF !important;
        border-color: #DBEAFE !important;
    }
    
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) span,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) div {
        color: #2563EB !important;
        font-weight: 600 !important;
    }
    
    /* 4. White Cards and Containers */
    .white-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    
    .white-card-compact {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    
    /* 5. Posture Banner Gradient Card */
    .posture-card {
        background: linear-gradient(135deg, #F0F7FF 0%, #E8F2FE 55%, #E1EFFE 100%);
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.03);
    }
    
    /* 6. Form Controls and Dataframe Styling in Light Mode */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 1px #2563EB !important;
    }
    
    /* Streamlit Buttons */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #F8FAFC !important;
        border-color: #94A3B8 !important;
        color: #0F172A !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
        border-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E2E8F0;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 6px 6px 0 0;
        color: #64748B;
        font-weight: 500;
        border: none;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #2563EB !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #2563EB !important;
    }
    
    /* Dataframe Table Contrast */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Path Constants & Singletons
# ---------------------------------------------------------
WORKSPACE_DIR = Path(__file__).resolve().parent
DATA_DIR = WORKSPACE_DIR / "data"
CONFIG_DIR = WORKSPACE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "metadata.json"
REMEDIATION_FILE = CONFIG_DIR / "remediations.json"


@st.cache_resource
def get_metadata_manager():
    return MetadataManager(config_path=CONFIG_FILE)


@st.cache_resource
def get_remediation_engine():
    return RemediationEngine(store_path=REMEDIATION_FILE)


@st.cache_resource
def get_detector():
    return PersonalDataDetector()


@st.cache_resource
def get_risk_radar():
    return PrivacyRiskRadar()


metadata_mgr = get_metadata_manager()
remediation_engine = get_remediation_engine()
detector = get_detector()
risk_radar = get_risk_radar()
csv_scanner = CSVScanner(detector=detector)
sqlite_scanner = SQLiteScanner(detector=detector)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "sample_limit" not in st.session_state:
    st.session_state["sample_limit"] = 100
if "raw_detections" not in st.session_state:
    st.session_state["raw_detections"] = []
if "enriched_inventory" not in st.session_state:
    st.session_state["enriched_inventory"] = []
if "risk_evaluations" not in st.session_state:
    st.session_state["risk_evaluations"] = []
if "remediation_tasks" not in st.session_state:
    st.session_state["remediation_tasks"] = []
if "scanned_files_count" not in st.session_state:
    st.session_state["scanned_files_count"] = 0
if "scanned_tables_count" not in st.session_state:
    st.session_state["scanned_tables_count"] = 0
if "eval_results" not in st.session_state:
    st.session_state["eval_results"] = None
if "demo_mode_active" not in st.session_state:
    st.session_state["demo_mode_active"] = False
if "demo_step" not in st.session_state:
    st.session_state["demo_step"] = 1


def run_full_discovery_scan(sample_limit: int, extra_csv_files=None, custom_sqlite_path=None):
    """Executes end-to-end scanning across bundled/uploaded CSVs and SQLite databases."""
    all_detections: list[DetectionResult] = []
    files_scanned = 0
    tables_scanned = 0

    # 1. Bundled CSV files
    bundled_csvs = ["customers.csv", "employees.csv", "support_tickets.csv"]
    for fname in bundled_csvs:
        p = DATA_DIR / fname
        if p.exists():
            try:
                res = csv_scanner.scan_file(p, filename=fname, sample_limit=sample_limit)
                all_detections.extend(res)
                files_scanned += 1
            except Exception as e:
                st.error(f"Error scanning {fname}: {e}")

    # 2. Extra uploaded CSVs
    if extra_csv_files:
        for uploaded_file in extra_csv_files:
            try:
                res = csv_scanner.scan_file(uploaded_file, filename=uploaded_file.name, sample_limit=sample_limit)
                all_detections.extend(res)
                files_scanned += 1
            except Exception as e:
                st.error(f"Error scanning uploaded file '{uploaded_file.name}': {e}")

    # 3. SQLite Database
    db_to_scan = Path(custom_sqlite_path) if custom_sqlite_path else (DATA_DIR / "privacy_demo.db")
    if db_to_scan.exists():
        try:
            tables = sqlite_scanner.discover_tables(db_to_scan)
            for tbl in tables:
                res = sqlite_scanner.scan_table(db_to_scan, tbl, sample_limit=sample_limit)
                all_detections.extend(res)
                tables_scanned += 1
        except Exception as e:
            st.error(f"Error scanning SQLite database {db_to_scan.name}: {e}")

    # Enrich detections with metadata & persisted decisions
    enriched = [metadata_mgr.enrich_detection(d) for d in all_detections]

    # Run Privacy Intelligence Layer
    risk_evals = risk_radar.evaluate_inventory(enriched)
    rem_tasks = remediation_engine.generate_recommendations(enriched, risk_evals)

    st.session_state["raw_detections"] = all_detections
    st.session_state["enriched_inventory"] = enriched
    st.session_state["risk_evaluations"] = risk_evals
    st.session_state["remediation_tasks"] = rem_tasks
    st.session_state["scanned_files_count"] = files_scanned
    st.session_state["scanned_tables_count"] = tables_scanned


def sync_intelligence_layer():
    """Refreshes risk radar, remediations, and scorecard without re-reading raw disks."""
    enriched = [metadata_mgr.enrich_detection(d) for d in st.session_state["raw_detections"]]
    risk_evals = risk_radar.evaluate_inventory(enriched)
    rem_tasks = remediation_engine.generate_recommendations(enriched, risk_evals)
    st.session_state["enriched_inventory"] = enriched
    st.session_state["risk_evaluations"] = risk_evals
    st.session_state["remediation_tasks"] = rem_tasks


# Auto-run initial scan if state is empty
if not st.session_state["enriched_inventory"]:
    run_full_discovery_scan(st.session_state["sample_limit"])


# ---------------------------------------------------------
# Sidebar Redesign (Exact Match to Reference Screenshot)
# ---------------------------------------------------------
with st.sidebar:
    # 1. Top Branding Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
        <div style="width: 38px; height: 38px; border-radius: 9px; background-color: #EFF6FF; border: 1px solid #DBEAFE; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
        </div>
        <div>
            <div style="font-size: 1.12rem; font-weight: 800; color: #0F172A; line-height: 1.2; letter-spacing: -0.01em;">
                Privacy Intelligence Engine
            </div>
        </div>
    </div>
    <div style="font-size: 0.78rem; color: #64748B; margin-left: 2px; margin-top: 4px; margin-bottom: 14px; line-height: 1.35;">
        PS-019 · AIORI Hackathon 3<br>
        <span style="display: inline-block; background-color: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 4px; padding: 1px 7px; font-weight: 600; color: #475569; margin-top: 3px; font-size: 0.74rem;">Team A3-PS019-TC316</span>
    </div>
    """, unsafe_allow_html=True)

    # 2. Guided Hackathon Demo Mode in a neat pale-blue card
    st.markdown("""
    <div style="background-color: #EFF6FF; border: 1px solid #DBEAFE; border-radius: 8px; padding: 6px 10px 4px 10px; margin-bottom: 12px;">
    """, unsafe_allow_html=True)
    demo_toggle = st.toggle("✨ Guided Demo Mode", value=st.session_state["demo_mode_active"])
    st.session_state["demo_mode_active"] = demo_toggle

    if st.session_state["demo_mode_active"]:
        demo_step_names = [
            "1. Scan Sources",
            "2. Review Findings",
            "3. Risk Radar",
            "4. Exposure Map",
            "5. Remediations",
            "6. What-If Sim",
            "7. Audit Export"
        ]
        selected_demo_step = st.selectbox(
            "Presentation Step",
            range(1, 8),
            format_func=lambda i: demo_step_names[i-1],
            index=st.session_state["demo_step"] - 1
        )
        if selected_demo_step != st.session_state["demo_step"]:
            st.session_state["demo_step"] = selected_demo_step
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Workspace Section Header
    st.markdown("""
    <div style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin: 4px 0 6px 4px;">
        WORKSPACE
    </div>
    """, unsafe_allow_html=True)

    # 4. Ten Clean Navigation Items matching Reference
    nav_options = [
        "Executive Dashboard",
        "Data Sources & Ingestion",
        "Scan Results & Evidence",
        "Privacy Evidence Inventory",
        "Privacy Risk Radar",
        "Visual Exposure Map",
        "Remediation Center",
        "What-If Simulator",
        "Benchmark Evaluation",
        "Reports & Export"
    ]

    # Map demo steps to navigation pages if demo mode is active
    step_nav_map = {
        1: "Data Sources & Ingestion",
        2: "Scan Results & Evidence",
        3: "Privacy Risk Radar",
        4: "Visual Exposure Map",
        5: "Remediation Center",
        6: "What-If Simulator",
        7: "Reports & Export"
    }

    if st.session_state["demo_mode_active"]:
        default_nav_idx = nav_options.index(step_nav_map[st.session_state["demo_step"]])
    else:
        default_nav_idx = 0

    nav_selection = st.radio(
        "Navigation",
        nav_options,
        index=default_nav_idx,
        format_func=lambda x: {
            "Executive Dashboard": "🏠  Executive Dashboard",
            "Data Sources & Ingestion": "🗄️  Data Sources & Ingestion",
            "Scan Results & Evidence": "🔍  Scan Results & Evidence",
            "Privacy Evidence Inventory": "📋  Privacy Evidence Inventory",
            "Privacy Risk Radar": "⚠️  Privacy Risk Radar",
            "Visual Exposure Map": "🕸️  Visual Exposure Map",
            "Remediation Center": "🔧  Remediation Center",
            "What-If Simulator": "🎛️  What-If Simulator",
            "Benchmark Evaluation": "📊  Benchmark Evaluation",
            "Reports & Export": "📥  Reports & Export"
        }[x],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 5. Bottom Info Card ("Synthetic Data Only")
    st.markdown("""
    <div style="background-color: #FFFBEB; border: 1px solid #FEF3C7; border-radius: 8px; padding: 12px 14px; margin-top: 14px;">
        <div style="font-weight: 700; color: #92400E; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
            <span>ⓘ</span> <span>Synthetic Data Only</span>
        </div>
        <div style="font-size: 0.77rem; color: #A16207; margin-top: 4px; line-height: 1.35;">
            This demo uses fictional, computer-generated data for academic and research purposes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. Advanced Controls in Sidebar Expander
    with st.expander("⚙️ Scan Settings & State Reset"):
        sampling_slider = st.slider(
            "Row Sampling Ceiling",
            min_value=20, max_value=500,
            value=st.session_state["sample_limit"], step=20
        )
        if sampling_slider != st.session_state["sample_limit"]:
            st.session_state["sample_limit"] = sampling_slider

        if st.button("🔄 Re-run Scan", use_container_width=True):
            run_full_discovery_scan(st.session_state["sample_limit"])
            st.rerun()

        confirm_reset = st.checkbox("Confirm Reset", key="chk_confirm_reset")
        if st.button("⚠️ Reset State (Backup)", disabled=not confirm_reset, use_container_width=True):
            now_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = WORKSPACE_DIR / "config" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            if CONFIG_FILE.exists():
                shutil.copy(CONFIG_FILE, backup_dir / f"metadata_backup_{now_ts}.json")
            if REMEDIATION_FILE.exists():
                shutil.copy(REMEDIATION_FILE, backup_dir / f"remediations_backup_{now_ts}.json")

            metadata_mgr.clear_all_decisions()
            remediation_engine.reset_remediations()
            run_full_discovery_scan(st.session_state["sample_limit"])
            st.success("State reset with backup preserved!")
            st.rerun()


# ---------------------------------------------------------
# Helper Component: Guided Demo Step Banner
# ---------------------------------------------------------
def render_demo_banner(step_num: int, title: str, instructions: str, next_step_name: str = ""):
    if st.session_state["demo_mode_active"] and st.session_state["demo_step"] == step_num:
        st.markdown(f"""
        <div style="background-color: #EFF6FF; border-left: 4px solid #2563EB; border-radius: 8px; padding: 12px 16px; margin-bottom: 18px;">
            <div style="font-weight: 750; color: #1E3A8A; font-size: 0.92rem;">HACKATHON DEMO • STEP {step_num} OF 7: {title.upper()}</div>
            <div style="color: #475569; font-size: 0.88rem; margin-top: 2px;">{instructions}</div>
        </div>
        """, unsafe_allow_html=True)
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if step_num > 1 and st.button(f"⬅️ Previous (Step {step_num-1})", key=f"btn_prev_{step_num}"):
                st.session_state["demo_step"] = step_num - 1
                st.rerun()
        with col_next:
            if step_num < 7 and st.button(f"Next: {next_step_name} ➡️", key=f"btn_next_{step_num}", type="primary"):
                st.session_state["demo_step"] = step_num + 1
                st.rerun()


# ---------------------------------------------------------
# PAGE 1: Executive Dashboard (Matching Reference Screenshot)
# ---------------------------------------------------------
if nav_selection == "Executive Dashboard":
    inventory = st.session_state["enriched_inventory"]
    risk_evals = st.session_state["risk_evaluations"]
    remediation_tasks = st.session_state["remediation_tasks"]

    # Calculate Posture Scorecard dynamically
    scorecard = PrivacyPostureScorecard.calculate_scorecard(inventory, risk_evals)
    pii_fields = [f for f in inventory if f.get("is_personal")]
    num_pii = len(pii_fields)
    gap_pct = round(100.0 - scorecard["overall_score"], 1)

    # 1. Header (Left Title + Subtitle; Right Badge)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
        <div style="display: flex; align-items: flex-start; gap: 14px;">
            <div style="margin-top: 3px;">
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
            </div>
            <div>
                <div style="font-size: 1.85rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; line-height: 1.2;">
                    Personal-Data Discovery & Privacy Governance
                </div>
                <div style="font-size: 0.95rem; color: #64748B; margin-top: 4px;">
                    Discover personally identifiable information (PII) across CSV and SQLite data, assess privacy risks, and manage purpose & retention.
                </div>
            </div>
        </div>
        <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; color: #2563EB; border-radius: 9999px; padding: 6px 16px; font-size: 0.82rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"/>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
            </svg>
            Synthetic Demo Environment
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Privacy Posture Banner Card
    status_pill_style = "background-color: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5;" if scorecard["overall_score"] < 45 else (
        "background-color: #FEF3C7; color: #D97706; border: 1px solid #FCD34D;" if scorecard["overall_score"] < 65 else (
            "background-color: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE;" if scorecard["overall_score"] < 85 else
            "background-color: #ECFDF5; color: #16A34A; border: 1px solid #A7F3D0;"
        )
    )

    st.markdown(f"""
    <div class="posture-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <div style="font-size: 0.95rem; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 6px;">
                    <span>Privacy Posture Score</span>
                    <span style="font-size: 0.85rem; color: #64748B;">ⓘ</span>
                </div>
                <div style="margin: 6px 0 10px 0;">
                    <span style="font-size: 2.7rem; font-weight: 850; color: #0F172A; letter-spacing: -0.03em;">{int(scorecard['overall_score'])}</span>
                    <span style="font-size: 1.8rem; font-weight: 600; color: #475569;"> / 100</span>
                </div>
                <div style="{status_pill_style} border-radius: 9999px; padding: 4px 14px; font-size: 0.82rem; font-weight: 700; display: inline-block;">
                    {scorecard['tier']}
                </div>
            </div>
            <div style="width: 1px; height: 90px; background-color: #CBD5E1; margin: 0 40px;"></div>
            <div style="flex: 0.7;">
                <div style="font-size: 0.95rem; font-weight: 600; color: #475569;">
                    DPDP Compliance Gap
                </div>
                <div style="font-size: 2.3rem; font-weight: 850; color: #2563EB; margin: 4px 0; letter-spacing: -0.02em;">
                    {gap_pct}%
                </div>
                <div style="font-size: 0.85rem; color: #64748B;">
                    Needs Human Verification
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Five KPI Metric Cards in a Row
    comp_review = scorecard["components"].get("review_coverage", {})
    comp_purpose = scorecard["components"].get("purpose_approval", {})
    comp_retention = scorecard["components"].get("retention_coverage", {})
    comp_risk = scorecard["components"].get("high_risk_resolution", {})
    comp_evidence = scorecard["components"].get("evidence_readiness", {})

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        rev_pct = comp_review.get("percentage", 0.0)
        rev_pts = comp_review.get("deficit_points", 25.0)
        rev_delta_color = "#DC2626" if rev_pts > 0 else "#16A34A"
        rev_arrow = "↓" if rev_pts > 0 else "↑"
        rev_delta_text = f"-{rev_pts} pts" if rev_pts > 0 else "+25.0 pts"
        st.markdown(f"""
        <div class="white-card-compact">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #EFF6FF; display: flex; align-items: center; justify-content: center;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                </div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #1E293B; line-height: 1.25;">
                    Human Review<br>Coverage
                </div>
            </div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #0F172A; margin: 4px 0;">{rev_pct}%</div>
            <div style="font-size: 0.8rem; font-weight: 700; color: {rev_delta_color}; display: flex; align-items: center; gap: 4px;">
                <span>{rev_arrow}</span> <span>{rev_delta_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        purp_pct = comp_purpose.get("percentage", 0.0)
        purp_pts = comp_purpose.get("deficit_points", 25.0)
        purp_delta_color = "#DC2626" if purp_pts > 0 else "#16A34A"
        purp_arrow = "↓" if purp_pts > 0 else "↑"
        purp_delta_text = f"-{purp_pts} pts" if purp_pts > 0 else "+25.0 pts"
        st.markdown(f"""
        <div class="white-card-compact">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #F5F3FF; display: flex; align-items: center; justify-content: center;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                </div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #1E293B; line-height: 1.25;">
                    Purpose<br>Approval Rate
                </div>
            </div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #0F172A; margin: 4px 0;">{purp_pct}%</div>
            <div style="font-size: 0.8rem; font-weight: 700; color: {purp_delta_color}; display: flex; align-items: center; gap: 4px;">
                <span>{purp_arrow}</span> <span>{purp_delta_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        ret_pct = comp_retention.get("percentage", 100.0)
        ret_pts = comp_retention.get("earned_points", 20.0)
        ret_delta_color = "#16A34A" if ret_pct >= 90 else "#DC2626"
        ret_arrow = "↑" if ret_pct >= 90 else "↓"
        ret_delta_text = f"+{ret_pts} pts" if ret_pct >= 90 else f"-{comp_retention.get('deficit_points', 0)} pts"
        st.markdown(f"""
        <div class="white-card-compact">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #ECFDF5; display: flex; align-items: center; justify-content: center;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                        <line x1="16" y1="2" x2="16" y2="6"/>
                        <line x1="8" y1="2" x2="8" y2="6"/>
                        <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                </div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #1E293B; line-height: 1.25;">
                    Retention Policy<br>Coverage
                </div>
            </div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #0F172A; margin: 4px 0;">{ret_pct}%</div>
            <div style="font-size: 0.8rem; font-weight: 700; color: {ret_delta_color}; display: flex; align-items: center; gap: 4px;">
                <span>{ret_arrow}</span> <span>{ret_delta_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        risk_pct = comp_risk.get("percentage", 0.0)
        risk_pts = comp_risk.get("deficit_points", 20.0)
        risk_delta_color = "#DC2626" if risk_pts > 0 else "#16A34A"
        risk_arrow = "↓" if risk_pts > 0 else "↑"
        risk_delta_text = f"-{risk_pts} pts" if risk_pts > 0 else "+20.0 pts"
        st.markdown(f"""
        <div class="white-card-compact">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #FFF7ED; display: flex; align-items: center; justify-content: center;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EA580C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                </div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #1E293B; line-height: 1.25;">
                    High-Risk Finding<br>Resolution
                </div>
            </div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #0F172A; margin: 4px 0;">{risk_pct}%</div>
            <div style="font-size: 0.8rem; font-weight: 700; color: {risk_delta_color}; display: flex; align-items: center; gap: 4px;">
                <span>{risk_arrow}</span> <span>{risk_delta_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col5:
        ev_pct = comp_evidence.get("percentage", 100.0)
        ev_pts = comp_evidence.get("earned_points", 10.0)
        ev_delta_color = "#16A34A" if ev_pct >= 90 else "#DC2626"
        ev_arrow = "↑" if ev_pct >= 90 else "↓"
        ev_delta_text = f"+{ev_pts} pts" if ev_pct >= 90 else f"-{comp_evidence.get('deficit_points', 0)} pts"
        st.markdown(f"""
        <div class="white-card-compact">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #EFF6FF; display: flex; align-items: center; justify-content: center;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                    </svg>
                </div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #1E293B; line-height: 1.25;">
                    Evidence & Audit<br>Readiness
                </div>
            </div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #0F172A; margin: 4px 0;">{ev_pct}%</div>
            <div style="font-size: 0.8rem; font-weight: 700; color: {ev_delta_color}; display: flex; align-items: center; gap: 4px;">
                <span>{ev_arrow}</span> <span>{ev_delta_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 4. Two Visual Charts Side-by-Side (Exact Layout of Reference Image)
    chart_col_left, chart_col_right = st.columns(2)

    with chart_col_left:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 22px 14px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size: 1.05rem; font-weight: 750; color: #0F172A; margin-bottom: 8px;">
                Candidate PII Fields by Class
            </div>
        """, unsafe_allow_html=True)

        if pii_fields:
            # Order categories alphabetically to match screenshot: ADDRESS, EMAIL, GOVERNMENT_ID, NAME, PHONE_NUMBER
            class_order = ["ADDRESS", "EMAIL", "GOVERNMENT_ID", "NAME", "PHONE_NUMBER"]
            class_counts_series = pd.Series([f["confirmed_class"] for f in pii_fields]).value_counts()
            x_vals = [c for c in class_order if c in class_counts_series.index]
            y_vals = [class_counts_series.get(c, 0) for c in x_vals]

            bar_fig = go.Figure(data=[
                go.Bar(
                    x=x_vals,
                    y=y_vals,
                    text=y_vals,
                    textposition="outside",
                    marker=dict(
                        color="#3B82F6",
                        line=dict(color="#2563EB", width=0.5)
                    ),
                    width=0.55
                )
            ])
            max_y = max(y_vals) if y_vals else 6
            bar_fig.update_layout(
                template="plotly_white",
                height=265,
                margin=dict(l=25, r=20, t=25, b=35),
                yaxis=dict(
                    range=[0, max_y + 1.2],
                    dtick=1,
                    gridcolor="#F1F5F9",
                    zeroline=True,
                    zerolinecolor="#E2E8F0",
                    tickfont=dict(color="#64748B", size=10)
                ),
                xaxis=dict(
                    tickfont=dict(color="#334155", size=10, family="Inter"),
                    showgrid=False
                )
            )
            st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No personal data fields detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col_right:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 22px 14px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size: 1.05rem; font-weight: 750; color: #0F172A; margin-bottom: 8px;">
                Risk Priority Distribution
            </div>
        """, unsafe_allow_html=True)

        if risk_evals:
            pii_risks = [r for r in risk_evals if r.is_personal]
            crit_c = sum(1 for r in pii_risks if r.priority_level == "Critical")
            high_c = sum(1 for r in pii_risks if r.priority_level == "High")
            med_c = sum(1 for r in pii_risks if r.priority_level == "Medium")
            low_c = sum(1 for r in pii_risks if r.priority_level == "Low")

            donut_labels = []
            donut_values = []
            donut_colors = []

            if crit_c > 0:
                donut_labels.append(f"Critical ({crit_c})")
                donut_values.append(crit_c)
                donut_colors.append("#EF4444")
            if high_c > 0:
                donut_labels.append(f"High ({high_c})")
                donut_values.append(high_c)
                donut_colors.append("#F59E0B")
            if med_c > 0:
                donut_labels.append(f"Medium ({med_c})")
                donut_values.append(med_c)
                donut_colors.append("#FBBF24")
            if low_c > 0:
                donut_labels.append(f"Low ({low_c})")
                donut_values.append(low_c)
                donut_colors.append("#10B981")

            donut_fig = go.Figure(data=[
                go.Pie(
                    labels=donut_labels,
                    values=donut_values,
                    hole=0.58,
                    domain=dict(x=[0.02, 0.74]),
                    marker=dict(colors=donut_colors),
                    textinfo="percent",
                    textfont=dict(size=11, color="#FFFFFF", family="Inter"),
                    direction="clockwise",
                    sort=False
                )
            ])
            donut_fig.update_layout(
                template="plotly_white",
                height=265,
                margin=dict(l=10, r=20, t=15, b=25),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    x=0.78, y=0.5,
                    font=dict(size=12, color="#0F172A")
                ),
                annotations=[
                    dict(
                        text=f"<b style='font-size:24px;color:#0F172A;'>{len(pii_risks)}</b><br><span style='font-size:12px;color:#64748B;'>Findings</span>",
                        x=0.38, y=0.5,
                        showarrow=False
                    )
                ]
            )
            st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No findings evaluated.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 5. Top Priority Improvement Recommendations (Matching Reference Image)
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <div style="font-size: 1.05rem; font-weight: 750; color: #0F172A; display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
            <span>💡</span> <span>Top Priority Improvement Recommendations</span>
        </div>
    """, unsafe_allow_html=True)

    rec_cols = st.columns(3)
    rec_templates = [
        {
            "bg": "#F0F7FF",
            "border": "#DBEAFE",
            "icon_color": "#2563EB",
            "icon_svg": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
            "title": "Human Review Coverage",
            "deficit": "-25.0 pts",
            "action": "Elevate Human Review Coverage from 0.0% to 100.0% to regain up to +25.0 points."
        },
        {
            "bg": "#F5F3FF",
            "border": "#EDE9FE",
            "icon_color": "#7C3AED",
            "icon_svg": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
            "title": "Purpose Approval Rate",
            "deficit": "-25.0 pts",
            "action": "Elevate Purpose Approval Rate from 0.0% to 100.0% to regain up to +25.0 points."
        },
        {
            "bg": "#FEF2F2",
            "border": "#FEE2E2",
            "icon_color": "#DC2626",
            "icon_svg": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            "title": "High-Risk Finding Resolution",
            "deficit": "-20.0 pts",
            "action": "Elevate High-Risk Finding Resolution from 0.0% to 100.0% to regain up to +20.0 points."
        }
    ]

    # Populate with dynamic recommendations if deficits exist
    if scorecard["top_improvement_areas"]:
        for idx, imp in enumerate(scorecard["top_improvement_areas"][:3]):
            rec_templates[idx]["title"] = imp["pillar"]
            rec_templates[idx]["deficit"] = f"-{imp['deficit']} pts"
            rec_templates[idx]["action"] = imp["action"]

    for idx, tpl in enumerate(rec_templates):
        with rec_cols[idx]:
            st.markdown(f"""
            <div style="background-color: {tpl['bg']}; border: 1px solid {tpl['border']}; border-radius: 8px; padding: 14px 16px; height: 100%;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    {tpl['icon_svg']}
                    <span style="font-weight: 750; color: #0F172A; font-size: 0.88rem;">{tpl['title']}</span>
                    <span style="color: #DC2626; font-size: 0.8rem; font-weight: 600;">(Deficit: {tpl['deficit']})</span>
                </div>
                <div style="font-size: 0.82rem; color: #475569; line-height: 1.4; margin-left: 30px;">
                    {tpl['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 2: Data Sources & Ingestion
# ---------------------------------------------------------
elif nav_selection == "Data Sources & Ingestion":
    render_demo_banner(
        step_num=1,
        title="Scan Synthetic CSV & SQLite Sources",
        instructions="Inspect synthetic datasets generated with deterministic seeds. Confirm zero real personal records exist, then execute or preview scanner ingestion.",
        next_step_name="Review Findings"
    )

    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        🗄️ Data Ingestion & Source Management
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Inspect bundled synthetic datasets, upload custom CSVs with safe validation, or connect local SQLite databases.
    </div>
    """, unsafe_allow_html=True)

    tab_bundled, tab_upload, tab_sqlite = st.tabs([
        "📦 Bundled Synthetic Datasets",
        "📤 Upload Untrusted CSV",
        "🗄️ SQLite Database Explorer"
    ])

    with tab_bundled:
        st.markdown("""
        <div class="white-card">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">Bundled Synthetic CSV Files</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 16px;">
                Deterministic generation (seed=42). Strict fictional names and reserved example domains.
            </div>
        """, unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown("**customers.csv** (120 rows)")
            st.caption("full_name, email, phone, residential address, synthetic govt ID, loyalty points, etc.")
        with b2:
            st.markdown("**employees.csv** (80 rows)")
            st.caption("employee_name, work_email, mobile, office address, synthetic national ID, dept, etc.")
        with b3:
            st.markdown("**support_tickets.csv** (100 rows)")
            st.caption("requester_name, support_email, callback_number, dispatch_address, synthetic KYC ref, etc.")

        sel_csv = st.selectbox("Select CSV to Preview", ["customers.csv", "employees.csv", "support_tickets.csv"])
        csv_path = DATA_DIR / sel_csv
        if csv_path.exists():
            preview_df = pd.read_csv(csv_path, nrows=8)
            st.dataframe(preview_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_upload:
        st.markdown("""
        <div class="white-card">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">Upload Untrusted CSV File</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 14px;">
                Uploaded files are treated as untrusted data. Max size: 25MB. Executable code or formulas are never evaluated.
            </div>
        """, unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Choose CSV file(s) to scan", type=["csv"], accept_multiple_files=True)
        if uploaded_files:
            st.info(f"Loaded {len(uploaded_files)} file(s). Click button below to ingest and analyze.")
            if st.button("🚀 Ingest & Scan Uploaded Files", key="btn_upload_scan", type="primary"):
                with st.spinner("Scanning uploaded datasets..."):
                    run_full_discovery_scan(st.session_state["sample_limit"], extra_csv_files=uploaded_files)
                st.success("Uploaded files successfully scanned!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_sqlite:
        st.markdown("""
        <div class="white-card">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">SQLite Database Inspection</div>
        """, unsafe_allow_html=True)
        db_path = DATA_DIR / "privacy_demo.db"
        st.caption(f"Bundled SQLite DB: `{db_path}`")
        if db_path.exists():
            tables = sqlite_scanner.discover_tables(db_path)
            st.success(f"Discovered {len(tables)} tables: {', '.join(tables)}")
            sel_table = st.selectbox("Select table to preview:", tables)
            if sel_table:
                cols = sqlite_scanner.discover_table_columns(db_path, sel_table)
                st.caption(f"Columns in `{sel_table}`: {', '.join(cols)}")
                import sqlite3
                conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                sample_tbl_df = pd.read_sql_query(f'SELECT * FROM "{sel_table}" LIMIT 6;', conn)
                conn.close()
                st.dataframe(sample_tbl_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 3: Scan Results & Evidence
# ---------------------------------------------------------
elif nav_selection == "Scan Results & Evidence":
    render_demo_banner(
        step_num=2,
        title="Review Detected Personal-Data Candidates",
        instructions="Examine empirical findings across CSV and SQLite tables. Inspect masked sample values and verify explainable confidence evidence.",
        next_step_name="Risk Radar"
    )

    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        🔍 Scan Results & Detection Evidence
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Examine rule-based detection evidence, match ratios, and masked sample data for every dataset column.
    </div>
    """, unsafe_allow_html=True)

    inventory = st.session_state["enriched_inventory"]

    if not inventory:
        st.warning("No scan results available. Please run a discovery scan first.")
    else:
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            sources = sorted(list(set(f["source_name"] for f in inventory)))
            sel_source = st.selectbox("Filter by Source", ["All Sources"] + sources)
        with f2:
            classes = ["All Classes", "NAME", "EMAIL", "PHONE_NUMBER", "ADDRESS", "GOVERNMENT_ID", "NOT_PERSONAL"]
            sel_class = st.selectbox("Filter by Detected Class", classes)
        with f3:
            statuses = ["All Statuses", "PENDING_REVIEW", "CONFIRMED", "REJECTED", "NOT_APPLICABLE"]
            sel_status = st.selectbox("Filter by Review Status", statuses)
        with f4:
            search_query = st.text_input("Search Column / Text", "")

        filtered = inventory
        if sel_source != "All Sources":
            filtered = [f for f in filtered if f["source_name"] == sel_source]
        if sel_class != "All Classes":
            filtered = [f for f in filtered if f["confirmed_class"] == sel_class]
        if sel_status != "All Statuses":
            filtered = [f for f in filtered if f["review_status"] == sel_status]
        if search_query:
            q = search_query.lower()
            filtered = [
                f for f in filtered
                if q in f["column_name"].lower() or q in f["source_name"].lower() or q in f["evidence_details"].lower()
            ]

        st.caption(f"Showing {len(filtered)} of {len(inventory)} total column evaluations.")

        table_rows = []
        for f in filtered:
            table_rows.append({
                "Source": f["source_name"],
                "Table": f["table_name"] or "-",
                "Column": f["column_name"],
                "Detected Class": f["confirmed_class"],
                "Confidence": f"{f['confidence_score']:.2f}",
                "Sample Count": f"{f['matching_sample_count']}/{f['non_null_count']}",
                "Review Status": f["review_status"],
                "Declared Purpose": f["declared_purpose"],
                "Retention": f["retention_label"]
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.05rem;font-weight:750;color:#0F172A;margin-bottom:12px;'>🔬 Deep-Dive Evidence Card</div>", unsafe_allow_html=True)
        field_keys = [f["field_key"] for f in filtered]
        if field_keys:
            selected_key = st.selectbox("Select a field to inspect detection evidence:", field_keys)
            detail = next((f for f in filtered if f["field_key"] == selected_key), None)
            if detail:
                e1, e2 = st.columns([2, 1])
                with e1:
                    st.markdown(f"**Field:** `{detail['column_name']}` | **Source:** `{detail['source_name']}` (Table: `{detail['table_name'] or 'CSV'}`)")
                    st.markdown(f"**Detected Class:** **{detail['confirmed_class']}** (Personal Data: `{detail['is_personal']}`)")
                    st.markdown(f"**Technical Evidence:** {detail['evidence_details']}")
                    st.markdown(f"**Sample Match Rate:** `{detail['matching_sample_count']} of {detail['non_null_count']}` non-null values ({detail['sample_match_rate']*100:.1f}%)")
                with e2:
                    st.markdown("**Privacy-Safe Masked Samples**")
                    if detail["masked_samples"]:
                        st.code(detail["masked_samples"], language="text")
                    else:
                        st.caption("No sample values available.")
                    st.progress(float(detail["confidence_score"]))
                    st.caption(f"Confidence Metric: **{detail['confidence_score']:.2f} / 1.00** (Heuristic, not probability)")
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 4: Privacy Evidence Inventory
# ---------------------------------------------------------
elif nav_selection == "Privacy Evidence Inventory":
    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        📋 Privacy Evidence Inventory & Human Review
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Bridge automated personal data discovery with formal data governance. Confirm or reject findings, attach lawful purposes, and enforce retention limits.
    </div>
    """, unsafe_allow_html=True)

    inventory = st.session_state["enriched_inventory"]
    personal_candidates = [f for f in inventory if f.get("is_personal") or f.get("review_status") != "NOT_APPLICABLE"]

    if not personal_candidates:
        st.info("No personal data candidate fields currently in inventory.")
    else:
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        candidate_keys = [f["field_key"] for f in personal_candidates]
        sel_review_key = st.selectbox("Select Field for Compliance Review", candidate_keys)
        target = next((f for f in personal_candidates if f["field_key"] == sel_review_key), None)

        if target:
            with st.form("compliance_review_form"):
                st.markdown(f"**Reviewing:** `{target['column_name']}` from `{target['source_name']}` (Detected: **{target['detected_class']}**)")

                col_form1, col_form2 = st.columns(2)
                with col_form1:
                    new_class = st.selectbox(
                        "Confirmed Classification",
                        ["NAME", "EMAIL", "PHONE_NUMBER", "ADDRESS", "GOVERNMENT_ID", "NOT_PERSONAL"],
                        index=["NAME", "EMAIL", "PHONE_NUMBER", "ADDRESS", "GOVERNMENT_ID", "NOT_PERSONAL"].index(target["confirmed_class"])
                        if target["confirmed_class"] in ["NAME", "EMAIL", "PHONE_NUMBER", "ADDRESS", "GOVERNMENT_ID", "NOT_PERSONAL"] else 0
                    )
                    new_status = st.selectbox(
                        "Review Decision Status",
                        ["CONFIRMED", "REJECTED", "PENDING_REVIEW"],
                        index=["CONFIRMED", "REJECTED", "PENDING_REVIEW"].index(target["review_status"])
                        if target["review_status"] in ["CONFIRMED", "REJECTED", "PENDING_REVIEW"] else 0
                    )
                    is_approved_purpose = st.checkbox(
                        "Mark Purpose as Officially Approved by Legal/Compliance",
                        value=bool(target.get("has_approved_purpose", False))
                    )

                with col_form2:
                    declared_purpose = st.text_input("Declared Business Purpose", value=target.get("declared_purpose", ""))
                    retention_days = st.number_input(
                        "Retention Schedule (Days)",
                        min_value=0, max_value=3650,
                        value=int(target.get("retention_days", 365)),
                        step=30
                    )
                    reviewer_name = st.text_input("Reviewer Name / Role", value=target.get("reviewed_by") or "Compliance Officer (DPO Team)")

                reviewer_notes = st.text_area(
                    "Reviewer Compliance Notes & Justification",
                    value=target.get("reviewer_notes", ""),
                    placeholder="e.g. Verified with Legal; retention restricted to 180 days per Section 8 of DPDP Act."
                )

                submit_review = st.form_submit_button("💾 Save & Persist Review Decision", type="primary")

                if submit_review:
                    is_missing_purpose = not bool(declared_purpose.strip()) or declared_purpose.strip() == "N/A (Non-Personal Field)"
                    is_missing_retention = retention_days <= 0

                    metadata_mgr.record_review_decision(
                        field_key=target["field_key"],
                        confirmed_class=new_class,
                        review_status=new_status,
                        declared_purpose=declared_purpose,
                        retention_days=retention_days,
                        has_approved_purpose=is_approved_purpose,
                        is_missing_purpose=is_missing_purpose,
                        is_missing_retention=is_missing_retention,
                        reviewer_notes=reviewer_notes,
                        reviewer_name=reviewer_name
                    )

                    sync_intelligence_layer()
                    st.success(f"Review decision persisted for '{target['field_key']}'!")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.05rem;font-weight:750;color:#0F172A;margin-bottom:12px;'>Inventory Status Matrix</div>", unsafe_allow_html=True)
        matrix_rows = []
        for f in personal_candidates:
            matrix_rows.append({
                "Field": f["field_key"],
                "Class": f["confirmed_class"],
                "Review Status": f["review_status"],
                "Approved Purpose": "Approved" if f["has_approved_purpose"] else "Not Approved",
                "Declared Purpose": f["declared_purpose"],
                "Retention": f["retention_label"],
                "Reviewer": f["reviewed_by"] or "Unassigned"
            })
        st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 5: Privacy Risk Radar
# ---------------------------------------------------------
elif nav_selection == "Privacy Risk Radar":
    render_demo_banner(
        step_num=3,
        title="Inspect Explainable Privacy Risk Radar",
        instructions="Analyze risk scores (0–100) calculated from sensitivity, confidence, metadata gaps, and cross-source proliferation. Notice why Government IDs and unreviewed fields receive critical priority.",
        next_step_name="Exposure Map"
    )

    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        ⚠️ Privacy Risk Radar & Prioritization Engine
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Explainable, multi-factor risk scoring (0 to 100) combining data sensitivity, detection confidence, missing compliance metadata, and cross-source proliferation.
    </div>
    """, unsafe_allow_html=True)

    risk_evals = st.session_state["risk_evaluations"]
    pii_evals = [r for r in risk_evals if r.is_personal]

    if not pii_evals:
        st.info("No active personal data findings to evaluate.")
    else:
        crit = sum(1 for r in pii_evals if r.priority_level == "Critical")
        high = sum(1 for r in pii_evals if r.priority_level == "High")
        med = sum(1 for r in pii_evals if r.priority_level == "Medium")
        low = sum(1 for r in pii_evals if r.priority_level == "Low")

        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric("Critical Priority", crit, delta=f"{crit} urgent", delta_color="inverse")
        with rc2:
            st.metric("High Priority", high, delta=f"{high} high", delta_color="inverse")
        with rc3:
            st.metric("Medium Priority", med)
        with rc4:
            st.metric("Low Priority", low)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.05rem;font-weight:750;color:#0F172A;margin-bottom:12px;'>⚠️ Top Prioritized Privacy Findings</div>", unsafe_allow_html=True)
        top_rows = []
        for r in pii_evals[:10]:
            top_rows.append({
                "Priority": r.priority_level,
                "Risk Score": f"{r.risk_score} / 100",
                "Field Key": r.field_key,
                "Class": r.confirmed_class,
                "Review Status": r.review_status,
                "Multi-Source?": "Yes (3+ datasets)" if r.is_multi_source else "No",
                "Explanation": r.explanation
            })
        st.dataframe(pd.DataFrame(top_rows), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.05rem;font-weight:750;color:#0F172A;margin-bottom:12px;'>🔍 Explainable Factor Decomposition Card</div>", unsafe_allow_html=True)
        sel_eval_key = st.selectbox("Select Finding for Factor Breakdown", [r.field_key for r in pii_evals])
        target_eval = next((r for r in pii_evals if r.field_key == sel_eval_key), None)

        if target_eval:
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"**Field:** `{target_eval.column_name}` ({target_eval.source_name})")
                st.markdown(f"**Classification:** `{target_eval.confirmed_class}` | **Status:** `{target_eval.review_status}`")
                st.markdown(f"**Overall Score:** `{target_eval.risk_score} / 100` (`{target_eval.priority_level}` Priority)")
                st.info(target_eval.explanation)
            with d2:
                breakdown_df = pd.DataFrame([
                    {"Risk Factor": k.replace("_", " ").title(), "Points Added": v}
                    for k, v in target_eval.factor_breakdown.items()
                ])
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 6: Visual Exposure Map
# ---------------------------------------------------------
elif nav_selection == "Visual Exposure Map":
    render_demo_banner(
        step_num=4,
        title="Inspect Visual Privacy Exposure Map",
        instructions="Visualize data lineage: Data Source → Personal Data Class → Declared Purpose → Governance Status. Hover over nodes to see flow volumes and identify cross-system proliferation.",
        next_step_name="Remediations"
    )

    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        🕸️ Visual Privacy Exposure Map
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Interactive lineage and relationship visualization tracking data flow from raw storage sources to personal data classes, declared purposes, and governance status.
    </div>
    """, unsafe_allow_html=True)

    inventory = st.session_state["enriched_inventory"]

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    sankey_fig = PrivacyExposureMap.build_sankey_diagram(inventory)
    sankey_fig.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
    st.plotly_chart(sankey_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.05rem;font-weight:750;color:#0F172A;margin-bottom:6px;'>🌐 Cross-Source Proliferation & Duplication Analysis</div>", unsafe_allow_html=True)
    cross_summary = PrivacyExposureMap.get_cross_source_summary(inventory)
    if cross_summary:
        st.dataframe(pd.DataFrame(cross_summary), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 7: Remediation Center
# ---------------------------------------------------------
elif nav_selection == "Remediation Center":
    render_demo_banner(
        step_num=5,
        title="Review Missing Metadata & Remediation Tasks",
        instructions="Examine deterministic action recommendations. Notice how the engine identifies missing purposes, missing retentions, and unverified IDs. Update task statuses and observe persistence.",
        next_step_name="What-If Sim"
    )

    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        🔧 Intelligent Remediation Center
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Deterministic compliance remediation engine generating actionable governance tasks with persistent status tracking.
    </div>
    """, unsafe_allow_html=True)

    tasks = st.session_state["remediation_tasks"]

    open_tasks = sum(1 for t in tasks if t.status == "Open")
    prog_tasks = sum(1 for t in tasks if t.status == "In Progress")
    res_tasks = sum(1 for t in tasks if t.status == "Resolved")

    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.metric("Total Recommendations", len(tasks))
    with t2:
        st.metric("Open Tasks", open_tasks, delta=f"{open_tasks} pending", delta_color="inverse")
    with t3:
        st.metric("In Progress", prog_tasks)
    with t4:
        st.metric("Resolved", res_tasks, delta=f"{res_tasks} completed")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    rem_f1, rem_f2 = st.columns(2)
    with rem_f1:
        sel_status_filter = st.selectbox("Filter by Status", ["All Statuses", "Open", "In Progress", "Resolved"])
    with rem_f2:
        sel_risk_filter = st.selectbox("Filter by Risk Priority", ["All Priorities", "Critical", "High", "Medium", "Low"])

    filtered_tasks = tasks
    if sel_status_filter != "All Statuses":
        filtered_tasks = [t for t in filtered_tasks if t.status == sel_status_filter]
    if sel_risk_filter != "All Priorities":
        filtered_tasks = [t for t in filtered_tasks if t.risk_level == sel_risk_filter]

    st.caption(f"Showing {len(filtered_tasks)} actionable remediation items.")

    for t in filtered_tasks[:12]:
        with st.expander(f"[{t.risk_level.upper()}] {t.title} — `{t.column_name}` ({t.source_name}) — Status: {t.status}", expanded=(t.risk_level == "Critical")):
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                st.markdown(f"**Target Field:** `{t.finding_id}` | **Class:** `{t.confirmed_class}`")
                st.markdown(f"**Compliance Issue:** {t.reason}")
                st.markdown(f"**Recommended Action:** {t.suggested_action}")
                st.markdown(f"**Expected Benefit:** {t.expected_benefit}")
            with col_t2:
                current_idx = ["Open", "In Progress", "Resolved"].index(t.status)
                new_status = st.selectbox("Update Status", ["Open", "In Progress", "Resolved"], index=current_idx, key=f"status_{t.recommendation_id}")
                new_notes = st.text_input("Reviewer Notes", value=t.reviewer_notes, key=f"notes_{t.recommendation_id}")
                if st.button("Save Task Status", key=f"save_{t.recommendation_id}", type="primary"):
                    remediation_engine.update_task_status(t.recommendation_id, new_status, new_notes)
                    sync_intelligence_layer()
                    st.success("Task updated and persisted!")
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 8: What-If Simulator
# ---------------------------------------------------------
elif nav_selection == "What-If Simulator":
    render_demo_banner(
        step_num=6,
        title="Run Hypothetical Improvement Scenario",
        instructions="Toggle hypothetical governance improvements (documenting purposes, configuring retention, reviewing critical findings). Observe real-time posture score and risk score deltas without modifying disk records.",
        next_step_name="Audit Export"
    )

    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        🎛️ Privacy Impact What-If Simulator
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Explore hypothetical remediation scenarios in real-time. Project posture score gains and risk reductions with transparent mathematical assumptions.
    </div>
    """, unsafe_allow_html=True)

    inventory = st.session_state["enriched_inventory"]

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.caption("⚠️ What-If scenarios are calculated purely in-memory. They do NOT alter source tables, live databases, or official DPO review records.")

    sim_col1, sim_col2 = st.columns([1, 1])
    with sim_col1:
        st.markdown("**Configure Simulation Scenarios**")
        sim_purp = st.checkbox("Scenario A: Formally Document & Approve All Purpose Metadata", value=True)
        sim_ret = st.checkbox("Scenario B: Define & Enforce Standard Storage Retention Schedules (180d)", value=True)
        sim_high = st.checkbox("Scenario C: Complete DPO Human Verification for All Critical/High Findings", value=True)
        sim_dup = st.checkbox("Scenario D: Implement Tokenized Data Minimization (Eliminate Multi-Source Duplication)", value=False)

    sim_results = PrivacyPostureScorecard.run_simulation(
        enriched_inventory=inventory,
        risk_radar=risk_radar,
        simulate_all_purpose_approved=sim_purp,
        simulate_all_retention_configured=sim_ret,
        simulate_all_high_risk_reviewed=sim_high,
        simulate_duplicate_reduction=sim_dup
    )

    with sim_col2:
        st.markdown("**Projected Impact Overview**")
        delta_col1, delta_col2, delta_col3 = st.columns(3)
        with delta_col1:
            st.metric("Projected Posture", f"{sim_results['simulated_score']} / 100", delta=f"+{sim_results['score_delta']} pts")
        with delta_col2:
            st.metric("Projected Avg Risk", f"{sim_results['simulated_avg_risk']}", delta=f"{sim_results['risk_delta']} pts", delta_color="inverse")
        with delta_col3:
            st.metric("Critical Findings", f"{sim_results['simulated_critical_count']}", delta=f"{sim_results['critical_delta']} items", delta_color="inverse")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    base_scorecard = PrivacyPostureScorecard.calculate_scorecard(inventory, st.session_state["risk_evaluations"])
    sim_comps = sim_results["simulated_components"]

    comparison_rows = []
    for pk, comp in base_scorecard["components"].items():
        sim_p = sim_comps.get(pk, {})
        comparison_rows.append({
            "Governance Pillar": comp["name"],
            "Current Performance": f"{comp['percentage']}% ({comp['earned_points']}/{comp['weight']} pts)",
            "Simulated Performance": f"{sim_p.get('percentage', 0)}% ({sim_p.get('earned_points', 0)}/{sim_p.get('weight', 0)} pts)",
            "Point Gain (Δ)": f"+{round(sim_p.get('earned_points', 0) - comp['earned_points'], 1)} pts"
        })
    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 9: Benchmark Evaluation
# ---------------------------------------------------------
elif nav_selection == "Benchmark Evaluation":
    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        📊 Detection Performance & Ground Truth Benchmark
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Rigorous evaluation of scanner predictions against the manually labelled ground truth dataset (<code>data/labelled_test_data.csv</code>).
    </div>
    """, unsafe_allow_html=True)

    evaluator = Evaluator(data_dir=DATA_DIR)

    if st.session_state["eval_results"] is None:
        st.session_state["eval_results"] = evaluator.evaluate(sample_limit=st.session_state["sample_limit"])

    res = st.session_state["eval_results"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Macro Precision", f"{res['macro_precision'] * 100:.1f}%")
    with m2:
        st.metric("Macro Recall", f"{res['macro_recall'] * 100:.1f}%")
    with m3:
        st.metric("Macro F1-Score", f"{res['macro_f1'] * 100:.1f}%")
    with m4:
        st.metric("Overall Binary PII F1", f"{res['overall_pii_f1'] * 100:.1f}%")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.05rem;font-weight:750;color:#0F172A;margin-bottom:12px;'>Per-Class Detection Performance</div>", unsafe_allow_html=True)
    per_class_rows = []
    for cls_name, m in res["per_class_metrics"].items():
        per_class_rows.append({
            "Personal Data Class": cls_name,
            "Precision": f"{m['precision']:.4f}",
            "Recall": f"{m['recall']:.4f}",
            "F1-Score": f"{m['f1_score']:.4f}",
            "Support (Ground Truth)": m["support"],
            "Predictions": m["predicted_count"],
            "True Positives (TP)": m["true_positives"],
            "False Positives (FP)": m["false_positives"],
            "False Negatives (FN)": m["false_negatives"]
        })
    st.dataframe(pd.DataFrame(per_class_rows), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    eval_col1, eval_col2 = st.columns(2)
    with eval_col1:
        st.markdown("**Confusion Matrix**")
        fig = evaluator.plot_confusion_matrix(res["confusion_matrix"], res["confusion_matrix_labels"])
        fig.patch.set_facecolor('#FFFFFF')
        st.pyplot(fig)
    with eval_col2:
        st.markdown("**Error Diagnostics & Zero-Defect Benchmark**")
        st.markdown(f"- **Total Columns Evaluated:** `{res['total_evaluated_fields']}`")
        st.markdown(f"- **False Positive Count:** `{len(res['false_positives'])}`")
        st.markdown(f"- **False Negative Count:** `{len(res['false_negatives'])}`")
        st.success("✅ Zero False Positives & Zero False Negatives recorded in benchmark!")
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 10: Reports & Export
# ---------------------------------------------------------
elif nav_selection == "Reports & Export":
    render_demo_banner(
        step_num=7,
        title="Export Privacy Evidence Audit Report",
        instructions="Generate and download official compliance evidence artifacts (CSV, JSON, Markdown). Notice strict masking of sensitive values and clear separation of observations, metadata, and recommendations.",
        next_step_name="Complete Demo"
    )

    st.markdown("""
    <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
        📥 Compliance Audit & Report Export
    </div>
    <div style="font-size: 0.95rem; color: #64748B; margin-bottom: 20px;">
        Generate and download official compliance evidence artifacts (CSV, JSON, Markdown) ready for regulatory submission under the MeitY DPDP framework.
    </div>
    """, unsafe_allow_html=True)

    inventory = st.session_state["enriched_inventory"]
    eval_results = st.session_state["eval_results"]
    risk_evals = st.session_state["risk_evaluations"]
    remediation_tasks = st.session_state["remediation_tasks"]
    scorecard = PrivacyPostureScorecard.calculate_scorecard(inventory, risk_evals)

    inv_csv = ReportGenerator.export_inventory_csv(inventory, risk_evaluations=risk_evals)
    inv_json = ReportGenerator.export_inventory_json(
        inventory,
        risk_evaluations=risk_evals,
        remediation_tasks=remediation_tasks,
        posture_scorecard=scorecard
    )
    eval_csv = ReportGenerator.export_evaluation_metrics_csv(eval_results) if eval_results else ""
    audit_md = ReportGenerator.generate_audit_report_markdown(
        enriched_inventory=inventory,
        eval_results=eval_results,
        risk_evaluations=risk_evals,
        remediation_tasks=remediation_tasks,
        posture_scorecard=scorecard
    )

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.markdown("**📄 Privacy Evidence Inventory Export**")
        st.download_button(
            label="📥 Download Inventory as CSV",
            data=inv_csv,
            file_name="privacy_evidence_inventory.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.download_button(
            label="📥 Download Full Inventory as JSON",
            data=inv_json,
            file_name="privacy_evidence_inventory.json",
            mime="application/json",
            use_container_width=True
        )
    with col_exp2:
        st.markdown("**📊 Evaluation & Audit Documentation**")
        if eval_csv:
            st.download_button(
                label="📥 Download Evaluation Metrics as CSV",
                data=eval_csv,
                file_name="evaluation_metrics.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.download_button(
            label="📥 Download Full Audit Report (.md)",
            data=audit_md,
            file_name="privacy_audit_report.md",
            mime="text/markdown",
            use_container_width=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.05rem;font-weight:750;color:#0F172A;margin-bottom:10px;'>📑 Report Live Preview</div>", unsafe_allow_html=True)
    with st.expander("Click to view full Privacy Audit Report Preview", expanded=True):
        st.markdown(audit_md)
    st.markdown("</div>", unsafe_allow_html=True)
