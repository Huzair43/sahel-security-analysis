from utils.style import apply_global_style, page_header
apply_global_style()
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats
import pandas as pd

from utils.data_loader import (
    load_monthly_by_country, load_monthly_by_type,
    load_monthly_total, EVENT_COLORS, COUNTRY_COLORS
)

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")
page_header(
    title="Temporal Trends",
    subtitle="Monthly evolution of conflict intensity, anomaly detection, and 6-month forecast.",
    icon="📈"
)

monthly        = load_monthly_by_country()
monthly_type   = load_monthly_by_type()
monthly_total  = load_monthly_total()

countries = st.session_state.get("countries", ["Burkina Faso", "Mali", "Niger"])
years     = st.session_state.get("years", (2020, 2025))

monthly_f      = monthly[monthly["country"].isin(countries)]
monthly_type_f = monthly_type.copy()
monthly_total_f = monthly_total.copy()

# --- Tab layout
tab1, tab2, tab3, tab4 = st.tabs([
    " Monthly incidents",
    " Fatalities",
    " Event types",
    " Trend & Forecast"
])

with tab1:
    fig1 = px.line(
        monthly_f, x="year_month_dt", y="incidents",
        color="country", color_discrete_map=COUNTRY_COLORS,
        title="Monthly Incidents by Country",
        labels={"year_month_dt": "Date", "incidents": "Incidents"},
        template="plotly_dark",
    )
    fig1.update_layout(hovermode="x unified", height=450)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.line(
        monthly_f, x="year_month_dt", y="fatalities",
        color="country", color_discrete_map=COUNTRY_COLORS,
        title="Monthly Fatalities by Country",
        labels={"year_month_dt": "Date", "fatalities": "Fatalities"},
        template="plotly_dark",
    )
    fig2.update_traces(fill="tozeroy", opacity=0.4)
    fig2.update_layout(hovermode="x unified", height=450)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.bar(
        monthly_type_f, x="year_month_dt", y="incidents",
        color="event_type", color_discrete_map=EVENT_COLORS,
        title="Monthly Incidents by Event Type",
        labels={"year_month_dt": "Date", "incidents": "Incidents"},
        template="plotly_dark",
    )
    fig3.update_layout(hovermode="x unified", height=450)
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    # Trend model
    monthly_total_f = monthly_total_f.sort_values("year_month_dt").reset_index(drop=True)
    monthly_total_f["t"] = np.arange(len(monthly_total_f))

    slope, intercept, r_value, p_value, _ = stats.linregress(
        monthly_total_f["t"], monthly_total_f["incidents"]
    )
    monthly_total_f["linear_trend"] = intercept + slope * monthly_total_f["t"]
    monthly_total_f["roll_3"]  = monthly_total_f["incidents"].rolling(3,  min_periods=1).mean()
    monthly_total_f["roll_6"]  = monthly_total_f["incidents"].rolling(6,  min_periods=1).mean()
    monthly_total_f["roll_12"] = monthly_total_f["incidents"].rolling(12, min_periods=1).mean()

    # Forecast
    last_t       = monthly_total_f["t"].max()
    last_date    = monthly_total_f["year_month_dt"].max()
    future_t     = np.arange(last_t + 1, last_t + 7)
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1), periods=6, freq="MS"
    )
    future_trend = intercept + slope * future_t

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Trend slope", f"{slope:+.2f} inc/month")
    col2.metric("R²", f"{r_value**2:.3f}")
    col3.metric("Significant", "Yes ✅" if p_value < 0.05 else "No ❌")

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=monthly_total_f["year_month_dt"], y=monthly_total_f["incidents"],
        name="Monthly incidents", marker_color="rgba(52,152,219,0.4)",
    ))
    for roll, color, name in [
        ("roll_3", "#f1c40f", "3-month MA"),
        ("roll_6", "#e67e22", "6-month MA"),
        ("roll_12", "#e74c3c", "12-month MA"),
    ]:
        fig4.add_trace(go.Scatter(
            x=monthly_total_f["year_month_dt"], y=monthly_total_f[roll],
            mode="lines", name=name, line=dict(color=color, width=2),
        ))
    fig4.add_trace(go.Scatter(
        x=monthly_total_f["year_month_dt"], y=monthly_total_f["linear_trend"],
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
    )
    st.plotly_chart(fig4, use_container_width=True)
