"""Central configuration for OG-OIP.

All data produced by the generator is SYNTHETIC. Database credentials are read
from environment variables and are never hard-coded.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
QUARANTINE_DIR = PROCESSED_DIR / "quarantine"
MARTS_DIR = DATA_DIR / "marts"
REAL_DIR = DATA_DIR / "real"
REFERENCE_DIR = DATA_DIR / "reference"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"
EXCEL_DIR = ROOT / "excel"

RANDOM_SEED = 42
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
COMPANY = "PetroNexa Energy"  # FICTIONAL

SYNTHETIC_NOTICE = (
    "All operational, production, financial, maintenance, inventory, sensor and HSE "
    "data in this project are synthetic/simulated and created for portfolio "
    "demonstration purposes. They do not represent actual operations of a real company."
)

# ---- Documented business assumptions (synthetic) -----------------------------
BBL_PER_M3 = 6.28981          # 1 Sm3 of liquid ~ 6.28981 US barrels
MCF_PER_SM3 = 0.0353147       # 1 Sm3 of gas ~ 35.3147 scf = 0.0353147 mcf
MCF_PER_BOE = 6.0             # common industry convention for gas-to-BOE
EXPOSURE_HOURS_PER_ACTIVE_WELL_DAY = 30.0   # ASSUMPTION for incident-rate denominators
INCIDENT_RATE_BASE_HOURS = 200_000          # TRIR-style normalisation base
FORECAST_HORIZON_DAYS = 30
ML_HORIZON_DAYS = 7


@dataclass(frozen=True)
class DBConfig:
    host: str = os.environ.get("PGHOST", "localhost")
    port: int = int(os.environ.get("PGPORT", "5432"))
    database: str = os.environ.get("PGDATABASE", "og_oip")
    user: str = os.environ.get("PGUSER", "postgres")
    password: str = os.environ.get("PGPASSWORD", "")  # never hard-code


def ensure_dirs() -> None:
    for d in (RAW_DIR, PROCESSED_DIR, QUARANTINE_DIR, MARTS_DIR, REAL_DIR,
              REFERENCE_DIR, FIGURES_DIR, TABLES_DIR, EXCEL_DIR):
        d.mkdir(parents=True, exist_ok=True)
