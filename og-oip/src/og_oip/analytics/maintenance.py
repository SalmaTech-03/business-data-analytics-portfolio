from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

CRIT_W = {"High": 3, "Medium": 2, "Low": 1}


def kpis(es: pd.DataFrame, maint: pd.DataFrame) -> dict:
    corr = maint[maint.maintenance_type == "Corrective"]
    return {"failure_count": int(len(corr)), "total_maintenance_events": int(len(maint)),
            "total_downtime_hours_equipment": float(maint.downtime_hours.sum()), "corrective_downtime_hours": float(corr.downtime_hours.sum()),
            "total_maintenance_cost_usd": float(maint.total_cost.sum()), "corrective_cost_share_pct": float(100 * corr.total_cost.sum() / maint.total_cost.sum()),
            "fleet_mttr_hours": float(corr.downtime_hours.mean()),
            "fleet_mtbf_hours": float(es.operating_hours.sum() / max(len(corr), 1)),
            "fleet_availability_pct": float(100 * es.operating_hours.sum() / es.period_hours.sum())}


def by_type(es: pd.DataFrame) -> pd.DataFrame:
    g = es.groupby("equipment_type").agg(units=("equipment_id", "size"), failures=("failures", "sum"), downtime_hours=("total_downtime_hours", "sum"),
                                          cost_usd=("maintenance_cost_usd", "sum"), operating_hours=("operating_hours", "sum"),
                                          corrective_downtime_hours=("corrective_downtime_hours", "sum"), period_hours=("period_hours", "sum")).reset_index()
    g["mtbf_hours"] = g.operating_hours / g.failures.replace(0, np.nan)
    g["mttr_hours"] = g.corrective_downtime_hours / g.failures.replace(0, np.nan)
    g["availability_pct"] = 100 * g.operating_hours / g.period_hours
    g["failures_per_unit_year"] = g.failures / g.units / (g.period_hours.iloc[0] / g.units.iloc[0] / 8766)
    return g.drop(columns=["period_hours"]).sort_values("failures", ascending=False)


def by_failure_type(maint: pd.DataFrame, eq: pd.DataFrame) -> pd.DataFrame:
    c = maint[maint.maintenance_type == "Corrective"].merge(eq[["equipment_id", "equipment_type"]], on="equipment_id")
    return c.groupby(["equipment_type", "failure_type"]).agg(failures=("maintenance_id", "size"), downtime_hours=("downtime_hours", "sum"),
                                                              avg_downtime_hours=("downtime_hours", "mean"), cost_usd=("total_cost", "sum")).reset_index().sort_values("failures", ascending=False)


def by_maintenance_type(maint: pd.DataFrame) -> pd.DataFrame:
    return maint.groupby("maintenance_type").agg(events=("maintenance_id", "size"), downtime_hours=("downtime_hours", "sum"), cost_usd=("total_cost", "sum"),
                                                  avg_cost_usd=("total_cost", "mean")).reset_index()


def critical_equipment(es: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """Priority score (explicit): criticality weight (High=3, Medium=2, Low=1) x total downtime hours."""
    d = es.copy(); d["criticality_weight"] = d.criticality.map(CRIT_W)
    d["priority_score"] = d.criticality_weight * d.total_downtime_hours
    cols = ["equipment_id", "equipment_name", "equipment_type", "field_id", "criticality", "failures", "total_downtime_hours", "maintenance_cost_usd", "mtbf_hours", "mttr_hours", "availability_pct", "priority_score"]
    return d.sort_values("priority_score", ascending=False)[cols].head(top)


def cost_pareto(es: pd.DataFrame) -> pd.DataFrame:
    d = es.sort_values("maintenance_cost_usd", ascending=False)[["equipment_id", "equipment_name", "equipment_type", "maintenance_cost_usd"]].reset_index(drop=True)
    d["cum_share_pct"] = 100 * d.maintenance_cost_usd.cumsum() / d.maintenance_cost_usd.sum()
    return d


def age_association(es: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for et, g in es.groupby("equipment_type"):
        if len(g) >= 6:
            r = stats.spearmanr(g.equipment_age_years_at_end, g.failures_per_year)
            rows.append({"equipment_type": et, "n_units": len(g), "spearman_rho_age_vs_failures_per_year": float(r.statistic), "p_value": float(r.pvalue)})
    r = stats.spearmanr(es.equipment_age_years_at_end, es.failures_per_year)
    rows.append({"equipment_type": "ALL (not type-adjusted)", "n_units": len(es), "spearman_rho_age_vs_failures_per_year": float(r.statistic), "p_value": float(r.pvalue)})
    return pd.DataFrame(rows)
