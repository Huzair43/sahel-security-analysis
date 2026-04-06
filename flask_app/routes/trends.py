import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from flask import Blueprint, render_template

from flask_app.utils.data_loader import (
    COUNTRY_COLORS,
    EVENT_COLORS,
    load_monthly_by_country,
    load_monthly_by_type,
    load_monthly_total,
)

trends_bp = Blueprint("trends", __name__)

_PLOTLY_OPTS = dict(full_html=False, include_plotlyjs=False, config={"responsive": True})


@trends_bp.route("/trends")
def trends():
    monthly       = load_monthly_by_country()
    monthly_type  = load_monthly_by_type()
    monthly_total = load_monthly_total()

    # ── Tab 1: Monthly incidents by country ──────────────────────────────────
    fig1 = px.line(
        monthly, x="year_month_dt", y="incidents",
        color="country", color_discrete_map=COUNTRY_COLORS,
        title="Monthly Incidents by Country",
        labels={"year_month_dt": "Date", "incidents": "Incidents"},
        template="plotly_dark",
    )
    fig1.update_layout(hovermode="x unified", height=450,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_incidents = fig1.to_html(**_PLOTLY_OPTS)

    # ── Tab 2: Monthly fatalities by country ──────────────────────────────────
    fig2 = px.line(
        monthly, x="year_month_dt", y="fatalities",
        color="country", color_discrete_map=COUNTRY_COLORS,
        title="Monthly Fatalities by Country",
        labels={"year_month_dt": "Date", "fatalities": "Fatalities"},
        template="plotly_dark",
    )
    fig2.update_traces(fill="tozeroy", opacity=0.4)
    fig2.update_layout(hovermode="x unified", height=450,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_fatalities = fig2.to_html(**_PLOTLY_OPTS)

    # ── Tab 3: Event types ────────────────────────────────────────────────────
    fig3 = px.bar(
        monthly_type, x="year_month_dt", y="incidents",
        color="event_type", color_discrete_map=EVENT_COLORS,
        title="Monthly Incidents by Event Type",
        labels={"year_month_dt": "Date", "incidents": "Incidents"},
        template="plotly_dark",
    )
    fig3.update_layout(hovermode="x unified", height=450,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    chart_types = fig3.to_html(**_PLOTLY_OPTS)

    # ── Tab 4: Trend & forecast ───────────────────────────────────────────────
    df_t = monthly_total.sort_values("year_month_dt").reset_index(drop=True).copy()
    df_t["t"] = np.arange(len(df_t))

    x, y         = df_t["t"].values, df_t["incidents"].values
    slope, intercept = np.polyfit(x, y, 1)
    y_pred       = intercept + slope * x
    ss_res       = np.sum((y - y_pred) ** 2)
    r_squared    = 1 - ss_res / np.sum((y - np.mean(y)) ** 2)

    df_t["linear_trend"] = y_pred
    df_t["roll_3"]  = df_t["incidents"].rolling(3,  min_periods=1).mean()
    df_t["roll_6"]  = df_t["incidents"].rolling(6,  min_periods=1).mean()
    df_t["roll_12"] = df_t["incidents"].rolling(12, min_periods=1).mean()

    last_t    = df_t["t"].max()
    last_date = df_t["year_month_dt"].max()
    future_t  = np.arange(last_t + 1, last_t + 7)
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1), periods=6, freq="MS"
    )
    future_trend = intercept + slope * future_t

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_t["year_month_dt"], y=df_t["incidents"],
        name="Monthly incidents", marker_color="rgba(52,152,219,0.4)",
    ))
    for col, color, name in [
        ("roll_3", "#f1c40f", "3-month MA"),
        ("roll_6", "#e67e22", "6-month MA"),
        ("roll_12", "#e74c3c", "12-month MA"),
    ]:
        fig4.add_trace(go.Scatter(
            x=df_t["year_month_dt"], y=df_t[col],
            mode="lines", name=name, line=dict(color=color, width=2),
        ))
    fig4.add_trace(go.Scatter(
        x=df_t["year_month_dt"], y=df_t["linear_trend"],
        mode="lines", name="Linear trend",
        line=dict(color="#2ecc71", width=2, dash="dot"),
    ))
    fig4.add_trace(go.Scatter(
        x=future_dates, y=future_trend,
        mode="lines+markers", name="6-month forecast",
        line=dict(color="#2ecc71", width=2, dash="dash"),
        marker=dict(size=8, symbol="diamond"),
    ))
    fig4.add_vrect(
        x0=future_dates[0], x1=future_dates[-1],
        fillcolor="rgba(46,204,113,0.05)", line_width=0,
        annotation_text="Forecast", annotation_position="top left",
    )
    fig4.update_layout(
        title="Trend Analysis & 6-Month Forecast",
        xaxis_title="Date", yaxis_title="Incidents",
        template="plotly_dark", hovermode="x unified", height=500,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    chart_forecast = fig4.to_html(**_PLOTLY_OPTS)

    trend_metrics = {
        "slope":     f"{slope:+.2f} inc/month",
        "r_squared": f"{r_squared:.3f}",
        "trend":     "Increasing ↑" if slope > 0 else "Decreasing ↓",
        "trend_color": "#e74c3c" if slope > 0 else "#2ecc71",
    }

    return render_template(
        "trends.html",
        chart_incidents=chart_incidents,
        chart_fatalities=chart_fatalities,
        chart_types=chart_types,
        chart_forecast=chart_forecast,
        trend_metrics=trend_metrics,
    )
