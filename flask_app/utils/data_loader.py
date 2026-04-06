"""
Data loader for the Flask app.

Equivalent to app/utils/data_loader.py (Streamlit) but sans @st.cache_data.
Les DataFrames sont chargés une seule fois au démarrage via lru_cache.
"""
import os
import functools

import pandas as pd

PROCESSED_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "data", "processed"
)


@functools.lru_cache(maxsize=None)
def load_main_data() -> pd.DataFrame:
    df = pd.read_csv(
        os.path.join(PROCESSED_PATH, "acled_processed.csv"),
        parse_dates=["event_date"],
    )
    return df


@functools.lru_cache(maxsize=None)
def load_monthly_by_country() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "monthly_by_country.csv"))
    df["year_month_dt"] = pd.to_datetime(df["year_month"])
    return df


@functools.lru_cache(maxsize=None)
def load_monthly_by_type() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "monthly_by_type.csv"))
    df["year_month_dt"] = pd.to_datetime(df["year_month"])
    return df


@functools.lru_cache(maxsize=None)
def load_monthly_total() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "monthly_total.csv"))
    df["year_month_dt"] = pd.to_datetime(df["year_month"])
    return df


# ── Shared colour palettes ────────────────────────────────────────────────────
EVENT_COLORS = {
    "Battles":                    "#e74c3c",
    "Violence against civilians": "#e67e22",
    "Explosions/Remote violence": "#9b59b6",
    "Protests":                   "#3498db",
    "Riots":                      "#f1c40f",
    "Strategic developments":     "#2ecc71",
}

COUNTRY_COLORS = {
    "Burkina Faso": "#e74c3c",
    "Mali":         "#3498db",
    "Niger":        "#2ecc71",
}
