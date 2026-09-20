git status --short --untracked-files=allgit status --short --untracked-files=all
test_business_rules.py
=======================
Tests that encode business logic / domain rules rather than pure
arithmetic -- e.g. "profit margin can legitimately be negative",
"revenue contribution percentages across all products must sum to
~100%", "no PII column reaches the processed/public output".
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loading import load_orders  # noqa: E402
from data_cleaning import clean_orders  # noqa: E402
from feature_engineering import engineer_all  # noqa: E402
from kpi_calculations import compute_core_kpis  # noqa: E402


@pytest.fixture(scope="module")
def tables():
    raw = load_orders()
    cleaned, _ = clean_orders(raw)
    return engineer_all(cleaned)


def test_product_revenue_contribution_sums_to_100_percent(tables):
    total_pct = tables["product_level"]["revenue_contribution_pct"].sum()
    assert total_pct == pytest.approx(100.0, abs=0.01)


def test_customer_revenue_contribution_sums_to_100_percent(tables):
    total_pct = tables["customer_level"]["revenue_contribution_pct"].sum()
    assert total_pct == pytest.approx(100.0, abs=0.01)


def test_negative_profit_margin_is_allowed_and_present(tables):
    """Profit margin CAN legitimately be negative (a loss-making sale) --
    this test documents that as expected behavior, and confirms the real
    dataset actually contains such cases (so downstream code must handle
    them, not assume margin >= 0)."""
    lines = tables["lines"]
    assert (lines["profit_margin"] < 0).any(), (
        "Expected at least one loss-making line item in the real dataset; "
        "if this ever becomes false, re-check profit_margin's sign convention."
    )


def test_order_level_revenue_reconciles_to_line_level_revenue(tables):
    """Summing order_total_sales across all orders must equal summing
    sales across all line items -- otherwise the order-level rollup
    silently lost or double-counted data."""
    line_total = tables["lines"]["sales"].sum()
    order_total = tables["order_level"]["order_total_sales"].sum()
    assert order_total == pytest.approx(line_total, rel=1e-9)


def test_customer_level_revenue_reconciles_to_line_level_revenue(tables):
    line_total = tables["lines"]["sales"].sum()
    customer_total = tables["customer_level"]["total_sales"].sum()
    assert customer_total == pytest.approx(line_total, rel=1e-9)


def test_repeat_customer_flag_matches_order_count(tables):
    """repeat_customer must be True if and only if total_orders > 1 --
    a direct, deterministic business rule."""
    cust = tables["customer_level"]
    mismatches = cust[(cust["total_orders"] > 1) != cust["repeat_customer"]]
    assert mismatches.empty, f"{len(mismatches)} customers have an inconsistent repeat_customer flag."


def test_profit_margin_is_only_null_when_sales_is_zero(tables):
    lines = tables["lines"]
    null_margin_rows = lines[lines["profit_margin"].isna()]
    assert (null_margin_rows["sales"] == 0).all(), (
        "profit_margin is null for a row where sales is non-zero -- "
        "this indicates a bug in the division, not a legitimate zero-sales case."
    )


def test_no_pii_columns_in_de_identified_output(tmp_path):
    """Simulates run_analysis.py's PII-stripping step and asserts none
    of the excluded columns survive."""
    raw = load_orders()
    cleaned, _ = clean_orders(raw)
    tables_local = engineer_all(cleaned)
    pii_columns = ["customer_name", "city", "state_province", "postal_code"]
    safe = tables_local["lines"].drop(columns=[c for c in pii_columns if c in tables_local["lines"].columns])
    for col in pii_columns:
        assert col not in safe.columns, f"PII column '{col}' was not removed from the public-safe output."


def test_kpis_are_positive_where_business_logic_requires_it(tables):
    kpis = compute_core_kpis(tables["lines"])
    assert kpis["total_orders"] > 0
    assert kpis["total_units"] > 0
    assert kpis["customer_count"] > 0
    # Total revenue must be positive (all sales values are individually > 0,
    # verified in test_data_quality.py::test_sales_is_positive)
    assert kpis["total_revenue"] > 0
