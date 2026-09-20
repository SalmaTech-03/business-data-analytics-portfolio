"""
test_kpi_calculations.py
=========================
Unit tests for every function in src/kpi_calculations.py.

Two kinds of tests:
1. Small, hand-built DataFrames with known-by-construction correct
   answers (isolates the formula from real-world data quirks).
2. Consistency checks against the REAL dataset (e.g. profit_margin
   must equal total_profit / total_revenue to within floating-point
   tolerance) -- these catch a KPI silently drifting out of sync with
   its own definition after a refactor.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loading import load_orders  # noqa: E402
from data_cleaning import clean_orders  # noqa: E402
from feature_engineering import engineer_all  # noqa: E402
import kpi_calculations as kpi  # noqa: E402


@pytest.fixture
def toy_df():
    """A tiny, hand-computable dataset: 2 orders, 2 customers, 3 line items."""
    return pd.DataFrame(
        {
            "order_id": ["O1", "O1", "O2"],
            "customer_id": ["C1", "C1", "C2"],
            "sales": [100.0, 50.0, 200.0],
            "profit": [20.0, -10.0, 40.0],
            "quantity": [2, 1, 4],
        }
    )


@pytest.fixture(scope="module")
def real_lines():
    raw = load_orders()
    cleaned, _ = clean_orders(raw)
    tables = engineer_all(cleaned)
    return tables["lines"]


# --- Formula-correctness tests on the toy dataset -----------------------

def test_total_revenue(toy_df):
    assert kpi.total_revenue(toy_df) == pytest.approx(350.0)


def test_total_profit(toy_df):
    assert kpi.total_profit(toy_df) == pytest.approx(50.0)


def test_total_orders(toy_df):
    assert kpi.total_orders(toy_df) == 2


def test_total_units(toy_df):
    assert kpi.total_units(toy_df) == 7


def test_profit_margin(toy_df):
    # 50 / 350
    assert kpi.profit_margin(toy_df) == pytest.approx(50.0 / 350.0)


def test_average_order_value(toy_df):
    # total revenue 350 / 2 orders = 175
    assert kpi.average_order_value(toy_df) == pytest.approx(175.0)


def test_average_units_per_order(toy_df):
    # 7 units / 2 orders = 3.5
    assert kpi.average_units_per_order(toy_df) == pytest.approx(3.5)


def test_customer_count(toy_df):
    assert kpi.customer_count(toy_df) == 2


def test_revenue_per_customer(toy_df):
    # 350 / 2
    assert kpi.revenue_per_customer(toy_df) == pytest.approx(175.0)


def test_repeat_customer_rate(toy_df):
    # C1 has 1 distinct order (O1, appears twice but same order_id) -> not repeat
    # C2 has 1 distinct order (O2) -> not repeat
    # repeat rate = 0 / 2 = 0.0
    assert kpi.repeat_customer_rate(toy_df) == pytest.approx(0.0)


def test_repeat_customer_rate_detects_repeat_customer():
    df = pd.DataFrame(
        {
            "order_id": ["O1", "O2", "O3"],
            "customer_id": ["C1", "C1", "C2"],
        }
    )
    # C1 has 2 distinct orders -> repeat. C2 has 1 -> not repeat.
    # repeat rate = 1 / 2 = 0.5
    assert kpi.repeat_customer_rate(df) == pytest.approx(0.5)


def test_kpis_handle_empty_dataframe_without_crashing():
    empty = pd.DataFrame(columns=["order_id", "customer_id", "sales", "profit", "quantity"])
    assert kpi.total_revenue(empty) == 0.0
    assert kpi.total_orders(empty) == 0
    assert kpi.average_order_value(empty) == 0.0
    assert kpi.profit_margin(empty) == 0.0
    assert kpi.repeat_customer_rate(empty) == 0.0


# --- Internal-consistency tests on the REAL dataset ----------------------

def test_profit_margin_matches_its_own_formula_on_real_data(real_lines):
    margin = kpi.profit_margin(real_lines)
    expected = kpi.total_profit(real_lines) / kpi.total_revenue(real_lines)
    assert margin == pytest.approx(expected)


def test_average_order_value_matches_manual_groupby_on_real_data(real_lines):
    aov = kpi.average_order_value(real_lines)
    manual = real_lines.groupby("order_id")["sales"].sum().mean()
    assert aov == pytest.approx(manual, rel=1e-9)


def test_core_kpis_are_internally_consistent_on_real_data(real_lines):
    kpis = kpi.compute_core_kpis(real_lines)
    assert kpis["total_revenue"] > 0
    assert kpis["total_orders"] > 0
    assert kpis["customer_count"] > 0
    # AOV * orders should reconstruct total revenue
    assert kpis["average_order_value"] * kpis["total_orders"] == pytest.approx(
        kpis["total_revenue"], rel=1e-6
    )
    # revenue per customer * customer count should reconstruct total revenue
    assert kpis["revenue_per_customer"] * kpis["customer_count"] == pytest.approx(
        kpis["total_revenue"], rel=1e-6
    )
    # repeat customer rate must be a valid fraction
    assert 0.0 <= kpis["repeat_customer_rate"] <= 1.0
