import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Blueprint, render_template

from flask_app.theme import (
    INK_3,
    INK_4,
    PLOTLY_OPTS,
    RULE_STRONG,
    SIGNAL,
    finalize,
)
from flask_app.utils.data_loader import (
    COUNTRY_COLORS,
    EVENT_COLORS,
    load_monthly_by_country,
    load_monthly_by_type,
    load_monthly_total,
)

trends_bp = Blueprint("trends", __name__)


@trends_bp.route("/trends")
def trends():
    monthly       = load_monthly_by_country()
    monthly_type  = load_monthly_by_type()
    monthly_total = load_monthly_total()

    period = (
        f"{monthly['year_month_dt'].min():%b %Y} : "
        f"{monthly['year_month_dt'].max():%b %Y}"
    )

    # ── Onglet 1 : incidents mensuels par pays ───────────────────────────────
    fig1 = px.line(
        monthly, x="year_month_dt", y="incidents",
        color="country", color_discrete_map=COUNTRY_COLORS,
        labels={"year_month_dt": "", "incidents": "Incidents", "country": ""},
    )
    fig1.update_traces(line=dict(width=1.6), hovertemplate="%{y:,}")
    finalize(fig1, height=420, hovermode="x unified",
             margin=dict(l=8, r=8, t=32, b=8))
    chart_incidents = fig1.to_html(**PLOTLY_OPTS)

    # ── Onglet 2 : décès mensuels par pays ───────────────────────────────────
    fig2 = px.area(
        monthly, x="year_month_dt", y="fatalities",
        color="country", color_discrete_map=COUNTRY_COLORS,
        labels={"year_month_dt": "", "fatalities": "Fatalities", "country": ""},
    )
    fig2.update_traces(line=dict(width=1.2), opacity=0.45,
                       hovertemplate="%{y:,}")
    finalize(fig2, height=420, hovermode="x unified",
             margin=dict(l=8, r=8, t=32, b=8))
    chart_fatalities = fig2.to_html(**PLOTLY_OPTS)

    # ── Onglet 3 : types d'événements ────────────────────────────────────────
    fig3 = px.bar(
        monthly_type, x="year_month_dt", y="incidents",
        color="event_type", color_discrete_map=EVENT_COLORS,
        labels={"year_month_dt": "", "incidents": "Incidents", "event_type": ""},
    )
    fig3.update_traces(hovertemplate="%{y:,}")
    finalize(fig3, height=420, hovermode="x unified",
             margin=dict(l=8, r=8, t=48, b=8))
    fig3.update_layout(bargap=0.1)
    chart_types = fig3.to_html(**PLOTLY_OPTS)

    # ── Onglet 4 : tendance et projection ────────────────────────────────────
    df_t = monthly_total.sort_values("year_month_dt").reset_index(drop=True).copy()
    df_t["t"] = np.arange(len(df_t))

    x, y             = df_t["t"].values, df_t["incidents"].values
    slope, intercept = np.polyfit(x, y, 1)
    y_pred           = intercept + slope * x
    ss_res           = np.sum((y - y_pred) ** 2)
    r_squared        = 1 - ss_res / np.sum((y - np.mean(y)) ** 2)

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

    # Les moyennes mobiles forment une rampe de gris vers la couleur signal :
    # plus la fenêtre est longue, plus la ligne est saillante.
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_t["year_month_dt"], y=df_t["incidents"],
        name="Monthly incidents",
        marker_color="rgba(255,255,255,0.10)",
        hovertemplate="%{y:,}<extra>Observed</extra>",
    ))
    for col, color, width, name in [
        ("roll_3",  INK_4,  1.2, "3 month MA"),
        ("roll_6",  INK_3,  1.4, "6 month MA"),
        ("roll_12", SIGNAL, 2.0, "12 month MA"),
    ]:
        fig4.add_trace(go.Scatter(
            x=df_t["year_month_dt"], y=df_t[col],
            mode="lines", name=name,
            line=dict(color=color, width=width),
            hovertemplate="%{y:,.0f}<extra>" + name + "</extra>",
        ))
    fig4.add_trace(go.Scatter(
        x=df_t["year_month_dt"], y=df_t["linear_trend"],
        mode="lines", name="Linear trend",
        line=dict(color=RULE_STRONG, width=1.4, dash="dot"),
        hovertemplate="%{y:,.0f}<extra>Trend</extra>",
    ))
    fig4.add_trace(go.Scatter(
        x=future_dates, y=future_trend,
        mode="lines+markers", name="6 month projection",
        line=dict(color=SIGNAL, width=1.4, dash="dash"),
        marker=dict(size=5, symbol="circle"),
        hovertemplate="%{y:,.0f}<extra>Projected</extra>",
    ))
    fig4.add_vrect(
        x0=future_dates[0], x1=future_dates[-1],
        fillcolor="rgba(229,72,77,0.05)", line_width=0, layer="below",
    )
    # Annotation ancrée sous le haut du cadre pour ne pas être rognée.
    fig4.add_annotation(
        x=future_dates[len(future_dates) // 2], y=1, yref="paper",
        text="PROJECTION", showarrow=False,
        font=dict(family="IBM Plex Mono, monospace", size=9, color=INK_4),
        yanchor="bottom", yshift=6,
    )
    finalize(fig4, height=460, hovermode="x unified", pad="y", pad_pct=0.10,
             margin=dict(l=8, r=8, t=48, b=8))
    chart_forecast = fig4.to_html(**PLOTLY_OPTS)

    trend_metrics = {
        "slope":     f"{slope:+.2f}",
        "r_squared": f"{r_squared:.3f}",
        "trend":     "Increasing" if slope > 0 else "Decreasing",
        "rising":    bool(slope > 0),
    }

    return render_template(
        "trends.html",
        period=period,
        chart_incidents=chart_incidents,
        chart_fatalities=chart_fatalities,
        chart_types=chart_types,
        chart_forecast=chart_forecast,
        trend_metrics=trend_metrics,
        n_months=len(df_t),
    )
