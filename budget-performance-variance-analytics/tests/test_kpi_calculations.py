"""
Unit tests for src/kpi_calculations.py.

Uses a small, hand-built DataFrame with known values so each KPI's
formula can be checked exactly, plus a couple of tests against the
real dataset for consistency checks (e.g. group-level sums must
equal the overall total).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
import pytest

from kpi_calculations import (
    total_budget_allocated,
    total_budget_utilized,
    overall_utilization_rate,
    total_revenue_forecast,
    total_actual_revenue,
    revenue_realization_rate,
    record_count,
    department_count,
    average_allocation_efficiency,
    budget_status_distribution,
    kpis_by_department,
)
from data_loading import load_dataset
from data_cleaning import clean_dataset
from feature_engineering import engineer_features


@pytest.fixture
def toy_df():
    return pd.DataFrame({
        "record_id": [1, 2, 3],
        "department": ["Sales", "Sales", "IT"],
        "budget_allocated": [100.0, 200.0, 300.0],
        "budget_utilized": [90.0, 220.0, 150.0],
        "revenue_forecast": [1000.0, 500.0, 250.0],
        "actual_revenue": [900.0, 600.0, 300.0],
        "allocation_efficiency": [80.0, 90.0, 70.0],
        "budget_status": ["Efficient", "Inefficient", "Moderate"],
    })


def test_total_budget_allocated(toy_df):
    assert total_budget_allocated(toy_df) == 600.0


def test_total_budget_utilized(toy_df):
    assert total_budget_utilized(toy_df) == 460.0


def test_overall_utilization_rate(toy_df):
    # 460 / 600
    assert overall_utilization_rate(toy_df) == pytest.approx(460 / 600)


def test_revenue_realization_rate(toy_df):
    # (900+600+300) / (1000+500+250) = 1800/1750
    assert revenue_realization_rate(toy_df) == pytest.approx(1800 / 1750)


def test_record_count(toy_df):
    assert record_count(toy_df) == 3


def test_department_count(toy_df):
    assert department_count(toy_df) == 2


def test_average_allocation_efficiency(toy_df):
    assert average_allocation_efficiency(toy_df) == pytest.approx(80.0)


def test_budget_status_distribution_sums_to_one(toy_df):
    dist = budget_status_distribution(toy_df)
    assert sum(dist.values()) == pytest.approx(1.0)


def test_zero_allocation_does_not_raise_divide_error():
    df = pd.DataFrame({
        "budget_allocated": [0.0],
        "budget_utilized": [50.0],
    })
    rate = overall_utilization_rate(df)
    assert rate != rate  # NaN check (NaN != NaN is True)


@pytest.fixture(scope="module")
def real_df():
    raw = load_dataset()
    cleaned, _ = clean_dataset(raw)
    return engineer_features(cleaned)


def test_department_totals_sum_to_overall_total(real_df):
    by_dept = kpis_by_department(real_df)
    assert by_dept["total_allocated"].sum() == pytest.approx(
        total_budget_allocated(real_df)
    )


def test_kpi_summary_utilization_rate_between_zero_and_two(real_df):
    # Sanity bound: utilization rate should be a small positive
    # multiple of 1, not an absurd outlier, on this dataset.
    rate = overall_utilization_rate(real_df)
    assert 0 < rate < 2


# --- Variance provenance regression tests -------------------------
# Added after a review question surfaced that the rollup tables
# expose two different "variance" quantities. These tests lock in
# the distinction so a future refactor can't quietly conflate them.

def test_supplied_variance_and_computed_gap_are_different_quantities(real_df):
    from kpi_calculations import supplied_budget_variance, computed_budget_gap
    supplied = supplied_budget_variance(real_df)
    computed = computed_budget_gap(real_df)
    # They differ by tens of millions on this dataset - assert they
    # are not accidentally treated as interchangeable.
    assert abs(computed - supplied) > 1_000_000


def test_computed_gap_equals_allocated_minus_utilized(real_df):
    from kpi_calculations import (
        computed_budget_gap, total_budget_allocated, total_budget_utilized
    )
    assert computed_budget_gap(real_df) == pytest.approx(
        total_budget_allocated(real_df) - total_budget_utilized(real_df)
    )


def test_utilization_rate_is_independent_of_supplied_variance_column(real_df):
    """Zeroing the supplied variance column must not move utilization."""
    from kpi_calculations import overall_utilization_rate
    before = overall_utilization_rate(real_df)
    tampered = real_df.copy()
    tampered["budget_variance"] = 0.0
    assert overall_utilization_rate(tampered) == pytest.approx(before)


def test_department_record_counts_sum_to_total_rows(real_df):
    """Guards against silent row loss in the department groupby."""
    from kpi_calculations import kpis_by_department, record_count
    by_dept = kpis_by_department(real_df)
    assert by_dept["record_count"].sum() == record_count(real_df)


def test_expense_category_record_counts_sum_to_total_rows(real_df):
    from kpi_calculations import kpis_by_expense_category, record_count
    by_cat = kpis_by_expense_category(real_df)
    assert by_cat["record_count"].sum() == record_count(real_df)
