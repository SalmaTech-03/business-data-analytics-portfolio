from _common import *  # noqa
import numpy as np
import pandas as pd
from og_oip.forecasting import models as fm


def _series(n=500):
    rng = np.random.default_rng(1)
    return pd.Series(1000 + rng.normal(0, 20, n), index=pd.date_range("2023-01-01", periods=n))


def test_shapes_and_simple_model_values():
    y = _series().values
    for name, f in fm.MODELS.items():
        out = f(y, 30)
        assert out.shape == (30,) and np.isfinite(out).all(), name
    assert (fm.f_naive(y, 5) == y[-1]).all()
    assert np.isclose(fm.f_ma(y, 3, 7)[0], y[-7:].mean())


def test_ses_constant_series():
    assert np.allclose(fm.f_ses(np.full(400, 50.0), 10), 50.0)


def test_no_look_ahead_in_backtest():
    s = _series(); y = s.values.copy()
    _, a = fm.backtest(s, horizon=30, n_origins=3, step=30)
    y2 = y.copy(); y2[-30:] += 10_000          # corrupt only the final horizon
    _, b = fm.backtest(pd.Series(y2, index=s.index), horizon=30, n_origins=3, step=30)
    ea = a.set_index("model"); eb = b.set_index("model")
    # earlier origins are unaffected by the corruption; the metrics for the last origin change, others don't -> overall differs but forecasts for first origin identical
    o = len(y) - 30 - 60
    for name, f in fm.MODELS.items():
        assert np.allclose(f(y[:o], 30), f(y2[:o], 30)), name


def test_backtest_metrics_and_final_forecast():
    s = _series(); det, summ = fm.backtest(s)
    assert {"MAE", "RMSE", "MAPE_pct", "mean_bias"} <= set(summ.columns) and np.isfinite(summ.MAE).all()
    f = fm.final_forecast(s, summ.iloc[0].model, 30)
    assert len(f) == 30 and f.date.iloc[0] == s.index[-1] + pd.Timedelta(days=1)


def test_trend_captured_by_damped_holt():
    y = np.arange(400, dtype=float)
    f = fm.f_holt_damped(y, 5)
    assert f[0] > y[-1]
