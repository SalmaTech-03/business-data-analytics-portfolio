"""
data_cleaning.py

Cleaning steps applied to the raw Financial Budgeting dataset.

Design principle: this module NEVER silently drops rows. Every check
returns counts/diagnostics; only clearly-defined, documented rules
(see CLEANING_DECISIONS below) remove or alter data, and every such
rule is logged via the returned report.

Verified against the actual raw file (6,780 rows, 20 columns):
- 0 missing values in any column
- 0 fully-duplicated rows
- 0 duplicate Record_ID values
- 0 negative values in fields that should be non-negative
  (Budget_Allocated, Budget_Utilized, Monthly_Expense,
  Revenue_Forecast, Actual_Revenue, Inflation_Rate, Allocation_Efficiency)
So on this dataset, cleaning is largely a no-op that still runs and
reports its findings — the checks stay in place for any future data
refresh that may not be as clean.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

CLEANING_DECISIONS = [
    "Column names are standardized to snake_case for programmatic use "
    "(original names are preserved in the data dictionary).",
    "Fiscal_Quarter is kept as a categorical label (Q1-Q4). The raw data "
    "contains no fiscal year, so quarters are NOT treated as a "
    "chronological time series - see docs/assumptions_and_constraints.md.",
    "Rows are never dropped automatically. If duplicates or nulls are "
    "found, they are reported; removal would be a separate, explicit, "
    "documented step reviewed by the analyst.",
    "Negative values in fields that are conceptually non-negative "
    "(budgets, expenses, revenue) are flagged, not silently corrected.",
]

_RENAME_MAP = {
    "Record_ID": "record_id",
    "Fiscal_Quarter": "fiscal_quarter",
    "Department": "department",
    "Expense_Category": "expense_category",
    "Budget_Allocated": "budget_allocated",
    "Budget_Utilized": "budget_utilized",
    "Monthly_Expense": "monthly_expense",
    "Revenue_Forecast": "revenue_forecast",
    "Actual_Revenue": "actual_revenue",
    "Budget_Variance": "budget_variance",
    "Revenue_Variance": "revenue_variance",
    "Expense_Growth_Rate": "expense_growth_rate",
    "Seasonal_Index": "seasonal_index",
    "Spending_Volatility": "spending_volatility",
    "Rolling_Expense_Mean": "rolling_expense_mean",
    "Rolling_Revenue_Mean": "rolling_revenue_mean",
    "Inflation_Rate": "inflation_rate",
    "Market_Index": "market_index",
    "Allocation_Efficiency": "allocation_efficiency",
    "Budget_Status": "budget_status",
}

NUMERIC_COLUMNS = [
    "budget_allocated", "budget_utilized", "monthly_expense",
    "revenue_forecast", "actual_revenue", "budget_variance",
    "revenue_variance", "expense_growth_rate", "seasonal_index",
    "spending_volatility", "rolling_expense_mean", "rolling_revenue_mean",
    "inflation_rate", "market_index", "allocation_efficiency",
]

NON_NEGATIVE_COLUMNS = [
    "budget_allocated", "budget_utilized", "monthly_expense",
    "revenue_forecast", "actual_revenue", "inflation_rate",
    "allocation_efficiency",
]

CATEGORICAL_COLUMNS = ["fiscal_quarter", "department", "expense_category",
                        "budget_status"]


@dataclass
class CleaningReport:
    starting_rows: int
    ending_rows: int
    duplicate_rows_found: int
    duplicate_record_ids_found: int
    nulls_by_column: dict = field(default_factory=dict)
    negative_value_counts: dict = field(default_factory=dict)
    categorical_values: dict = field(default_factory=dict)
    decisions: list = field(default_factory=lambda: list(CLEANING_DECISIONS))

    def summary(self) -> str:
        lines = [
            f"Rows in: {self.starting_rows:,}  ->  Rows out: {self.ending_rows:,}",
            f"Fully duplicated rows found: {self.duplicate_rows_found}",
            f"Duplicate Record_ID values found: {self.duplicate_record_ids_found}",
            "Nulls by column (non-zero only): "
            + (str({k: v for k, v in self.nulls_by_column.items() if v})
               or "none"),
            "Negative values in non-negative fields: "
            + (str({k: v for k, v in self.negative_value_counts.items() if v})
               or "none"),
        ]
        return "\n".join(lines)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw columns to snake_case."""
    return df.rename(columns=_RENAME_MAP)


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce numeric columns to numeric dtype, categoricals to category."""
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("category")
    return df


def clean_dataset(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Run the full (non-destructive) cleaning pass and return the
    cleaned DataFrame alongside a CleaningReport documenting what
    was found.
    """
    starting_rows = len(df_raw)

    df = standardize_columns(df_raw)
    df = convert_types(df)

    duplicate_rows = int(df.duplicated().sum())
    duplicate_ids = int(df["record_id"].duplicated().sum()) if "record_id" in df else 0
    nulls_by_column = df.isna().sum().to_dict()

    negative_counts = {
        col: int((df[col] < 0).sum())
        for col in NON_NEGATIVE_COLUMNS if col in df.columns
    }

    categorical_values = {
        col: sorted(df[col].dropna().unique().tolist())
        for col in CATEGORICAL_COLUMNS if col in df.columns
    }

    report = CleaningReport(
        starting_rows=starting_rows,
        ending_rows=len(df),
        duplicate_rows_found=duplicate_rows,
        duplicate_record_ids_found=duplicate_ids,
        nulls_by_column=nulls_by_column,
        negative_value_counts=negative_counts,
        categorical_values=categorical_values,
    )
    return df, report


if __name__ == "__main__":
    from data_loading import load_dataset

    raw = load_dataset()
    cleaned, report = clean_dataset(raw)
    print(report.summary())
