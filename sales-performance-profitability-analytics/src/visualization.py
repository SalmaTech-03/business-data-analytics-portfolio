"""
visualization.py
=================
Chart-producing functions used by the notebooks and by run_analysis.py.

Every function here answers a specific business question (see the
docstring). None are decorative -- if a chart doesn't map to a
question in docs/business_questions.md, it doesn't belong here.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def _save(fig, out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_monthly_revenue_profit(revenue_by_month: pd.DataFrame, out_path: str) -> None:
    """Answers: 'How is revenue changing over time?' Plots monthly
    revenue and profit trend lines side by side."""
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(revenue_by_month["order_year_month"], revenue_by_month["revenue"], label="Revenue", marker="o", markersize=3)
    ax.plot(revenue_by_month["order_year_month"], revenue_by_month["profit"], label="Profit", marker="o", markersize=3)
    ax.set_title("Monthly Revenue and Profit Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("USD")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    step = max(1, len(revenue_by_month) // 12)
    ax.set_xticks(revenue_by_month["order_year_month"][::step])
    ax.tick_params(axis="x", rotation=90)
    ax.legend()
    _save(fig, out_path)


def plot_category_revenue_profit(category_summary: pd.DataFrame, out_path: str) -> None:
    """Answers: 'Which categories generate the most revenue/profit?'"""
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(category_summary))
    width = 0.35
    ax.bar([i - width / 2 for i in x], category_summary["revenue"], width, label="Revenue")
    ax.bar([i + width / 2 for i in x], category_summary["profit"], width, label="Profit")
    ax.set_xticks(list(x))
    ax.set_xticklabels(category_summary["category"])
    ax.set_title("Revenue and Profit by Category")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend()
    _save(fig, out_path)


def plot_subcategory_margin(subcategory_summary: pd.DataFrame, out_path: str) -> None:
    """Answers: 'Which sub-categories perform poorly (weak/negative margin)?'"""
    df_sorted = subcategory_summary.sort_values("margin")
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = ["#c0392b" if m < 0 else "#2980b9" for m in df_sorted["margin"]]
    ax.barh(df_sorted["sub_category"], df_sorted["margin"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Profit Margin by Sub-Category")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))
    _save(fig, out_path)


def plot_region_performance(region_summary: pd.DataFrame, out_path: str) -> None:
    """Answers: 'Which regions perform best?'"""
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(region_summary["region"], region_summary["revenue"], color="#2980b9", label="Revenue")
    ax1.set_ylabel("Revenue (USD)")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax2 = ax1.twinx()
    ax2.plot(region_summary["region"], region_summary["margin"], color="#c0392b", marker="o", label="Profit Margin")
    ax2.set_ylabel("Profit Margin")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax1.set_title("Revenue and Profit Margin by Region")
    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))
    _save(fig, out_path)


def plot_discount_vs_margin(discount_bucket_summary: pd.DataFrame, out_path: str) -> None:
    """Answers: 'How does discount relate to profitability?'
    Shows an ASSOCIATION, not a causal claim (see docs/findings.md)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#c0392b" if m < 0 else "#27ae60" for m in discount_bucket_summary["margin"]]
    ax.bar(discount_bucket_summary["discount_bucket"].astype(str), discount_bucket_summary["margin"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Profit Margin by Discount Level (Association, Not Causation)")
    ax.set_xlabel("Discount Bucket")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))
    _save(fig, out_path)


def plot_top_products(product_summary: pd.DataFrame, out_path: str, n: int = 10) -> None:
    """Answers: 'Which products contribute the most revenue?'"""
    top = product_summary.nlargest(n, "total_sales")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top["product_name"].str.slice(0, 40), top["total_sales"], color="#2980b9")
    ax.invert_yaxis()
    ax.set_title(f"Top {n} Products by Revenue")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    _save(fig, out_path)


def plot_customer_revenue_distribution(customer_summary: pd.DataFrame, out_path: str) -> None:
    """Answers: 'Who are the highest-value customers, and how concentrated is revenue?'
    (Pareto-style view without exposing customer names -- axis uses rank, not identity.)"""
    ranked = customer_summary.sort_values("total_sales", ascending=False).reset_index(drop=True)
    ranked["cumulative_pct"] = ranked["total_sales"].cumsum() / ranked["total_sales"].sum() * 100
    ranked["customer_rank"] = ranked.index + 1

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.bar(ranked["customer_rank"], ranked["total_sales"], color="#95a5a6", width=1.0)
    ax1.set_xlabel("Customer Rank (by revenue, no names shown)")
    ax1.set_ylabel("Revenue per Customer (USD)")
    ax2 = ax1.twinx()
    ax2.plot(ranked["customer_rank"], ranked["cumulative_pct"], color="#c0392b")
    ax2.set_ylabel("Cumulative % of Revenue")
    ax2.set_ylim(0, 100)
    ax1.set_title("Customer Revenue Concentration (Pareto View)")
    _save(fig, out_path)
