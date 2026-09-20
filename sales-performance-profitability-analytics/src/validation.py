"""
validation.py
==============
Business-rule and data-quality validation, run independently of the
cleaning pipeline so it can be reused by pytest and by run_analysis.py
as a pre-flight check.

Every check returns a ValidationResult (pass/fail + details) rather
than raising, so a full report can be produced even if several checks
fail. run_analysis.py decides whether any failure should stop the
pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

import pandas as pd

REQUIRED_COLUMNS = [
    "row_id", "order_id", "order_date", "ship_date", "ship_mode",
    "customer_id", "customer_name", "segment", "country_region", "city",
    "state_province", "postal_code", "region", "product_id", "category",
    "sub_category", "product_name", "sales", "quantity", "discount", "profit",
]


@dataclass
class ValidationResult:
    name: str
    passed: bool
    detail: str

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.name}: {self.detail}"


def check_required_columns(df: pd.DataFrame) -> ValidationResult:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    return ValidationResult(
        "required_columns",
        passed=len(missing) == 0,
        detail="all required columns present" if not missing else f"missing: {missing}",
    )


def check_no_missing_values(df: pd.DataFrame) -> ValidationResult:
    total_missing = int(df[REQUIRED_COLUMNS].isna().sum().sum())
    return ValidationResult(
        "no_missing_values",
        passed=total_missing == 0,
        detail="no missing values" if total_missing == 0 else f"{total_missing} missing values found",
    )


def check_no_full_duplicates(df: pd.DataFrame) -> ValidationResult:
    dup = int(df.duplicated().sum())
    return ValidationResult(
        "no_full_duplicate_rows",
        passed=dup == 0,
        detail="no duplicate rows" if dup == 0 else f"{dup} duplicate rows found",
    )

def check_row_id_unique(df: pd.DataFrame) -> ValidationResult:
    dup = int(df["row_id"].duplicated().sum())
    return ValidationResult(
        "row_id_is_unique",
        passed=dup == 0,
        detail="row_id is unique" if dup == 0 else f"{dup} duplicate row_id values found",
    )


def check_dates_valid(df: pd.DataFrame) -> ValidationResult:
    order_date = pd.to_datetime(df["order_date"], errors="coerce")
    ship_date = pd.to_datetime(df["ship_date"], errors="coerce")
    unparseable = int(order_date.isna().sum() + ship_date.isna().sum())
    ship_before_order = int((ship_date < order_date).sum())
    ok = unparseable == 0 and ship_before_order == 0
    return ValidationResult(
        "dates_valid",
        passed=ok,
        detail=(
            "all dates parse and ship_date >= order_date for every row" if ok
            else f"unparseable={unparseable}, ship_before_order={ship_before_order}"
        ),
    )


def check_positive_quantity(df: pd.DataFrame) -> ValidationResult:
    bad = int((df["quantity"] <= 0).sum())
    return ValidationResult(
        "positive_quantity",
        passed=bad == 0,
        detail="all quantities > 0" if bad == 0 else f"{bad} rows with quantity <= 0",
    )


def check_positive_sales(df: pd.DataFrame) -> ValidationResult:
    bad = int((df["sales"] <= 0).sum())
    return ValidationResult(
        "positive_sales",
        passed=bad == 0,
        detail="all sales values > 0" if bad == 0 else f"{bad} rows with sales <= 0",
    )


def check_discount_range(df: pd.DataFrame) -> ValidationResult:
    bad = int(((df["discount"] < 0) | (df["discount"] > 1)).sum())
    return ValidationResult(
        "discount_in_valid_range",
        passed=bad == 0,
        detail="all discounts in [0, 1]" if bad == 0 else f"{bad} rows with discount outside [0, 1]",
    )


def check_order_customer_consistency(df: pd.DataFrame) -> ValidationResult:
    """Each order_id should map to exactly one customer_id. This is a
    KNOWN QUIRK in this dataset (2 order IDs violate it) -- the check
    reports it rather than treating it as a hard failure, since the
    root cause is a source-system data-entry artifact, not a pipeline bug.
    """
    bad = int((df.groupby("order_id")["customer_id"].nunique() > 1).sum())
    return ValidationResult(
        "order_maps_to_single_customer",
        passed=bad == 0,
        detail=(
            "every order_id maps to exactly one customer_id" if bad == 0
            else f"{bad} order_id(s) span multiple customer_id values (documented known quirk, see docs/data_quality.md)"
        ),
    )


def check_referential_integrity_returns(df_orders: pd.DataFrame, df_returns: pd.DataFrame) -> ValidationResult:
    orphan = int((~df_returns["Order ID"].isin(df_orders["order_id"])).sum()) if "Order ID" in df_returns.columns else int((~df_returns["order_id"].isin(df_orders["order_id"])).sum())
    return ValidationResult(
        "returns_reference_valid_orders",
        passed=orphan == 0,
        detail="every Returns Order ID exists in Orders" if orphan == 0 else f"{orphan} Returns rows reference an unknown Order ID",
    )


DEFAULT_CHECKS: List[Callable[[pd.DataFrame], ValidationResult]] = [
    check_required_columns,
    check_no_missing_values,
    check_no_full_duplicates,
    check_row_id_unique,
    check_dates_valid,
    check_positive_quantity,
    check_positive_sales,
    check_discount_range,
    check_order_customer_consistency,
]


def run_all_checks(df: pd.DataFrame) -> List[ValidationResult]:
    return [check(df) for check in DEFAULT_CHECKS]


if __name__ == "__main__":
    from data_loading import load_orders
    from data_cleaning import clean_orders

    raw = load_orders()
    cleaned, _ = clean_orders(raw)
    results = run_all_checks(cleaned)
    for r in results:
        print(r)
    failed = [r for r in results if not r.passed]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
