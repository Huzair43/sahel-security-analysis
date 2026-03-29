import streamlit as st

from utils.data_loader import load_main_data

# --- Page config
st.set_page_config(
    page_title="Sahel Conflict Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load data once at startup
df = load_main_data()

# --- Sidebar
with st.sidebar:
    st.image("https://flagcdn.com/w40/bf.png", width=30)
    st.image("https://flagcdn.com/w40/ml.png", width=30)
    st.image("https://flagcdn.com/w40/ne.png", width=30)

    st.markdown("## 🌍 Sahel Conflict Monitor")
    st.markdown("---")

    st.markdown("**Data source:** [ACLED](https://acleddata.com)")
    st.markdown("**Period:** Jan 2020 — Mar 2025")
    st.markdown("**Countries:** Burkina Faso, Mali, Niger")
    st.markdown("---")

    # Global filters — shared across pages via session_state
    st.markdown("### Filters")

    selected_countries = st.multiselect(
        "Countries",
        options=["Burkina Faso", "Mali", "Niger"],
        default=["Burkina Faso", "Mali", "Niger"],
    )

    selected_years = st.slider(
        "Year range",
        min_value=2020,
        max_value=2025,
        value=(2020, 2025),
    )

    selected_event_types = st.multiselect(
        "Event types",
        options=sorted(df["event_type"].unique()),
        default=sorted(df["event_type"].unique()),
    )

    # Store filters in session state for use in all pages
    st.session_state["countries"]    = selected_countries
    st.session_state["years"]        = selected_years
    st.session_state["event_types"]  = selected_event_types

    st.markdown("---")
    st.caption("Built with ACLED data · Streamlit")

# --- Home page content
st.title("🌍 Sahel Conflict Monitor")
st.markdown(
    """
    This dashboard provides an interactive analysis of armed conflict dynamics 
    in the **Sahel region** (Burkina Faso, Mali, Niger) from 2020 to 2025,
    based on weekly-updated data from [ACLED](https://acleddata.com).

    ---
    ### Navigate using the sidebar pages:
    | Page | Description |
    |---|---|
    | **Overview** | Global KPIs and summary statistics |
    | **Map** | Interactive incident map with filters |
    | **Trends** | Temporal analysis and forecasting |
    | **Hotspots** | Most affected zones and regions |
    """
)

# --- Quick KPIs on home page
st.markdown("---")
st.markdown("### At a glance")

# Apply global filters
df_filtered = df[
    (df["country"].isin(selected_countries)) &
    (df["year"].between(*selected_years)) &
    (df["event_type"].isin(selected_event_types))
]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Incidents",
        value=f"{len(df_filtered):,}",
        delta=f"{len(df_filtered) - len(df):,} vs full dataset",
    )

with col2:
    st.metric(
        label="Total Fatalities",
        value=f"{df_filtered['fatalities'].sum():,}",
    )

with col3:
    st.metric(
        label="Most Affected Country",
        value=df_filtered.groupby("country")["event_id_cnty"].count().idxmax()
        if not df_filtered.empty else "N/A",
    )

with col4:
    st.metric(
        label="Deadliest Event Type",
        value=df_filtered.groupby("event_type")["fatalities"].sum().idxmax()
        if not df_filtered.empty else "N/A",
    )
