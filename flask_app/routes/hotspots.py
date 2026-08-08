import plotly.express as px
from flask import Blueprint, render_template

from flask_app.theme import (
    PLOTLY_OPTS,
    SEQUENTIAL,
    bar_categories,
    finalize,
    hide_axis,
)
from flask_app.utils.data_loader import COUNTRY_COLORS, EVENT_COLORS, load_main_data

hotspots_bp = Blueprint("hotspots", __name__)

_MAX_LABEL = 26


def _shorten(name: str) -> str:
    """Étiquette d'axe lisible. Le nom complet reste dans le survol."""
    return name if len(name) <= _MAX_LABEL else name[: _MAX_LABEL - 1] + "…"


@hotspots_bp.route("/hotspots")
def hotspots():
    df = load_main_data()

    # ── Chart 1 : 15 premières régions ───────────────────────────────────────
    top_regions = (
        df.groupby(["country", "admin1"])
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("incidents", ascending=False)
        .head(15)
    )
    top_regions["label"] = top_regions["incidents"].map("{:,}".format)

    fig1 = px.bar(
        top_regions, x="incidents", y="admin1",
        color="country", color_discrete_map=COUNTRY_COLORS,
        orientation="h", text="label",
        custom_data=["country", "fatalities"],
        labels={"incidents": "Incidents", "admin1": "", "country": ""},
    )
    fig1.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b>, %{customdata[0]}<br>"
                      "Incidents %{x:,}<br>Fatalities %{customdata[1]:,}<extra></extra>",
    )
    # Marge droite réservée aux étiquettes de valeur : avec cliponaxis=False
    # elles se dessinent dans la marge au lieu d'être rognées par le cadre.
    finalize(fig1, height=520, pad="x", pad_pct=0.02,
             margin=dict(l=8, r=64, t=32, b=8))
    bar_categories(fig1, axis="y")
    hide_axis(fig1, axis="x")
    fig1.update_yaxes(categoryorder="total ascending")
    chart_regions = fig1.to_html(**PLOTLY_OPTS)

    # ── Chart 2 : 10 premières localités par décès ───────────────────────────
    top_locations = (
        df.groupby(["location", "country"])
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("fatalities", ascending=False)
        .head(10)
    )
    top_locations["label"] = top_locations["fatalities"].map("{:,}".format)

    fig2 = px.bar(
        top_locations, x="fatalities", y="location",
        color="country", color_discrete_map=COUNTRY_COLORS,
        orientation="h", text="label",
        custom_data=["country", "incidents"],
        labels={"fatalities": "Fatalities", "location": "", "country": ""},
    )
    fig2.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b>, %{customdata[0]}<br>"
                      "Fatalities %{x:,}<br>Incidents %{customdata[1]:,}<extra></extra>",
    )
    finalize(fig2, height=400, pad="x", pad_pct=0.02, legend=False,
             margin=dict(l=8, r=56, t=8, b=8))
    bar_categories(fig2, axis="y")
    hide_axis(fig2, axis="x")
    fig2.update_yaxes(categoryorder="total ascending")
    chart_locations = fig2.to_html(**PLOTLY_OPTS)

    # ── Chart 3 : 10 acteurs les plus actifs ─────────────────────────────────
    top_actors = (
        df.groupby("actor1")
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("incidents", ascending=False)
        .head(10)
    )
    top_actors["short"] = top_actors["actor1"].map(_shorten)
    top_actors["label"] = top_actors["incidents"].map("{:,}".format)

    fig3 = px.bar(
        top_actors, x="incidents", y="short",
        orientation="h", text="label",
        color="incidents", color_continuous_scale=SEQUENTIAL,
        custom_data=["actor1", "fatalities"],
        labels={"incidents": "Incidents", "short": ""},
    )
    fig3.update_traces(
        textposition="outside",
        hovertemplate="<b>%{customdata[0]}</b><br>"
                      "Incidents %{x:,}<br>Fatalities %{customdata[1]:,}<extra></extra>",
    )
    finalize(fig3, height=400, pad="x", pad_pct=0.02,
             margin=dict(l=8, r=56, t=8, b=8))
    # L'échelle de couleur redouble le classement : la barre suffit, pas de barre de couleur.
    fig3.update_layout(coloraxis_showscale=False)
    bar_categories(fig3, axis="y")
    hide_axis(fig3, axis="x")
    fig3.update_yaxes(categoryorder="total ascending")
    chart_actors = fig3.to_html(**PLOTLY_OPTS)

    # ── Incidents les plus meurtriers ────────────────────────────────────────
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
        event_colors=EVENT_COLORS,
        n_regions=df["admin1"].nunique(),
        n_actors=df["actor1"].nunique(),
    )
