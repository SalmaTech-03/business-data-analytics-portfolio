"""Loading, validation and cleaning of the customer and mailing-list datasets.

The two source files are:
    data/raw/p1-customers.xlsx    historical customers with a known Avg_Sale_Amount
    data/raw/p1-mailinglist.xlsx  the 250 prospects targeted by the campaign

Nothing in this module imputes or silently repairs data. Issues are reported
back to the caller so that they can be documented in docs/data_quality.md.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

CUSTOMERS_FILE = "p1-customers.xlsx"
MAILINGLIST_FILE = "p1-mailinglist.xlsx"

TARGET = "Avg_Sale_Amount"
ID_COLUMN = "Customer_ID"

# Columns excluded from modelling: personally identifying or purely locational.
NON_MODEL_COLUMNS = ["Name", "Address", "City", "State", "ZIP", "Store_Number"]

VALID_SEGMENTS = [
    "Credit Card Only",
    "Loyalty Club Only",
    "Loyalty Club and Credit Card",
    "Store Mailing List",
]


def load_customers(path: str | Path | None = None) -> pd.DataFrame:
    """Load the historical customer file used to train the model."""
    path = Path(path) if path else RAW_DIR / CUSTOMERS_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Customer file not found at {path}. Place p1-customers.xlsx in data/raw/."
        )
    return pd.read_excel(path)


def load_mailing_list(path: str | Path | None = None) -> pd.DataFrame:
    """Load the 250-prospect mailing list scored by the campaign model."""
    path = Path(path) if path else RAW_DIR / MAILINGLIST_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Mailing list not found at {path}. Place p1-mailinglist.xlsx in data/raw/."
        )
    return pd.read_excel(path)


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names so both files share one vocabulary.

    `#_Years_as_Customer` is renamed to `Years_as_Customer` because the leading
    `#` is awkward in formulas, SQL and BI tools.
    """
    out = df.copy()
    out.columns = [c.strip() for c in out.columns]
    return out.rename(columns={"#_Years_as_Customer": "Years_as_Customer"})


def check_data_quality(df: pd.DataFrame, name: str = "dataset") -> dict:
    """Run the data-quality checks documented in docs/data_quality.md.

    Returns a dictionary of findings rather than raising, so that the notebook
    can print the evidence behind every claim made in the documentation.
    """
    report: dict = {"dataset": name, "rows": len(df), "columns": len(df.columns)}
    report["missing_values"] = df.isna().sum().to_dict()
    report["total_missing"] = int(df.isna().sum().sum())
    report["duplicate_rows"] = int(df.duplicated().sum())
    if ID_COLUMN in df.columns:
        report["duplicate_ids"] = int(df[ID_COLUMN].duplicated().sum())
    if "Customer_Segment" in df.columns:
        report["segment_levels"] = sorted(df["Customer_Segment"].dropna().unique().tolist())
        report["unexpected_segments"] = sorted(
            set(report["segment_levels"]) - set(VALID_SEGMENTS)
        )
    if TARGET in df.columns:
        report["non_positive_target"] = int((df[TARGET] <= 0).sum())
        report["target_min"] = float(df[TARGET].min())
        report["target_max"] = float(df[TARGET].max())
    if "Avg_Num_Products_Purchased" in df.columns:
        report["negative_products"] = int((df["Avg_Num_Products_Purchased"] < 0).sum())
    for col in ("Score_Yes", "Score_No"):
        if col in df.columns:
            report[f"{col}_out_of_range"] = int(
                ((df[col] < 0) | (df[col] > 1)).sum()
            )
    if {"Score_Yes", "Score_No"}.issubset(df.columns):
        report["max_score_sum_deviation"] = float(
            (df["Score_Yes"] + df["Score_No"] - 1).abs().max()
        )
    report["dtypes"] = {c: str(t) for c, t in df.dtypes.items()}
    return report


def flag_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Boolean mask of Tukey-fence outliers. Used for reporting, not removal."""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return (series < q1 - k * iqr) | (series > q3 + k * iqr)


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the training frame: standardise names, enforce dtypes, sort."""
    out = standardise_columns(df)
    out["Customer_Segment"] = out["Customer_Segment"].astype(str).str.strip()
    numeric = ["Avg_Sale_Amount", "Avg_Num_Products_Purchased", "Years_as_Customer"]
    for col in numeric:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    if "ZIP" in out.columns:
        out["ZIP"] = out["ZIP"].astype(str).str.zfill(5)
    return out.sort_values(ID_COLUMN).reset_index(drop=True)


def clean_mailing_list(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the scoring frame using the same rules as the training frame."""
    out = clean_customers(df)
    for col in ("Score_Yes", "Score_No"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out
