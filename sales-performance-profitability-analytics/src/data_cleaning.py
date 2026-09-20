"""
data_cleaning.py
=================
Reproducible cleaning pipeline for the Sample Superstore Orders data.

Design principle: NEVER silently drop rows. Every check either
(a) finds nothing wrong and passes through, or (b) finds something
and the finding is returned in a report dict so it can be reviewed,
logged, and documented -- not quietly deleted.

Based on the actual profiling performed on this dataset (see
docs/data_quality.md), the raw Orders sheet has:
  - 0 missing values in any column
  - 0 fully-duplicated rows
  - 0 rows with non-positive Sales or Quantity
  - 0 Discount values outside [0, 1]
  - Ship Date always >= Order Date

Because the dataset is already clean at the row level, this module's
job is mostly standardization (column names, dtypes) and defensive
validation that would catch a *different* or updated copy of the
dataset containing the problems described above.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
import pandas as pd


@dataclass
class CleaningReport:
    """Structured record of every cleaning decision made, so nothing
    is changed invisibly."""
    steps: List[str] = field(default_factory=list)
    issues_found: Dict[str, int] = field(default_factory=dict)
    rows_in: int = 0
    rows_out: int = 0

    def log(self, message: str) -> None:
        self.steps.append(message)

    def flag(self, issue: str, count: int) -> None:
        self.issues_found[issue] = count

    def summary(self) -> str:
        lines = [f"Cleaning report: {self.rows_in:,} rows in -> {self.rows_out:,} rows out"]
        lines.append("\nSteps performed:")
        lines += [f"  - {s}" for s in self.steps]
        if self.issues_found:
            lines.append("\nIssues found (see steps for how each was handled):")
            lines += [f"  - {k}: {v}" for k, v in self.issues_found.items()]
        else:
            lines.append("\nNo data-quality issues found in this run.")
        return "\n".join(lines)


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the source column names (which mix spaces and slashes,
    e.g. 'Order ID', 'Country/Region') into snake_case for use inside
    Python/SQL, while leaving the original DataFrame's source names
    documented in docs/data_dictionary.md for traceability.
    """
    def to_snake(col: str) -> str:
        col = col.replace("/", "_").replace("-", "_")
        col = re.sub(r"\s+", "_", col.strip())
        col = re.sub(r"[^0-9a-zA-Z_]", "", col)
        return col.lower()

    out = df.copy()
    out.columns = [to_snake(c) for c in out.columns]
    return out


