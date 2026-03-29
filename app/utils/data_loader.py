import pandas as pd
import streamlit as st
import os

PROCESSED_PATH = "data/processed/"

@st.cache_data
def load_main_data() -> pd.DataFrame:
    """Load and cache the main ACLED processed dataset."""
    df = pd.read_csv(
        os.path.join(PROCESSED_PATH, "acled_processed.csv"),
        parse_dates=["event_date"]
    )
    return df

@st.cache_data
def load_monthly_by_country() -> pd.DataFrame:
    """Load monthly aggregation by country."""
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "monthly_by_country.csv"))
    df["year_month_dt"] = pd.to_datetime(df["year_month"])
    return df

@st.cache_data
def load_monthly_by_type() -> pd.DataFrame:
    """Load monthly aggregation by event type."""
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "monthly_by_type.csv"))
    df["year_month_dt"] = pd.to_datetime(df["year_month"])
    return df

@st.cache_data
def load_monthly_total() -> pd.DataFrame:
    """Load total monthly aggregation (all countries combined)."""
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "monthly_total.csv"))
    df["year_month_dt"] = pd.to_datetime(df["year_month"])
    return df

# --- Shared color palettes (consistent across all pages)
EVENT_COLORS = {
    "Battles":                       "#e74c3c",
    "Violence against civilians":    "#e67e22",
    "Explosions/Remote violence":    "#9b59b6",
    "Protests":                      "#3498db",
    "Riots":                         "#f1c40f",
    "Strategic developments":        "#2ecc71",
}

COUNTRY_COLORS = {
    "Burkina Faso": "#e74c3c",
    "Mali":         "#3498db",
    "Niger":        "#2ecc71",
}