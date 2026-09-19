"""Model evaluation helpers.

R-squared is reported as the proportion of variance in average sale amount that
the model explains. It is not an accuracy rate and is never described as one
anywhere in this repository.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(y_true, y_pred) -> dict:
    """R-squared, MAE, RMSE and MAPE for a set of predictions."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100) if np.all(y_true != 0) else float("nan")
    return {
        "n": int(len(y_true)),
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mape_pct": mape,
    }


def residual_frame(y_true, y_pred) -> pd.DataFrame:
    """Tidy frame of actuals, fitted values and residuals for diagnostics."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    resid = y_true - y_pred
    std = resid.std(ddof=1)
    return pd.DataFrame({
        "Actual": y_true,
        "Predicted": y_pred,
        "Residual": resid,
        "Standardised_Residual": resid / std if std else np.nan,
    })


def interpret_r2(r2: float) -> str:
    """One sentence a non-technical stakeholder can read without being misled."""
    return (
        f"The model explains approximately {r2 * 100:.1f}% of the variation in "
        "average sale amount across the customers evaluated. This is a measure of "
        "explained variance, not an accuracy rate, and it says nothing on its own "
        "about the size of the error on any individual customer."
    )


def financial_error_band(mae: float, n_customers: int, gross_margin: float) -> dict:
    """Translate average prediction error into campaign-level dollars.

    Prediction errors are not all in the same direction, so this is a worst-case
    framing: it assumes every customer is mispredicted by the average error in
    the same direction. The realistic band is materially narrower.
    """
    revenue_swing = mae * n_customers
    return {
        "mae": mae,
        "customers": n_customers,
        "worst_case_revenue_swing": revenue_swing,
        "worst_case_gross_profit_swing": revenue_swing * gross_margin,
    }
