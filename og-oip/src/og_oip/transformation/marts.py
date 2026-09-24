"""Analytical marts built from PROCESSED tables. KPI formulas are documented in business-analysis/kpi_dictionary.md."""
from __future__ import annotations

import numpy as np
import pandas as pd

from og_oip import config
from og_oip.data_generation.operations import spill_hours


def attributed_downtime(maint: pd.DataFrame, bridge: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Well-day downtime hours ASSOCIATED with maintenance events (assumption: downtime starts on the maintenance date
    and spills forward at <=24h/day; well impact = hours x impact_factor from bridge_equipment_well)."""
    day_of = {d: i for i, d in enumerate(dates)}
    eq_w = bridge.groupby("equipment_id")[["well_id", "impact_factor"]].apply(lambda g: list(zip(g.well_id, g.impact_factor)), include_groups=False).to_dict()
    acc: dict[tuple, float] = {}
    for r in maint.itertuples():
        for d, h in spill_hours(day_of[r.date], r.downtime_hours, len(dates)):
            for w, imp in eq_w.get(r.equipment_id, []):
                acc[(dates[d], w)] = acc.get((dates[d], w), 0.0) + h * imp
    df = pd.DataFrame([(k[0], k[1], min(v, 24.0)) for k, v in acc.items()], columns=["date", "well_id", "maintenance_attributed_downtime_hours"])
    return df


def build_mart_well_daily(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
    p, w, s = t["fact_production"], t["dim_well"], t["fact_sales"]
    d = p.merge(w[["well_id", "well_name", "field_id", "commission_date", "well_type", "reservoir"]], on="well_id")
    d["well_age_days"] = (d["date"] - d["commission_date"]).dt.days
    d["production_loss_bbl"] = (d.potential_production_bbl - d.oil_production_bbl).clip(lower=0)
    d["downtime_loss_bbl"] = np.minimum(d.potential_production_bbl * d.downtime_hours / 24, d.production_loss_bbl)
    d["other_loss_bbl"] = (d.production_loss_bbl - d.downtime_loss_bbl).clip(lower=0)
    dates = pd.DatetimeIndex(sorted(t["dim_date"]["date"]))
    att = attributed_downtime(t["fact_maintenance"], t["bridge_equipment_well"], dates)
    d = d.merge(att, on=["date", "well_id"], how="left")
    d["maintenance_attributed_downtime_hours"] = d["maintenance_attributed_downtime_hours"].fillna(0).clip(upper=d.downtime_hours)
    d["unattributed_downtime_hours"] = (d.downtime_hours - d.maintenance_attributed_downtime_hours).clip(lower=0)
    d = d.merge(s[["date", "field_id", "oil_price_usd"]], on=["date", "field_id"], how="left")
    d["estimated_lost_revenue_usd"] = d.production_loss_bbl * d.oil_price_usd
    d["month"] = d["date"].dt.to_period("M").dt.to_timestamp()
    return d.drop(columns=["commission_date"])


def build_mart_field_monthly(t, wd: pd.DataFrame) -> pd.DataFrame:
    g = wd.groupby(["field_id", "month"]).agg(
        oil_bbl=("oil_production_bbl", "sum"), gas_mcf=("gas_production_mcf", "sum"), water_bbl=("water_production_bbl", "sum"),
        potential_bbl=("potential_production_bbl", "sum"), loss_bbl=("production_loss_bbl", "sum"),
        downtime_loss_bbl=("downtime_loss_bbl", "sum"), downtime_hours=("downtime_hours", "sum"),
        maint_attributed_downtime_hours=("maintenance_attributed_downtime_hours", "sum"),
        lost_revenue_usd=("estimated_lost_revenue_usd", "sum"), well_days=("well_id", "size")).reset_index()
    g["loss_pct"] = 100 * g.loss_bbl / g.potential_bbl
    s = t["fact_sales"].copy(); s["month"] = s.date.dt.to_period("M").dt.to_timestamp()
    sm = s.groupby(["field_id", "month"]).agg(oil_sold_bbl=("oil_volume_bbl", "sum"), gas_sold_mcf=("gas_volume_mcf", "sum"), revenue_usd=("revenue_usd", "sum")).reset_index()
    c = t["fact_operating_cost"].copy(); c["month"] = c.date.dt.to_period("M").dt.to_timestamp()
    cm = c.pivot_table(index=["field_id", "month"], columns="cost_category", values="cost_amount_usd", aggfunc="sum").reset_index()
    cm.columns = [x if x in ("field_id", "month") else f"cost_{x.lower()}_usd" for x in cm.columns]
    cm["opex_total_usd"] = cm.filter(like="cost_").sum(axis=1)
    m = g.merge(sm, on=["field_id", "month"], how="left").merge(cm, on=["field_id", "month"], how="left")
    m["cost_per_bbl_oil_sold"] = m.opex_total_usd / m.oil_sold_bbl
    m["cost_per_boe_sold"] = m.opex_total_usd / (m.oil_sold_bbl + m.gas_sold_mcf / config.MCF_PER_BOE)
    m["revenue_per_bbl_oil_sold"] = m.revenue_usd / m.oil_sold_bbl
    m["operating_margin_usd"] = m.revenue_usd - m.opex_total_usd
    return m


def build_mart_equipment_summary(t) -> pd.DataFrame:
    e, m = t["dim_equipment"], t["fact_maintenance"]
    days = (pd.Timestamp(config.END_DATE) - pd.Timestamp(config.START_DATE)).days + 1
    period_h = days * 24.0
    corr = m[m.maintenance_type == "Corrective"]
    a = m.groupby("equipment_id").agg(maintenance_events=("maintenance_id", "size"), total_downtime_hours=("downtime_hours", "sum"),
                                      maintenance_cost_usd=("total_cost", "sum")).reset_index()
    b = corr.groupby("equipment_id").agg(failures=("maintenance_id", "size"), corrective_downtime_hours=("downtime_hours", "sum"),
                                         corrective_cost_usd=("total_cost", "sum")).reset_index()
    out = e.merge(a, on="equipment_id", how="left").merge(b, on="equipment_id", how="left")
    for c in ["maintenance_events", "total_downtime_hours", "maintenance_cost_usd", "failures", "corrective_downtime_hours", "corrective_cost_usd"]:
        out[c] = out[c].fillna(0)
    out["period_hours"] = period_h
    out["operating_hours"] = (period_h - out.total_downtime_hours).clip(lower=0)
    out["availability_pct"] = 100 * out.operating_hours / period_h
    out["mtbf_hours"] = np.where(out.failures > 0, out.operating_hours / out.failures.replace(0, np.nan), np.nan)
    out["mttr_hours"] = np.where(out.failures > 0, out.corrective_downtime_hours / out.failures.replace(0, np.nan), np.nan)
    out["failures_per_year"] = out.failures / (days / 365.25)
    out["equipment_age_years_at_end"] = (pd.Timestamp(config.END_DATE) - out.installation_date).dt.days / 365.25
    return out


def build_mart_equipment_monthly(t) -> pd.DataFrame:
    m = t["fact_maintenance"].copy(); m["month"] = m.date.dt.to_period("M").dt.to_timestamp()
    m["is_failure"] = (m.maintenance_type == "Corrective").astype(int)
    g = m.groupby(["equipment_id", "month"]).agg(failures=("is_failure", "sum"), downtime_hours=("downtime_hours", "sum"),
                                                 maintenance_cost_usd=("total_cost", "sum"), events=("maintenance_id", "size")).reset_index()
    return g.merge(t["dim_equipment"][["equipment_id", "equipment_type", "field_id", "criticality"]], on="equipment_id")


def build_mart_sensor_daily(t) -> pd.DataFrame:
    s = t["fact_sensor"].copy(); s["date"] = s.timestamp.dt.normalize()
    g = s.groupby(["equipment_id", "date"]).agg(
        temperature_c_mean=("temperature_c", "mean"), pressure_psi_mean=("pressure_psi", "mean"),
        vibration_mm_s_mean=("vibration_mm_s", "mean"), vibration_mm_s_max=("vibration_mm_s", "max"),
        flow_rate_mean=("flow_rate", "mean"), energy_kwh_sum=("energy_consumption_kwh", "sum"),
        operating_hours_sum=("operating_hours", "sum")).reset_index()
    return g


def build_mart_inventory(t):
    inv = t["fact_inventory"].copy()
    mat = t["dim_material"].set_index("material_id")
    g = inv.groupby(["material_id", "warehouse_id"]).agg(
        avg_closing_stock=("closing_stock", "mean"), total_consumption=("consumption", "sum"), total_receipts=("receipts", "sum"),
        stockout_days=("stockout_flag", "sum"), days=("date", "nunique"), avg_reorder_level=("reorder_level", "mean"),
        unit_cost=("unit_cost", "mean")).reset_index()
    g["stockout_rate_pct"] = 100 * g.stockout_days / g.days
    g["avg_inventory_value_usd"] = g.avg_closing_stock * g.unit_cost
    g["consumption_value_usd"] = g.total_consumption * g.unit_cost
    g["inventory_turnover"] = g.consumption_value_usd / g.avg_inventory_value_usd.replace(0, np.nan) / (g.days / 365.25)   # annualised
    g["days_of_inventory"] = g.avg_closing_stock / (g.total_consumption / g.days).replace(0, np.nan)
    g = g.merge(t["dim_material"][["material_id", "material_name", "material_category", "primary_supplier_id"]], on="material_id")
    return g


def build_mart_supplier_performance(t) -> pd.DataFrame:
    po = t["fact_purchase_order"]
    r = po[po.received_date.notna()].copy()
    r["actual_lead_days"] = (r.received_date - r.order_date).dt.days
    r["delay_days"] = (r.received_date - r.promised_date).dt.days
    r["on_time"] = (r.delay_days <= 0).astype(int)
    g = r.groupby("supplier_id").agg(pos_received=("po_id", "size"), on_time_pct=("on_time", "mean"), avg_quoted_lead_days=("quoted_lead_time_days", "mean"),
                                     avg_actual_lead_days=("actual_lead_days", "mean"), avg_delay_days=("delay_days", "mean"),
                                     po_value_usd=("unit_cost", lambda s: float((s * r.loc[s.index, "quantity"]).sum()))).reset_index()
    g["on_time_pct"] *= 100
    sk = t["fact_inventory"].groupby("supplier_id")["stockout_flag"].sum().rename("stockout_days_on_supplied_items")
    return g.merge(t["dim_supplier"], on="supplier_id").merge(sk, on="supplier_id", how="left")


def build_mart_hse_monthly(t, wd: pd.DataFrame) -> pd.DataFrame:
    h = t["fact_hse"].copy(); h["month"] = h.date.dt.to_period("M").dt.to_timestamp()
    h["recordable"] = h.incident_type.isin(["First Aid", "Injury"]).astype(int)
    g = h.groupby(["field_id", "month"]).agg(incidents=("incident_id", "size"), lost_time_incidents=("lost_time_flag", "sum"),
                                              days_lost=("days_lost", "sum"), recordable_incidents=("recordable", "sum")).reset_index()
    expo = wd.groupby(["field_id", "month"]).size().mul(config.EXPOSURE_HOURS_PER_ACTIVE_WELL_DAY).rename("exposure_hours").reset_index()
    idx = expo.merge(g, on=["field_id", "month"], how="left").fillna({"incidents": 0, "lost_time_incidents": 0, "days_lost": 0, "recordable_incidents": 0})
    idx["incident_rate_per_200k_h"] = idx.incidents * config.INCIDENT_RATE_BASE_HOURS / idx.exposure_hours
    idx["ltir_per_200k_h"] = idx.lost_time_incidents * config.INCIDENT_RATE_BASE_HOURS / idx.exposure_hours
    return idx


def build_all_marts(t) -> dict[str, pd.DataFrame]:
    wd = build_mart_well_daily(t)
    return {"mart_well_daily": wd, "mart_field_monthly": build_mart_field_monthly(t, wd),
            "mart_equipment_summary": build_mart_equipment_summary(t), "mart_equipment_monthly": build_mart_equipment_monthly(t),
            "mart_sensor_daily": build_mart_sensor_daily(t), "mart_inventory": build_mart_inventory(t),
            "mart_supplier_performance": build_mart_supplier_performance(t), "mart_hse_monthly": build_mart_hse_monthly(t, wd)}
