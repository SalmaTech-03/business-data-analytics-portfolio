"""Feature construction for the average-sale-amount regression model.

The predictor set deliberately mirrors the source project: average number of
products purchased plus the customer segment. See docs/business_rules.md
(BRule-05) for why the location and identity fields are excluded.
"""

from __future__ import annotations

import pandas as pd

NUMERIC_FEATURES = ["Avg_Num_Products_Purchased"]
CATEGORICAL_FEATURES = ["Customer_Segment"]

# "Credit Card Only" is the reference level. Every segment coefficient is
# therefore read as a difference versus a Credit-Card-Only customer.
REFERENCE_SEGMENT = "Credit Card Only"


def build_feature_matrix(
    df: pd.DataFrame,
    reference_segment: str = REFERENCE_SEGMENT,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """One-hot encode segment and return a numeric design matrix.

    Parameters
    ----------
    df
        Frame containing `Avg_Num_Products_Purchased` and `Customer_Segment`.
    reference_segment
        Segment dropped to avoid the dummy-variable trap.
    columns
        If given, the output is reindexed to exactly these columns. Use the
        training matrix columns when scoring the mailing list so that a segment
        missing from the prospects still produces a valid zero column.
    """
    missing = [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required feature columns: {missing}")

    X = pd.get_dummies(
        df[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
        columns=CATEGORICAL_FEATURES,
        prefix=CATEGORICAL_FEATURES,
    ).astype(float)

    ref_col = f"Customer_Segment_{reference_segment}"
    if ref_col in X.columns:
        X = X.drop(columns=[ref_col])

    if columns is not None:
        X = X.reindex(columns=columns, fill_value=0.0)
    return X


def feature_names(reference_segment: str = REFERENCE_SEGMENT) -> list[str]:
    """Canonical column order of the design matrix."""
    segments = [
        "Credit Card Only",
        "Loyalty Club Only",
        "Loyalty Club and Credit Card",
        "Store Mailing List",
    ]
    return NUMERIC_FEATURES + [
        f"Customer_Segment_{s}" for s in segments if s != reference_segment
    ]
