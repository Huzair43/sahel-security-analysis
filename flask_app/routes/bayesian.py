import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from flask import Blueprint, render_template

from flask_app.utils.data_loader import COUNTRY_COLORS

bayesian_bp = Blueprint("bayesian", __name__)

_PLOTLY_OPTS = dict(full_html=False, include_plotlyjs=False, config={"responsive": True})
_DATA_PATH   = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed"
)


@bayesian_bp.route("/bayesian")
def bayesian():
    # ── Load bayesian results ─────────────────────────────────────────────────
    try:
        posterior_df = pd.read_csv(os.path.join(_DATA_PATH, "bayesian_posterior.csv"))
        summary_df   = pd.read_csv(os.path.join(_DATA_PATH, "bayesian_summary.csv"))
        df_joined    = pd.read_csv(os.path.join(_DATA_PATH, "conflict_inflation_joined.csv"))
    except FileNotFoundError:
        return render_template("bayesian.html", error=True)

    beta_mean = float(summary_df["mean"].iloc[0])
    hdi_low   = float(summary_df["hdi_low"].iloc[0])
    hdi_high  = float(summary_df["hdi_high"].iloc[0])
    prob_pos  = float(summary_df["prob_pos"].iloc[0])
    prob_neg  = float(summary_df["prob_neg"].iloc[0])

    kpis = {
        "beta_mean": f"{beta_mean:+.3f}%",
        "hdi":       f"[{hdi_low:.2f}, {hdi_high:.2f}]",
        "prob_pos":  f"{prob_pos:.1f}%",
        "prob_neg":  f"{prob_neg:.1f}%",
    }

    # ── Chart 1: Posterior distribution ──────────────────────────────────────
    beta_samples = posterior_df["beta_samples"].values
    hdi_mask     = (beta_samples >= hdi_low) & (beta_samples <= hdi_high)

    fig1 = go.Figure()
    fig1.add_trace(go.Histogram(
        x=beta_samples, nbinsx=100, name="Full posterior",
        marker_color="#3498db", opacity=0.6, histnorm="probability density",
    ))
    fig1.add_trace(go.Histogram(
        x=beta_samples[hdi_mask], nbinsx=80, name="94% HDI",
        marker_color="#e74c3c", opacity=0.6, histnorm="probability density",
    ))
    fig1.add_vline(x=0, line_dash="dash", line_color="white", line_width=2,
                   annotation_text="No effect (β=0)", annotation_position="top right",
                   annotation_font_color="white")
    fig1.add_vline(x=beta_mean, line_dash="dot", line_color="#f1c40f", line_width=2,
                   annotation_text=f"Mean β = {beta_mean:+.3f}",
                   annotation_position="top left", annotation_font_color="#f1c40f")
    fig1.update_layout(
        xaxis_title="β (% inflation per 1 SD increase in conflict)",
        yaxis_title="Density", template="plotly_dark", height=420,
        barmode="overlay", legend=dict(orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    chart_posterior = fig1.to_html(**_PLOTLY_OPTS)

    # ── Chart 2: Conflict vs inflation scatter ────────────────────────────────
    df_plot = df_joined.dropna(subset=["incidents_lag1", "inflation_pct"])
    z       = np.polyfit(df_plot["incidents_lag1"], df_plot["inflation_pct"], 1)
    p       = np.poly1d(z)
    x_line  = np.linspace(df_plot["incidents_lag1"].min(),
                          df_plot["incidents_lag1"].max(), 100)

    fig2 = go.Figure()
    for country, color in COUNTRY_COLORS.items():
        sub = df_plot[df_plot["country"] == country]
        if sub.empty:
            continue
        fig2.add_trace(go.Scatter(
            x=sub["incidents_lag1"], y=sub["inflation_pct"],
            mode="markers+text", name=country,
            text=sub["year"].astype(str), textposition="top center",
            textfont=dict(size=10),
            marker=dict(color=color, size=(sub["fatalities"].clip(upper=500) / 25 + 8),
                        opacity=0.85),
        ))
    fig2.add_trace(go.Scatter(
        x=x_line, y=p(x_line), mode="lines", name="OLS trend",
        line=dict(color="white", width=1, dash="dot"),
    ))
    fig2.update_layout(
        title="Conflict (T-1) vs Inflation (T) — Sahel 2021–2024",
        xaxis_title="Conflict Incidents (previous year)",
        yaxis_title="Inflation Rate (%)",
        template="plotly_dark", height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    chart_scatter = fig2.to_html(**_PLOTLY_OPTS)

    model_text = {
        "beta_mean": beta_mean,
        "hdi_low":   hdi_low,
        "hdi_high":  hdi_high,
        "prob_pos":  prob_pos,
        "prob_neg":  prob_neg,
    }

    return render_template(
        "bayesian.html",
        error=False,
        kpis=kpis,
        chart_posterior=chart_posterior,
        chart_scatter=chart_scatter,
        model=model_text,
    )
