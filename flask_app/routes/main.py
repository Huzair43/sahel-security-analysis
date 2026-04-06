import plotly.express as px
import plotly.graph_objects as go
from flask import Blueprint, render_template

from flask_app.utils.data_loader import (
    COUNTRY_COLORS,
    EVENT_COLORS,
    load_main_data,
    load_monthly_by_country,
)

main_bp = Blueprint("main", __name__)

# Plotly export options (Plotly.js already loaded in base.html)
_PLOTLY_OPTS = dict(full_html=False, include_plotlyjs=False, config={"responsive": True})


@main_bp.route("/")
def index():
    df      = load_main_data()
    monthly = load_monthly_by_country()

    # ── KPIs ─────────────────────────────────────────────────────────────────
    most_affected  = df.groupby("country")["event_id_cnty"].count().idxmax()
    deadliest_type = df.groupby("event_type")["fatalities"].sum().idxmax()

    kpis = {
        "total_incidents":  f"{len(df):,}",
        "total_fatalities": f"{df['fatalities'].sum():,}",
        "locations":        f"{df['location'].nunique():,}",
        "most_affected":    most_affected,
        "deadliest_type":   deadliest_type,
    }

    # ── Chart 1: Incidents by Country (bar) ──────────────────────────────────
    by_country = (
        df.groupby("country")
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .reset_index()
    )
    fig1 = px.bar(
        by_country, x="country", y="incidents",
        color="country", color_discrete_map=COUNTRY_COLORS,
        title="Incidents by Country",
        template="plotly_dark",
        text="incidents",
        labels={"incidents": "Incidents", "country": "Country"},
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, height=350,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_country = fig1.to_html(**_PLOTLY_OPTS)

    # ── Chart 2: Distribution by Event Type (donut) ───────────────────────────
    by_type = (
        df.groupby("event_type")["event_id_cnty"]
        .count().reset_index(name="incidents")
    )
    fig2 = px.pie(
        by_type, names="event_type", values="incidents",
        color="event_type", color_discrete_map=EVENT_COLORS,
        title="Distribution by Event Type",
        template="plotly_dark",
        hole=0.4,
    )
    fig2.update_layout(height=350,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_type = fig2.to_html(**_PLOTLY_OPTS)

    # ── Chart 3: Monthly incidents by country (line) ──────────────────────────
    fig3 = px.line(
        monthly, x="year_month_dt", y="incidents",
        color="country", color_discrete_map=COUNTRY_COLORS,
        title="Monthly Incidents by Country",
        labels={"year_month_dt": "Date", "incidents": "Incidents", "country": "Country"},
        template="plotly_dark",
    )
    fig3.update_layout(hovermode="x unified", height=400,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_monthly = fig3.to_html(**_PLOTLY_OPTS)

    # ── Raw data sample ───────────────────────────────────────────────────────
    raw_cols = ["event_date", "country", "admin1", "location", "event_type", "fatalities"]
    raw_data = (
        df.sort_values("event_date", ascending=False)
        .head(50)[raw_cols]
        .assign(event_date=lambda d: d["event_date"].dt.strftime("%Y-%m-%d"))
        .to_dict(orient="records")
    )

    return render_template(
        "overview.html",
        kpis=kpis,
        chart_country=chart_country,
        chart_type=chart_type,
        chart_monthly=chart_monthly,
        raw_data=raw_data,
        raw_cols=raw_cols,
    )
