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


# ── Palettes partagées ────────────────────────────────────────────────────────
# Source unique : flask_app/theme.py. Réexportées ici pour les imports existants.
from flask_app.theme import COUNTRY_COLORS, EVENT_COLORS, EVENT_ORDER  # noqa: E402,F401
