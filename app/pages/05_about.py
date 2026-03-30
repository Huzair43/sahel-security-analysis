# app/pages/05_about.py
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.style import apply_global_style, page_header

st.set_page_config(page_title="About", page_icon="📖", layout="wide")
apply_global_style()

page_header(
    title="About this Project",
    subtitle="Methodology, data sources, findings and limitations",
    icon="📖"
)

# ── Section 1: Project overview ───────────────────────────
st.markdown("### What is the Sahel Security Analysis?")
st.markdown("""
The Sahel Security Analysis is an open-source data intelligence platform
that analyzes armed conflict dynamics and their economic consequences
in three countries: Burkina Faso, Mali, and Niger.

The project was built to answer a fundamental question: does conflict
in a given zone affect food prices and economic stability in that same
zone? To answer this, we combine conflict event data from ACLED with
macroeconomic indicators from the IMF, and apply both classical
statistical methods and Bayesian probabilistic modeling.

The platform is designed for researchers, humanitarian organizations,
policy analysts, and anyone working on fragility and food security
in the Sahel region.
""")

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 2: Data sources ───────────────────────────────
st.markdown("### Data Sources")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **ACLED: Armed Conflict Location and Event Data**

    ACLED is the primary data source for conflict events. It is a
    disaggregated conflict database that collects real-time data on
    political violence and protest events around the world.

    For this project, we collected 23,156 conflict events across
    Burkina Faso, Mali, and Niger from January 2020 to March 2025,
    using the ACLED API with OAuth2 authentication.

    Each event contains the date, location (latitude and longitude),
    administrative region, event type, actors involved, number of
    fatalities, and a detailed narrative note.

    Access level: Research (12-month data lag applies).
    """)

with col2:
    st.markdown("""
    **IMF World Economic Outlook: Inflation Data**

    For economic indicators, we use the IMF DataMapper API, which
    provides annual consumer price inflation rates (indicator PCPIPCH)
    for Burkina Faso, Mali, and Niger from 2018 to 2024.

    The IMF was selected over other sources (WFP/HDX, World Bank JMR)
    for three reasons: it is fully independent from ACLED (avoiding
    circular reasoning), it covers our entire study period, and it
    is the institutional reference for macroeconomic data in West Africa.

    Known limitation: the data is annual and national-level, which
    limits the granularity of our economic analysis. Sub-national
    monthly price data remains a priority for future work, conditioned
    on data availability in the region.
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 3: Methodology ────────────────────────────────
st.markdown("### Methodology")

tab1, tab2, tab3, tab4 = st.tabs([
    "Conflict Analysis",
    "Economic Integration",
    "Bayesian Model",
    "Data Pipeline",
])

with tab1:
    st.markdown("""
    **Temporal Analysis**

    Conflict events are aggregated at the monthly level per country
    to produce time series of incident counts and fatality totals.
    We apply a 3-month rolling average to smooth short-term volatility
    and reveal the underlying trend.

    **Anomaly Detection**

    We use Z-score normalization to identify months with abnormally
    high conflict activity. A month is flagged as anomalous when its
    Z-score exceeds 1.5 standard deviations from the mean,
    following the formula: Z = (x minus μ) divided by σ.

    These anomalous months consistently correspond to real events:
    the coups d'état in Burkina Faso (January and September 2022),
    military operations in northern Mali, and the Niger coup of
    July 2023.

    **Trend Forecasting**

    We fit a linear regression on the monthly incident time series
    to estimate the overall conflict trajectory. The model produces
    a 6-month forward projection based on the historical trend.
    This is a baseline model whose uncertainty is more rigorously
    treated in the Bayesian module.

    **Cross-country Correlation**

    We compute Pearson correlation coefficients between the monthly
    incident series of the three countries to test whether conflict
    dynamics are regionally synchronized. A high positive correlation
    suggests that the same armed groups operate across borders,
    which is consistent with the known activity of JNIM and ISWAP
    in the Sahel.
    """)

