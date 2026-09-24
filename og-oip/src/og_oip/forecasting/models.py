"""Production forecasting: naive, moving average, exponential smoothing (SES, damped Holt), AR(p) via OLS.

ARIMA is intentionally NOT included: statsmodels is not available in the build environment and
the project does not force complex models. An OLS autoregression is provided as a labelled stand-in.
Evaluation uses rolling-origin backtests (no look-ahead).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def f_naive(y, h):
    return np.repeat(y[-1], h)


def f_ma(y, h, window=7):
    return np.repeat(np.mean(y[-window:]), h)


def _ses_fit(y):
    def sse(a):
        l, e = y[0], 0.0
        for v in y[1:]:
            e += (v - l) ** 2; l = a[0] * v + (1 - a[0]) * l
        return e
    r = minimize(sse, [0.3], bounds=[(0.01, 0.99)], method="L-BFGS-B")
    return r.x[0]


def f_ses(y, h):
    a = _ses_fit(y[-365:]); l = y[-365:][0]
    for v in y[-365:][1:]:
        l = a * v + (1 - a) * l
    return np.repeat(l, h)


def f_holt_damped(y, h):
    y = y[-365:]
    def run(p):
        a, b, phi = p; l, t, e = y[0], 0.0, 0.0
        for v in y[1:]:
            f = l + phi * t; e += (v - f) ** 2
            ln = a * v + (1 - a) * f; t = b * (ln - l) + (1 - b) * phi * t; l = ln
        return e, l, t
    r = minimize(lambda p: run(p)[0], [0.3, 0.05, 0.9], bounds=[(0.01, 0.99), (0.001, 0.5), (0.8, 0.98)], method="L-BFGS-B")
    _, l, t = run(r.x); phi = r.x[2]
    return np.array([l + sum(phi ** i for i in range(1, k + 1)) * t for k in range(1, h + 1)])


def f_ar(y, h, p=7, train=365):
    y = np.asarray(y[-train:], dtype=float)
    X = np.column_stack([y[p - k - 1:len(y) - k - 1] for k in range(p)] + [np.ones(len(y) - p)])
    coef, *_ = np.linalg.lstsq(X, y[p:], rcond=None)
    hist = list(y[-p:]); out = []
    for _ in range(h):
        x = np.array(hist[::-1][:p] + [1.0]); v = float(x @ coef); out.append(v); hist.append(v)
    return np.array(out)


MODELS = {"Naive (last value)": f_naive, "Moving average (7d)": f_ma, "Moving average (30d)": lambda y, h: f_ma(y, h, 30),
          "Simple exponential smoothing": f_ses, "Damped Holt (trend) smoothing": f_holt_damped, "Autoregression AR(7) OLS": f_ar}


def backtest(series: pd.Series, horizon: int = 30, n_origins: int = 6, step: int = 30, min_train: int = 365, models: dict | None = None):
    y = series.values.astype(float); n = len(y)
    origins = [n - horizon - step * k for k in range(n_origins)][::-1]
    rows = []
    for name, fn in (models or MODELS).items():
        for o in origins:
            if o < min_train:
                continue
            f = fn(y[:o], horizon); a = y[o:o + horizon]
            rows.append({"model": name, "origin": series.index[o - 1], "mae": np.mean(np.abs(a - f)), "rmse": np.sqrt(np.mean((a - f) ** 2)),
                         "mape_pct": 100 * np.mean(np.abs((a - f) / a)), "bias": np.mean(f - a)})
    d = pd.DataFrame(rows)
    summ = d.groupby("model").agg(MAE=("mae", "mean"), RMSE=("rmse", "mean"), MAPE_pct=("mape_pct", "mean"), mean_bias=("bias", "mean"), origins=("origin", "size")).reset_index().sort_values("MAE")
    return d, summ


def final_forecast(series: pd.Series, model_name: str, horizon: int = 30) -> pd.DataFrame:
    f = MODELS[model_name](series.values.astype(float), horizon)
    idx = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon)
    return pd.DataFrame({"date": idx, "forecast_oil_bbl": f, "model": model_name})
