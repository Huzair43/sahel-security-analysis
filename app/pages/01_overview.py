from utils.style import apply_global_style, page_header
apply_global_style()
import streamlit as st
import plotly.express as px

from utils.data_loader import (
load_main_data, load_monthly_by_country,
 EVENT_COLORS, COUNTRY_COLORS
)

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")
page_header(
    title="Overview",
    subtitle="Global summary of conflict activity across the Sahel region.",
    icon="📊"
)

# --- Load data
df = load_main_data()
monthly = load_monthly_by_country()

# --- Apply filters from session state
countries  = st.session_state.get("countries",  ["Burkina Faso", "Mali", "Niger"])
years  = st.session_state.get("years",  (2020, 2025))
event_types = st.session_state.get("event_types", list(df["event_type"].unique()))

df_f = df[
 (df["country"].isin(countries)) &
 (df["year"].between(*years)) &
 (df["event_type"].isin(event_types))
]

# --- KPI row
st.markdown("### Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

metrics = {
 "Incidents":  len(df_f),
 "Fatalities": df_f["fatalities"].sum(),
 "Locations": df_f["location"].nunique(),
 "Armed groups":  df_f["actor1"].nunique(),
 "Avg fatalities": round(df_f["fatalities"].mean(), 1),
}

for col, (label, value) in zip([col1, col2, col3, col4, col5], metrics.items()):
 col.metric(label, f"{value:,}" if isinstance(value, int) else value)

st.markdown("---")

# --- Two columns layout
left, right = st.columns(2)

with left:
 # Incidents by country (bar)
 by_country = (
 df_f.groupby("country")
 .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
 .reset_index()
 )
 fig1 = px.bar(
 by_country, x="country", y="incidents",
 color="country",
 color_discrete_map=COUNTRY_COLORS,
 title="Incidents by Country",
 template="plotly_dark",
 text="incidents",
 )
 fig1.update_traces(textposition="outside")
 fig1.update_layout(showlegend=False, height=350)
 st.plotly_chart(fig1, use_container_width=True)

with right:
 # Event type distribution (pie)
 by_type = df_f.groupby("event_type")["event_id_cnty"].count().reset_index()
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

# --- Monthly trend
st.markdown("### Monthly Trend")
monthly_f = monthly[
(monthly["country"].isin(countries)) &
(monthly["year_month_dt"].dt.year.between(*years))
]
fig3 = px.line(
 monthly_f, x="year_month_dt", y="incidents",
 color="country",
 color_discrete_map=COUNTRY_COLORS,
 title="Monthly Incidents by Country",
 labels={"year_month_dt": "Date", "incidents": "Incidents"},
 template="plotly_dark",
)
fig3.update_layout(hovermode="x unified", height=400)
st.plotly_chart(fig3, use_container_width=True)

# --- Raw data table
with st.expander("View raw data sample (50 rows)"):
 st.dataframe(
 df_f.sort_values("event_date", ascending=False).head(50),
 use_container_width=True,
 )