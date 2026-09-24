from _common import *  # noqa
import numpy as np
from og_oip import config
from og_oip.real_data import bsee, volve

_c = {}


def _v():
    if "v" not in _c:
        _c["v"] = volve.load()
    return _c["v"]


def test_volve_loads_and_reconciles_daily_to_monthly():
    daily, monthly = _v()
    assert len(daily) == 15634 and len(monthly) > 500
    q = volve.analyse(daily, monthly)["data_quality"].set_index("check")["value"]
    assert q["daily-vs-monthly sheet: max |oil diff| Sm3"] < 1e-3
    assert q["duplicate (date, wellbore) rows"] == 0


def test_volve_unit_conversion_and_separation():
    daily, _ = _v()
    d = volve.prepare_daily(daily)
    assert np.isclose(d.oil_bbl.sum(), d.oil_sm3.sum() * config.BBL_PER_M3)
    assert "PetroNexa" not in str(d.columns.tolist())


def test_bsee_layout_and_quality():
    d = bsee.load()
    assert d.shape[1] >= 19 and len(d) == 85205 and d.month.nunique() == 18
    assert d.month.isna().sum() == 0 and (d[["oil_bbl", "gas_mcf", "water_bbl"]] >= 0).all().all()
    a = bsee.analyse(d)
    assert np.isclose(a["monthly"].oil_bbl.sum(), d.oil_bbl.sum()) and np.isclose(a["operators"].oil_share_pct.sum(), 100)
    assert 0 < a["concentration"].iloc[0]["hhi_oil (0-10000)"] <= 10000


def test_real_and_synthetic_are_not_merged():
    t = truth()
    assert not any("volve" in c.lower() or "bsee" in c.lower() for df in t.values() for c in df.columns)
