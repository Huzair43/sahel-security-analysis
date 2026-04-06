import plotly.express as px
from flask import Blueprint, render_template

from flask_app.utils.data_loader import COUNTRY_COLORS, load_main_data

hotspots_bp = Blueprint("hotspots", __name__)

_PLOTLY_OPTS = dict(full_html=False, include_plotlyjs=False, config={"responsive": True})


@hotspots_bp.route("/hotspots")
def hotspots():
    df = load_main_data()

    # ── Chart 1: Top 15 regions ───────────────────────────────────────────────
    top_regions = (
        df.groupby(["country", "admin1"])
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
        template="plotly_dark", text="incidents",
    )
    fig1.update_layout(height=500, yaxis={"categoryorder": "total ascending"},
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_regions = fig1.to_html(**_PLOTLY_OPTS)

    # ── Chart 2: Top 10 locations by fatalities ───────────────────────────────
    top_locations = (
        df.groupby(["location", "country"])
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
        template="plotly_dark", text="fatalities",
    )
    fig2.update_layout(height=420, yaxis={"categoryorder": "total ascending"},
                       showlegend=False,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_locations = fig2.to_html(**_PLOTLY_OPTS)

    # ── Chart 3: Top 10 actors ────────────────────────────────────────────────
    top_actors = (
        df.groupby("actor1")
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
        template="plotly_dark", color="incidents",
        color_continuous_scale="Reds", text="incidents",
    )
    fig3.update_layout(height=420, yaxis={"categoryorder": "total ascending"},
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_actors = fig3.to_html(**_PLOTLY_OPTS)

    # ── Deadliest incidents table ─────────────────────────────────────────────
    deadliest = (
        df[df["fatalities"] > 0]
        .sort_values("fatalities", ascending=False)
        [["event_date", "country", "admin1", "location", "event_type", "actor1", "fatalities"]]
        .head(20)
        .assign(event_date=lambda d: d["event_date"].dt.strftime("%Y-%m-%d"))
        .to_dict(orient="records")
    )

    return render_template(
        "hotspots.html",
        chart_regions=chart_regions,
        chart_locations=chart_locations,
        chart_actors=chart_actors,
        deadliest=deadliest,
    )
