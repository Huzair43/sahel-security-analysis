from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path


def _load_dotenv_if_available() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    dotenv_path = repo_root / ".env"

    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        if dotenv_path.exists():
            raise RuntimeError(
                "Found a .env file but 'python-dotenv' is not installed. "
                "Install dependencies with: pip install -r requirements.txt"
            )
        return

    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    else:
        load_dotenv()


_load_dotenv_if_available()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Create a .env file (see .env.example) or export it in your shell."
        )
    return value


@dataclass(frozen=True)
class Settings:
    acled_username: str
    acled_password: str
    acled_token_url: str
    acled_base_url: str
    countries: list[str]
    start_date: str
    end_date: str
    data_raw_path: str
    data_processed_path: str
    request_timeout_s: int


def get_settings() -> Settings:
    end_date = os.getenv("END_DATE") or date.today().isoformat()
    request_timeout_s = int(os.getenv("REQUEST_TIMEOUT_S") or "30")

    return Settings(
        acled_username=_require_env("ACLED_USERNAME"),
        acled_password=_require_env("ACLED_PASSWORD"),
        acled_token_url=os.getenv("ACLED_TOKEN_URL") or "https://acleddata.com/oauth/token",
        acled_base_url=os.getenv("ACLED_BASE_URL")
        or "https://acleddata.com/api/acled/read?_format=json",
        countries=[
            c.strip()
            for c in (os.getenv("COUNTRIES") or "Burkina Faso,Mali,Niger").split(",")
            if c.strip()
        ],
        start_date=os.getenv("START_DATE") or "2020-01-01",
        end_date=end_date,
        data_raw_path=os.getenv("DATA_RAW_PATH") or "data/raw/",
        data_processed_path=os.getenv("DATA_PROCESSED_PATH") or "data/processed/",
        request_timeout_s=request_timeout_s,
    )