with tab2:
    st.markdown("""
    **Source Selection Process**

    The selection of economic data involved several iterations.
    Our first attempt used the WFP Global Food Prices dataset via
    the HDX API, which provides market-level food prices (millet,
    sorghum, maize) for our three countries. However, the WFP data
    only covers up to 2021, leaving only 24 months of overlap with
    our conflict data: insufficient for robust analysis.

    We then evaluated the World Bank Joint Monitoring Report (JMR),
    which already integrates ACLED conflict data as an input. Using
    this dataset would have introduced circular reasoning, that is,
    using a conclusion to prove itself, so it was discarded on
    methodological grounds.

    The IMF DataMapper API was ultimately selected as it provides
    independent, reliable, annual inflation data covering our full
    study period.

    **Conflict-Inflation Join**

    We aggregate ACLED data at the country-year level and join it
    with IMF inflation data on the country and year keys. We build
    two versions of the joined dataset: a contemporaneous join
    (conflict and inflation in the same year) and a lagged join
    (conflict at year T predicts inflation at year T+1).

    **Correlation Results**

    The Pearson correlation analysis found no statistically significant
    linear relationship between conflict intensity and national inflation
    at any lag. This is expected given the small sample size (N=15)
    and the aggregation mismatch between local conflict dynamics and
    national price indices. These limitations directly motivated the
    Bayesian model.
    """)

with tab3:
    st.markdown("""
    **Why Bayesian Statistics?**

    With only 12 country-year observations after applying the lag,
    frequentist inference has very low statistical power. A p-value
    of 0.05 requires roughly 30 observations for reliable inference
    in simple regression: we have less than half that.

    The Bayesian approach addresses this by quantifying uncertainty
    explicitly through posterior distributions rather than producing
    binary significant or not-significant decisions.

    **Model Specification**

    We fit two models. The simple model uses a single global intercept:
    inflation(t) = α + β × conflict_z(t-1) + ε.

    The hierarchical model gives each country its own baseline
    inflation intercept while sharing the conflict effect β across
    all three countries: α_c drawn from Normal(μ_α, σ_α),
    where c belongs to the set of Burkina Faso, Mali, and Niger.

    **Priors**

    We use weakly informative priors that encode minimal assumptions.
    The prior on α reflects that inflation in the Sahel is typically
    between 0% and 15%. The prior on β is centered at zero because
    we do not assume a positive or negative effect a priori.

    **Sampling**

    Both models were fit using MCMC with the NUTS sampler via PyMC v5.
    We ran 4 chains with 4,000 draws and 2,000 tuning steps each,
    for a total of 16,000 posterior samples. All R-hat values
    converged to 1.0, confirming reliable inference.

    **Results**

    The posterior mean of β is -0.416 with a 94% Highest Density
    Interval of [-2.302, +1.399]. The HDI includes zero, meaning
    we cannot establish a credible positive or negative effect
    of conflict on national inflation with the available data.

    The probability that β is positive (conflict increases inflation)
    is 33%. The probability that β is negative is 67%. Neither is
    conclusive. The result is consistent across both the simple and
    hierarchical models, confirming its robustness.

    The country-specific intercepts are nearly identical across
    the three countries (approximately 5%), which is economically
    meaningful given their shared currency (CFA Franc) and
    central bank (BCEAO).
    """)

