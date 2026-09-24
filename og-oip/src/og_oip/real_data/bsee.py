"""REAL-DATA CASE STUDY 2: BSEE OGOR-A monthly well/completion production (user-supplied delimited files).

NOT part of PetroNexa. Files have NO header row. Column names below follow the layout of the BSEE OGOR-A delimited
file as understood by the author; the three volume columns were checked ONLY by magnitude/behaviour (oil ~ bbl, gas ~ mcf,
water ~ bbl) - verify against the official BSEE data dictionary before publishing conclusions. Codes (product/status) are
not decoded here. OGOR-B and OGOR-C files were supplied but are not used.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from og_oip import config

COLS = ["lease_number", "completion_name", "production_month", "days_on_production", "product_code", "oil_bbl", "gas_mcf", "water_bbl",
        "api_well_number", "well_status_code", "area_block", "operator_number", "operator_name", "field_name_code", "injection_volume",
        "production_interval_code", "first_production_date", "unit_agreement_number", "unit_allocation_suffix"]
FILES = ["ogora2025delimit.txt", "ogoradelimit.txt"]


def load(base=config.REAL_DIR) -> pd.DataFrame:
    frames = []
    for f in FILES:
        d = pd.read_csv(base / f, header=None, names=COLS, dtype=str, keep_default_na=False, encoding="latin-1")
        d["source_file"] = f
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    for c in ["lease_number", "completion_name", "area_block", "operator_name", "well_status_code", "product_code"]:
        d[c] = d[c].str.strip()
    for c in ["days_on_production", "oil_bbl", "gas_mcf", "water_bbl", "injection_volume"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["month"] = pd.to_datetime(d.production_month.str.strip(), format="%Y%m", errors="coerce")
    d["area_prefix"] = d.area_block.str.split().str[0]
    return d


def data_quality(d: pd.DataFrame) -> pd.DataFrame:
    key = ["lease_number", "completion_name", "production_month", "api_well_number", "production_interval_code"]
    rows = [("rows", len(d)), ("distinct months", d.month.nunique()), ("unparsable month", int(d.month.isna().sum())),
            ("non-numeric oil/gas/water values", int(d[["oil_bbl", "gas_mcf", "water_bbl"]].isna().sum().sum())),
            ("negative oil/gas/water values", int((d[["oil_bbl", "gas_mcf", "water_bbl"]] < 0).sum().sum())),
            ("days_on_production > 31", int((d.days_on_production > 31).sum())),
            ("rows repeated on (lease, completion, month, API, interval)", int(d.duplicated(key).sum())),
            ("rows with all three volumes = 0", int(((d.oil_bbl == 0) & (d.gas_mcf == 0) & (d.water_bbl == 0)).sum())),
            ("rows with volumes > 0 but days_on_production == 0", int(((d.days_on_production == 0) & ((d.oil_bbl > 0) | (d.gas_mcf > 0))).sum())),
            ("rows with days_on_production > 0 but all volumes = 0", int(((d.days_on_production > 0) & (d.oil_bbl == 0) & (d.gas_mcf == 0) & (d.water_bbl == 0)).sum()))]
    return pd.DataFrame(rows, columns=["check", "value"])


def analyse(d: pd.DataFrame) -> dict:
    out = {"data_quality": data_quality(d)}
    m = d.groupby("month").agg(oil_bbl=("oil_bbl", "sum"), gas_mcf=("gas_mcf", "sum"), water_bbl=("water_bbl", "sum"),
                                completions=("completion_name", "size"), operators=("operator_number", "nunique"),
                                leases=("lease_number", "nunique")).reset_index()
    m["water_to_oil_ratio"] = m.water_bbl / m.oil_bbl.replace(0, np.nan)
    m["gas_to_oil_mcf_per_bbl"] = m.gas_mcf / m.oil_bbl.replace(0, np.nan)
    m["oil_bbl_per_day_calendar"] = m.oil_bbl / m.month.dt.days_in_month
    out["monthly"] = m
    op = d.groupby(["operator_number", "operator_name"]).agg(oil_bbl=("oil_bbl", "sum"), gas_mcf=("gas_mcf", "sum"), water_bbl=("water_bbl", "sum"),
                                                              completion_months=("completion_name", "size"), leases=("lease_number", "nunique")).reset_index()
    op["oil_share_pct"] = 100 * op.oil_bbl / op.oil_bbl.sum(); op["water_to_oil_ratio"] = op.water_bbl / op.oil_bbl.replace(0, np.nan)
    op = op.sort_values("oil_bbl", ascending=False); op["cum_oil_share_pct"] = op.oil_share_pct.cumsum()
    out["operators"] = op
    s = op.oil_share_pct / 100
    out["concentration"] = pd.DataFrame([{"operators": len(op), "top5_oil_share_pct": float(op.oil_share_pct.head(5).sum()), "top10_oil_share_pct": float(op.oil_share_pct.head(10).sum()),
                                          "hhi_oil (0-10000)": float((s ** 2).sum() * 10000)}])
    a = d.groupby("area_prefix").agg(oil_bbl=("oil_bbl", "sum"), gas_mcf=("gas_mcf", "sum"), water_bbl=("water_bbl", "sum"), completion_months=("completion_name", "size")).reset_index()
    a["oil_share_pct"] = 100 * a.oil_bbl / a.oil_bbl.sum(); out["areas"] = a.sort_values("oil_bbl", ascending=False)
    d2 = d.copy(); d2["dop_bucket"] = pd.cut(d2.days_on_production, [-1, 0, 15, 27, 31], labels=["0", "1-15", "16-27", "28-31"])
    out["days_on_production"] = d2.groupby("dop_bucket", observed=True).agg(rows=("oil_bbl", "size"), oil_bbl=("oil_bbl", "sum")).reset_index()
    out["status_codes"] = d.well_status_code.value_counts().rename_axis("well_status_code").reset_index(name="rows").head(15)
    return out
