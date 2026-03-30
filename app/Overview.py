# app/Overview.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import (
    load_main_data, load_monthly_by_country,
    EVENT_COLORS, COUNTRY_COLORS
)
from utils.style import apply_global_style, page_header, stat_card
from utils.icons import icon

st.set_page_config(page_title="Overview", page_icon="https://img.icons8.com/ios/50/ffffff/shield.png", layout="wide")

apply_global_style()

df      = load_main_data()
monthly = load_monthly_by_country()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 0.3rem 0;">
        <div style="
            font-size: 0.7rem;
            color: #e74c3c;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 4px;
        ">SECURITY INTELLIGENCE</div>
        <div style="
            font-size: 1.1rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.01em;
        ">Sahel Security Analysis</div>
    </div>
    <hr style="border-color:#2d3250; margin: 0.8rem 0 1rem 0;">
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
        value=st.session_state.get("years", (2020, 2025)),
        label_visibility="collapsed",
        key="sidebar_years",
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Sahel Security Analysis · Built with ACLED data")

# ── Apply filters ─────────────────────────────────────────
df_f = df[
    (df["country"].isin(selected_countries)) &
    (df["year"].between(*selected_years)) &
    (df["event_type"].isin(selected_event_types))
]

monthly_f = monthly[
    (monthly["country"].isin(selected_countries)) &
    (monthly["year_month_dt"].dt.year.between(*selected_years))
]

# ── Page header ───────────────────────────────────────────
page_header(
    title="Security Analysis",
    subtitle="Armed conflict dynamics in the Sahel: Burkina Faso, Mali, Niger"
)

# ── KPI row ───────────────────────────────────────────────
st.markdown("### Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

most_affected = (
    df_f.groupby("country")["event_id_cnty"].count().idxmax()
    if not df_f.empty else "N/A"
)
deadliest_type = (
    df_f.groupby("event_type")["fatalities"].sum().idxmax()
    if not df_f.empty else "N/A"
)

with col1:
    stat_card("Total Incidents",  f"{len(df_f):,}",             color="#e74c3c")
with col2:
    stat_card("Total Fatalities", f"{df_f['fatalities'].sum():,}", color="#e67e22")
with col3:
    stat_card("Locations",        f"{df_f['location'].nunique():,}", color="#9b59b6")
with col4:
    stat_card("Most Affected",    most_affected,                 color="#3498db")
with col5:
    stat_card("Deadliest Type",   deadliest_type,                color="#2ecc71")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts row ────────────────────────────────────────────
left, right = st.columns(2)

with left:
    by_country = (
        df_f.groupby("country")
        .agg(incidents=("event_id_cnty", "count"),
             fatalities=("fatalities", "sum"))
        .reset_index()
    )
    fig1 = px.bar(
        by_country, x="country", y="incidents",
        color="country",
        color_discrete_map=COUNTRY_COLORS,
        title="Incidents by Country",
        template="plotly_dark",
        text="incidents",
        labels={"incidents": "Incidents", "country": "Country"},
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig1, use_container_width=True)

with right:
    by_type = (
        df_f.groupby("event_type")["event_id_cnty"]
        .count().reset_index()
    )
    by_type.columns = ["event_type", "incidents"]
    fig2 = px.pie(
        by_type, names="event_type", values="incidents",
        color="event_type",
        color_discrete_map=EVENT_COLORS,
        title="Distribution by Event Type",
        template="plotly_dark",
        hole=0.4,
    )
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

# ── Monthly trend ─────────────────────────────────────────
st.markdown("### Monthly Trend")
fig3 = px.line(
    monthly_f,
    x="year_month_dt", y="incidents",
    color="country",
    color_discrete_map=COUNTRY_COLORS,
    title="Monthly Incidents by Country",
    labels={
        "year_month_dt": "Date",
        "incidents":     "Incidents",
        "country":       "Country",
    },
    template="plotly_dark",
)
fig3.update_layout(hovermode="x unified", height=400)
st.plotly_chart(fig3, use_container_width=True)

# ── Navigation cards ──────────────────────────────────────
st.markdown("### Explore the Dashboard")

col1, col2, col3, col4 = st.columns(4)

cards = [
    ("map",         "Map",      "Interactive incident map"),
    ("trending-up", "Trends",   "Temporal analysis"),
    ("target",      "Hotspots", "Most affected zones"),
    ("activity",    "Bayesian", "Probabilistic model"),
]

for col, (icon_name, label, desc) in zip([col1, col2, col3, col4], cards):
    with col:
        st.markdown(f"""
        <div style="
            background: #1a1d2e;
            border: 1px solid #2d3250;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        ">
            <div style="display:flex;justify-content:center;margin-bottom:10px;">
                {icon(icon_name, size=28, color="#e74c3c")}
            </div>
            <div style="color:#fff;font-weight:600;font-size:0.95rem;">{label}</div>
            <div style="color:#606480;font-size:0.78rem;margin-top:4px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Raw data ──────────────────────────────────────────────
with st.expander("View raw data sample (50 rows)"):
    st.dataframe(
        df_f.sort_values("event_date", ascending=False).head(50),
        use_container_width=True,
    )

