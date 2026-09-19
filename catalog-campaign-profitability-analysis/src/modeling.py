"""Training and scoring of the linear regression baseline.

Linear regression is used because the business question is not "what is the
most accurate possible prediction" but "which customer characteristics move
average sale amount, and by how much in dollars". A linear model answers both
and its coefficients can be read directly by a marketing stakeholder.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score, train_test_split

from . import feature_engineering as fe

RANDOM_STATE = 42
TEST_SIZE = 0.25


@dataclass
class TrainedModel:
    """A fitted estimator plus everything needed to score new customers."""

    estimator: LinearRegression
    columns: list[str]
    reference_segment: str = fe.REFERENCE_SEGMENT
    metrics: dict = field(default_factory=dict)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        X = fe.build_feature_matrix(
            df, reference_segment=self.reference_segment, columns=self.columns
        )
        return self.estimator.predict(X)

    @property
    def coefficients(self) -> pd.Series:
        s = pd.Series(self.estimator.coef_, index=self.columns)
        s.loc["Intercept"] = self.estimator.intercept_
        return s


def fit_linear_model(
    df: pd.DataFrame,
    target: str = "Avg_Sale_Amount",
    reference_segment: str = fe.REFERENCE_SEGMENT,
) -> TrainedModel:
    """Fit the model on the full historical file (the source-project setup)."""
    X = fe.build_feature_matrix(df, reference_segment=reference_segment)
    y = df[target].to_numpy(dtype=float)
    estimator = LinearRegression().fit(X, y)
    return TrainedModel(
        estimator=estimator,
        columns=list(X.columns),
        reference_segment=reference_segment,
    )


def holdout_evaluation(
    df: pd.DataFrame,
    target: str = "Avg_Sale_Amount",
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict:
    """Refit on a train split and report out-of-sample performance.

    The source project reported R-squared on the fitted data. This adds an
    honest generalisation check without changing the production model.
    """
    from .evaluation import regression_metrics

    X = fe.build_feature_matrix(df)
    y = df[target].to_numpy(dtype=float)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    est = LinearRegression().fit(X_train, y_train)
    return {
        "train": regression_metrics(y_train, est.predict(X_train)),
        "test": regression_metrics(y_test, est.predict(X_test)),
        "n_train": len(y_train),
        "n_test": len(y_test),
    }


def cross_validated_r2(
    df: pd.DataFrame,
    target: str = "Avg_Sale_Amount",
    folds: int = 5,
    random_state: int = RANDOM_STATE,
) -> dict:
    """5-fold cross-validated R-squared, reported as mean and standard deviation."""
    X = fe.build_feature_matrix(df)
    y = df[target].to_numpy(dtype=float)
    cv = KFold(n_splits=folds, shuffle=True, random_state=random_state)
    scores = cross_val_score(LinearRegression(), X, y, cv=cv, scoring="r2")
    return {"folds": folds, "scores": scores.tolist(),
            "mean_r2": float(scores.mean()), "std_r2": float(scores.std())}


def compare_alternatives(
    df: pd.DataFrame,
    target: str = "Avg_Sale_Amount",
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """Benchmark the baseline against two sensible alternatives.

    This is a sanity check on model choice, not a leaderboard. If a far more
    flexible model does not beat linear regression by a wide margin, the
    interpretable model is the right one for a decision-support product.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.tree import DecisionTreeRegressor

    from .evaluation import regression_metrics

    X = fe.build_feature_matrix(df)
    y = df[target].to_numpy(dtype=float)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=random_state
    )
    candidates = {
        "Linear Regression (baseline)": LinearRegression(),
        "Decision Tree (depth 5)": DecisionTreeRegressor(
            max_depth=5, random_state=random_state
        ),
        "Random Forest (200 trees)": RandomForestRegressor(
            n_estimators=200, random_state=random_state, n_jobs=-1
        ),
    }
    rows = []
    for name, est in candidates.items():
        est.fit(X_train, y_train)
        m = regression_metrics(y_test, est.predict(X_test))
        rows.append({"Model": name, "Test R2": m["r2"],
                     "Test MAE": m["mae"], "Test RMSE": m["rmse"]})
    return pd.DataFrame(rows)


def score_mailing_list(model: TrainedModel, mailing: pd.DataFrame) -> pd.DataFrame:
    """Attach `Predicted_Sale_Amount` to the 250-prospect mailing list."""
    out = mailing.copy()
    out["Predicted_Sale_Amount"] = model.predict(out)
    return out
