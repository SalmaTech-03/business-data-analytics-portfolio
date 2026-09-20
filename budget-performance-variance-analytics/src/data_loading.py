"""
data_loading.py

Locates and loads the raw Financial Budgeting dataset into a pandas
DataFrame, and validates that the columns the rest of the pipeline
depends on are actually present.

This module deliberately does NOT hard-code a machine-specific
absolute path. It looks for the dataset relative to the project
root (data/raw/) so the project runs the same way on any machine
that has this repo checked out.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd

# Columns the pipeline requires to exist in the raw file.
REQUIRED_COLUMNS = [
    "Record_ID",
    "Fiscal_Quarter",
    "Department",
    "Expense_Category",
    "Budget_Allocated",
    "Budget_Utilized",
    "Monthly_Expense",
    "Revenue_Forecast",
    "Actual_Revenue",
    "Budget_Variance",
    "Revenue_Variance",
    "Expense_Growth_Rate",
    "Seasonal_Index",
    "Spending_Volatility",
    "Rolling_Expense_Mean",
    "Rolling_Revenue_Mean",
    "Inflation_Rate",
    "Market_Index",
    "Allocation_Efficiency",
    "Budget_Status",
]

DEFAULT_FILENAME = "Financial_Budgeting_Dataset.csv"


def _project_root() -> Path:
    """Return the project root (the parent of the src/ directory)."""
    return Path(__file__).resolve().parent.parent


def find_dataset(filename: str = DEFAULT_FILENAME) -> Path:
    """
    Locate the raw dataset file under data/raw/ relative to the
    project root. Raises FileNotFoundError with a clear, actionable
    message if it isn't there.
    """
    candidate = _project_root() / "data" / "raw" / filename
    if candidate.exists():
        return candidate

    raise FileNotFoundError(
        f"Could not find '{filename}' in data/raw/.\n"
        f"Expected it at: {candidate}\n"
        "Place the dataset file in data/raw/ (this folder is git-ignored, "
        "see data/README.md) and re-run."
    )


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    """
    Load the Financial Budgeting dataset into a DataFrame.

    Parameters
    ----------
    path : str | Path | None
        Optional explicit path to a CSV file. If omitted, the loader
        searches data/raw/ for the default filename.

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    FileNotFoundError
        If no dataset file can be located.
    ValueError
        If the file exists but is missing required columns, or is an
        unsupported file type.
    """
    if path is None:
        path = find_dataset()
    else:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"No file found at: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Expected .csv, .xlsx or .xls."
        )

    validate_columns(df, REQUIRED_COLUMNS)
    return df


def validate_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    """Raise ValueError listing any required columns missing from df."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{missing}. Found columns: {list(df.columns)}"
        )


if __name__ == "__main__":
    data = load_dataset()
    print(f"Loaded {len(data):,} rows, {len(data.columns)} columns from "
          f"{find_dataset()}")
