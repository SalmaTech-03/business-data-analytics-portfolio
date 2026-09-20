"""
kpi_calculations.py
====================
Reusable, independently-testable KPI functions.

Every function:
  * takes the cleaned/feature-engineered line-item DataFrame (or the
    relevant pre-aggregated table) as input
  * returns a plain Python number (or a small DataFrame for
    time-series/breakdown KPIs)
  * has a docstring stating its exact formula and business meaning
  * is covered by tests/test_kpi_calculations.py

Formula reference
------------------
Total Revenue        = sum(sales)
Total Profit         = sum(profit)
Total Orders         = count(distinct order_id)
Total Units           = sum(quantity)
Profit Margin         = Total Profit / Total Revenue   (revenue-based margin; no cost data exists)
Average Order Value   = Total Revenue / Total Orders
Average Units/Order   = Total Units / Total Orders
Customer Count         = count(distinct customer_id)
Revenue per Customer   = Total Revenue / Customer Count
Repeat Customer Rate   = count(customers with >1 distinct order_id) / Customer Count
"""

from __future__ import annotations

import pandas as pd


def total_revenue(df: pd.DataFrame) -> float:
    """Total Revenue = sum(sales) across all line items."""
    return float(df["sales"].sum())


def total_profit(df: pd.DataFrame) -> float:
    """Total Profit = sum(profit) across all line items."""
    return float(df["profit"].sum())


def total_orders(df: pd.DataFrame) -> int:
    """Total Orders = count of distinct order_id values."""
    return int(df["order_id"].nunique())


def total_units(df: pd.DataFrame) -> int:
    """Total Units = sum(quantity) across all line items."""
    return int(df["quantity"].sum())


def profit_margin(df: pd.DataFrame) -> float:
    """Profit Margin = Total Profit / Total Revenue.

    This is a REVENUE-based margin. The source dataset has no
    unit-cost column, so a cost-based margin cannot be computed and
    is never implied by this function.
    """
    revenue = total_revenue(df)
    if revenue == 0:
        return 0.0
    return total_profit(df) / revenue


def average_order_value(df: pd.DataFrame) -> float:
    """Average Order Value = Total Revenue / Total Orders.

    Computed at the ORDER grain: revenue is first summed within each
    order_id, then averaged across orders -- equivalent to
    Total Revenue / Total Orders since both sums are over the same
    full dataset.
    """
    orders = total_orders(df)
    if orders == 0:
        return 0.0
    return total_revenue(df) / orders


def average_units_per_order(df: pd.DataFrame) -> float:
    """Average Units per Order = Total Units / Total Orders."""
    orders = total_orders(df)
    if orders == 0:
        return 0.0
    return total_units(df) / orders


def customer_count(df: pd.DataFrame) -> int:
    """Customer Count = count of distinct customer_id values."""
    return int(df["customer_id"].nunique())


def revenue_per_customer(df: pd.DataFrame) -> float:
    """Revenue per Customer = Total Revenue / Customer Count."""
    customers = customer_count(df)
    if customers == 0:
        return 0.0
    return total_revenue(df) / customers


def repeat_customer_rate(df: pd.DataFrame) -> float:
    """Repeat Customer Rate = (customers with > 1 distinct order_id)
    / (total distinct customers).

    Expressed as a fraction in [0, 1], not a percentage.
    """
    orders_per_customer = df.groupby("customer_id")["order_id"].nunique()
    repeat = int((orders_per_customer > 1).sum())
    total = int(orders_per_customer.shape[0])
    if total == 0:
        return 0.0
    return repeat / total


def revenue_by_period(df: pd.DataFrame, period_col: str = "order_year_month") -> pd.DataFrame:
    """Revenue, profit, and order count grouped by a time period
    column (default: calendar month, 'order_year_month')."""
    return (
        df.groupby(period_col)
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity", "sum"),
        )
        .reset_index()
        .sort_values(period_col)
    )


def revenue_growth(df: pd.DataFrame, period_col: str = "order_year") -> pd.DataFrame:
    """Period-over-period revenue and profit growth rate.

    growth_rate = (current_period - previous_period) / previous_period

    Only meaningful for periods with a full prior period of data --
    the caller is responsible for excluding partial periods (e.g. an
    in-progress current year) from any "growth" claim.
    """
    by_period = (
        df.groupby(period_col)
        .agg(revenue=("sales", "sum"), profit=("profit", "sum"))
        .reset_index()
        .sort_values(period_col)
    )
    by_period["revenue_growth_rate"] = by_period["revenue"].pct_change()
    by_period["profit_growth_rate"] = by_period["profit"].pct_change()
    return by_period


def compute_core_kpis(df: pd.DataFrame) -> dict:
    """Return every headline KPI in a single dict -- used by
    run_analysis.py to print the summary and by tests to check
    internal consistency."""
    return {
        "total_revenue": total_revenue(df),
        "total_profit": total_profit(df),
        "total_orders": total_orders(df),
        "total_units": total_units(df),
        "profit_margin": profit_margin(df),
        "average_order_value": average_order_value(df),
        "average_units_per_order": average_units_per_order(df),
        "customer_count": customer_count(df),
        "revenue_per_customer": revenue_per_customer(df),
        "repeat_customer_rate": repeat_customer_rate(df),
    }


if __name__ == "__main__":
    from data_loading import load_orders
    from data_cleaning import clean_orders
    from feature_engineering import engineer_all

    raw = load_orders()
    cleaned, _ = clean_orders(raw)
    tables = engineer_all(cleaned)
    kpis = compute_core_kpis(tables["lines"])
    for k, v in kpis.items():
        print(f"{k}: {v:,.4f}" if isinstance(v, float) else f"{k}: {v:,}")
