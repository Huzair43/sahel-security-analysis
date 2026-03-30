# app/app.py
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_main_data
from utils.style import apply_global_style, page_header, stat_card

st.set_page_config(
    page_title="Sahel Conflict Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()

df = load_main_data()

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:

    # Header with real flag images
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0;">
        <div style="
            font-size: 0.7rem;
            color: #e74c3c;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 6px;
        ">CONFLICT INTELLIGENCE</div>
        <div style="
            font-size: 1.1rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.01em;
        ">Sahel Monitor</div>
    </div>
    <hr style="border-color:#2d3250; margin: 0 0 1rem 0;">
    """, unsafe_allow_html=True)

    # Real country flags via flagcdn.com
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <div style="
            font-size: 0.72rem;
            color: #606480;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        ">Coverage</div>
        <div style="display:flex; flex-direction:column; gap:6px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="https://flagcdn.com/w40/bf.png"
                     style="width:24px; border-radius:2px; border:1px solid #2d3250;">
                <span style="color:#e8e8e8; font-size:0.85rem;">Burkina Faso</span>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="https://flagcdn.com/w40/ml.png"
                     style="width:24px; border-radius:2px; border:1px solid #2d3250;">
                <span style="color:#e8e8e8; font-size:0.85rem;">Mali</span>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="https://flagcdn.com/w40/ne.png"
                     style="width:24px; border-radius:2px; border:1px solid #2d3250;">
                <span style="color:#e8e8e8; font-size:0.85rem;">Niger</span>
            </div>
        </div>
    </div>
    <hr style="border-color:#2d3250; margin: 0 0 1rem 0;">
    """, unsafe_allow_html=True)

    # Data info
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <div style="
            font-size: 0.72rem;
            color: #606480;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        ">Data</div>
        <div style="color:#a0a8c0; font-size:0.82rem; line-height:1.6;">
            Source: <a href="https://acleddata.com" target="_blank"
                style="color:#e74c3c; text-decoration:none;">ACLED</a><br>
            Period: Jan 2020 — Mar 2025<br>
            Updated: Weekly
        </div>
    </div>
    <hr style="border-color:#2d3250; margin: 0 0 1rem 0;">
    """, unsafe_allow_html=True)

    # Global filters
    st.markdown("""
    <div style="
        font-size: 0.72rem;
        color: #606480;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    ">Global Filters</div>
    """, unsafe_allow_html=True)

    selected_countries = st.multiselect(
        "Countries",
        options=["Burkina Faso", "Mali", "Niger"],
        default=["Burkina Faso", "Mali", "Niger"],
        label_visibility="collapsed",
    )

    selected_years = st.slider(
        "Year range",
        min_value=2020, max_value=2025,
        value=(2020, 2025),
        label_visibility="collapsed",
    )

    selected_event_types = st.multiselect(
        "Event types",
        options=sorted(df["event_type"].unique()),
        default=sorted(df["event_type"].unique()),
        label_visibility="collapsed",
    )

    st.session_state["countries"]   = selected_countries
    st.session_state["years"]       = selected_years
    st.session_state["event_types"] = selected_event_types

# ── Home page ────────────────────────────────────────────
page_header(
    title="Conflict Monitor",
    subtitle="Armed conflict dynamics in the Sahel — Burkina Faso, Mali, Niger",
    icon="🌍"
)

# Apply filters
df_f = df[
    (df["country"].isin(selected_countries)) &
    (df["year"].between(*selected_years)) &
    (df["event_type"].isin(selected_event_types))
]

# ── KPI row ──
col1, col2, col3, col4 = st.columns(4)
with col1:
    stat_card("Total Incidents",  f"{len(df_f):,}", color="#e74c3c")
with col2:
    stat_card("Total Fatalities", f"{df_f['fatalities'].sum():,}", color="#e67e22")
with col3:
    most_affected = (
        df_f.groupby("country")["event_id_cnty"].count().idxmax()
        if not df_f.empty else "N/A"
    )
    stat_card("Most Affected", most_affected, color="#9b59b6")
with col4:
    deadliest_type = (
        df_f.groupby("event_type")["fatalities"].sum().idxmax()
        if not df_f.empty else "N/A"
    )
    stat_card("Deadliest Type", deadliest_type, color="#3498db")

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation cards ──
st.markdown("""
<div style="
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 0.5rem;
">
    <div style="
        background: #1a1d2e;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    ">
        <div style="font-size:1.8rem;">📊</div>
        <div style="color:#fff;font-weight:600;margin-top:8px;">Overview</div>
        <div style="color:#606480;font-size:0.78rem;margin-top:4px;">
            KPIs & statistics
        </div>
    </div>
    <div style="
        background: #1a1d2e;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    ">
        <div style="font-size:1.8rem;">🗺️</div>
        <div style="color:#fff;font-weight:600;margin-top:8px;">Map</div>
        <div style="color:#606480;font-size:0.78rem;margin-top:4px;">
            Interactive incident map
        </div>
    </div>
    <div style="
        background: #1a1d2e;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    ">
        <div style="font-size:1.8rem;">📈</div>
        <div style="color:#fff;font-weight:600;margin-top:8px;">Trends</div>
        <div style="color:#606480;font-size:0.78rem;margin-top:4px;">
            Temporal analysis
        </div>
    </div>
    <div style="
        background: #1a1d2e;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    ">
        <div style="font-size:1.8rem;">🔥</div>
        <div style="color:#fff;font-weight:600;margin-top:8px;">Hotspots</div>
        <div style="color:#606480;font-size:0.78rem;margin-top:4px;">
            Most affected zones
        </div>
    </div>
</div>
""", unsafe_allow_html=True)