"""Inject realistic data-quality defects into COPIES of the clean synthetic tables.

The clean tables are never modified. The injected-defect log is saved so the
cleaning pipeline can be evaluated against ground truth.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from og_oip import config

DATE_FORMATS = [("%Y-%m-%d", 0.85), ("%d-%b-%Y", 0.06), ("%Y/%m/%d", 0.05), ("%Y%m%d", 0.04)]


def _fmt_dates(rng, s: pd.Series, log: dict, key: str, invalid_rate: float = 0.0005) -> pd.Series:
    d = pd.to_datetime(s)
    fmts = rng.choice([f for f, _ in DATE_FORMATS], size=len(d), p=[p for _, p in DATE_FORMATS])
    out = pd.Series(index=d.index, dtype=object)
    for f in set(fmts):
        m = fmts == f
        out[m] = d[m].dt.strftime(str(f))
    inv = rng.random(len(d)) < invalid_rate
    out[inv] = "2023-13-45"
    log[key + "_nonstandard_date_format"] = int((fmts != "%Y-%m-%d").sum())
    log[key + "_invalid_date"] = int(inv.sum())
    return out


def _dup(rng, df, rate, log, key):
    idx = rng.choice(len(df), size=int(len(df) * rate), replace=False)
    log[key + "_exact_duplicates"] = int(len(idx))
    return pd.concat([df, df.iloc[idx]], ignore_index=True)


def _nan(rng, df, col, rate, log, key):
    idx = rng.choice(len(df), size=int(len(df) * rate), replace=False)
    df.loc[df.index[idx], col] = np.nan
    log[f"{key}_missing_{col}"] = int(len(idx))


def raw_production(rng, df, log):
    d = df.copy()
    d["date"] = _fmt_dates(rng, d["date"], log, "production")
    d["oil_uom"] = "bbl"
    m = rng.random(len(d)) < 0.004
    d.loc[m, "oil_production_bbl"] = (d.loc[m, "oil_production_bbl"] / config.BBL_PER_M3).round(2)
    d.loc[m, "oil_uom"] = "m3"
    log["production_oil_reported_in_m3"] = int(m.sum())
    for c, r in [("pressure_psi", .005), ("temperature_c", .005), ("water_cut_pct", .003), ("oil_production_bbl", .001)]:
        _nan(rng, d, c, r, log, "production")
    k = rng.choice(len(d), size=int(len(d) * .001), replace=False)
    d.loc[d.index[k], "oil_production_bbl"] *= 10; log["production_oil_outliers_x10"] = int(len(k))
    k = rng.choice(len(d), size=int(len(d) * .0005), replace=False)
    d.loc[d.index[k], "oil_production_bbl"] *= -1; log["production_negative_oil"] = int(len(k))
    k = rng.choice(len(d), size=int(len(d) * .0005), replace=False)
    d.loc[d.index[k], "downtime_hours"] = 24 + rng.uniform(1, 10, len(k)); log["production_downtime_gt_24"] = int(len(k))
    k = rng.choice(len(d), size=int(len(d) * .003), replace=False)
    d.loc[d.index[k], "well_id"] = d.loc[d.index[k], "well_id"].str.lower().map(lambda x: " " + x + " "); log["production_well_id_naming"] = int(len(k))
    return _dup(rng, d, .003, log, "production")


def raw_sensor(rng, df, log):
    d = df.copy()
    ts = d["timestamp"]
    alt = rng.random(len(d)) < 0.02
    d["timestamp"] = ts.dt.strftime("%Y-%m-%d %H:%M:%S")
    d.loc[alt, "timestamp"] = ts[alt].dt.strftime("%d-%b-%Y %H:%M")
    log["sensor_nonstandard_timestamp"] = int(alt.sum())
    for c in ["temperature_c", "pressure_psi", "vibration_mm_s", "flow_rate", "energy_consumption_kwh"]:
        _nan(rng, d, c, .004, log, "sensor")
    k = rng.choice(len(d), size=int(len(d) * .0005), replace=False)
    d.loc[d.index[k], "vibration_mm_s"] = 999.0; log["sensor_vibration_spikes_999"] = int(len(k))
    k = rng.choice(len(d), size=int(len(d) * .0003), replace=False)
    d.loc[d.index[k], "temperature_c"] = -999.0; log["sensor_temperature_spikes_minus999"] = int(len(k))
    return _dup(rng, d, .001, log, "sensor")


TYPE_VARIANTS = {"Corrective": ["corrective", "CORRECTIVE", "Corr.", " Corrective "], "Preventive": ["preventive ", "PM", "PREVENTIVE"],
                 "Inspection": ["inspection", "INSPECTION"]}


def raw_maintenance(rng, df, log):
    d = df.copy()
    d["date"] = _fmt_dates(rng, d["date"], log, "maintenance")
    m = rng.random(len(d)) < 0.08
    d.loc[m, "maintenance_type"] = [str(rng.choice(TYPE_VARIANTS[t])) for t in d.loc[m, "maintenance_type"]]
    log["maintenance_type_naming_variants"] = int(m.sum())
    k = rng.choice(len(d), size=int(len(d) * .007), replace=False)
    d.loc[d.index[k], "equipment_id"] = np.nan; log["maintenance_missing_equipment_id"] = int(len(k))
    k = rng.choice(len(d), size=int(len(d) * .003), replace=False)
    d.loc[d.index[k], "labor_cost"] *= -1; log["maintenance_negative_labor_cost"] = int(len(k))
    k = rng.choice(len(d), size=int(len(d) * .01), replace=False)
    d.loc[d.index[k], "total_cost"] = (d.loc[d.index[k], "total_cost"] * rng.uniform(0.8, 1.2, len(k))).round(2); log["maintenance_total_cost_mismatch"] = int(len(k))
    dup_id = _dup(rng, d, .01, log, "maintenance")           # same maintenance_id twice
    k = rng.choice(len(d), size=int(len(d) * .01), replace=False)
    biz = d.iloc[k].copy()
    biz["maintenance_id"] = [f"MNT-D{i:05d}" for i in range(len(biz))]
    log["maintenance_business_duplicates_new_id"] = int(len(biz))
    return pd.concat([dup_id, biz], ignore_index=True)


def raw_inventory(rng, df, log):
    d = df.copy()
    d["date"] = _fmt_dates(rng, d["date"], log, "inventory")
    _nan(rng, d, "supplier_id", .01, log, "inventory")
    _nan(rng, d, "unit_cost", .005, log, "inventory")
    k = rng.choice(len(d), size=int(len(d) * .0003), replace=False)
    d.loc[d.index[k], "consumption"] *= -1; log["inventory_negative_consumption"] = int((d.loc[d.index[k], "consumption"] != 0).sum())
    k = rng.choice(len(d), size=int(len(d) * .001), replace=False)
    d.loc[d.index[k], "closing_stock"] += rng.integers(1, 20, len(k)); log["inventory_closing_stock_mismatch"] = int(len(k))
    return _dup(rng, d, .0005, log, "inventory")


def raw_supplier(rng, df, log):
    d = df.copy()
    extra = []
    for r in d.sample(6, random_state=int(rng.integers(0, 1e6))).itertuples():
        v = rng.choice(["upper", "inc", "and"])
        name = r.supplier_name.upper() if v == "upper" else (r.supplier_name + " Inc." if v == "inc" else r.supplier_name.replace("&", "and"))
        row = d[d.supplier_id == r.supplier_id].iloc[0].copy(); row["supplier_name"] = name
        extra.append(row)
    log["supplier_name_variant_rows"] = len(extra)
    return pd.concat([d, pd.DataFrame(extra)], ignore_index=True)


def raw_sales(rng, df, log):
    d = df.copy()
    d["date"] = _fmt_dates(rng, d["date"], log, "sales")
    d["gas_uom"] = "mcf"
    m = rng.random(len(d)) < 0.003
    d.loc[m, "gas_volume_mcf"] = (d.loc[m, "gas_volume_mcf"] / 1000).round(4); d.loc[m, "gas_uom"] = "mmcf"
    log["sales_gas_reported_in_mmcf"] = int(m.sum())
    _nan(rng, d, "oil_price_usd", .003, log, "sales")
    _nan(rng, d, "revenue_usd", .003, log, "sales")
    return _dup(rng, d, .002, log, "sales")


COST_VARIANTS = {"Energy": ["energy ", "ENERGY"], "Production": ["Prod.", "production"], "Labor": ["labour", "LABOR"],
                 "Maintenance": ["maint", "MAINTENANCE"], "Transportation": ["transport"], "Utilities": ["utilities "], "Other": ["other"]}


def raw_operating_cost(rng, df, log):
    d = df.copy()
    d["date"] = _fmt_dates(rng, d["date"], log, "opcost")
    m = rng.random(len(d)) < 0.02
    d.loc[m, "cost_category"] = [str(rng.choice(COST_VARIANTS[c])) for c in d.loc[m, "cost_category"]]
    log["opcost_category_naming_variants"] = int(m.sum())
    k = rng.choice(len(d), size=int(len(d) * .0005), replace=False)
    d.loc[d.index[k], "cost_amount_usd"] *= -1; log["opcost_negative_amount"] = int(len(k))
    return _dup(rng, d, .001, log, "opcost")


def raw_hse(rng, df, log):
    d = df.copy()
    d["date"] = _fmt_dates(rng, d["date"], log, "hse", invalid_rate=0.0)
    m = rng.random(len(d)) < 0.1
    d.loc[m, "severity"] = [str(rng.choice([s.upper(), " " + s.lower()])) for s in d.loc[m, "severity"]]
    log["hse_severity_case_variants"] = int(m.sum())
    m = rng.random(len(d)) < 0.08
    d.loc[m, "field_id"] = [str(rng.choice([f.replace("FIELD-", "Field-"), f.replace("-", "")])) for f in d.loc[m, "field_id"]]
    log["hse_field_id_variants"] = int(m.sum())
    return _dup(rng, d, .01, log, "hse")


def build_raw(tables: dict[str, pd.DataFrame], seed: int = config.RANDOM_SEED):
    rng = np.random.default_rng(seed + 1)
    log: dict = {}
    raw = {k: v.copy() for k, v in tables.items() if not k.startswith("_")}
    raw["fact_production"] = raw_production(rng, tables["fact_production"], log)
    raw["fact_sensor"] = raw_sensor(rng, tables["fact_sensor"], log)
    raw["fact_maintenance"] = raw_maintenance(rng, tables["fact_maintenance"], log)
    raw["fact_inventory"] = raw_inventory(rng, tables["fact_inventory"], log)
    raw["dim_supplier"] = raw_supplier(rng, tables["dim_supplier"], log)
    raw["fact_sales"] = raw_sales(rng, tables["fact_sales"], log)
    raw["fact_operating_cost"] = raw_operating_cost(rng, tables["fact_operating_cost"], log)
    raw["fact_hse"] = raw_hse(rng, tables["fact_hse"], log)
    return raw, log
