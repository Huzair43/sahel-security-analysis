"""
API Blueprint — endpoints de données pour les graphiques interactifs.
Ces endpoints retournent du JSON consommé par Plotly.js côté client,
ou du HTML Folium pour la carte.
"""
import html as html_lib

import folium
import pandas as pd
from flask import Blueprint, Response, jsonify, request
from folium.plugins import HeatMap, MarkerCluster

from flask_app.utils.data_loader import (
    EVENT_COLORS,
    load_main_data,
    load_monthly_by_country,
    load_monthly_by_type,
    load_monthly_total,
)

data_bp = Blueprint("data", __name__)

# ── Données JSON ──────────────────────────────────────────────────────────────

@data_bp.route("/data/summary")
def summary():
    df = load_main_data()
    return jsonify({
        "total_incidents": int(df.shape[0]),
        "total_fatalities": int(df["fatalities"].sum()),
        "countries": df["country"].unique().tolist(),
        "date_range": {
            "start": str(df["event_date"].min().date()),
            "end":   str(df["event_date"].max().date()),
        },
    })


@data_bp.route("/data/monthly")
def monthly():
    country = request.args.get("country")
    df = load_monthly_by_country()
    if country:
        df = df[df["country"] == country]
    return jsonify(df.drop(columns=["year_month_dt"]).to_dict(orient="records"))


@data_bp.route("/data/monthly-type")
def monthly_type():
    df = load_monthly_by_type()
    return jsonify(df.drop(columns=["year_month_dt"]).to_dict(orient="records"))


@data_bp.route("/data/monthly-total")
def monthly_total():
    df = load_monthly_total()
    return jsonify(df.drop(columns=["year_month_dt"]).to_dict(orient="records"))


# ── Carte Folium ──────────────────────────────────────────────────────────────

def _safe(value) -> str:
    if value is None:
        return ""
    return html_lib.escape(str(value))


def _build_incident_map(df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=[15.0, -2.0], zoom_start=6, tiles="CartoDB dark_matter")
    cluster = MarkerCluster(
        options={"maxClusterRadius": 50, "disableClusteringAtZoom": 9}
    ).add_to(m)

    df = df.copy()
    df["color"]  = df["event_type"].map(EVENT_COLORS).fillna("#95a5a6")
    df["radius"] = (df["fatalities"] * 0.5 + 4).clip(4, 20)

    for row in df.itertuples():
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
            tooltip=f"{_safe(row.event_type)} — {row.fatalities} fatalities",
        ).add_to(cluster)

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


def _build_heatmap(df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=[15.0, -2.0], zoom_start=6, tiles="CartoDB dark_matter")
    heat_data = df[["latitude", "longitude", "fatalities"]].copy()
    heat_data["fatalities"] = heat_data["fatalities"].clip(lower=1)
    HeatMap(
        heat_data.values.tolist(),
        min_opacity=0.3,
        radius=15,
        blur=10,
        gradient={"0.2": "blue", "0.4": "lime", "0.6": "orange", "1.0": "red"},
    ).add_to(m)
    return m


@data_bp.route("/map/html")
def map_html():
    """Retourne le HTML complet de la carte Folium — chargé dans un <iframe>."""
    df = load_main_data().copy()

    # ── Filtres depuis query params ───────────────────────────────────────────
    countries  = request.args.getlist("countries") or ["Burkina Faso", "Mali", "Niger"]
    year_start = int(request.args.get("year_start", 2020))
    year_end   = int(request.args.get("year_end",   2025))
    map_type   = request.args.get("map_type", "incidents")
    max_points = request.args.get("max_points", "2000")

    df_f = df[
        df["country"].isin(countries) &
        df["year"].between(year_start, year_end)
    ].copy()

    # ── Limite de points ──────────────────────────────────────────────────────
    if max_points != "all" and not df_f.empty:
        limit = int(max_points)
        if len(df_f) > limit:
            df_deadly = df_f[df_f["fatalities"] > 0].nlargest(limit // 2, "fatalities")
            df_sample = df_f[df_f["fatalities"] == 0].sample(
                min(limit // 2, len(df_f[df_f["fatalities"] == 0])), random_state=42
            )
            df_f = pd.concat([df_deadly, df_sample]).drop_duplicates()

    if df_f.empty:
        return Response(
            "<html><body style='background:#0f1117;color:#a0a8c0;"
            "font-family:Inter,sans-serif;display:flex;align-items:center;"
            "justify-content:center;height:100vh;margin:0;'>"
            "<p>No data for the selected filters.</p></body></html>",
            mimetype="text/html",
        )

    m = _build_incident_map(df_f) if map_type == "incidents" else _build_heatmap(df_f)
    return Response(m.get_root().render(), mimetype="text/html")
