"""
feature_engineering.py

Derives analytical features that are actually supported by this
dataset. The raw data has NO real calendar date (only a Q1-Q4 label
with no fiscal year), so calendar features like Year/Month/Year-Month
are intentionally NOT created here - doing so would fabricate a
timeline the data doesn't contain. See docs/assumptions_and_constraints.md.

Features added:
- utilization_rate            = budget_utilized / budget_allocated
- budget_variance_pct         = budget_variance / budget_allocated
- revenue_variance_pct        = revenue_variance / revenue_forecast
- revenue_realization_rate    = actual_revenue / revenue_forecast
- monthly_expense_to_budget   = monthly_expense / budget_allocated
- is_overspent                = budget_utilized > budget_allocated
- is_underspent                = budget_utilized < budget_allocated * 0.7
- efficiency_tier             = binned Allocation_Efficiency (Low/Medium/High)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["utilization_rate"] = np.where(
        df["budget_allocated"] != 0,
        df["budget_utilized"] / df["budget_allocated"],
        np.nan,
    )
    df["budget_variance_pct"] = np.where(
        df["budget_allocated"] != 0,
        df["budget_variance"] / df["budget_allocated"],
        np.nan,
    )
    df["revenue_variance_pct"] = np.where(
        df["revenue_forecast"] != 0,
        df["revenue_variance"] / df["revenue_forecast"],
        np.nan,
    )
    df["revenue_realization_rate"] = np.where(
        df["revenue_forecast"] != 0,
        df["actual_revenue"] / df["revenue_forecast"],
        np.nan,
    )
    df["monthly_expense_to_budget"] = np.where(
        df["budget_allocated"] != 0,
        df["monthly_expense"] / df["budget_allocated"],
        np.nan,
    )
    return df


def add_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_overspent"] = df["budget_utilized"] > df["budget_allocated"]
    df["is_underspent"] = df["budget_utilized"] < (df["budget_allocated"] * 0.7)
    return df


def add_efficiency_tier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bin Allocation_Efficiency into Low / Medium / High tiers using
    tertiles computed from the data itself (not arbitrary fixed
    cutoffs), so the tiers are meaningful for THIS dataset.
    """
    df = df.copy()
    df["efficiency_tier"] = pd.qcut(
        df["allocation_efficiency"], q=3, labels=["Low", "Medium", "High"]
    )
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full feature engineering pipeline."""
    df = add_ratio_features(df)
    df = add_flags(df)
    df = add_efficiency_tier(df)
    return df


if __name__ == "__main__":
    from data_loading import load_dataset
    from data_cleaning import clean_dataset

    raw = load_dataset()
    cleaned, _ = clean_dataset(raw)
    featured = engineer_features(cleaned)
    print(featured[[
        "department", "utilization_rate", "budget_variance_pct",
        "revenue_realization_rate", "efficiency_tier",
    ]].head())
