"""Catalog Campaign Profitability & Customer Targeting Analysis."""

from . import data_cleaning, feature_engineering, modeling, profitability, evaluation  # noqa: F401

__all__ = [
    "data_cleaning",
    "feature_engineering",
    "modeling",
    "profitability",
    "evaluation",
]
__version__ = "1.0.0"
