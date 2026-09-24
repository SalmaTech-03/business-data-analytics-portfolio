from _common import *  # noqa
import numpy as np
import pandas as pd
from og_oip.ml import predictive_maintenance as pm

_cache = {}


def _ds():
    if "d" not in _cache:
        t = processed_typed()
        _cache["d"] = pm.build_dataset(marts()["mart_sensor_daily"], t["fact_maintenance"], t["dim_equipment"])
    return _cache["d"]


def test_label_matches_definition():
    d = _ds(); m = processed_typed()["fact_maintenance"]
    f = m[m.maintenance_type == "Corrective"]
    s = d.sample(300, random_state=1)
    for r in s.itertuples():
        ev = f[(f.equipment_id == r.equipment_id) & (f.date > r.date) & (f.date <= r.date + pd.Timedelta(days=pm.H))]
        assert int(len(ev) > 0) == r.label


def test_split_is_time_ordered_without_overlap():
    tr, va, te = pm.split(_ds())
    assert tr.date.max() < va.date.min() and va.date.max() < te.date.min()
    assert (te.date.min() - va.date.max()).days >= pm.H


def test_features_complete_and_no_nan():
    d = _ds()
    assert set(pm.FEATURES) <= set(d.columns) and not d[pm.FEATURES].isna().any().any()


def test_metrics_are_computed_not_fabricated():
    res, info, fitted, (tr, va, te), scores = pm.run_experiment(_ds())
    assert set(["Logistic Regression", "Random Forest", "Gradient Boosting (HistGB)"]) <= set(res.model)
    for c in ["roc_auc", "pr_auc", "precision", "recall", "f1"]:
        assert res[c].between(0, 1).all()
    r = res.iloc[1]; y = te.label.values
    assert r.tp + r.fn == y.sum() and r.tp + r.fp + r.fn + r.tn == len(y)
    from sklearn.metrics import roc_auc_score
    assert np.isclose(roc_auc_score(y, scores["Random Forest"]), r.roc_auc)
    assert (res.pr_auc.iloc[:3] > y.mean()).all()      # better than the random-model PR-AUC (prevalence)
