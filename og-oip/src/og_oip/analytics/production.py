"""Production analytics. Metric definitions: business-analysis/kpi_dictionary.md."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def portfolio_kpis(wd: pd.DataFrame) -> dict:
    daily = wd.groupby("date")[["oil_production_bbl", "potential_production_bbl"]].sum()
    return {
        "total_oil_bbl": float(wd.oil_production_bbl.sum()), "total_gas_mcf": float(wd.gas_production_mcf.sum()),
        "total_water_bbl": float(wd.water_production_bbl.sum()), "avg_daily_oil_bbl_portfolio": float(daily.oil_production_bbl.mean()),
        "potential_oil_bbl": float(wd.potential_production_bbl.sum()), "production_loss_bbl": float(wd.production_loss_bbl.sum()),
        "production_loss_pct": float(100 * wd.production_loss_bbl.sum() / wd.potential_production_bbl.sum()),
        "downtime_loss_bbl": float(wd.downtime_loss_bbl.sum()), "other_loss_bbl": float(wd.other_loss_bbl.sum()),
        "downtime_share_of_loss_pct": float(100 * wd.downtime_loss_bbl.sum() / wd.production_loss_bbl.sum()),
        "total_downtime_hours": float(wd.downtime_hours.sum()),
        "maintenance_associated_downtime_share_pct": float(100 * wd.maintenance_attributed_downtime_hours.sum() / wd.downtime_hours.sum()),
        "estimated_lost_revenue_usd": float(wd.estimated_lost_revenue_usd.sum()),
        "overall_water_cut_pct": float(100 * wd.water_production_bbl.sum() / (wd.water_production_bbl.sum() + wd.oil_production_bbl.sum())),
    }


def by_field(wd: pd.DataFrame, fields: pd.DataFrame) -> pd.DataFrame:
    g = wd.groupby("field_id").agg(oil_bbl=("oil_production_bbl", "sum"), gas_mcf=("gas_production_mcf", "sum"),
                                    water_bbl=("water_production_bbl", "sum"), potential_bbl=("potential_production_bbl", "sum"),
                                    loss_bbl=("production_loss_bbl", "sum"), downtime_hours=("downtime_hours", "sum"),
                                    lost_revenue_usd=("estimated_lost_revenue_usd", "sum"), wells=("well_id", "nunique")).reset_index()
    g["loss_pct"] = 100 * g.loss_bbl / g.potential_bbl
    g["water_cut_pct"] = 100 * g.water_bbl / (g.water_bbl + g.oil_bbl)
    return g.merge(fields[["field_id", "field_name"]], on="field_id").sort_values("loss_bbl", ascending=False)


def by_well(wd: pd.DataFrame) -> pd.DataFrame:
    """Ranking metric (explicit): rank_by_loss = total production loss (bbl); avg_oil_rate = oil / producing days."""
    g = wd.groupby(["well_id", "well_name", "field_id"]).agg(
        producing_days=("date", "size"), oil_bbl=("oil_production_bbl", "sum"), potential_bbl=("potential_production_bbl", "sum"),
        loss_bbl=("production_loss_bbl", "sum"), downtime_hours=("downtime_hours", "sum"), avg_water_cut_pct=("water_cut_pct", "mean"),
        avg_pressure_psi=("pressure_psi", "mean"), lost_revenue_usd=("estimated_lost_revenue_usd", "sum")).reset_index()
    g["avg_oil_rate_bbl_d"] = g.oil_bbl / g.producing_days
    g["loss_pct"] = 100 * g.loss_bbl / g.potential_bbl
    g["rank_by_loss_bbl"] = g.loss_bbl.rank(ascending=False, method="min").astype(int)
    g["rank_by_loss_pct"] = g.loss_pct.rank(ascending=False, method="min").astype(int)
    return g.sort_values("rank_by_loss_bbl")


def monthly_trend(wd: pd.DataFrame) -> pd.DataFrame:
    g = wd.groupby("month").agg(oil_bbl=("oil_production_bbl", "sum"), potential_bbl=("potential_production_bbl", "sum"),
                                 loss_bbl=("production_loss_bbl", "sum"), wells=("well_id", "nunique"), days=("date", "nunique")).reset_index()
    g["avg_daily_oil_bbl"] = g.oil_bbl / g.days
    g["loss_pct"] = 100 * g.loss_bbl / g.potential_bbl
    return g


def decline_analysis(wd: pd.DataFrame, min_months: int = 18) -> pd.DataFrame:
    """Log-linear (exponential) decline fit on monthly mean oil rate per well (actual production).
    Step changes (e.g. workovers) and downtime contaminate the fit - treat as indicative."""
    rows = []
    m = wd.groupby(["well_id", "well_name", "field_id", "month"]).agg(oil=("oil_production_bbl", "sum"), n=("date", "size")).reset_index()
    m = m[m.n >= 20]; m["rate"] = m.oil / m.n
    for (wid, wn, fid), g in m.groupby(["well_id", "well_name", "field_id"]):
        g = g.sort_values("month"); g = g[g.rate > 0]
        if len(g) < min_months:
            continue
        x = (g.month.dt.year - g.month.dt.year.min()) * 12 + g.month.dt.month
        r = stats.linregress(x - x.min(), np.log(g.rate))
        rows.append({"well_id": wid, "well_name": wn, "field_id": fid, "months_used": len(g), "start_rate_bbl_d": g.rate.iloc[:3].mean(),
                     "end_rate_bbl_d": g.rate.iloc[-3:].mean(), "nominal_annual_decline_pct": 100 * (1 - np.exp(12 * r.slope)),
                     "r_squared": r.rvalue ** 2, "slope_p_value": r.pvalue})
    return pd.DataFrame(rows).sort_values("nominal_annual_decline_pct", ascending=False)


def pressure_trend(wd: pd.DataFrame) -> pd.DataFrame:
    g = wd.groupby(["field_id", wd.date.dt.year.rename("year")]).agg(avg_pressure_psi=("pressure_psi", "mean"), avg_water_cut_pct=("water_cut_pct", "mean")).reset_index()
    return g


def loss_associations(wd: pd.DataFrame) -> pd.DataFrame:
    """Spearman correlations at well-month level (ASSOCIATION only, not causal proof)."""
    m = wd.groupby(["well_id", "month"]).agg(loss=("production_loss_bbl", "sum"), pot=("potential_production_bbl", "sum"),
                                              wc=("water_cut_pct", "mean"), pr=("pressure_psi", "mean"), age=("well_age_days", "mean"),
                                              dt=("downtime_hours", "sum"), other=("other_loss_bbl", "sum")).reset_index()
    m["loss_pct"] = 100 * m.loss / m.pot; m["other_loss_pct"] = 100 * m.other / m.pot
    rows = []
    for target in ["loss_pct", "other_loss_pct"]:
        for f, lab in [("wc", "avg water cut %"), ("pr", "avg pressure psi"), ("age", "well age (days)"), ("dt", "downtime hours in month")]:
            r = stats.spearmanr(m[f], m[target])
            rows.append({"target": target, "factor": lab, "spearman_rho": float(r.statistic), "p_value": float(r.pvalue), "n": len(m)})
    return pd.DataFrame(rows)
