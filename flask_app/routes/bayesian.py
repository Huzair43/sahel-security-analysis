import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from flask import Blueprint, render_template

from flask_app.theme import (
    FONT_MONO,
    INK_3,
    INK_4,
    PLOTLY_OPTS,
    RULE_STRONG,
    SIGNAL,
    finalize,
)
from flask_app.utils.data_loader import COUNTRY_COLORS

bayesian_bp = Blueprint("bayesian", __name__)

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed"
)


@bayesian_bp.route("/bayesian")
def bayesian():
    # ── Chargement des résultats ─────────────────────────────────────────────
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
        "beta_mean": f"{beta_mean:+.3f}",
        "hdi":       f"{hdi_low:.2f} : {hdi_high:.2f}",
        "prob_pos":  f"{prob_pos:.1f}%",
        "prob_neg":  f"{prob_neg:.1f}%",
    }

    # ── Chart 1 : distribution a posteriori ──────────────────────────────────
    beta_samples = posterior_df["beta_samples"].values
    hdi_mask     = (beta_samples >= hdi_low) & (beta_samples <= hdi_high)

    fig1 = go.Figure()
    fig1.add_trace(go.Histogram(
        x=beta_samples, nbinsx=100, name="Full posterior",
        marker_color="rgba(255,255,255,0.10)",
        histnorm="probability density",
        hovertemplate="β %{x:.2f}<extra></extra>",
    ))
    fig1.add_trace(go.Histogram(
        x=beta_samples[hdi_mask], nbinsx=80, name="94% HDI",
        marker_color=SIGNAL, opacity=0.75,
        histnorm="probability density",
        hovertemplate="β %{x:.2f}<extra>94% HDI</extra>",
    ))
    fig1.add_vline(x=0, line_dash="solid", line_color=RULE_STRONG, line_width=1)
    fig1.add_vline(x=beta_mean, line_dash="dot", line_color=SIGNAL, line_width=1)

    # Annotations ancrées sur le papier : elles ne peuvent plus être rognées.
    for x_pos, text, color, anchor in [
        (0, "no effect, β = 0", INK_4, "left"),
        (beta_mean, f"mean β = {beta_mean:+.3f}", INK_3, "right"),
    ]:
        fig1.add_annotation(
            x=x_pos, y=1, yref="paper", text=text, showarrow=False,
            font=dict(family=FONT_MONO, size=9, color=color),
            xanchor=anchor, xshift=6 if anchor == "left" else -6,
            yanchor="bottom", yshift=4,
        )

    fig1.update_layout(barmode="overlay")
    finalize(fig1, height=380, margin=dict(l=8, r=8, t=48, b=8))
    fig1.update_xaxes(title_text="β, inflation points per 1 SD of conflict")
    fig1.update_yaxes(title_text="Density", showticklabels=False)
    chart_posterior = fig1.to_html(**PLOTLY_OPTS)

    # ── Chart 2 : conflit contre inflation ───────────────────────────────────
    df_plot = df_joined.dropna(subset=["incidents_lag1", "inflation_pct"])
    z       = np.polyfit(df_plot["incidents_lag1"], df_plot["inflation_pct"], 1)
    p       = np.poly1d(z)
    x_line  = np.linspace(df_plot["incidents_lag1"].min(),
                          df_plot["incidents_lag1"].max(), 100)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=x_line, y=p(x_line), mode="lines", name="OLS trend",
        line=dict(color=RULE_STRONG, width=1, dash="dot"),
        hoverinfo="skip",
    ))
    for country, color in COUNTRY_COLORS.items():
        sub = df_plot[df_plot["country"] == country]
        if sub.empty:
            continue
        fig2.add_trace(go.Scatter(
            x=sub["incidents_lag1"], y=sub["inflation_pct"],
            mode="markers+text", name=country,
            text=sub["year"].astype(str), textposition="top center",
            customdata=sub[["fatalities", "year"]].values,
            marker=dict(color=color,
                        size=(sub["fatalities"].clip(upper=500) / 30 + 7),
                        opacity=0.9,
                        line=dict(width=0)),
            hovertemplate="<b>" + country + " %{customdata[1]}</b><br>"
                          "Incidents %{x:,}<br>Inflation %{y:.1f}%<br>"
                          "Fatalities %{customdata[0]:,}<extra></extra>",
        ))
    # pad="y" : les étiquettes d'année placées au-dessus des points
    # seraient tronquées par le haut du cadre.
    finalize(fig2, height=420, pad="y", pad_pct=0.16,
             margin=dict(l=8, r=8, t=32, b=8))
    fig2.update_xaxes(title_text="Conflict incidents, previous year")
    fig2.update_yaxes(title_text="Inflation rate, %")
    chart_scatter = fig2.to_html(**PLOTLY_OPTS)

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
        n_obs=len(df_plot),
    )
