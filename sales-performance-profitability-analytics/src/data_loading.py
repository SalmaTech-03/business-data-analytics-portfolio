"""
data_loading.py
================
Locates and loads the Sample Superstore dataset, validating that the
expected sheets and columns are present before handing a DataFrame
back to the rest of the pipeline.

The loader is deliberately defensive: it does not assume a fixed,
machine-specific path, it does not assume the file is `.xlsx` (the
distributed sample is a legacy `.xls` file), and it fails with a
clear, actionable error message rather than a raw traceback if the
data is missing or structurally different than expected.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd

# Columns that MUST exist in the Orders sheet for the rest of the
# pipeline to function. This list reflects the columns actually
# present in the Sample Superstore file supplied with this project
# (verified in docs/data_quality.md) -- it is not a generic guess.
REQUIRED_ORDERS_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country/Region",
    "City",
    "State/Province",
    "Postal Code",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]

DEFAULT_CANDIDATE_PATHS = [
    "data/raw/sample_-_superstore.xlsx",
    "data/raw/sample_-_superstore.xls",
    "data/raw/Sample - Superstore.xls",
    "data/raw/Sample - Superstore.xlsx",
]


class DataLoadingError(RuntimeError):
    """Raised when the dataset cannot be located or does not match
    the structure this pipeline was built for."""


def _find_dataset(
    explicit_path: Optional[str] = None,
    search_dir: str = "data/raw",
) -> Path:
    """Resolve the raw dataset path from the project root.

    Search order:
    1. explicit_path, if provided.
    2. Known candidate filenames under the project root.
    3. Any .xlsx/.xls file found under the project's data/raw folder.
    """
    if explicit_path:
        p = Path(explicit_path)

        if not p.is_absolute():
            p = Path.cwd() / p

        if p.exists():
            return p.resolve()

        raise DataLoadingError(
            f"Explicit dataset path was given but does not exist: {p}"
        )

    # Project structure:
    #
    # project/
    # ├── src/
    # │   └── data_loading.py
    # ├── data/
    # │   └── raw/
    # └── notebooks/
    #
    # Therefore parent.parent is the project root.
    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data" / "raw"

    candidate_names = [
        "sample_-_superstore.xlsx",
        "sample_-_superstore.xls",
        "Sample - Superstore.xls",
        "Sample - Superstore.xlsx",
    ]

    for filename in candidate_names:
        candidate = raw_dir / filename

        if candidate.exists():
            return candidate.resolve()

    if raw_dir.exists():
        excel_files = sorted(
            list(raw_dir.glob("*.xlsx"))
            + list(raw_dir.glob("*.xls"))
        )

        if excel_files:
            return excel_files[0].resolve()

    raise DataLoadingError(
        "Could not locate the Superstore dataset. "
        f"Place the raw Excel file in '{raw_dir}', "
        "or pass an explicit path to load_orders(path=...)."
    )


def _read_excel_any_engine(path: Path, sheet_name):
    """Read an Excel sheet, transparently handling legacy .xls files
    that require the `xlrd` engine as well as modern .xlsx files that
    require `openpyxl`.
    """
    suffix = path.suffix.lower()
    try:
        if suffix == ".xls":
            return pd.read_excel(path, sheet_name=sheet_name, engine="xlrd")
        return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    except ImportError as exc:
        raise DataLoadingError(
            f"Missing optional dependency required to read '{path.name}': {exc}. "
            "Install 'xlrd' for legacy .xls files or 'openpyxl' for .xlsx files."
        ) from exc
    except ValueError as exc:
        # Common cause: sheet name not found.
        raise DataLoadingError(
            f"Could not read sheet '{sheet_name}' from '{path.name}': {exc}"
        ) from exc


def load_orders(path: Optional[str] = None) -> pd.DataFrame:
    """Load the Orders sheet and validate its structure.

    Returns
    -------
    pd.DataFrame
        The raw Orders data, unmodified (cleaning happens in
        data_cleaning.py).

    Raises
    ------
    DataLoadingError
        If the file cannot be found, cannot be read, or is missing
        columns the rest of the pipeline depends on.
    """
    resolved = _find_dataset(path)
    df = _read_excel_any_engine(resolved, sheet_name="Orders")

    missing = [c for c in REQUIRED_ORDERS_COLUMNS if c not in df.columns]
    if missing:
        raise DataLoadingError(
            f"Loaded '{resolved.name}' but it is missing expected columns: {missing}. "
            "This pipeline was built against the standard Sample Superstore "
            "schema -- if you are using a different export, update "
            "REQUIRED_ORDERS_COLUMNS in src/data_loading.py to match."
        )

    if df.empty:
        raise DataLoadingError(f"'{resolved.name}' Orders sheet loaded but contains 0 rows.")

    return df


def load_people(path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Load the People sheet (Regional Manager -> Region mapping).

    Returns None (rather than raising) if the sheet is absent, since
    it is a supplementary lookup table, not a hard dependency of the
    core analysis.
    """
    resolved = _find_dataset(path)
    try:
        return _read_excel_any_engine(resolved, sheet_name="People")
    except DataLoadingError:
        return None


def load_returns(path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Load the Returns sheet (Order ID -> Returned flag).

    Returns None if the sheet is absent -- return analysis is an
    optional enrichment, not a hard dependency.
    """
    resolved = _find_dataset(path)
    try:
        return _read_excel_any_engine(resolved, sheet_name="Returns")
    except DataLoadingError:
        return None


def load_all(path: Optional[str] = None) -> Dict[str, pd.DataFrame]:
    """Convenience loader returning every sheet the pipeline uses.

    Returns
    -------
    dict with keys: "orders" (always present), "people", "returns"
    (either may be None if that sheet is absent from the workbook).
    """
    return {
        "orders": load_orders(path),
        "people": load_people(path),
        "returns": load_returns(path),
    }


if __name__ == "__main__":
    data = load_all()
    print(f"Orders loaded: {data['orders'].shape[0]:,} rows, {data['orders'].shape[1]} columns")
    print(f"People loaded: {'yes' if data['people'] is not None else 'no'}")
    print(f"Returns loaded: {'yes' if data['returns'] is not None else 'no'}")
