# app/pages/04_hotspots.py
from utils.style import apply_global_style, page_header
apply_global_style()
import streamlit as st
import plotly.express as px

from utils.data_loader import load_main_data, EVENT_COLORS, COUNTRY_COLORS

from utils.icons import icon


st.set_page_config(page_title="Hotspots", page_icon="https://img.icons8.com/ios/50/ffffff/target.png", layout="wide")
page_header(
    title="Conflict Hotspots",
    subtitle="Most affected regions, locations, and armed groups."
)

df = load_main_data()

countries   = st.session_state.get("countries",   ["Burkina Faso", "Mali", "Niger"])
years       = st.session_state.get("years",       (2020, 2025))
event_types = st.session_state.get("event_types", list(df["event_type"].unique()))

df_f = df[
    (df["country"].isin(countries)) &
    (df["year"].between(*years)) &
    (df["event_type"].isin(event_types))
]

# --- Top regions
st.markdown("### Top 15 Most Affected Regions (Admin1)")
top_regions = (
    df_f.groupby(["country", "admin1"])
    .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
    .reset_index()
    .sort_values("incidents", ascending=False)
    .head(15)
)
fig1 = px.bar(
    top_regions, x="incidents", y="admin1",
    color="country", color_discrete_map=COUNTRY_COLORS,
    orientation="h",
    title="Top 15 Regions by Number of Incidents",
    labels={"incidents": "Incidents", "admin1": "Region"},
    template="plotly_dark",
    text="incidents",
)
fig1.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# --- Top locations and top actors side by side
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top 10 Most Affected Locations")
    top_locations = (
        df_f.groupby(["location", "country"])
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("fatalities", ascending=False)
        .head(10)
    )
    fig2 = px.bar(
        top_locations, x="fatalities", y="location",
        color="country", color_discrete_map=COUNTRY_COLORS,
        orientation="h",
        title="Top 10 Locations by Fatalities",
        labels={"fatalities": "Fatalities", "location": "Location"},
        template="plotly_dark",
        text="fatalities",
    )
    fig2.update_layout(height=400, yaxis={"categoryorder": "total ascending"}, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("### Top 10 Most Active Armed Groups")
    top_actors = (
        df_f.groupby("actor1")
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("incidents", ascending=False)
        .head(10)
    )
    fig3 = px.bar(
        top_actors, x="incidents", y="actor1",
        orientation="h",
        title="Top 10 Actors by Number of Incidents",
        labels={"incidents": "Incidents", "actor1": "Actor"},
        template="plotly_dark",
        color="incidents",
        color_continuous_scale="Reds",
        text="incidents",
    )
    fig3.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig3, use_container_width=True)

# --- Fatality intensity table
st.markdown("---")
st.markdown("### Deadliest Incidents")
deadliest = (
    df_f[df_f["fatalities"] > 0]
    .sort_values("fatalities", ascending=False)
    [["event_date", "country", "admin1", "location", "event_type", "actor1", "fatalities", "notes"]]
    .head(20)
    .reset_index(drop=True)
)
st.dataframe(deadliest, use_container_width=True)
