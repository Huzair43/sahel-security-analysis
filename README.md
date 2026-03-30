# Sahel Security Analysis

## Project Status

 This project is currently under development.

Planned completion: June 2026

Current progress:

* [x] Project setup
* [ ] Data collection & cleaning
* [ ] Exploratory Data Analysis (EDA)
* [ ] Visualization & mapping
* [ ] Dashboard deployment

---

## Overview

The Sahel region, particularly the AES zone (Burkina Faso, Mali, Niger), continues to experience overlapping security and economic shocks. The dataset produced by the pipeline is designed to feed both descriptive dashboards and causal/statistical modeling that explains how violence, prices, and policy signals co-move.

The goal is to combine rigorous time-series modeling with transparent dashboards so that technical partners and policy stakeholders can interrogate both trends (exploratory) and credible model-based statements about uncertainty and confounding.

---

## Objectives

* Analyze 10+ years of security incidents across Burkina Faso, Mali, and Niger
* Identify temporal patterns: trends, seasonality, and structural changes
* Detect and visualize geographical hotspots of violence
* Explore links between conflict intensity and economic indicators (GDP, food prices)
* Build an interactive dashboard for data exploration

---

## Data Sources

* **ACLED**: Geolocated conflict event data
* **World Bank**: Macroeconomic indicators (GDP, inflation, etc.)
* **FAOSTAT**: Food price data
* **UEMOA**:Macroeconomic indicators

---  

## Modeling roadmap

1. **Bayesian VAR with explicit uncertainty** – build a hierarchical VAR that pools across Burkina Faso, Mali, and Niger while allowing parameter uncertainty to propagate into credible intervals for impulse responses. The model will rely on `statsmodels`, `pymc`, and `arviz` to sample the posterior and report `95%` intervals for projected incidents, fatalities, and inflation.
2. **Confounder controls** – include lagged economic variables, conflict intensity indices, and seasonality dummies to control for omitted variable bias when estimating cross-series effects. The pipeline already creates lagged incidents/fatalities/intensity, and we extend this with conditional regressions inside the Bayesian VAR.
3. **Dashboard-ready outputs** – surface the posterior distributions as fan charts in the dashboard so end users see both the median forecast and the associated uncertainty bands.

---  

## Quickstart

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   ./.venv/Scripts/activate  # use `./.venv/bin/activate` on macOS/Linux
   pip install -r requirements.txt
   ```

2. Configure credentials and overrides:
   * Copy `.env.example` to `.env`.
   * Set `ACLED_USERNAME` and `ACLED_PASSWORD`; optionally override `START_DATE`, `END_DATE`, `COUNTRIES`, `DATA_RAW_PATH`, or `DATA_PROCESSED_PATH` in the same `.env`.

3. Run the pipeline:

   ```bash
   python main.py
   ```

   After the run you will find `data/raw/acled_raw_<date>.csv` plus the latest `data/processed/acled_processed.csv`, `monthly_*`, and `conflict_inflation_joined.csv`.

4. Launch the dashboard (Streamlit):

   ```bash
   cd app
   streamlit run app.py
   ```

   The dashboard reads `data/processed/acled_processed.csv` and caches aggregated views via `app/utils/data_loader.py`.

5. Inspect modeling notebooks:
   * Open `notebooks/03_temporal_analysis.ipynb` to follow the Bayesian VAR scaffolding and credible interval outputs; it now loads secrets from `.env`.
   * Clean or rerun the other notebooks (`notebooks/01_data_exploration.ipynb`, `notebooks/02_interactive_map.ipynb`) if you want fresher snapshots or smaller output sizes.

---  

## Key Features (Planned)

### Temporal Analysis

* Evolution of incidents over time
* Detection of peaks and major shifts
* Seasonality patterns

### Geospatial Analysis

* Interactive conflict maps
* Hotspot detection
* Focus on the “three borders” region

### Dashboard

* Built with Streamlit
* Filters by country, event type, and time range
* Publicly accessible via web deployment

---

## Tech Stack

* Python
* Pandas
* Plotly
* Geopandas
* Folium
* Streamlit
* Git

---

## Project Structure

```
sahel-security-analysis/
│
├── data/              # Raw and processed datasets
├── notebooks/         # Exploratory analysis
├── app/               # Streamlit dashboard
├── config/            # Settings loader (env vars)
├── src/               # Data pipeline code
├── main.py            # Pipeline entrypoint
├── debug.py           # API diagnostics
├── debug2.py          # API diagnostics
├── README.md
└── requirements.txt
```

---

## Why This Project Matters

This project goes beyond technical analysis. It focuses on a region that is often underrepresented in data science work, aiming to provide meaningful insights through both data and contextual understanding.

---

## Next Steps

* Data collection and preprocessing
* Exploratory data analysis (EDA)
* Feature engineering
* Visualization development
* Dashboard implementation and deployment

---

## Author

Ousaïrou Bagagnan
Data Science Student