with tab4:
    st.markdown("""
    **Architecture**

    The project follows a modular pipeline architecture with clear
    separation between data collection, processing, analysis, and
    visualization layers.

    The data pipeline (src/acled_pipeline.py) authenticates with
    the ACLED API using OAuth2, fetches data for each country
    separately using pagination, cleans and enriches the raw data,
    and saves both a timestamped raw snapshot and a processed file
    that is overwritten on each update.

    **Technology Stack**

    The project is built entirely in Python. Data processing uses
    Pandas and NumPy. Geospatial visualization uses Folium with
    the streamlit-folium integration. Time series visualization
    uses Plotly. The Bayesian model uses PyMC v5 with ArviZ for
    diagnostics. The dashboard is built with Streamlit.

    **Update Frequency**

    ACLED publishes new conflict data weekly. The pipeline can be
    re-run at any time to fetch the latest events. At the Research
    access level, data is available with a 12-month lag relative
    to real-time. Partner and Enterprise access levels provide
    weekly real-time data.

    **Reproducibility**

    All analysis notebooks are self-contained and can be run in
    sequence to reproduce the full pipeline from raw API data to
    final dashboard. Credentials are stored in a local config file
    that is excluded from version control via .gitignore.
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 4: Key findings ───────────────────────────────
st.markdown("### Key Findings")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Conflict Escalation**

    The Sahel experienced a sharp escalation in conflict intensity
    between 2020 and 2022, peaking at 5,649 incidents in 2022.
    Burkina Faso is the most affected country with 10,086 incidents
    and 26,720 fatalities over the study period, followed by Mali
    with 9,270 incidents and Niger with 3,800 incidents.

    Violence against civilians is the most common event type,
    accounting for 31% of all incidents. This reflects the
    deliberate targeting of non-combatants by armed groups as
    a strategy of territorial control and population displacement.
    """)

with col2:
    st.markdown("""
    **Regional Synchronization**

    The cross-country correlation analysis reveals that conflict
    dynamics in Burkina Faso, Mali, and Niger are moderately
    synchronized. This is consistent with the known cross-border
    operations of JNIM (Jama'at Nusrat al-Islam wal-Muslimin)
    and ISWAP (Islamic State West Africa Province), which operate
    across the three countries without respecting national borders.

    The year 2022 was a regional inflection point, marked by
    two coups in Burkina Faso, continued military operations
    in northern Mali, and the beginning of the security
    deterioration in western Niger.
    """)

with col3:
    st.markdown("""
    **Economic Impact**

    The Bayesian analysis found no statistically credible linear
    relationship between conflict intensity and national inflation
    at the country-year level. The posterior mean of β is -0.416
    with a 94% HDI that includes zero.

    This null result is methodologically expected given the
    aggregation mismatch between local conflict events and
    national price indices. The high residual noise (σ = 4.1)
    suggests that other factors, namely global commodity prices,
    rainfall shocks, ECOWAS sanctions, and monetary policy,
    explain more of the inflation variance than conflict alone.
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 5: Limitations ────────────────────────────────
st.markdown("### Limitations and Future Work")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Current limitations**

    The most significant limitation is the aggregation mismatch
    between conflict data (sub-national, weekly) and economic data
    (national, annual). A conflict in the Sahel region of Burkina
    Faso affects local market prices immediately, but this signal
    is diluted when aggregated to the national CPI level.

    The 12-month data lag at the Research access level means that
    the most recent conflict events are not reflected in the analysis.
    Partner or Enterprise access would enable real-time monitoring.

    The linear Bayesian model does not capture threshold effects,
    where conflict below a certain intensity may have no economic
    impact but above a threshold triggers sharp price responses.
    """)

with col2:
    st.markdown("""
    **Planned improvements**

    The primary constraint for sub-national economic analysis is
    data availability. While the FAO FPMA tool and WFP VAM platform
    collect market-level food prices across the Sahel, these datasets
    either stop before 2022 or are not accessible in a structured
    format suitable for automated analysis. Obtaining reliable
    sub-national monthly price data for Burkina Faso, Mali, and Niger
    remains an open challenge that conditions all future modeling work.

    On the modeling side, a non-linear threshold model would better
    capture the regime-switching dynamics observed in conflict-affected
    food markets. Controlling for confounders such as rainfall anomalies,
    global cereal prices, and exchange rate movements would also
    significantly improve the explanatory power of the economic model.
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 6: Citation ───────────────────────────────────
st.markdown("### Citation and Attribution")
st.markdown("""
If you use this platform or its analysis in your work, please cite
the underlying data sources.

ACLED (Armed Conflict Location and Event Data Project). Raleigh, C.,
Linke, A., Hegre, H. and Karlsen, J. 2010. Introducing ACLED: Armed
Conflict Location and Event Data. Journal of Peace Research 47(5).

International Monetary Fund. World Economic Outlook Database.
Washington DC: IMF, 2024.
""")

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Sahel Security Analysis · Built with ACLED and IMF data · Streamlit")