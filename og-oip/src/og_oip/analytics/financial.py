from __future__ import annotations

import pandas as pd


def kpis(fm: pd.DataFrame) -> dict:
    rev, opex = fm.revenue_usd.sum(), fm.opex_total_usd.sum()
    return {"revenue_usd_synthetic": float(rev), "operating_cost_usd": float(opex), "operating_margin_usd": float(rev - opex),
            "maintenance_cost_usd": float(fm.cost_maintenance_usd.sum()), "energy_cost_usd": float(fm.cost_energy_usd.sum()),
            "cost_per_bbl_oil_sold": float(opex / fm.oil_sold_bbl.sum()),
            "cost_per_boe_sold": float(opex / (fm.oil_sold_bbl.sum() + fm.gas_sold_mcf.sum() / 6.0)),
            "revenue_per_bbl_oil_sold": float(rev / fm.oil_sold_bbl.sum()),
            "estimated_lost_revenue_usd": float(fm.lost_revenue_usd.sum()),
            "lost_revenue_pct_of_revenue": float(100 * fm.lost_revenue_usd.sum() / rev)}


def by_field(fm: pd.DataFrame, fields: pd.DataFrame) -> pd.DataFrame:
    g = fm.groupby("field_id").agg(revenue_usd=("revenue_usd", "sum"), opex_usd=("opex_total_usd", "sum"), maint_usd=("cost_maintenance_usd", "sum"),
                                    energy_usd=("cost_energy_usd", "sum"), oil_sold_bbl=("oil_sold_bbl", "sum"), lost_revenue_usd=("lost_revenue_usd", "sum")).reset_index()
    g["cost_per_bbl"] = g.opex_usd / g.oil_sold_bbl; g["revenue_per_bbl"] = g.revenue_usd / g.oil_sold_bbl
    g["margin_usd"] = g.revenue_usd - g.opex_usd
    return g.merge(fields[["field_id", "field_name"]], on="field_id")


def by_year(fm: pd.DataFrame) -> pd.DataFrame:
    d = fm.copy(); d["year"] = d.month.dt.year
    g = d.groupby("year").agg(revenue_usd=("revenue_usd", "sum"), opex_usd=("opex_total_usd", "sum"), oil_sold_bbl=("oil_sold_bbl", "sum"), lost_revenue_usd=("lost_revenue_usd", "sum")).reset_index()
    g["cost_per_bbl"] = g.opex_usd / g.oil_sold_bbl; g["revenue_per_bbl"] = g.revenue_usd / g.oil_sold_bbl
    return g


def cost_breakdown(fm: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in fm.columns if c.startswith("cost_") and c.endswith("_usd") and c != "cost_per_bbl_oil_sold"]
    s = fm[cols].sum().rename("usd").reset_index().rename(columns={"index": "category"})
    s["category"] = s.category.str.replace("cost_", "").str.replace("_usd", "").str.title(); s["share_pct"] = 100 * s.usd / s.usd.sum()
    return s.sort_values("usd", ascending=False)
