"""Reusable data-quality checks. Every function returns a list of result dicts."""
from __future__ import annotations

import numpy as np
import pandas as pd

from og_oip.cleaning.cleaners import parse_dates, TS_FMTS


def _res(table, check, column, failed, total, detail="", severity="ERROR"):
    return {"table": table, "check": check, "column": column, "failed_rows": int(failed), "total_rows": int(total),
            "status": "PASS" if failed == 0 else ("WARN" if severity == "WARN" else "FAIL"), "detail": detail}


def null_check(df, table, cols, severity="ERROR"):
    return [_res(table, "null_check", c, df[c].isna().sum(), len(df), severity=severity) for c in cols if c in df]


def pk_check(df, table, key):
    return [_res(table, "primary_key_uniqueness", "+".join(key), df.duplicated(key, keep="first").sum(), len(df))]


def duplicate_row_check(df, table):
    return [_res(table, "duplicate_rows", "*", df.duplicated(keep="first").sum(), len(df))]


def range_check(df, table, col, lo=None, hi=None):
    v = pd.to_numeric(df[col], errors="coerce")
    bad = pd.Series(False, index=df.index)
    if lo is not None:
        bad |= v < lo
    if hi is not None:
        bad |= v > hi
    return [_res(table, "range_check", col, bad.sum(), len(df), f"allowed [{lo}, {hi}]")]


def numeric_validity(df, table, col):
    v = pd.to_numeric(df[col], errors="coerce")
    bad = v.isna() & df[col].notna()
    return [_res(table, "numeric_validity", col, bad.sum() + np.isinf(v.dropna()).sum(), len(df))]


def date_validity(df, table, col, lo="2000-01-01", hi="2030-12-31", fmts=None):
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        d = df[col]
    else:
        d = parse_dates(df[col].astype(str), fmts) if fmts else parse_dates(df[col].astype(str))
    bad = d.isna() | (d < pd.Timestamp(lo)) | (d > pd.Timestamp(hi))
    return [_res(table, "date_validity", col, bad.sum(), len(df), f"parsable and within [{lo}, {hi}]")]


