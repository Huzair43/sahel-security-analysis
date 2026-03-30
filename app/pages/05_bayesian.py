# app/pages/05_bayesian.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_main_data, COUNTRY_COLORS
from utils.style import apply_global_style, page_header

st.set_page_config(page_title="Bayesian Model", page_icon="🔬", layout="wide")
apply_global_style()

page_header(
    title="Bayesian Model",
    subtitle="Probabilistic analysis of conflict impact on inflation — Sahel 2020–2024",
    icon="🔬"
)

# --- Load data
@st.cache_data
def load_bayesian_data():
    posterior = pd.read_csv("data/processed/bayesian_posterior.csv")
    summary   = pd.read_csv("data/processed/bayesian_summary.csv")
    joined    = pd.read_csv("data/processed/conflict_inflation_joined.csv")
    return posterior, summary, joined

try:
    posterior_df, summary_df, df_joined = load_bayesian_data()
except FileNotFoundError:
    st.error("Bayesian model results not found. Please run notebook 05_bayesian_model.ipynb first.")
    st.stop()

# --- Extract key stats
beta_mean = summary_df["mean"].iloc[0]
hdi_low   = summary_df["hdi_low"].iloc[0]
hdi_high  = summary_df["hdi_high"].iloc[0]
prob_pos  = summary_df["prob_pos"].iloc[0]
prob_neg  = summary_df["prob_neg"].iloc[0]

# ── Section 1: Key metrics ────────────────────────────────
st.markdown("### Model Results at a Glance")

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label="β Mean",
    value=f"{beta_mean:+.3f}%",
    help="Average effect of +1 SD conflict on inflation"
)
col2.metric(
    label="94% HDI",
    value=f"[{hdi_low:.2f}, {hdi_high:.2f}]",
    help="Highest Density Interval — credible range for β"
)
col3.metric(
    label="P(β > 0)",
    value=f"{prob_pos:.1f}%",
    help="Probability that conflict increases inflation"
)
col4.metric(
    label="P(β < 0)",
    value=f"{prob_neg:.1f}%",
    help="Probability that conflict decreases inflation"
)

st.markdown("---")

# ── Section 2: Posterior distribution ────────────────────
st.markdown("### Posterior Distribution of β")
st.markdown(
    "The full probability distribution over the conflict effect on inflation. "
    "A distribution centered on zero means the effect is uncertain."
)

beta_samples = posterior_df["beta_samples"].values

# HDI mask
hdi_mask    = (beta_samples >= hdi_low) & (beta_samples <= hdi_high)
hdi_samples = beta_samples[hdi_mask]

fig1 = go.Figure()

# Full posterior
fig1.add_trace(go.Histogram(
    x=beta_samples,
    nbinsx=100,
    name="Full posterior",
    marker_color="#3498db",
    opacity=0.6,
    histnorm="probability density",
))

# HDI region
fig1.add_trace(go.Histogram(
    x=hdi_samples,
    nbinsx=80,
    name="94% HDI",
    marker_color="#e74c3c",
    opacity=0.6,
    histnorm="probability density",
))

# Reference lines
fig1.add_vline(
    x=0, line_dash="dash", line_color="white", line_width=2,
    annotation_text="No effect (β=0)",
    annotation_position="top right",
    annotation_font_color="white",
)
fig1.add_vline(
    x=beta_mean, line_dash="dot", line_color="#f1c40f", line_width=2,
    annotation_text=f"Mean β = {beta_mean:+.3f}",
    annotation_position="top left",
    annotation_font_color="#f1c40f",
)

