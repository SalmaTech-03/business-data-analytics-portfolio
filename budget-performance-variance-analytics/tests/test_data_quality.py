"""
Meaningful data-quality tests run against the actual raw dataset.
These assert properties that were verified during data profiling -
if the underlying CSV changes and these break, that's a real signal
worth investigating, not a false alarm.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from data_loading import load_dataset, REQUIRED_COLUMNS
from data_cleaning import clean_dataset


@pytest.fixture(scope="module")
def raw_df():
    return load_dataset()


@pytest.fixture(scope="module")
def clean_df(raw_df):
    cleaned, _ = clean_dataset(raw_df)
    return cleaned


def test_dataset_loads_and_is_not_empty(raw_df):
    assert len(raw_df) > 0


def test_required_columns_present(raw_df):
    for col in REQUIRED_COLUMNS:
        assert col in raw_df.columns, f"Missing required column: {col}"


def test_no_fully_duplicated_rows(raw_df):
    assert raw_df.duplicated().sum() == 0


def test_no_duplicate_record_ids(raw_df):
    assert raw_df["Record_ID"].duplicated().sum() == 0


def test_no_missing_values(raw_df):
    assert raw_df.isna().sum().sum() == 0


def test_fiscal_quarter_is_valid_domain(raw_df):
    assert set(raw_df["Fiscal_Quarter"].unique()) <= {"Q1", "Q2", "Q3", "Q4"}


def test_budget_status_is_valid_domain(raw_df):
    assert set(raw_df["Budget_Status"].unique()) <= {
        "Efficient", "Moderate", "Inefficient"
    }


def test_no_negative_budget_allocated(raw_df):
    assert (raw_df["Budget_Allocated"] < 0).sum() == 0


def test_no_negative_budget_utilized(raw_df):
    assert (raw_df["Budget_Utilized"] < 0).sum() == 0


def test_no_negative_revenue_fields(raw_df):
    assert (raw_df["Revenue_Forecast"] < 0).sum() == 0
    assert (raw_df["Actual_Revenue"] < 0).sum() == 0


def test_cleaning_does_not_drop_rows(raw_df, clean_df):
    # This dataset has no missing/duplicate rows to legitimately drop,
    # so cleaning must be row-count-preserving.
    assert len(clean_df) == len(raw_df)


def test_cleaning_standardizes_column_names(clean_df):
    assert "budget_allocated" in clean_df.columns
    assert "Budget_Allocated" not in clean_df.columns
