"""Cleaning functions: raw (defective) tables -> processed tables + quarantine + action log.

Design rules: never overwrite raw files; every fix is counted in the log; rows that
cannot be repaired defensibly are QUARANTINED (not silently dropped or guessed).
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from og_oip import config

DATE_FMTS = ["%Y-%m-%d", "%d-%b-%Y", "%Y/%m/%d", "%Y%m%d"]
TS_FMTS = ["%Y-%m-%d %H:%M:%S", "%d-%b-%Y %H:%M"]


def parse_dates(s: pd.Series, fmts=DATE_FMTS) -> pd.Series:
    s = s.astype(str).str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for f in fmts:
        m = out.isna()
        if not m.any():
            break
        out[m] = pd.to_datetime(s[m], format=f, errors="coerce")
    return out


def _q(df, mask, reason):
    q = df[mask].copy()
    q["quarantine_reason"] = reason
    return q


def _flag(flags: pd.Series, mask, name: str) -> pd.Series:
    add = np.where(mask, name, "")
    return np.where(flags == "", add, np.where(add == "", flags, flags + "|" + add))


def clean_production(raw, wells):
    log, quar = {"rows_in": len(raw)}, []
    d = raw.copy()
    d["well_id"] = d["well_id"].astype(str).str.strip().str.upper()
    log["well_id_normalised"] = int((raw["well_id"].astype(str) != d["well_id"]).sum())
    bad = ~d.well_id.isin(wells.well_id)
    quar.append(_q(d, bad, "unknown_well_id")); d = d[~bad].copy()
    d["date"] = parse_dates(d["date"])
    bad = d.date.isna()
    quar.append(_q(d, bad, "invalid_date")); d = d[~bad].copy()
    log["quarantined_invalid_date"] = int(bad.sum())
    m3 = d["oil_uom"].astype(str).str.lower().eq("m3")
    d.loc[m3, "oil_production_bbl"] *= config.BBL_PER_M3
    log["oil_m3_to_bbl_converted"] = int(m3.sum())
    d = d.drop(columns=["oil_uom"])
    n0 = len(d); d = d.drop_duplicates(["date", "well_id"], keep="first"); log["duplicates_removed"] = n0 - len(d)
    d = d.reset_index(drop=True)
    neg = d.oil_production_bbl < 0
    d.loc[neg, "oil_production_bbl"] = np.nan; log["negative_oil_set_missing"] = int(neg.sum())
    out = d.oil_production_bbl > 1.25 * d.potential_production_bbl
    d.loc[out, "oil_production_bbl"] = np.nan; log["outlier_oil_set_missing"] = int(out.sum())
    bad_dt = (d.downtime_hours > 24) | (d.downtime_hours < 0)
    d["downtime_hours"] = d.downtime_hours.clip(0, 24); log["downtime_clipped"] = int(bad_dt.sum())
    op_bad = (d.operating_hours - (24 - d.downtime_hours)).abs() > 0.01
    d["operating_hours"] = (24 - d.downtime_hours).round(2); log["operating_hours_recomputed"] = int(op_bad.sum())
    # oil imputation: potential x uptime x well-level median efficiency (documented, flagged)
    valid = d.oil_production_bbl.notna() & (d.potential_production_bbl > 0) & (d.operating_hours > 0)
    eff = (d.oil_production_bbl / (d.potential_production_bbl * d.operating_hours / 24)).where(valid)
    well_eff = eff.groupby(d.well_id).transform("median").fillna(0.97)
    miss = d.oil_production_bbl.isna()
    d.loc[miss, "oil_production_bbl"] = (d.potential_production_bbl * d.operating_hours / 24 * well_eff)[miss].round(1)
    log["oil_imputed"] = int(miss.sum())
    wc_missing = d.water_cut_pct.isna()
    log["water_cut_missing_before"] = int(wc_missing.sum())
    denom = (d.oil_production_bbl + d.water_production_bbl).replace(0, np.nan)
    recomputed = (100 * d.water_production_bbl / denom).fillna(0).round(2)
    d["water_cut_pct"] = d.water_cut_pct.where(~(wc_missing | miss), recomputed).round(2)
    d["_f_oil"], d["_f_dt"], d["_f_wc"] = miss, bad_dt, wc_missing
    d = d.sort_values(["well_id", "date"]).reset_index(drop=True)
    d["dq_flag"] = ""
    d["dq_flag"] = _flag(d["dq_flag"], d["_f_oil"], "oil_imputed")
    d["dq_flag"] = _flag(d["dq_flag"], d["_f_dt"], "downtime_clipped")
    d["dq_flag"] = _flag(d["dq_flag"], d["_f_wc"], "water_cut_recomputed")
    for c in ["pressure_psi", "temperature_c"]:
        m = d[c].isna()
        d[c] = d.groupby("well_id")[c].transform(lambda s: s.interpolate(limit=7, limit_direction="both"))
        d[c] = d[c].fillna(d.groupby("well_id")[c].transform("median"))
        d["dq_flag"] = _flag(d["dq_flag"], m, f"{c}_imputed")
        log[f"{c}_imputed"] = int(m.sum())
    cols = ["date", "well_id", "operating_hours", "downtime_hours", "oil_production_bbl", "gas_production_mcf",
            "water_production_bbl", "pressure_psi", "temperature_c", "water_cut_pct", "potential_production_bbl", "dq_flag"]
    d["date"] = d["date"].dt.date
    log["rows_out"] = len(d)
    q = pd.concat(quar) if quar else pd.DataFrame()
    log["rows_quarantined"] = len(q)
    return d[cols], q, log


def clean_sensor(raw, equipment):
    log = {"rows_in": len(raw)}
    d = raw.copy()
    d["timestamp"] = parse_dates(d["timestamp"], TS_FMTS)
    bad = d.timestamp.isna() | ~d.equipment_id.isin(equipment.equipment_id)
    q = _q(d, bad, "invalid_timestamp_or_equipment"); d = d[~bad].copy()
    n0 = len(d); d = d.drop_duplicates(["timestamp", "equipment_id"]); log["duplicates_removed"] = n0 - len(d)
    d = d.sort_values(["equipment_id", "timestamp"]).reset_index(drop=True)
    sp = (d.vibration_mm_s >= 100) | (d.vibration_mm_s < 0); d.loc[sp, "vibration_mm_s"] = np.nan
    st = (d.temperature_c <= -100); d.loc[st, "temperature_c"] = np.nan
    log["spikes_set_missing"] = int(sp.sum() + st.sum())
    d["dq_flag"] = ""
    for c in ["temperature_c", "pressure_psi", "vibration_mm_s", "flow_rate", "energy_consumption_kwh"]:
        m = d[c].isna()
        d[c] = d.groupby("equipment_id")[c].transform(lambda s: s.interpolate(limit=4, limit_direction="both"))
        d[c] = d[c].fillna(d.groupby("equipment_id")[c].transform("median"))
        d["dq_flag"] = _flag(d["dq_flag"], m, f"{c}_imputed")
        log[f"{c}_imputed"] = int(m.sum())
    log["rows_out"] = len(d); log["rows_quarantined"] = len(q)
    return d, q, log


MAINT_TYPE_MAP = {"corrective": "Corrective", "corr.": "Corrective", "preventive": "Preventive", "pm": "Preventive", "inspection": "Inspection"}


def clean_maintenance(raw, equipment):
    log = {"rows_in": len(raw)}
    d = raw.copy()
    mt = d.maintenance_type.astype(str).str.strip().str.lower().map(MAINT_TYPE_MAP)
    log["type_names_standardised"] = int((mt != d.maintenance_type).sum())
    d["maintenance_type"] = mt
    d["date"] = parse_dates(d["date"])
    d["failure_type"] = d.failure_type.astype(str).str.strip().replace({"nan": "None"})
    q = []
    bad = d.equipment_id.isna() | ~d.equipment_id.isin(equipment.equipment_id)
    q.append(_q(d, bad, "missing_or_unknown_equipment_id")); d = d[~bad].copy()
    bad = d.date.isna() | d.maintenance_type.isna()
    q.append(_q(d, bad, "invalid_date_or_type")); d = d[~bad].copy()
    n0 = len(d); d = d.drop_duplicates("maintenance_id", keep="first"); log["duplicate_ids_removed"] = n0 - len(d)
    key = ["equipment_id", "date", "maintenance_type", "failure_type", "downtime_hours", "material_cost", "contractor_cost"]
    n0 = len(d); d = d.drop_duplicates(key, keep="first"); log["business_duplicates_removed"] = n0 - len(d)
    for c in ["labor_cost", "material_cost", "contractor_cost"]:
        neg = d[c] < 0; d.loc[neg, c] = d.loc[neg, c].abs(); log[f"{c}_sign_corrected"] = int(neg.sum())
    tot = (d.labor_cost + d.material_cost + d.contractor_cost).round(2)
    log["total_cost_recomputed"] = int(((d.total_cost - tot).abs() > 0.02).sum())
    d["total_cost"] = tot
    d["date"] = d["date"].dt.date
    d = d.sort_values(["date", "maintenance_id"]).reset_index(drop=True)
    qq = pd.concat(q); log["rows_out"] = len(d); log["rows_quarantined"] = len(qq)
    return d, qq, log


def clean_inventory(raw, materials):
    log = {"rows_in": len(raw)}
    d = raw.copy()
    d["date"] = parse_dates(d["date"])
    bad = d.date.isna()
    q = _q(d, bad, "invalid_date"); d = d[~bad].copy(); log["quarantined_invalid_date"] = int(bad.sum())
    n0 = len(d); d = d.drop_duplicates(["date", "material_id", "warehouse_id"]); log["duplicates_removed"] = n0 - len(d)
    mat = materials.set_index("material_id")
    m = d.supplier_id.isna(); d.loc[m, "supplier_id"] = d.loc[m, "material_id"].map(mat["primary_supplier_id"]); log["supplier_id_filled_from_material"] = int(m.sum())
    m = d.unit_cost.isna(); d.loc[m, "unit_cost"] = d.loc[m, "material_id"].map(mat["unit_cost"]); log["unit_cost_filled_from_material"] = int(m.sum())
    neg = d.consumption < 0; d.loc[neg, "consumption"] = d.loc[neg, "consumption"].abs(); log["negative_consumption_sign_corrected"] = int(neg.sum())
    cl = (d.opening_stock + d.receipts - d.consumption)
    log["closing_stock_recomputed"] = int(((d.closing_stock - cl).abs() > 1e-6).sum())
    d["closing_stock"] = cl
    d["date"] = d["date"].dt.date
    d = d.sort_values(["date", "warehouse_id", "material_id"]).reset_index(drop=True)
    log["rows_out"] = len(d); log["rows_quarantined"] = len(q)
    return d, q, log


def _norm_name(n: str) -> str:
    n = n.lower().replace("&", " and ")
    n = re.sub(r"\b(inc|ltd|co)\b\.?", "", n)
    return re.sub(r"[^a-z0-9]+", "", n)


def clean_supplier(raw):
    log = {"rows_in": len(raw)}
    d = raw.copy()
    d["_k"] = d.supplier_name.map(_norm_name)
    def pick(g):
        cands = sorted(g.supplier_name.unique(), key=lambda x: (x.isupper(), "inc" in x.lower(), " and " in x.lower(), len(x)))
        return cands[0]
    canon = d.groupby("supplier_id").apply(pick, include_groups=False)
    log["name_variants_standardised"] = int((d.supplier_name != d.supplier_id.map(canon)).sum())
    d["supplier_name"] = d.supplier_id.map(canon)
    n0 = len(d); d = d.drop_duplicates("supplier_id").drop(columns="_k"); log["duplicate_suppliers_removed"] = n0 - len(d)
    log["rows_out"] = len(d); log["rows_quarantined"] = 0
    return d.reset_index(drop=True), pd.DataFrame(), log


def clean_sales(raw, fields):
    log = {"rows_in": len(raw)}
    d = raw.copy()
    d["date"] = parse_dates(d["date"])
    bad = d.date.isna() | ~d.field_id.isin(fields.field_id)
    q = _q(d, bad, "invalid_date_or_field"); d = d[~bad].copy()
    n0 = len(d); d = d.drop_duplicates(["date", "field_id"]); log["duplicates_removed"] = n0 - len(d)
    mm = d.gas_uom.astype(str).str.lower().eq("mmcf"); d.loc[mm, "gas_volume_mcf"] *= 1000; log["gas_mmcf_to_mcf_converted"] = int(mm.sum())
    d = d.drop(columns=["gas_uom"])
    d["_m"] = pd.to_datetime(d["date"]).dt.to_period("M")
    m = d.oil_price_usd.isna()
    d.loc[m, "oil_price_usd"] = d.groupby(["field_id", "_m"])["oil_price_usd"].transform("median")[m].round(2); log["oil_price_filled_month_median"] = int(m.sum())
    d = d.drop(columns="_m")
    rev = (d.oil_volume_bbl * d.oil_price_usd + d.gas_volume_mcf * d.gas_price_usd).round(2)
    log["revenue_recomputed"] = int(((d.revenue_usd - rev).abs() > 1).sum() + d.revenue_usd.isna().sum())
    d["revenue_usd"] = rev
    d["date"] = d["date"].dt.date
    d = d.sort_values(["date", "field_id"]).reset_index(drop=True)
    log["rows_out"] = len(d); log["rows_quarantined"] = len(q)
    return d, q, log


COST_MAP = {"energy": "Energy", "prod.": "Production", "production": "Production", "labour": "Labor", "labor": "Labor",
            "maint": "Maintenance", "maintenance": "Maintenance", "transport": "Transportation", "transportation": "Transportation",
            "utilities": "Utilities", "other": "Other"}


def clean_operating_cost(raw, fields):
    log = {"rows_in": len(raw)}
    d = raw.copy()
    cat = d.cost_category.astype(str).str.strip().str.lower().map(COST_MAP)
    log["category_names_standardised"] = int((cat != d.cost_category).sum()); d["cost_category"] = cat
    d["date"] = parse_dates(d["date"])
    bad = d.date.isna() | d.cost_category.isna() | ~d.field_id.isin(fields.field_id)
    q = _q(d, bad, "invalid_date_category_or_field"); d = d[~bad].copy()
    n0 = len(d); d = d.drop_duplicates(["date", "field_id", "cost_category"]); log["duplicates_removed"] = n0 - len(d)
    neg = d.cost_amount_usd < 0; d.loc[neg, "cost_amount_usd"] = d.loc[neg, "cost_amount_usd"].abs(); log["negative_amount_sign_corrected"] = int(neg.sum())
    d["date"] = d["date"].dt.date
    d = d.sort_values(["date", "field_id", "cost_category"]).reset_index(drop=True)
    log["rows_out"] = len(d); log["rows_quarantined"] = len(q)
    return d, q, log


def clean_hse(raw, fields):
    log = {"rows_in": len(raw)}
    d = raw.copy()
    d["date"] = parse_dates(d["date"])
    sev = d.severity.astype(str).str.strip().str.title(); log["severity_standardised"] = int((sev != d.severity).sum()); d["severity"] = sev
    f = d.field_id.astype(str).str.strip().str.upper().str.replace(r"^FIELD-?(\d{3})$", r"FIELD-\1", regex=True)
    log["field_id_standardised"] = int((f != d.field_id).sum()); d["field_id"] = f
    bad = d.date.isna() | ~d.field_id.isin(fields.field_id)
    q = _q(d, bad, "invalid_date_or_field"); d = d[~bad].copy()
    n0 = len(d); d = d.drop_duplicates("incident_id"); log["duplicates_removed"] = n0 - len(d)
    d["date"] = d["date"].dt.date
    d = d.sort_values(["date", "incident_id"]).reset_index(drop=True)
    log["rows_out"] = len(d); log["rows_quarantined"] = len(q)
    return d, q, log


def clean_all(raw: dict[str, pd.DataFrame]):
    """Returns (processed dict, quarantine dict, log dict)."""
    out, quar, logs = {}, {}, {}
    supp, qs, lg = clean_supplier(raw["dim_supplier"]); out["dim_supplier"] = supp; quar["dim_supplier"] = qs; logs["dim_supplier"] = lg
    for t in ["dim_date", "dim_field", "dim_well", "dim_equipment", "dim_material", "dim_warehouse", "bridge_equipment_well",
              "fact_maintenance_material", "fact_purchase_order"]:
        out[t] = raw[t].copy(); logs[t] = {"rows_in": len(raw[t]), "rows_out": len(raw[t]), "rows_quarantined": 0}
    fields, wells, eq, mats = out["dim_field"], out["dim_well"], out["dim_equipment"], out["dim_material"]
    for t, fn, arg in [("fact_production", clean_production, wells), ("fact_sensor", clean_sensor, eq),
                       ("fact_maintenance", clean_maintenance, eq), ("fact_inventory", clean_inventory, mats),
                       ("fact_sales", clean_sales, fields), ("fact_operating_cost", clean_operating_cost, fields),
                       ("fact_hse", clean_hse, fields)]:
        out[t], quar[t], logs[t] = fn(raw[t], arg)
    # referential clean-up of dependent table: maintenance_material rows must reference surviving maintenance ids
    mm = out["fact_maintenance_material"]
    keep = mm.maintenance_id.isin(out["fact_maintenance"].maintenance_id)
    logs["fact_maintenance_material"]["rows_quarantined"] = int((~keep).sum())
    quar["fact_maintenance_material"] = mm[~keep].assign(quarantine_reason="parent_maintenance_record_quarantined")
    out["fact_maintenance_material"] = mm[keep].reset_index(drop=True)
    logs["fact_maintenance_material"]["rows_out"] = int(keep.sum())
    return out, quar, logs
