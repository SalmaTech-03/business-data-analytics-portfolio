"""
kpi_calculations.py

Reusable, unit-testable KPI functions for the Budget Performance &
Variance Analytics project. Every function has a docstring stating
its formula and returns a plain Python float/int/dict so results are
easy to test and to print in reports.
"""

from __future__ import annotations

import pandas as pd


def total_budget_allocated(df: pd.DataFrame) -> float:
    """Sum of Budget_Allocated across all records."""
    return float(df["budget_allocated"].sum())


def total_budget_utilized(df: pd.DataFrame) -> float:
    """Sum of Budget_Utilized across all records."""
    return float(df["budget_utilized"].sum())


def overall_utilization_rate(df: pd.DataFrame) -> float:
    """Total Budget_Utilized / Total Budget_Allocated."""
    allocated = total_budget_allocated(df)
    if allocated == 0:
        return float("nan")
    return total_budget_utilized(df) / allocated


def supplied_budget_variance(df: pd.DataFrame) -> float:
    """
    Sum of the raw Budget_Variance column as supplied in the source.

    WARNING: this does NOT equal Allocated - Utilized. It is an
    independently-generated field (correlation ~0.005 with the
    computed gap) and is reported for provenance only. Use
    computed_budget_gap() for any budget-gap analysis.
    """
    return float(df["budget_variance"].sum())


def computed_budget_gap(df: pd.DataFrame) -> float:
    """Total Budget_Allocated minus total Budget_Utilized (the real gap)."""
    return total_budget_allocated(df) - total_budget_utilized(df)


def total_revenue_forecast(df: pd.DataFrame) -> float:
    """Sum of Revenue_Forecast across all records."""
    return float(df["revenue_forecast"].sum())


def total_actual_revenue(df: pd.DataFrame) -> float:
    """Sum of Actual_Revenue across all records."""
    return float(df["actual_revenue"].sum())


def revenue_realization_rate(df: pd.DataFrame) -> float:
    """Total Actual_Revenue / Total Revenue_Forecast."""
    forecast = total_revenue_forecast(df)
    if forecast == 0:
        return float("nan")
    return total_actual_revenue(df) / forecast


def record_count(df: pd.DataFrame) -> int:
    """Number of budget records (rows) in the dataset."""
    return int(len(df))


def department_count(df: pd.DataFrame) -> int:
    """Number of distinct departments represented."""
    return int(df["department"].nunique())


def average_allocation_efficiency(df: pd.DataFrame) -> float:
    """Mean of Allocation_Efficiency across all records (0-100 scale)."""
    return float(df["allocation_efficiency"].mean())


def budget_status_distribution(df: pd.DataFrame) -> dict:
    """Share of records in each Budget_Status category (Efficient/Moderate/Inefficient)."""
    counts = df["budget_status"].value_counts(normalize=True)
    return {str(k): float(v) for k, v in counts.items()}


def kpis_by_department(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-department rollup: total allocated, total utilized,
    utilization rate, average allocation efficiency, and record count.
    Sorted by total budget allocated, descending.

    Two distinct variance quantities are returned, deliberately named
    apart because they do NOT agree (correlation ~0.005):
      - supplied_budget_variance: SUM of the raw Budget_Variance
        column, an independently-generated field in this dataset.
      - computed_budget_gap:      total_allocated - total_utilized,
        the genuine budget gap. Use this one for analysis.
    See docs/data_dictionary.md.
    """
    grouped = df.groupby("department", observed=True).agg(
        total_allocated=("budget_allocated", "sum"),
        total_utilized=("budget_utilized", "sum"),
        supplied_budget_variance=("budget_variance", "sum"),
        avg_allocation_efficiency=("allocation_efficiency", "mean"),
        record_count=("record_id", "count"),
    )
    grouped["utilization_rate"] = (
        grouped["total_utilized"] / grouped["total_allocated"]
    )
    grouped["computed_budget_gap"] = (
        grouped["total_allocated"] - grouped["total_utilized"]
    )
    return grouped.sort_values("total_allocated", ascending=False)


def kpis_by_expense_category(df: pd.DataFrame) -> pd.DataFrame:
    """Per-expense-category rollup, same shape as kpis_by_department."""
    grouped = df.groupby("expense_category", observed=True).agg(
        total_allocated=("budget_allocated", "sum"),
        total_utilized=("budget_utilized", "sum"),
        supplied_budget_variance=("budget_variance", "sum"),
        avg_allocation_efficiency=("allocation_efficiency", "mean"),
        record_count=("record_id", "count"),
    )
    grouped["utilization_rate"] = (
        grouped["total_utilized"] / grouped["total_allocated"]
    )
    grouped["computed_budget_gap"] = (
        grouped["total_allocated"] - grouped["total_utilized"]
    )
    return grouped.sort_values("total_allocated", ascending=False)


def kpis_by_quarter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-fiscal-quarter rollup. NOTE: Fiscal_Quarter has no year in
    this dataset, so this is a cross-sectional comparison of Q1 vs
    Q2 vs Q3 vs Q4 records pooled across the whole file - NOT a
    chronological trend. See docs/assumptions_and_constraints.md.
    """
    grouped = df.groupby("fiscal_quarter", observed=True).agg(
        total_allocated=("budget_allocated", "sum"),
        total_utilized=("budget_utilized", "sum"),
        avg_allocation_efficiency=("allocation_efficiency", "mean"),
        record_count=("record_id", "count"),
    )
    grouped["utilization_rate"] = (
        grouped["total_utilized"] / grouped["total_allocated"]
    )
    return grouped


def top_overspent_department_category(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Department x Expense_Category combinations with the highest
    average utilization rate (spend relative to allocation) -
    candidates for management investigation.
    """
    df = df.copy()
    df["utilization_rate"] = df["budget_utilized"] / df["budget_allocated"]
    grouped = (
        df.groupby(["department", "expense_category"], observed=True)["utilization_rate"]
        .mean()
        .reset_index()
        .sort_values("utilization_rate", ascending=False)
    )
    return grouped.head(n)


def kpi_summary(df: pd.DataFrame) -> dict:
    """One dict containing all headline KPIs, for printing / JSON export."""
    return {
        "record_count": record_count(df),
        "department_count": department_count(df),
        "total_budget_allocated": total_budget_allocated(df),
        "total_budget_utilized": total_budget_utilized(df),
        "overall_utilization_rate": overall_utilization_rate(df),
        "computed_budget_gap": computed_budget_gap(df),
        "supplied_budget_variance_do_not_use_for_analysis":
            supplied_budget_variance(df),
        "total_revenue_forecast": total_revenue_forecast(df),
        "total_actual_revenue": total_actual_revenue(df),
        "revenue_realization_rate": revenue_realization_rate(df),
        "average_allocation_efficiency": average_allocation_efficiency(df),
        "budget_status_distribution": budget_status_distribution(df),
    }


if __name__ == "__main__":
    from data_loading import load_dataset
    from data_cleaning import clean_dataset

    raw = load_dataset()
    cleaned, _ = clean_dataset(raw)
    import json
    print(json.dumps(kpi_summary(cleaned), indent=2))