fig1.update_layout(
    xaxis_title="β (% inflation per 1 SD increase in conflict)",
    yaxis_title="Density",
    template="plotly_dark",
    height=420,
    barmode="overlay",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ── Section 3: Conflict vs inflation scatter ─────────────
st.markdown("### Conflict Intensity vs Inflation — Raw Data")
st.markdown(
    "Each point represents one country-year observation. "
    "The trend line shows the direction suggested by the data."
)

df_plot = df_joined.dropna(subset=["incidents_lag1", "inflation_pct"])

# Manual OLS trendline (avoids statsmodels numpy conflict)
z      = np.polyfit(df_plot["incidents_lag1"], df_plot["inflation_pct"], 1)
p      = np.poly1d(z)
x_line = np.linspace(
    df_plot["incidents_lag1"].min(),
    df_plot["incidents_lag1"].max(), 100
)
y_line = p(x_line)

fig2 = go.Figure()

# Points per country
for country, color in COUNTRY_COLORS.items():
    sub = df_plot[df_plot["country"] == country]
    if sub.empty:
        continue
    fig2.add_trace(go.Scatter(
        x=sub["incidents_lag1"],
        y=sub["inflation_pct"],
        mode="markers+text",
        name=country,
        text=sub["year"].astype(str),
        textposition="top center",
        textfont=dict(size=10),
        marker=dict(
            color=color,
            size=(sub["fatalities"].clip(upper=500) / 25 + 8),
            opacity=0.85,
        ),
    ))

# Manual trendline
fig2.add_trace(go.Scatter(
    x=x_line, y=y_line,
    mode="lines",
    name="OLS trend",
    line=dict(color="white", width=1, dash="dot"),
))

fig2.update_layout(
    title="Conflict (T-1) vs Inflation (T) — Sahel 2021–2024",
    xaxis_title="Conflict Incidents (previous year)",
    yaxis_title="Inflation Rate (%)",
    template="plotly_dark",
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Section 4: Model interpretation ──────────────────────
st.markdown("### How to Read This Model")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **What the model estimates:**

    We fit a Bayesian hierarchical linear regression:

    > *inflation(t) = α_country + β × conflict(t-1) + ε*

    - **α** = country-specific baseline inflation
    - **β** = effect of lagged conflict on inflation
    - **ε** = unexplained noise

    **Key finding:**

    β = {beta_mean:.3f} with 94% HDI [{hdi_low:.2f}, {hdi_high:.2f}]

    The HDI includes zero — we **cannot conclusively establish**
    a positive or negative causal effect with the available data.
    """)

with col2:
    st.markdown(f"""
    **Why the result is uncertain:**

    | Limitation | Impact |
    |---|---|
    | N = 12 observations | Low statistical power |
    | Annual national CPI | Too aggregated |
    | No confounders | Rainfall, oil prices not controlled |
    | Linear model only | May miss threshold effects |

    **What this means:**

    P(β > 0) = {prob_pos:.1f}% — conflict *may* increase inflation

    P(β < 0) = {prob_neg:.1f}% — conflict *may* decrease inflation

    Neither is conclusive. Sub-national monthly data
    would significantly improve the model's power.
    """)

st.markdown("---")

# ── Section 5: Methodology note ──────────────────────────
with st.expander("Methodology: Bayesian Hierarchical Model"):
    st.markdown("""
    ### Model Specification

    **Simple model:**
```
    α  ~ Normal(3, 5)
    β  ~ Normal(0, 2)
    σ  ~ HalfNormal(5)
    inflation ~ Normal(α + β × conflict_z, σ)
```

    **Hierarchical model:**
```
    μ_α ~ Normal(3, 5)
    σ_α ~ HalfNormal(3)
    α_c ~ Normal(μ_α, σ_α)   # country-specific intercept
    β   ~ Normal(0, 2)        # shared effect across countries
    σ   ~ HalfNormal(5)
    inflation ~ Normal(α_c + β × conflict_z, σ)
```

    **Sampling configuration:**
    - Sampler : NUTS (No-U-Turn Sampler)
    - Draws   : 4,000 × 4 chains = 16,000 posterior samples
    - Tuning  : 2,000 steps
    - target_accept = 0.95
    - All R-hat = 1.0 

    **Software:** PyMC v5, ArviZ, Python 3.10
    """)