from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def kpis(inv: pd.DataFrame, mi: pd.DataFrame, dim_mat: pd.DataFrame) -> dict:
    last = inv[inv.date == inv.date.max()]
    val = float((last.closing_stock * last.unit_cost).sum())
    low = last[last.closing_stock <= last.reorder_level]
    return {"inventory_value_end_usd": val, "avg_inventory_value_usd": float(mi.avg_inventory_value_usd.sum()),
            "stockout_rate_pct": float(100 * inv.stockout_flag.mean()), "stockout_days_total": int(inv.stockout_flag.sum()),
            "annualised_inventory_turnover": float(mi.consumption_value_usd.sum() / (mi.avg_inventory_value_usd.sum() * (mi.days.iloc[0] / 365.25))),
            "avg_days_of_inventory": float(mi.days_of_inventory.replace([np.inf, -np.inf], np.nan).median()),
            "low_stock_items_at_end": int(len(low)), "consumption_value_usd": float(mi.consumption_value_usd.sum())}


def by_category(mi: pd.DataFrame) -> pd.DataFrame:
    g = mi.groupby("material_category").agg(stockout_days=("stockout_days", "sum"), item_warehouse_pairs=("material_id", "size"),
                                             avg_inventory_value_usd=("avg_inventory_value_usd", "sum"), consumption_value_usd=("consumption_value_usd", "sum"),
                                             total_consumption=("total_consumption", "sum"), days=("days", "max")).reset_index()
    g["stockout_rate_pct"] = 100 * g.stockout_days / (g.item_warehouse_pairs * g.days)
    return g.sort_values("stockout_rate_pct", ascending=False)


def excess_inventory(mi: pd.DataFrame, days_threshold: float = 90) -> pd.DataFrame:
    """Excess (assumption): average days of inventory above threshold."""
    e = mi[mi.days_of_inventory > days_threshold].copy()
    return e.sort_values("avg_inventory_value_usd", ascending=False)[["material_id", "material_name", "warehouse_id", "avg_closing_stock", "days_of_inventory", "avg_inventory_value_usd"]]


def low_stock(inv: pd.DataFrame, dim_mat: pd.DataFrame) -> pd.DataFrame:
    last = inv[inv.date == inv.date.max()]
    l = last[last.closing_stock <= last.reorder_level].merge(dim_mat[["material_id", "material_name"]], on="material_id")
    return l[["material_id", "material_name", "warehouse_id", "closing_stock", "reorder_level"]]


def supplier_association(sp: pd.DataFrame) -> dict:
    r = stats.spearmanr(sp.on_time_pct, sp.stockout_days_on_supplied_items)
    return {"n_suppliers": len(sp), "spearman_rho_ontime_vs_stockout_days": float(r.statistic), "p_value": float(r.pvalue)}
