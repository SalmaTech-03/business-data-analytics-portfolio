"""Predictive maintenance experiment on SYNTHETIC sensor data.

Target: corrective failure within the next 7 days. The sensor-failure relationship is SIMULATED
(documented in docs/data_generation_methodology.md); metrics describe performance on synthetic data only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from og_oip import config

H = config.ML_HORIZON_DAYS
TRAIN_END, VAL_END, TEST_START = "2023-01-31", "2023-06-30", "2023-07-15"
FEATURES = ["vib_mean", "vib_max", "temp", "pressure", "flow", "kwh", "op_hours", "vib_ratio_3d", "vib_ratio_7d", "temp_delta_3d",
            "flow_ratio_3d", "kwh_ratio_3d", "vib_std_7d", "days_since_maintenance", "age_years", "crit_num"] + \
           [f"type_{t}" for t in ["Pump", "Compressor", "Separator", "Generator", "Valve", "Heat Exchanger", "Pipeline Equipment"]]


def build_dataset(sd: pd.DataFrame, maint: pd.DataFrame, eq: pd.DataFrame) -> pd.DataFrame:
    d = sd.sort_values(["equipment_id", "date"]).copy()
    d["date"] = d["date"].astype("datetime64[ns]")
    maint = maint.assign(date=maint["date"].astype("datetime64[ns]"))
    eq = eq.assign(installation_date=eq["installation_date"].astype("datetime64[ns]"))
    d = d.rename(columns={"vibration_mm_s_mean": "vib_mean", "vibration_mm_s_max": "vib_max", "temperature_c_mean": "temp",
                          "pressure_psi_mean": "pressure", "flow_rate_mean": "flow", "energy_kwh_sum": "kwh", "operating_hours_sum": "op_hours"})
    g = d.groupby("equipment_id")
    def roll(col, w, fn="mean"):
        return g[col].transform(lambda s: getattr(s.rolling(w, min_periods=max(2, w // 2)), fn)())
    d["vib_r3"], d["vib_r7"] = roll("vib_mean", 3), roll("vib_mean", 7)
    base = lambda col: g[col].transform(lambda s: s.rolling(60, min_periods=30).median().shift(7))
    d["vib_base"], d["temp_base"], d["flow_base"], d["kwh_base"] = base("vib_mean"), base("temp"), base("flow"), base("kwh")
    d["vib_ratio_3d"] = d.vib_r3 / d.vib_base; d["vib_ratio_7d"] = d.vib_r7 / d.vib_base
    d["temp_delta_3d"] = roll("temp", 3) - d.temp_base
    d["flow_ratio_3d"] = roll("flow", 3) / d.flow_base.replace(0, np.nan); d["kwh_ratio_3d"] = roll("kwh", 3) / d.kwh_base.replace(0, np.nan)
    d["vib_std_7d"] = roll("vib_mean", 7, "std")
    e = eq.set_index("equipment_id")
    d["age_years"] = (d.date - d.equipment_id.map(e["installation_date"])).dt.days / 365.25
    d["crit_num"] = d.equipment_id.map(e["criticality"]).map({"Low": 1, "Medium": 2, "High": 3})
    et = d.equipment_id.map(e["equipment_type"])
    for t in ["Pump", "Compressor", "Separator", "Generator", "Valve", "Heat Exchanger", "Pipeline Equipment"]:
        d[f"type_{t}"] = (et == t).astype(int)
    # days since last maintenance event (any type) on or before date
    ev = maint[["equipment_id", "date"]].drop_duplicates().sort_values("date")
    d = pd.merge_asof(d.sort_values("date"), ev.rename(columns={"date": "last_maint"}).assign(last_maint_date=lambda x: x.last_maint).sort_values("last_maint"),
                      left_on="date", right_on="last_maint", by="equipment_id", direction="backward")
    d["days_since_maintenance"] = (d.date - d.last_maint_date).dt.days.fillna(365).clip(upper=365)
    # label: corrective failure in (t, t+H]
    fails = maint[maint.maintenance_type == "Corrective"][["equipment_id", "date"]].sort_values("date")
    fd = fails.groupby("equipment_id")["date"].apply(lambda s: s.values).to_dict()
    lab = np.zeros(len(d), dtype=int)
    for i, (eid, dt) in enumerate(zip(d.equipment_id.values, d.date.values)):
        arr = fd.get(eid)
        if arr is not None:
            k = np.searchsorted(arr, dt, side="right")
            if k < len(arr) and arr[k] <= dt + np.timedelta64(H, "D"):
                lab[i] = 1
    d["label"] = lab
    d = d.sort_values(["equipment_id", "date"]).reset_index(drop=True)
    d = d.dropna(subset=["vib_ratio_3d", "vib_ratio_7d", "temp_delta_3d", "flow_ratio_3d", "kwh_ratio_3d", "vib_std_7d"])
    return d


def split(d: pd.DataFrame):
    last_labelled = d.date.max() - pd.Timedelta(days=H)
    tr = d[d.date <= TRAIN_END]; va = d[(d.date > TRAIN_END) & (d.date <= VAL_END)]
    te = d[(d.date >= TEST_START) & (d.date <= last_labelled)]
    return tr, va, te


def _metrics(y, p, thr):
    yh = (p >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, yh, labels=[0, 1]).ravel()
    return {"roc_auc": roc_auc_score(y, p), "pr_auc": average_precision_score(y, p), "threshold": float(thr),
            "precision": precision_score(y, yh, zero_division=0), "recall": recall_score(y, yh), "f1": f1_score(y, yh),
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)}


def best_threshold(y, p):
    qs = np.unique(np.quantile(p, np.linspace(0.5, 0.995, 100)))
    return max(qs, key=lambda t: f1_score(y, (p >= t).astype(int)))


def run_experiment(d: pd.DataFrame, seed: int = config.RANDOM_SEED):
    tr, va, te = split(d)
    X = lambda x: x[FEATURES].astype(float)
    models = {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed)),
        "Random Forest": RandomForestClassifier(n_estimators=150, min_samples_leaf=10, class_weight="balanced_subsample", random_state=seed, n_jobs=1),
        "Gradient Boosting (HistGB)": HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, random_state=seed),
    }
    results, fitted, test_scores = [], {}, {}
    for n, m in models.items():
        m.fit(X(tr), tr.label)
        thr = best_threshold(va.label.values, m.predict_proba(X(va))[:, 1])     # threshold chosen on validation only
        p = m.predict_proba(X(te))[:, 1]
        r = _metrics(te.label.values, p, thr); r["model"] = n
        results.append(r); fitted[n] = m; test_scores[n] = p
    # simple rule baseline on the test set (no training): vib_ratio_3d threshold chosen on validation
    thr_b = best_threshold(va.label.values, va.vib_ratio_3d.values)
    rb = _metrics(te.label.values, te.vib_ratio_3d.values, thr_b); rb["model"] = "Rule baseline: 3-day vibration ratio"
    results.append(rb)
    res = pd.DataFrame(results)[["model", "roc_auc", "pr_auc", "precision", "recall", "f1", "threshold", "tp", "fp", "fn", "tn"]]
    info = {"train_rows": len(tr), "val_rows": len(va), "test_rows": len(te), "train_positive_rate_pct": 100 * tr.label.mean(),
            "test_positive_rate_pct": 100 * te.label.mean(), "test_failure_events_positive_rows": int(te.label.sum()),
            "split": {"train_end": TRAIN_END, "val_end": VAL_END, "test_start": TEST_START, "test_end": str(te.date.max().date())},
            "note": "Positive-rate baseline: PR-AUC of a random model equals the test positive rate."}
    return res, info, fitted, (tr, va, te), test_scores


def event_level_recall(te: pd.DataFrame, p: np.ndarray, thr: float) -> dict:
    d = te[["equipment_id", "date", "label"]].copy(); d["alert"] = (p >= thr).astype(int)
    # a failure "event" = first positive day run start; approximate with positive rows grouped per equipment by gaps
    pos = d[d.label == 1].sort_values(["equipment_id", "date"])
    grp = (pos.groupby("equipment_id")["date"].diff().dt.days.fillna(99) > H).cumsum()
    detected = pos.assign(g=grp.values).groupby("g")["alert"].max()
    eq_years = d.groupby("equipment_id").date.nunique().sum() / 365.25
    fa = d[(d.label == 0) & (d.alert == 1)]
    return {"failure_windows": int(len(detected)), "failure_windows_with_alert_pct": float(100 * detected.mean()),
            "false_alert_days_per_equipment_year": float(len(fa) / eq_years)}


def feature_importance(fitted: dict) -> pd.DataFrame:
    rf = fitted["Random Forest"]; lr = fitted["Logistic Regression"][-1]
    return pd.DataFrame({"feature": FEATURES, "rf_importance": rf.feature_importances_, "logreg_abs_coef_standardised": np.abs(lr.coef_[0])}).sort_values("rf_importance", ascending=False)


def latest_risk(d: pd.DataFrame, model, eq: pd.DataFrame) -> pd.DataFrame:
    last = d[d.date == d.date.max()].copy()
    last["failure_risk_score_7d"] = model.predict_proba(last[FEATURES].astype(float))[:, 1]
    return last.merge(eq[["equipment_id", "equipment_name", "equipment_type", "field_id", "criticality"]], on="equipment_id")[
        ["equipment_id", "equipment_name", "equipment_type", "field_id", "criticality", "date", "failure_risk_score_7d"]].sort_values("failure_risk_score_7d", ascending=False)
