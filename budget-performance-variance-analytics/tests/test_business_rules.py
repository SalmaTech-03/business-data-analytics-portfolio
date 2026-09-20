"""
Business-rule / feature-engineering tests: confirm derived fields
behave the way the business logic promises, on both toy data and
the real dataset.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
import pytest

from feature_engineering import engineer_features, add_efficiency_tier
from data_loading import load_dataset
from data_cleaning import clean_dataset
from validation import run_all_validations


@pytest.fixture
def toy_df():
    return pd.DataFrame({
        "record_id": [1, 2, 3, 4],
        "department": ["Sales", "IT", "HR", "Finance"],
        "expense_category": ["Training", "Technology", "Salaries", "Operations"],
        "budget_allocated": [1000.0, 1000.0, 1000.0, 1000.0],
        "budget_utilized": [900.0, 1100.0, 700.0, 1000.0],
        "revenue_forecast": [500.0, 500.0, 500.0, 500.0],
        "actual_revenue": [450.0, 550.0, 500.0, 0.0],
        "budget_variance": [100.0, -100.0, 300.0, 0.0],
        "revenue_variance": [-50.0, 50.0, 0.0, -500.0],
        "monthly_expense": [80.0, 90.0, 70.0, 85.0],
        "allocation_efficiency": [60.0, 75.0, 90.0, 80.0],
        "budget_status": ["Efficient", "Inefficient", "Moderate", "Efficient"],
    })


def test_is_overspent_flag(toy_df):
    df = engineer_features(toy_df)
    # only row index 1 (IT, 1100 > 1000) is overspent
    assert df.loc[df["department"] == "IT", "is_overspent"].iloc[0] == True
    assert df.loc[df["department"] == "Sales", "is_overspent"].iloc[0] == False


def test_is_underspent_flag(toy_df):
    df = engineer_features(toy_df)
    # HR utilized 700 of 1000 = 70%, threshold is < 70% -> not flagged
    assert df.loc[df["department"] == "HR", "is_underspent"].iloc[0] == False


def test_utilization_rate_matches_manual_calc(toy_df):
    df = engineer_features(toy_df)
    expected = toy_df["budget_utilized"] / toy_df["budget_allocated"]
    pd.testing.assert_series_equal(
        df["utilization_rate"].reset_index(drop=True),
        expected.reset_index(drop=True),
        check_names=False,
    )


def test_revenue_realization_rate_handles_zero_actual(toy_df):
    df = engineer_features(toy_df)
    finance_row = df[df["department"] == "Finance"].iloc[0]
    assert finance_row["revenue_realization_rate"] == 0.0


def test_efficiency_tier_has_three_labels(toy_df):
    df = engineer_features(pd.concat([toy_df] * 5, ignore_index=True))
    assert set(df["efficiency_tier"].unique()) <= {"Low", "Medium", "High"}


def test_real_dataset_passes_validation_with_no_errors():
    raw = load_dataset()
    cleaned, _ = clean_dataset(raw)
    result = run_all_validations(cleaned)
    assert result.passed is True
    assert result.errors == []
