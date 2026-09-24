"""Load raw CSV tables from data/raw (as delivered, defects included)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from og_oip import config
from og_oip.data_generation.generator import DIM_TABLES, FACT_TABLES


def load_table(name: str, base: Path | None = None) -> pd.DataFrame:
    base = base or config.RAW_DIR
    return pd.read_csv(base / f"{name}.csv", low_memory=False)


def load_all(base: Path | None = None) -> dict[str, pd.DataFrame]:
    return {t: load_table(t, base) for t in DIM_TABLES + FACT_TABLES}


DATE_COLS = ["date", "commission_date", "installation_date", "order_date", "promised_date", "received_date"]


def load_processed(base: Path | None = None) -> dict[str, pd.DataFrame]:
    """Processed tables with proper dtypes (dates -> datetime64)."""
    t = load_all(base or config.PROCESSED_DIR)
    for name, df in t.items():
        for c in DATE_COLS:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        if "dq_flag" in df.columns:
            df["dq_flag"] = df["dq_flag"].fillna("")
    t["dim_date"]["date"] = pd.to_datetime(t["dim_date"]["date"])
    return t
