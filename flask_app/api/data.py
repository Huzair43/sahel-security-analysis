"""
API Blueprint — endpoints de données pour les graphiques interactifs.
Ces endpoints retournent du JSON consommé par Plotly.js côté client.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Blueprint, jsonify, request

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


# ── Données carte (JSON compact, chargé une seule fois) ──────────────────────

@data_bp.route("/data/map-points")
def map_points():
    """
    Retourne tous les incidents en JSON compact.
    Chargé une seule fois, filtré et rendu entièrement côté client.
    Noms de colonnes courts + coordonnées arrondies pour réduire la taille.
    """
    df = load_main_data()
    out = pd.DataFrame({
        "la": df["latitude"].round(4),
        "lo": df["longitude"].round(4),
        "et": df["event_type"],
        "fa": df["fatalities"].astype(int),
        "yr": df["year"].astype(int),
        "dt": df["event_date"].astype(str).str[:10],
        "co": df["country"],
        "r":  df["admin1"],
        "lc": df["location"],
        "ac": df["actor1"],
    })
    return jsonify(out.to_dict(orient="records"))


# ── Carte Plotly (WebGL, supporte 23 000+ points sans lag) ───────────────────

_PLOTLY_OPTS = dict(full_html=False, include_plotlyjs=False, config={"responsive": True})


def _build_scatter_map(df: pd.DataFrame) -> str:
    df = df.copy()
    df["size"]       = (df["fatalities"] * 0.4 + 5).clip(5, 22)
    df["date_str"]   = df["event_date"].astype(str).str[:10]
    df["fatalities"] = df["fatalities"].astype(int)

    fig = px.scatter_mapbox(
        df,
        lat="latitude", lon="longitude",
        color="event_type",
        color_discrete_map=EVENT_COLORS,
        size="size",
        size_max=22,
        hover_name="event_type",
        hover_data={
            "date_str":   True,
            "country":    True,
            "admin1":     True,
            "location":   True,
            "actor1":     True,
            "fatalities": True,
            "size":       False,
            "latitude":   False,
            "longitude":  False,
        },
        labels={
            "date_str":   "Date",
            "admin1":     "Region",
            "actor1":     "Actor",
            "fatalities": "Fatalities",
        },
        mapbox_style="carto-darkmatter",
        center={"lat": 15.0, "lon": -2.0},
        zoom=5,
        opacity=0.75,
        template="plotly_dark",
    )
    fig.update_layout(
        height=580,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            bgcolor="rgba(15,17,23,0.85)",
            bordercolor="#2d3250",
            borderwidth=1,
            font=dict(color="#e8e8e8", size=12),
            title=dict(text="Event Type", font=dict(color="#a0a8c0", size=11)),
        ),
    )
    return fig.to_html(**_PLOTLY_OPTS)


def _build_density_map(df: pd.DataFrame) -> str:
    df = df.copy()
    df["weight"] = (df["fatalities"].clip(lower=1))

    fig = px.density_mapbox(
        df,
        lat="latitude", lon="longitude",
        z="weight",
        radius=14,
        mapbox_style="carto-darkmatter",
        center={"lat": 15.0, "lon": -2.0},
        zoom=5,
        color_continuous_scale=["#0d1b2a", "#1565c0", "#00e676", "#ff9800", "#e74c3c"],
        template="plotly_dark",
    )
    fig.update_layout(
        height=580,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=dict(text="Intensity", font=dict(color="#a0a8c0")),
            tickfont=dict(color="#a0a8c0"),
        ),
    )
    return fig.to_html(**_PLOTLY_OPTS)


@data_bp.route("/map/chart")
def map_chart():
    """Retourne le HTML Plotly de la carte, injecté directement dans la page."""
    df = load_main_data().copy()

    countries  = request.args.getlist("countries") or ["Burkina Faso", "Mali", "Niger"]
    year_start = int(request.args.get("year_start", 2020))
    year_end   = int(request.args.get("year_end",   2025))
    map_type   = request.args.get("map_type", "incidents")

    df_f = df[
        df["country"].isin(countries) &
        df["year"].between(year_start, year_end)
    ].copy()

    if df_f.empty:
        return "<p style='color:#a0a8c0;padding:2rem;'>No data for the selected filters.</p>"

    chart_html = (
        _build_scatter_map(df_f) if map_type == "incidents"
        else _build_density_map(df_f)
    )
    return chart_html
