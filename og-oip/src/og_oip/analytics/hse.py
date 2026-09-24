from __future__ import annotations

import pandas as pd
from scipy import stats


def kpis(h: pd.DataFrame, hm: pd.DataFrame) -> dict:
    return {"incident_count": int(len(h)), "lost_time_incidents": int(h.lost_time_flag.sum()), "days_lost": int(h.days_lost.sum()),
            "portfolio_incident_rate_per_200k_h": float(hm.incidents.sum() * 200000 / hm.exposure_hours.sum()),
            "portfolio_ltir_per_200k_h": float(hm.lost_time_incidents.sum() * 200000 / hm.exposure_hours.sum()),
            "high_or_critical_share_pct": float(100 * h.severity.isin(["High", "Critical"]).mean())}


def distributions(h: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {"severity": h.severity.value_counts().rename_axis("severity").reset_index(name="incidents"),
            "root_cause": h.root_cause.value_counts().rename_axis("root_cause").reset_index(name="incidents"),
            "incident_type": h.incident_type.value_counts().rename_axis("incident_type").reset_index(name="incidents"),
            "field": h.groupby("field_id").agg(incidents=("incident_id", "size"), lost_time=("lost_time_flag", "sum"), days_lost=("days_lost", "sum")).reset_index()}


def by_field_rate(hm: pd.DataFrame) -> pd.DataFrame:
    g = hm.groupby("field_id").agg(incidents=("incidents", "sum"), lti=("lost_time_incidents", "sum"), exposure_hours=("exposure_hours", "sum")).reset_index()
    g["incident_rate_per_200k_h"] = g.incidents * 200000 / g.exposure_hours; g["ltir_per_200k_h"] = g.lti * 200000 / g.exposure_hours
    return g


def maintenance_association(hm: pd.DataFrame, em: pd.DataFrame) -> dict:
    fm = em.groupby(["field_id", "month"])["failures"].sum().reset_index()
    d = hm.merge(fm, on=["field_id", "month"], how="left").fillna({"failures": 0})
    r = stats.spearmanr(d.failures, d.incidents)
    return {"n_field_months": len(d), "spearman_rho_failures_vs_incidents": float(r.statistic), "p_value": float(r.pvalue)}


def post_failure_window(h: pd.DataFrame, maint: pd.DataFrame, eq: pd.DataFrame, window: int = 3) -> dict:
    """Share of incidents occurring within `window` days after a corrective event in the same field vs share of field-days in such a window."""
    c = maint[maint.maintenance_type == "Corrective"].merge(eq[["equipment_id", "field_id"]], on="equipment_id")
    days = pd.date_range(h.date.min(), h.date.max())
    inwin = set()
    for r in c.itertuples():
        for k in range(window + 1):
            inwin.add((r.field_id, r.date + pd.Timedelta(days=k)))
    hit = sum((r.field_id, r.date) in inwin for r in h.itertuples())
    fields = h.field_id.unique()
    tot_fd = len(days) * len(fields)
    win_fd = len([1 for k in inwin if k[1] >= days[0] and k[1] <= days[-1]])
    return {"window_days": window, "incident_share_in_window_pct": 100 * hit / len(h), "field_day_share_in_window_pct": 100 * win_fd / tot_fd}