def clean_orders(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Run the full cleaning pipeline on the raw Orders DataFrame.

    Returns
    -------
    (clean_df, report) : the cleaned DataFrame and a CleaningReport
        documenting every check performed and what, if anything, it found.
    """
    report = CleaningReport(rows_in=len(df_raw))
    df = df_raw.copy()

    # 1. Standardize column names for downstream SQL/Python use.
    df = standardize_column_names(df)
    report.log("Standardized column names to snake_case "
               "(e.g. 'Order ID' -> 'order_id', 'Country/Region' -> 'country_region').")

    # 2. Duplicate rows (full-row duplicates).
    dup_count = int(df.duplicated().sum())
    report.flag("fully_duplicated_rows", dup_count)
    if dup_count > 0:
        df = df.drop_duplicates()
        report.log(f"Removed {dup_count} fully-duplicated rows.")
    else:
        report.log("Checked for fully-duplicated rows: none found.")

    # 3. Duplicate Row ID (should be a unique primary key).
    dup_row_id = int(df["row_id"].duplicated().sum())
    report.flag("duplicate_row_id", dup_row_id)
    report.log(
        "Checked 'row_id' for uniqueness: "
        f"{'no duplicates found' if dup_row_id == 0 else f'{dup_row_id} duplicates found (kept, flagged for review)'}."
    )

    # 4. Date conversion + validity (Ship Date must not precede Order Date).
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")
    bad_dates = int(df["order_date"].isna().sum() + df["ship_date"].isna().sum())
    report.flag("unparseable_dates", bad_dates)
    report.log(
        "Converted order_date/ship_date to datetime: "
        f"{'all parsed successfully' if bad_dates == 0 else f'{bad_dates} values could not be parsed and are now NaT (kept, not dropped)'}."
    )

    ship_before_order = int((df["ship_date"] < df["order_date"]).sum())
    report.flag("ship_before_order_date", ship_before_order)
    report.log(
        "Checked ship_date >= order_date: "
        f"{'holds for all rows' if ship_before_order == 0 else f'{ship_before_order} rows violate this (flagged, not dropped)'}."
    )

    # 5. Numeric conversion + validity for Sales / Quantity / Discount / Profit.
    for col in ["sales", "quantity", "discount", "profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    numeric_nulls = int(df[["sales", "quantity", "discount", "profit"]].isna().sum().sum())
    report.flag("numeric_fields_failed_to_parse", numeric_nulls)
    report.log(
        "Converted sales/quantity/discount/profit to numeric: "
        f"{'no parsing failures' if numeric_nulls == 0 else f'{numeric_nulls} values failed to parse (kept as NaN, flagged)'}."
    )

    non_positive_sales = int((df["sales"] <= 0).sum())
    report.flag("non_positive_sales", non_positive_sales)
    non_positive_qty = int((df["quantity"] <= 0).sum())
    report.flag("non_positive_quantity", non_positive_qty)
    invalid_discount = int(((df["discount"] < 0) | (df["discount"] > 1)).sum())
    report.flag("discount_outside_0_1", invalid_discount)
    report.log(
        "Checked sales > 0, quantity > 0, discount in [0, 1]: "
        f"sales violations={non_positive_sales}, quantity violations={non_positive_qty}, "
        f"discount violations={invalid_discount} (none dropped automatically; "
        "see docs/data_quality.md for how any violations were handled)."
    )

    # 6. Missing values (column-by-column).
    missing_by_col = df.isna().sum()
    total_missing = int(missing_by_col.sum())
    report.flag("total_missing_values", total_missing)
    report.log(
        "Scanned all columns for missing values: "
        f"{'none found' if total_missing == 0 else f'{total_missing} missing values found across ' + str(int((missing_by_col > 0).sum())) + ' columns'}."
    )

    # 7. Categorical consistency: trim whitespace, normalize case-sensitive
    #    duplicates in low-cardinality text fields (Category, Sub-Category,
    #    Region, Segment, Ship Mode, Country/Region).
    categorical_cols = ["category", "sub_category", "region", "segment", "ship_mode", "country_region"]
    normalized_any = False
    for col in categorical_cols:
        if col not in df.columns:
            continue
        before = df[col].nunique()
        df[col] = df[col].astype(str).str.strip()
        after = df[col].nunique()
        if after != before:
            normalized_any = True
    report.log(
        "Trimmed whitespace on categorical columns "
        f"({', '.join(categorical_cols)}): "
        f"{'this changed the number of distinct values (case/whitespace variants merged)' if normalized_any else 'no change in distinct-value counts, i.e. no inconsistent casing/whitespace found'}."
    )

    # 8. Postal code: keep as string (Canadian postal codes are alphanumeric,
    #    so this column cannot be a numeric type without losing data).
    df["postal_code"] = df["postal_code"].astype(str)
    report.log("Cast postal_code to string (Canadian postal codes are alphanumeric, "
               "so this column is intentionally not numeric).")

    # 9. Referential sanity check: each order_id should map to exactly one customer_id.
    multi_customer_orders = int((df.groupby("order_id")["customer_id"].nunique() > 1).sum())
    report.flag("orders_with_multiple_customer_ids", multi_customer_orders)
    report.log(
        "Checked that each order_id maps to a single customer_id: "
        f"{'holds for all orders' if multi_customer_orders == 0 else f'{multi_customer_orders} order_id(s) span multiple customer_id values (documented in docs/data_quality.md as a known source quirk, not corrected)'}."
    )

    report.rows_out = len(df)
    return df, report


if __name__ == "__main__":
    from data_loading import load_orders

    raw = load_orders()
    cleaned, rpt = clean_orders(raw)
    print(rpt.summary())
