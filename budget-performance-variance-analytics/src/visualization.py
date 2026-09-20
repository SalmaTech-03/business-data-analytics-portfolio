"""
visualization.py

Chart-producing functions used by the notebooks and run_analysis.py.
Every chart here answers a specific business question - no
decorative/meaningless charts. Uses matplotlib only (no seaborn
dependency) to keep requirements.txt minimal.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless-safe for pipeline runs
import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)


def plot_budget_vs_utilized_by_department(kpi_by_dept: pd.DataFrame, out_path: Path):
    """Q: Which departments consume the most budget, and how does
    utilization compare to allocation?"""
    fig, ax = plt.subplots(figsize=(9, 5))
    kpi_by_dept[["total_allocated", "total_utilized"]].plot(kind="bar", ax=ax)
    ax.set_title("Budget Allocated vs. Utilized by Department")
    ax.set_ylabel("USD")
    ax.set_xlabel("Department")
    plt.xticks(rotation=45, ha="right")
    _save(fig, out_path)


def plot_utilization_rate_by_department(kpi_by_dept: pd.DataFrame, out_path: Path):
    """Q: Which departments over- or under-spend their allocation?"""
    fig, ax = plt.subplots(figsize=(9, 5))
    data = kpi_by_dept["utilization_rate"].sort_values()
    colors = ["#c0392b" if v > 1 else "#2980b9" for v in data.values]
    data.plot(kind="barh", ax=ax, color=colors)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_title("Budget Utilization Rate by Department (1.0 = fully spent)")
    ax.set_xlabel("Utilization Rate")
    _save(fig, out_path)


def plot_allocation_efficiency_distribution(df: pd.DataFrame, out_path: Path):
    """Q: How is allocation efficiency distributed across all records?"""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["allocation_efficiency"], bins=30, color="#27ae60", edgecolor="white")
    ax.set_title("Distribution of Allocation Efficiency")
    ax.set_xlabel("Allocation Efficiency (0-100)")
    ax.set_ylabel("Record Count")
    _save(fig, out_path)


def plot_budget_status_by_department(df: pd.DataFrame, out_path: Path):
    """Q: How does the mix of Efficient/Moderate/Inefficient records
    vary by department?"""
    cross = pd.crosstab(df["department"], df["budget_status"], normalize="index")
    fig, ax = plt.subplots(figsize=(9, 5))
    cross.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Budget Status Mix by Department (share of records)")
    ax.set_ylabel("Share of records")
    plt.xticks(rotation=45, ha="right")
    ax.legend(title="Budget Status", bbox_to_anchor=(1.02, 1), loc="upper left")
    _save(fig, out_path)


def plot_revenue_forecast_vs_actual(kpi_by_dept: pd.DataFrame, df: pd.DataFrame, out_path: Path):
    """Q: How accurate is revenue forecasting, by department?"""
    grouped = df.groupby("department", observed=True).agg(
        forecast=("revenue_forecast", "sum"), actual=("actual_revenue", "sum")
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    grouped.plot(kind="bar", ax=ax)
    ax.set_title("Revenue Forecast vs. Actual Revenue by Department")
    ax.set_ylabel("USD")
    plt.xticks(rotation=45, ha="right")
    _save(fig, out_path)


def plot_spending_volatility_vs_status(df: pd.DataFrame, out_path: Path):
    """Q: Is there an observable relationship between spending
    volatility and budget status?"""
    fig, ax = plt.subplots(figsize=(8, 5))
    df.boxplot(column="spending_volatility", by="budget_status", ax=ax)
    ax.set_title("Spending Volatility by Budget Status")
    plt.suptitle("")
    ax.set_xlabel("Budget Status")
    ax.set_ylabel("Spending Volatility")
    _save(fig, out_path)
