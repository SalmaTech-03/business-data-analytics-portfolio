"""
test_data_quality.py
=====================
Tests that the raw/cleaned dataset satisfies the structural and
business-rule assumptions the rest of the pipeline depends on.

These are NOT "1 == 1" tests -- each one encodes a real rule from
docs/data_quality.md and will fail loudly if a future refresh of the
dataset violates it.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loading import load_orders, REQUIRED_ORDERS_COLUMNS  # noqa: E402
from data_cleaning import clean_orders, standardize_column_names  # noqa: E402
from validation import (  # noqa: E402
    check_required_columns,
    check_no_missing_values,
    check_no_full_duplicates,
    check_row_id_unique,
    check_dates_valid,
    check_positive_quantity,
    check_positive_sales,
    check_discount_range,
)


@pytest.fixture(scope="module")
def raw_df():
    return load_orders()


@pytest.fixture(scope="module")
def clean_df(raw_df):
    cleaned, _ = clean_orders(raw_df)
    return cleaned


def test_required_columns_present(raw_df):
    missing = [c for c in REQUIRED_ORDERS_COLUMNS if c not in raw_df.columns]
    assert not missing, f"Dataset is missing required columns: {missing}"


def test_dataset_not_empty(raw_df):
    assert len(raw_df) > 0, "Orders dataset loaded with zero rows."


def test_no_missing_values(clean_df):
    result = check_no_missing_values(clean_df)
    assert result.passed, result.detail


def test_no_full_duplicate_rows(clean_df):
    result = check_no_full_duplicates(clean_df)
    assert result.passed, result.detail


def test_row_id_is_unique(clean_df):
    result = check_row_id_unique(clean_df)
    assert result.passed, result.detail


def test_dates_are_valid(clean_df):
    result = check_dates_valid(clean_df)
    assert result.passed, result.detail


def test_quantity_is_positive(clean_df):
    result = check_positive_quantity(clean_df)
    assert result.passed, result.detail


def test_sales_is_positive(clean_df):
    result = check_positive_sales(clean_df)
    assert result.passed, result.detail


def test_discount_within_valid_range(clean_df):
    result = check_discount_range(clean_df)
    assert result.passed, result.detail


def test_postal_code_is_never_numeric_dtype(clean_df):
    """Postal codes must stay text -- Canadian postal codes are
    alphanumeric (e.g. 'M7A'), so a numeric dtype would corrupt them."""
    assert clean_df["postal_code"].dtype == object or pd.api.types.is_string_dtype(clean_df["postal_code"])


def test_known_multi_customer_order_quirk_is_exactly_two():
    """Documents and pins the exact scope of the one known data quirk
    in this dataset (see docs/data_quality.md) -- if a dataset refresh
    changes this count, that is a signal worth investigating, not
    something to silently absorb."""
    raw = load_orders()
    df = standardize_column_names(raw)
    multi = (df.groupby("order_id")["customer_id"].nunique() > 1).sum()
    assert multi == 2, (
        f"Expected exactly 2 order_ids spanning multiple customer_ids "
        f"(the documented Harry Olson quirk), found {multi}. "
        "Update docs/data_quality.md if this dataset has changed."
    )


def test_country_region_has_exactly_two_values():
    """This dataset spans US + Canada -- pinning this guards against
    silently treating it as US-only in future analysis."""
    raw = load_orders()
    df = standardize_column_names(raw)
    countries = set(df["country_region"].unique())
    assert countries == {"United States", "Canada"}, (
        f"Expected exactly {{'United States', 'Canada'}}, found {countries}."
    )