def date_format_consistency(df, table, col):
    s = df[col].astype(str).str.strip()
    iso = s.str.match(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$")
    return [_res(table, "date_format_consistency", col, (~iso).sum(), len(df), "non-ISO formatted values")]


def referential_check(child, table, col, parent, pcol):
    bad = child[col].notna() & ~child[col].isin(parent[pcol])
    return [_res(table, "referential_integrity", col, bad.sum(), len(child), f"-> {pcol} in parent")]


def domain_check(df, table, col, allowed):
    bad = df[col].notna() & ~df[col].astype(str).isin(allowed)
    return [_res(table, "domain_check", col, bad.sum(), len(df), f"allowed: {sorted(allowed)}")]


def logic_check(table, name, mask_bad, total, detail=""):
    return [_res(table, name, "-", int(mask_bad.sum()), total, detail)]


RANGES = {
    "fact_production": {"operating_hours": (0, 24), "downtime_hours": (0, 24), "oil_production_bbl": (0, 10000),
                        "gas_production_mcf": (0, 20000), "water_production_bbl": (0, 20000), "pressure_psi": (0, 10000),
                        "temperature_c": (-50, 200), "water_cut_pct": (0, 100), "potential_production_bbl": (0, 10000)},
    "fact_sensor": {"temperature_c": (-50, 300), "pressure_psi": (0, 5000), "vibration_mm_s": (0, 50), "flow_rate": (0, 5000),
                    "energy_consumption_kwh": (0, 50000), "operating_hours": (0, 12)},
    "fact_maintenance": {"downtime_hours": (0, 500), "labor_cost": (0, None), "material_cost": (0, None),
                         "contractor_cost": (0, None), "total_cost": (0, None)},
    "fact_inventory": {"opening_stock": (0, None), "receipts": (0, None), "consumption": (0, None), "closing_stock": (0, None),
                       "unit_cost": (0.01, None), "stockout_flag": (0, 1)},
    "fact_sales": {"oil_volume_bbl": (0, None), "gas_volume_mcf": (0, None), "oil_price_usd": (0, 300), "gas_price_usd": (0, 50),
                   "revenue_usd": (0, None)},
    "fact_operating_cost": {"cost_amount_usd": (0, None)},
    "fact_hse": {"days_lost": (0, 365), "lost_time_flag": (0, 1)},
}
PKS = {"dim_field": ["field_id"], "dim_well": ["well_id"], "dim_equipment": ["equipment_id"], "dim_supplier": ["supplier_id"],
       "dim_material": ["material_id"], "dim_warehouse": ["warehouse_id"], "dim_date": ["date_key"],
       "fact_production": ["date", "well_id"], "fact_sensor": ["timestamp", "equipment_id"], "fact_maintenance": ["maintenance_id"],
       "fact_maintenance_material": ["maintenance_id", "material_id"], "fact_sales": ["date", "field_id"],
       "fact_operating_cost": ["date", "field_id", "cost_category"], "fact_inventory": ["date", "material_id", "warehouse_id"],
       "fact_purchase_order": ["po_id"], "fact_hse": ["incident_id"], "bridge_equipment_well": ["equipment_id", "well_id"]}
FKS = [("dim_well", "field_id", "dim_field", "field_id"), ("dim_well", "primary_equipment_id", "dim_equipment", "equipment_id"),
       ("dim_equipment", "field_id", "dim_field", "field_id"), ("dim_material", "primary_supplier_id", "dim_supplier", "supplier_id"),
       ("dim_warehouse", "field_id", "dim_field", "field_id"),
       ("bridge_equipment_well", "equipment_id", "dim_equipment", "equipment_id"), ("bridge_equipment_well", "well_id", "dim_well", "well_id"),
       ("fact_production", "well_id", "dim_well", "well_id"), ("fact_sensor", "equipment_id", "dim_equipment", "equipment_id"),
       ("fact_maintenance", "equipment_id", "dim_equipment", "equipment_id"),
       ("fact_maintenance_material", "maintenance_id", "fact_maintenance", "maintenance_id"),
       ("fact_maintenance_material", "material_id", "dim_material", "material_id"),
       ("fact_maintenance_material", "warehouse_id", "dim_warehouse", "warehouse_id"),
       ("fact_sales", "field_id", "dim_field", "field_id"), ("fact_operating_cost", "field_id", "dim_field", "field_id"),
       ("fact_inventory", "material_id", "dim_material", "material_id"), ("fact_inventory", "supplier_id", "dim_supplier", "supplier_id"),
       ("fact_inventory", "warehouse_id", "dim_warehouse", "warehouse_id"),
       ("fact_purchase_order", "material_id", "dim_material", "material_id"), ("fact_purchase_order", "supplier_id", "dim_supplier", "supplier_id"),
       ("fact_purchase_order", "warehouse_id", "dim_warehouse", "warehouse_id"), ("fact_hse", "field_id", "dim_field", "field_id")]
DATE_COLS = {"fact_production": "date", "fact_maintenance": "date", "fact_sales": "date", "fact_operating_cost": "date",
             "fact_inventory": "date", "fact_hse": "date"}
NOT_NULL = {"fact_production": ["date", "well_id", "oil_production_bbl", "pressure_psi", "temperature_c", "water_cut_pct", "potential_production_bbl"],
            "fact_sensor": ["timestamp", "equipment_id", "temperature_c", "pressure_psi", "vibration_mm_s", "flow_rate", "energy_consumption_kwh"],
            "fact_maintenance": ["maintenance_id", "equipment_id", "date", "maintenance_type", "total_cost"],
            "fact_inventory": ["date", "material_id", "supplier_id", "warehouse_id", "unit_cost"],
            "fact_sales": ["date", "field_id", "oil_price_usd", "revenue_usd"], "fact_operating_cost": ["date", "field_id", "cost_category", "cost_amount_usd"],
            "fact_hse": ["incident_id", "date", "field_id", "severity"]}
DOMAINS = {("fact_maintenance", "maintenance_type"): {"Corrective", "Preventive", "Inspection"},
           ("fact_operating_cost", "cost_category"): {"Production", "Energy", "Labor", "Maintenance", "Transportation", "Utilities", "Other"},
           ("fact_hse", "severity"): {"Low", "Medium", "High", "Critical"},
           ("fact_maintenance", "priority"): {"Critical", "High", "Medium", "Low"}}


def run_all_checks(t: dict[str, pd.DataFrame], stage: str) -> pd.DataFrame:
    """stage: 'raw' or 'processed'. Returns a tidy DataFrame of check results."""
    res = []
    for name, key in PKS.items():
        if name in t:
            res += pk_check(t[name], name, key)
    for name in [n for n in t if n.startswith("fact_")]:
        res += duplicate_row_check(t[name], name)
    for name, cols in NOT_NULL.items():
        res += null_check(t[name], name, cols)
    for name, r in RANGES.items():
        for col, (lo, hi) in r.items():
            res += numeric_validity(t[name], name, col) + range_check(t[name], name, col, lo, hi)
    for child, col, parent, pcol in FKS:
        if child in t and parent in t:
            res += referential_check(t[child], child, col, t[parent], pcol)
    for name, col in DATE_COLS.items():
        res += date_validity(t[name], name, col) + date_format_consistency(t[name], name, col)
    res += date_validity(t["fact_sensor"], "fact_sensor", "timestamp", fmts=TS_FMTS) + date_format_consistency(t["fact_sensor"], "fact_sensor", "timestamp")
    for (name, col), allowed in DOMAINS.items():
        res += domain_check(t[name], name, col, allowed)
    # unit consistency
    p = t["fact_production"]
    if "oil_uom" in p:
        res += [_res("fact_production", "unit_consistency", "oil_uom", (p.oil_uom.astype(str).str.lower() != "bbl").sum(), len(p), "oil must be reported in bbl")]
    else:
        res += logic_check("fact_production", "unit_consistency_oil_vs_potential", p.oil_production_bbl > 1.25 * p.potential_production_bbl, len(p), "oil > 1.25 x potential suggests unit/scale error")
    s = t["fact_sales"]
    if "gas_uom" in s:
        res += [_res("fact_sales", "unit_consistency", "gas_uom", (s.gas_uom.astype(str).str.lower() != "mcf").sum(), len(s), "gas must be reported in mcf")]
    # logic checks
    res += logic_check("fact_production", "operating_plus_downtime_eq_24", (p.operating_hours + p.downtime_hours - 24).abs() > 0.02, len(p))
    wc = (100 * p.water_production_bbl / (p.oil_production_bbl + p.water_production_bbl).replace(0, np.nan)).fillna(0)
    res += logic_check("fact_production", "water_cut_consistent_with_volumes", (wc - p.water_cut_pct).abs() > 1.0, len(p), "tolerance 1 percentage point")
    m = t["fact_maintenance"]
    res += logic_check("fact_maintenance", "total_cost_eq_components", (m.labor_cost + m.material_cost + m.contractor_cost - m.total_cost).abs() > 0.02, len(m))
    i = t["fact_inventory"]
    res += logic_check("fact_inventory", "closing_eq_open_plus_receipts_minus_consumption", (i.opening_stock + i.receipts - i.consumption - i.closing_stock).abs() > 1e-6, len(i))
    res += logic_check("fact_sales", "revenue_eq_volume_x_price", (s.oil_volume_bbl * s.oil_price_usd + s.gas_volume_mcf * s.gas_price_usd - s.revenue_usd).abs() > 1.0, len(s), "tolerance $1")
    h = t["fact_hse"]
    res += logic_check("fact_hse", "lost_time_flag_consistent_with_days_lost", (h.lost_time_flag == 0) & (h.days_lost > 0), len(h))
    sup = t["dim_supplier"]
    res += [_res("dim_supplier", "supplier_name_uniqueness_per_id", "supplier_name", sup.duplicated("supplier_id").sum() + (sup.groupby("supplier_id")["supplier_name"].transform("nunique") > 1).sum(), len(sup), "one canonical name per supplier_id")]
    out = pd.DataFrame(res)
    out.insert(0, "stage", stage)
    return out
