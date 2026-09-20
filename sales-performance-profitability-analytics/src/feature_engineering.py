"""
feature_engineering.py
=======================
Derives analysis-ready features from the cleaned Orders DataFrame.

Only features that are directly computable from columns that exist in
the source data are created here. In particular:

  * There is NO unit-cost or unit-price column in the source data, so
    a cost-based margin (Profit / Cost) CANNOT be computed. The only
    valid margin definition available is Profit / Sales
    ("profit margin on sales"), and that is what `profit_margin`
    means everywhere in this project. This is documented explicitly
    so it is never confused with a cost-based margin.
  * "Repeat customer" is defined as a customer_id associated with more
    than one distinct order_id. This is a standard, defensible
    definition given the columns available.
"""

from __future__ import annotations

import pandas as pd


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add Year / Quarter / Month / Month Name / Year-Month columns
    derived from order_date."""
    out = df.copy()
    out["order_year"] = out["order_date"].dt.year
    out["order_quarter"] = out["order_date"].dt.quarter
    out["order_month"] = out["order_date"].dt.month
    out["order_month_name"] = out["order_date"].dt.strftime("%B")
    out["order_year_month"] = out["order_date"].dt.to_period("M").astype(str)
    out["order_year_quarter"] = (
        out["order_year"].astype(str) + "-Q" + out["order_quarter"].astype(str)
    )
    return out


def add_order_line_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add line-item-level derived metrics.

    profit_margin here is Profit / Sales (a margin on revenue), NOT a
    cost-based margin -- the source data has no unit cost field.
    """
    out = df.copy()
    out["profit_margin"] = out["profit"] / out["sales"].replace(0, pd.NA)
    out["is_loss_making"] = out["profit"] < 0
    return out


def build_order_level_table(df_lines: pd.DataFrame) -> pd.DataFrame:
    """Collapse line items to one row per order_id.

    Average Order Value is computed at THIS granularity: it is the
    average of order_total_sales across distinct orders, not the
    average of individual line-item sales.
    """
    order_level = (
        df_lines.groupby("order_id")
        .agg(
            order_date=("order_date", "min"),
            customer_id=("customer_id", "first"),
            segment=("segment", "first"),
            region=("region", "first"),
            order_total_sales=("sales", "sum"),
            order_total_profit=("profit", "sum"),
            order_total_quantity=("quantity", "sum"),
            line_items=("row_id", "count"),
        )
        .reset_index()
    )
    order_level["order_profit_margin"] = (
        order_level["order_total_profit"] / order_level["order_total_sales"].replace(0, pd.NA)
    )
    return order_level


def build_customer_level_table(df_lines: pd.DataFrame) -> pd.DataFrame:
    """Collapse to one row per customer_id, with order-frequency and
    revenue-contribution features.

    repeat_customer = True if the customer has more than one distinct
    order_id in the dataset.
    """
    customer_level = (
        df_lines.groupby("customer_id")
        .agg(
            segment=("segment", "first"),
            region=("region", "first"),
            total_orders=("order_id", "nunique"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            total_quantity=("quantity", "sum"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    customer_level["repeat_customer"] = customer_level["total_orders"] > 1
    customer_level["avg_order_value"] = (
        customer_level["total_sales"] / customer_level["total_orders"]
    )
    total_sales_all = df_lines["sales"].sum()
    total_profit_all = df_lines["profit"].sum()
    customer_level["revenue_contribution_pct"] = (
        customer_level["total_sales"] / total_sales_all * 100
    )
    customer_level["profit_contribution_pct"] = (
        customer_level["total_profit"] / total_profit_all * 100
    )
    return customer_level.sort_values("total_sales", ascending=False)


def build_product_level_table(df_lines: pd.DataFrame) -> pd.DataFrame:
    """Collapse to one row per product_id with revenue/profit
    contribution shares."""
    product_level = (
        df_lines.groupby(["product_id", "product_name", "category", "sub_category"])
        .agg(
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            total_quantity=("quantity", "sum"),
            order_count=("order_id", "nunique"),
            avg_discount=("discount", "mean"),
        )
        .reset_index()
    )
    product_level["profit_margin"] = (
        product_level["total_profit"] / product_level["total_sales"].replace(0, pd.NA)
    )
    total_sales_all = df_lines["sales"].sum()
    total_profit_all = df_lines["profit"].sum()
    product_level["revenue_contribution_pct"] = product_level["total_sales"] / total_sales_all * 100
    product_level["profit_contribution_pct"] = product_level["total_profit"] / total_profit_all * 100
    return product_level.sort_values("total_sales", ascending=False)


def engineer_all(df_clean: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Run the full feature-engineering pipeline and return every
    derived table used downstream."""
    lines = add_date_features(df_clean)
    lines = add_order_line_features(lines)
    return {
        "lines": lines,
        "order_level": build_order_level_table(lines),
        "customer_level": build_customer_level_table(lines),
        "product_level": build_product_level_table(lines),
    }


if __name__ == "__main__":
    from data_loading import load_orders
    from data_cleaning import clean_orders

    raw = load_orders()
    cleaned, _ = clean_orders(raw)
    tables = engineer_all(cleaned)
    for name, t in tables.items():
        print(f"{name}: {t.shape[0]:,} rows x {t.shape[1]} columns")
