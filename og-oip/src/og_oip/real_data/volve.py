"""REAL-DATA CASE STUDY 1: Volve production data (user-supplied workbook).

This dataset is NOT part of the fictional PetroNexa company and is never merged with it.
Source: Volve_production_data.xlsx supplied by the project author (publicly released Equinor Volve field data as far as the
file structure indicates - the original licence/terms must be checked by anyone redistributing it).
Units in the file: liquids/gas in Sm3; converted here with documented factors (config.py).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from og_oip import config

FILE = config.REAL_DIR / "Volve_production_data.xlsx"


def load(path=FILE):
    daily = pd.read_excel(path, sheet_name="Daily Production Data")
    monthly = pd.read_excel(path, sheet_name="Monthly Production Data", header=0).iloc[1:].copy()   # row 1 holds units
    monthly.columns = ["wellbore", "npd_code", "year", "month", "on_stream_hrs", "oil_sm3", "gas_sm3", "water_sm3", "gi_sm3", "wi_sm3"]
    for c in monthly.columns[1:]:
        monthly[c] = pd.to_numeric(monthly[c], errors="coerce")
    monthly = monthly.dropna(subset=["year"]).reset_index(drop=True)
    return daily, monthly


def prepare_daily(daily: pd.DataFrame) -> pd.DataFrame:
    d = daily.rename(columns={"DATEPRD": "date", "NPD_WELL_BORE_NAME": "wellbore", "ON_STREAM_HRS": "on_stream_hrs", "BORE_OIL_VOL": "oil_sm3",
                              "BORE_GAS_VOL": "gas_sm3", "BORE_WAT_VOL": "water_sm3", "BORE_WI_VOL": "wi_sm3", "FLOW_KIND": "flow_kind",
                              "WELL_TYPE": "well_type", "AVG_DOWNHOLE_PRESSURE": "downhole_pressure", "AVG_WHP_P": "whp"}).copy()
    d["oil_bbl"] = d.oil_sm3 * config.BBL_PER_M3
    d["gas_mcf"] = d.gas_sm3 * config.MCF_PER_SM3
    d["water_bbl"] = d.water_sm3 * config.BBL_PER_M3
    d["month"] = d.date.dt.to_period("M").dt.to_timestamp()
    return d


def data_quality(daily_raw: pd.DataFrame, d: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    rows = [("daily rows", len(d)), ("duplicate (date, wellbore) rows", int(d.duplicated(["date", "wellbore"]).sum())),
            ("rows with ON_STREAM_HRS > 24", int((d.on_stream_hrs > 24).sum())), ("rows with negative oil volume", int((d.oil_sm3 < 0).sum())),
            ("production rows with missing oil volume", int(d[d.flow_kind == "production"].oil_sm3.isna().sum())),
            ("production rows with missing on-stream hours", int(d[d.flow_kind == "production"].on_stream_hrs.isna().sum())),
            ("production rows with oil > 0 but on-stream hours == 0", int(((d.flow_kind == "production") & (d.oil_sm3 > 0) & (d.on_stream_hrs == 0)).sum()))]
    dm = d[d.flow_kind == "production"].groupby(["wellbore", d.date.dt.year.rename("year"), d.date.dt.month.rename("month")])[["oil_sm3", "on_stream_hrs"]].sum().reset_index()
    j = dm.merge(monthly.rename(columns={"oil_sm3": "oil_monthly_sheet", "on_stream_hrs": "hrs_monthly_sheet"}), on=["wellbore", "year", "month"], how="inner")
    j["diff"] = (j.oil_sm3 - j.oil_monthly_sheet).abs()
    rows += [("daily-vs-monthly sheet: matched well-months", len(j)),
             ("daily-vs-monthly sheet: well-months with |oil diff| > 1 Sm3", int((j["diff"] > 1).sum())),
             ("daily-vs-monthly sheet: max |oil diff| Sm3", float(j["diff"].max())),
             ("monthly sheet well-months not found in daily", int(len(monthly) - len(j)))]
    return pd.DataFrame(rows, columns=["check", "value"])


def analyse(daily: pd.DataFrame, monthly: pd.DataFrame) -> dict:
    d = prepare_daily(daily)
    p = d[d.flow_kind == "production"].copy()
    out = {"data_quality": data_quality(daily, d, monthly)}
    fm = p.groupby("month").agg(oil_bbl=("oil_bbl", "sum"), gas_mcf=("gas_mcf", "sum"), water_bbl=("water_bbl", "sum"), wells=("wellbore", "nunique"),
                                 on_stream_hrs=("on_stream_hrs", "sum"), well_days=("date", "size")).reset_index()
    fm["water_cut_pct"] = 100 * fm.water_bbl / (fm.water_bbl + fm.oil_bbl)
    fm["gor_mcf_per_bbl"] = fm.gas_mcf / fm.oil_bbl.replace(0, np.nan)
    fm["avg_daily_oil_bbl"] = fm.oil_bbl / fm.month.dt.days_in_month
    out["field_monthly"] = fm
    w = p.groupby("wellbore").agg(first_date=("date", "min"), last_date=("date", "max"), cum_oil_bbl=("oil_bbl", "sum"), cum_gas_mcf=("gas_mcf", "sum"),
                                   cum_water_bbl=("water_bbl", "sum"), days_on_stream=("on_stream_hrs", lambda s: int((s > 0).sum())),
                                   on_stream_hrs=("on_stream_hrs", "sum"), rows=("date", "size"), peak_daily_oil_bbl=("oil_bbl", "max")).reset_index()
    w["uptime_pct_of_calendar_span"] = 100 * w.on_stream_hrs / ((w.last_date - w.first_date).dt.days.add(1) * 24)
    w["water_cut_pct"] = 100 * w.cum_water_bbl / (w.cum_water_bbl + w.cum_oil_bbl)
    w["oil_share_pct"] = 100 * w.cum_oil_bbl / w.cum_oil_bbl.sum()
    out["well_summary"] = w.sort_values("cum_oil_bbl", ascending=False)
    inj = d[d.flow_kind == "injection"].copy()
    inj["wi_bbl"] = inj.wi_sm3 * config.BBL_PER_M3
    out["injection_by_well"] = inj.groupby("wellbore").agg(injection_rows=("date", "size"), water_injected_bbl=("wi_bbl", "sum")).reset_index()
    # decline: exponential fit from peak month to end (field level)
    pk = fm.loc[fm.avg_daily_oil_bbl.idxmax()]
    post = fm[fm.month >= pk.month].copy(); post = post[post.avg_daily_oil_bbl > 0]
    x = np.arange(len(post)); r = stats.linregress(x, np.log(post.avg_daily_oil_bbl))
    out["field_decline"] = pd.DataFrame([{"peak_month": pk.month.date(), "peak_avg_daily_oil_bbl": pk.avg_daily_oil_bbl, "months_fitted": len(post),
                                          "nominal_annual_decline_pct": 100 * (1 - np.exp(12 * r.slope)), "r_squared": r.rvalue ** 2,
                                          "note": "single exponential fit peak->end; ignores shut-ins/wells added; indicative only"}])
    yr = p.assign(year=p.date.dt.year).groupby("year").agg(oil_bbl=("oil_bbl", "sum"), gas_mcf=("gas_mcf", "sum"), water_bbl=("water_bbl", "sum")).reset_index()
    yr["water_cut_pct"] = 100 * yr.water_bbl / (yr.water_bbl + yr.oil_bbl)
    out["yearly"] = yr
    return out


def forecast_backtest(fm: pd.DataFrame):
    from og_oip.forecasting.models import MODELS, backtest
    s = fm.set_index("month")["avg_daily_oil_bbl"]
    keep = {k: v for k, v in MODELS.items() if k in ("Naive (last value)", "Moving average (7d)", "Simple exponential smoothing", "Damped Holt (trend) smoothing")}
    keep["Moving average (3 months)"] = lambda y, h: np.repeat(np.mean(y[-3:]), h)
    keep.pop("Moving average (7d)")
    return backtest(s, horizon=6, n_origins=4, step=6, min_train=36, models=keep)
