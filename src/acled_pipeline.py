import requests
import pandas as pd
import os
from datetime import datetime
from config.config import (
    ACLED_USERNAME, ACLED_PASSWORD,
    ACLED_TOKEN_URL, ACLED_BASE_URL,
    COUNTRIES, START_DATE,
    DATA_RAW_PATH, DATA_PROCESSED_PATH
)


class ACLEDPipeline:
    """
    Pipeline for collecting and cleaning ACLED conflict data
    for the Sahel region (Burkina Faso, Mali, Niger).
    Uses OAuth2 authentication and automatic pagination.
    """

    def __init__(self):
        self.token         = None
        self.refresh_token = None
        self._authenticate()

    # ------------------------------------------------------------------
    # 0. AUTHENTICATION
    # ------------------------------------------------------------------
    def _authenticate(self):
        """Obtain an OAuth2 access token and refresh token."""
        print("Authenticating with ACLED API...")
        response = requests.post(
            ACLED_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username":   ACLED_USERNAME,
                "password":   ACLED_PASSWORD,
                "grant_type": "password",
                "client_id":  "acled",
            },
        )
        if response.status_code == 200:
            data               = response.json()
            self.token         = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            print("Authentication successful. Token valid for 24 hours.")
        else:
            raise Exception(
                f"Authentication failed: {response.status_code} — {response.text}"
            )

    def _refresh_access_token(self):
        """Renew the access token using the refresh token (valid 14 days)."""
        print("Refreshing access token...")
        response = requests.post(
            ACLED_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "refresh_token": self.refresh_token,
                "grant_type":    "refresh_token",
                "client_id":     "acled",
            },
        )
        if response.status_code == 200:
            data               = response.json()
            self.token         = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            print("Token successfully refreshed.")
        else:
            raise Exception(f"Token refresh failed: {response.text}")

    @property
    def _headers(self) -> dict:
        """Authorization headers for all API requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

    # ------------------------------------------------------------------
    # 1. DATA FETCHING WITH PAGINATION
    # ------------------------------------------------------------------
    def fetch_country(self, country: str, page_size: int = 5000) -> pd.DataFrame:
        """Fetch all data for a single country using pagination."""
        all_frames = []
        page       = 1

        while True:
            url = (
                f"https://acleddata.com/api/acled/read?_format=json"
                f"&country={country}"
                f"&event_date={START_DATE}"
                f"&event_date_where=BETWEEN"
                f"&event_date={START_DATE}|2026-12-31"
                f"&limit={page_size}"
                f"&page={page}"
                f"&fields=event_id_cnty|event_date|event_type|sub_event_type|"
                f"disorder_type|actor1|actor2|country|admin1|admin2|"
                f"location|latitude|longitude|fatalities|notes"
            )

            response  = requests.get(url, headers=self._headers)
            json_data = response.json()

            if json_data.get("status") != 200:
                print(f"  API error on page {page} for {country}: {json_data}")
                break

            data = json_data.get("data", [])
            if not data:
                break

            df = pd.DataFrame(data)
            all_frames.append(df)
            print(f"  [{country}] Page {page} -> {len(df):,} records")

            if len(data) < page_size:
                break

            page += 1

        if not all_frames:
            print(f"  No data retrieved for {country}.")
            return pd.DataFrame()

        return pd.concat(all_frames, ignore_index=True)


    def fetch_all_countries(self, page_size: int = 5000) -> pd.DataFrame:
        """
        Fetch data for all Sahel countries individually and merge.
        Separate requests per country to avoid ACLED's OR syntax issues.
        """
        print(f"Fetching data for: {', '.join(COUNTRIES)}")
        print(f"Date range: {START_DATE} to today\n")

        all_frames = []
        for country in COUNTRIES:
            df = self.fetch_country(country, page_size)
            if not df.empty:
                all_frames.append(df)

        if not all_frames:
            raise Exception("No data retrieved for any country.")

        combined = pd.concat(all_frames, ignore_index=True)
        print(f"\nTotal raw records: {len(combined):,}")
        return combined

    # ------------------------------------------------------------------
    # 2. DATA CLEANING
    # ------------------------------------------------------------------
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and enrich the raw ACLED data.
        - Enforce correct data types
        - Extract time features from event_date
        - Remove rows with missing coordinates
        - Remove duplicate records
        """

        # --- Parse dates
        df["event_date"] = pd.to_datetime(df["event_date"])

        # --- Numeric types
        df["fatalities"] = pd.to_numeric(df["fatalities"], errors="coerce").fillna(0).astype(int)
        df["latitude"]   = pd.to_numeric(df["latitude"],   errors="coerce")
        df["longitude"]  = pd.to_numeric(df["longitude"],  errors="coerce")

        # --- Extract time features (used later for trend analysis and dashboard filters)
        df["year"]       = df["event_date"].dt.year
        df["month"]      = df["event_date"].dt.month
        df["week"]       = df["event_date"].dt.isocalendar().week.astype(int)
        df["year_month"] = df["event_date"].dt.strftime("%Y-%m")
        df["year_week"]  = df["event_date"].dt.strftime("%Y-W%V")

        # --- Drop rows with missing coordinates (cannot be mapped)
        before  = len(df)
        df      = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
        dropped = before - len(df)
        if dropped:
            print(f"  Removed {dropped} rows with missing coordinates.")

        # --- Remove duplicates based on ACLED unique event ID
        before = len(df)
        df     = df.drop_duplicates(subset=["event_id_cnty"]).reset_index(drop=True)
        dupes  = before - len(df)
        if dupes:
            print(f"  Removed {dupes} duplicate records.")

        # --- Sort chronologically
        df = df.sort_values("event_date").reset_index(drop=True)

        print(f"Cleaning complete: {len(df):,} valid records.")
        return df

    # ------------------------------------------------------------------
    # 3. SAVING
    # ------------------------------------------------------------------
    def save_data(self, df: pd.DataFrame):
        """
        Save both a dated raw snapshot and the latest processed file.
        - Raw file: timestamped, kept for historical reference
        - Processed file: always overwritten with the latest clean data
        """
        os.makedirs(DATA_RAW_PATH,       exist_ok=True)
        os.makedirs(DATA_PROCESSED_PATH, exist_ok=True)

        today          = datetime.today().strftime("%Y-%m-%d")
        raw_path       = f"{DATA_RAW_PATH}acled_raw_{today}.csv"
        processed_path = f"{DATA_PROCESSED_PATH}acled_processed.csv"

        df.to_csv(raw_path,       index=False)
        df.to_csv(processed_path, index=False)

        print(f"\nSaved raw snapshot  -> {raw_path}")
        print(f"Saved processed file -> {processed_path}")

    # ------------------------------------------------------------------
    # 4. SUMMARY
    # ------------------------------------------------------------------
    def summary(self, df: pd.DataFrame):
        """Print a quick overview of the collected dataset."""
        print("\n" + "="*55)
        print("DATASET SUMMARY — SAHEL CONFLICT MONITOR")
        print("="*55)
        print(f"Date range      : {df['event_date'].min().date()} -> {df['event_date'].max().date()}")
        print(f"Total incidents : {len(df):,}")
        print(f"Total fatalities: {df['fatalities'].sum():,}")

        print("\nBy country:")
        print(df.groupby("country").agg(
            incidents  =("event_type",  "count"),
            fatalities =("fatalities",  "sum")
        ).to_string())

        print("\nBy event type:")
        print(df["event_type"].value_counts().to_string())

        print("\nBy year:")
        print(df.groupby("year")["event_id_cnty"].count().to_string())