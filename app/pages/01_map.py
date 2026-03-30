# app/pages/02_map.py
from utils.style import apply_global_style, page_header
apply_global_style()
import streamlit as st
import folium
import html
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import pandas as pd

from utils.data_loader import load_main_data, EVENT_COLORS



st.set_page_config(page_title="Map", page_icon="https://img.icons8.com/ios/50/ffffff/map.png", layout="wide")
page_header(
    title="Conflict Map",
    subtitle="Interactive visualization of all conflict incidents."
)

df = load_main_data()

# --- Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    countries = st.multiselect(
        "Countries", ["Burkina Faso", "Mali", "Niger"],
        default=["Burkina Faso", "Mali", "Niger"]
    )
with col2:
    years = st.slider("Year range", 2020, 2025, (2022, 2025))
with col3:
    map_type = st.radio("Map type", ["Incidents", "Heatmap"], horizontal=True)
with col4:
    max_points = st.select_slider(
        "Max points",
        options=[1000, 2000, 5000, 10000, "All"],
        value=2000,
    )

# --- Filter data
df_f = df[
    (df["country"].isin(countries)) &
    (df["year"].between(*years))
].copy()

# --- Limit points for performance
if max_points != "All":
    if len(df_f) > max_points:
        # Sample but keep deadliest events (sort by fatalities first)
        df_deadly  = df_f[df_f["fatalities"] > 0].nlargest(max_points // 2, "fatalities")
        df_sample  = df_f[df_f["fatalities"] == 0].sample(
            min(max_points // 2, len(df_f[df_f["fatalities"] == 0])),
            random_state=42
        )
        df_f = pd.concat([df_deadly, df_sample]).drop_duplicates()

st.caption(f"Displaying **{len(df_f):,}** incidents")

# --- Build map (cached by filter parameters)
@st.cache_data
def build_incident_map(data_hash, _df):
    """Build Folium incident map — cached to avoid rebuild on every interaction."""
    def _safe(value) -> str:
        if value is None:
            return ""
        return html.escape(str(value))

    m = folium.Map(
        location=[15.0, -2.0],
        zoom_start=6,
        tiles="CartoDB dark_matter",
    )

    cluster = MarkerCluster(
        options={"maxClusterRadius": 50, "disableClusteringAtZoom": 9}
    ).add_to(m)

    # Vectorized color mapping
    _df["color"] = _df["event_type"].map(EVENT_COLORS).fillna("#95a5a6")
    _df["radius"] = (_df["fatalities"] * 0.5 + 4).clip(4, 20)

    # Add markers — still a loop but on filtered/limited data
    for row in _df.itertuples():
        popup_html = (
            f"<div style='font-family:Arial;font-size:12px;width:200px;'>"
            f"<b style='color:{row.color};'>{_safe(row.event_type)}</b><br>"
            f"<hr style='margin:3px 0;'>"
            f"<b>Date:</b> {_safe(str(row.event_date)[:10])}<br>"
            f"<b>Location:</b> {_safe(row.location)}, {_safe(row.admin1)}<br>"
            f"<b>Country:</b> {_safe(row.country)}<br>"
            f"<b>Fatalities:</b> {row.fatalities}<br>"
            f"<b>Actor:</b> {_safe(row.actor1)}"
            f"</div>"
        )
        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=row.radius,
            color=row.color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=230),
            tooltip=f"{_safe(row.event_type)} - {row.fatalities} fatalities",
        ).add_to(cluster)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:40px;left:40px;
        background:rgba(0,0,0,0.75);color:white;
        padding:12px 16px;border-radius:8px;font-size:13px;z-index:1000;">
        <b>Event Types</b><br><br>
        <span style="color:#e74c3c;">●</span> Battles<br>
        <span style="color:#e67e22;">●</span> Violence against civilians<br>
        <span style="color:#9b59b6;">●</span> Explosions / Remote violence<br>
        <span style="color:#3498db;">●</span> Protests<br>
        <span style="color:#f1c40f;">●</span> Riots<br>
        <span style="color:#2ecc71;">●</span> Strategic developments<br>
        <br><i style="font-size:11px;">Circle size = fatalities</i>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


@st.cache_data
def build_heatmap(_df):
    """Build Folium heatmap — cached."""
    m = folium.Map(
        location=[15.0, -2.0],
        zoom_start=6,
        tiles="CartoDB dark_matter",
    )
    heat_data = _df[["latitude", "longitude", "fatalities"]].copy()
    heat_data["fatalities"] = heat_data["fatalities"].clip(lower=1)
    HeatMap(
        heat_data.values.tolist(),
        min_opacity=0.3,
        radius=15,
        blur=10,
        gradient={"0.2": "blue", "0.4": "lime", "0.6": "orange", "1.0": "red"},
    ).add_to(m)
    return m


# --- Render map
if df_f.empty:
    st.warning("No data for the selected filters.")
else:
    with st.spinner("Building map..."):
        if map_type == "Incidents":
            # Use a hash of filters as cache key
            cache_key = f"{countries}_{years}_{len(df_f)}"
            m = build_incident_map(cache_key, df_f)
        else:
            m = build_heatmap(df_f)

    st_folium(m, width="100%", height=580, returned_objects=[])
