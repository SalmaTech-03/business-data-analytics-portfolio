"""Runs the full analytics suite and writes reports/tables/*.csv, reports/figures/*.png, reports/tables/kpi_summary.json."""
from __future__ import annotations

import numpy as np
import pandas as pd

from og_oip import config
from og_oip.analytics import financial, hse, inventory, maintenance, production
from og_oip.forecasting import models as fmod
from og_oip.ingestion.loaders import load_processed
from og_oip.ml import predictive_maintenance as pm
from og_oip.real_data import bsee, volve
from og_oip.reporting import charts
from og_oip.utils.io import write_csv, write_json
from og_oip.utils.logging_utils import get_logger

log = get_logger("analytics")


def _read_marts():
    M = {}
    for f in config.MARTS_DIR.glob("mart_*.csv"):
        df = pd.read_csv(f)
        for c in ("date", "month"):
            if c in df.columns:
                df[c] = pd.to_datetime(df[c])
        if "installation_date" in df.columns:
            df["installation_date"] = pd.to_datetime(df["installation_date"])
        M[f.stem] = df
    return M


def _tab(name, df):
    write_csv(df, config.TABLES_DIR / f"{name}.csv")


def run_synthetic() -> dict:
    t = load_processed(); M = _read_marts()
    wd, fm, es, em, hm, mi, sp = (M[k] for k in ["mart_well_daily", "mart_field_monthly", "mart_equipment_summary", "mart_equipment_monthly", "mart_hse_monthly", "mart_inventory", "mart_supplier_performance"])
    K = {"notice": config.SYNTHETIC_NOTICE, "period": [config.START_DATE, config.END_DATE]}
    # production
    K["production"] = production.portfolio_kpis(wd)
    bf = production.by_field(wd, t["dim_field"]); _tab("production_by_field", bf)
    bw = production.by_well(wd); _tab("production_by_well_ranking", bw)
    _tab("production_monthly_trend", production.monthly_trend(wd))
    dec = production.decline_analysis(wd); _tab("well_decline_analysis", dec)
    K["production"]["wells_with_decline_fit"] = int(len(dec)); K["production"]["median_nominal_annual_decline_pct"] = float(dec.nominal_annual_decline_pct.median())
    _tab("pressure_trend_by_field_year", production.pressure_trend(wd)); _tab("loss_associations", production.loss_associations(wd))
    # maintenance
    K["maintenance"] = maintenance.kpis(es, t["fact_maintenance"])
    bt = maintenance.by_type(es); _tab("maintenance_by_equipment_type", bt)
    _tab("maintenance_by_failure_type", maintenance.by_failure_type(t["fact_maintenance"], t["dim_equipment"]))
    _tab("maintenance_by_maintenance_type", maintenance.by_maintenance_type(t["fact_maintenance"]))
    ce = maintenance.critical_equipment(es); _tab("critical_equipment_top10", ce)
    pareto = maintenance.cost_pareto(es); _tab("maintenance_cost_pareto", pareto)
    K["maintenance"]["top10_equipment_cost_share_pct"] = float(pareto.cum_share_pct.iloc[9]); _tab("equipment_age_association", maintenance.age_association(es))
    _tab("equipment_summary", es)
    # financial
    K["financial"] = financial.kpis(fm); _tab("financial_by_field", financial.by_field(fm, t["dim_field"])); _tab("financial_by_year", financial.by_year(fm)); _tab("cost_breakdown", financial.cost_breakdown(fm))
    # inventory
    K["inventory"] = inventory.kpis(t["fact_inventory"], mi, t["dim_material"])
    bc = inventory.by_category(mi); _tab("inventory_by_category", bc); _tab("excess_inventory", inventory.excess_inventory(mi)); _tab("low_stock_items", inventory.low_stock(t["fact_inventory"], t["dim_material"]))
    _tab("supplier_performance", sp); K["inventory"]["supplier_association"] = inventory.supplier_association(sp)
    K["inventory"]["overall_on_time_delivery_pct"] = float(np.average(sp.on_time_pct, weights=sp.pos_received))
    # hse
    K["hse"] = hse.kpis(t["fact_hse"], hm)
    for n, d in hse.distributions(t["fact_hse"]).items():
        _tab(f"hse_by_{n}", d)
    _tab("hse_rate_by_field", hse.by_field_rate(hm)); K["hse"]["maintenance_association"] = hse.maintenance_association(hm, em)
    K["hse"]["post_failure_window"] = hse.post_failure_window(t["fact_hse"], t["fact_maintenance"], t["dim_equipment"])
    # forecasting
    ser = t["fact_production"].groupby("date")["oil_production_bbl"].sum().asfreq("D")
    bt_all, bt_sum = fmod.backtest(ser); _tab("forecast_backtest_detail", bt_all); _tab("forecast_backtest_summary", bt_sum)
    best = bt_sum.iloc[0]["model"]; fc = fmod.final_forecast(ser, best, config.FORECAST_HORIZON_DAYS); _tab("forecast_next_30d", fc)
    K["forecast"] = {"best_model_by_MAE": best, "series": "portfolio daily oil (processed)", "horizon_days": config.FORECAST_HORIZON_DAYS, "backtest_origins": int(bt_sum.origins.max()),
                     "arima": "not included (statsmodels unavailable in build environment)"}
    # ML
    ds = pm.build_dataset(M["mart_sensor_daily"], t["fact_maintenance"], t["dim_equipment"])
    res, info, fitted, (tr, va, te), scores = pm.run_experiment(ds); _tab("ml_model_metrics_test", res)
    fi = pm.feature_importance(fitted); _tab("ml_feature_importance", fi)
    best_ml = res.iloc[:3].sort_values("pr_auc", ascending=False).iloc[0]
    K["ml"] = {"dataset": info, "best_model_by_test_pr_auc": best_ml["model"],
               "event_level": pm.event_level_recall(te, scores[best_ml["model"]], best_ml["threshold"]),
               "warning": "Sensor-failure relationship is SIMULATED; metrics apply to synthetic data only."}
    _tab("ml_latest_equipment_risk", pm.latest_risk(ds, fitted[best_ml["model"]], t["dim_equipment"]))
    # charts
    charts.production_trend(fm); charts.loss_by_field(bf); charts.loss_decomposition(wd); charts.downtime_pareto(es); charts.mtbf_mttr(bt)
    charts.cost_per_bbl(fm); charts.stockout_by_category(bc); charts.hse_monthly(hm); charts.forecast_plot(ser, fc)
    charts.ml_curves(res, scores, te.label.values); charts.ml_importance(fi)
    write_json(K, config.TABLES_DIR / "kpi_summary.json")
    return K


def run_real() -> dict:
    R = {}
    dl, mo = volve.load(); v = volve.analyse(dl, mo)
    for k, d in v.items():
        _tab(f"volve_{k}", d)
    bt_all, bt_sum = volve.forecast_backtest(v["field_monthly"]); _tab("volve_forecast_backtest_summary", bt_sum)
    charts.volve_field(v["field_monthly"]); charts.volve_wells(v["well_summary"])
    b = bsee.analyse(bsee.load())
    for k, d in b.items():
        _tab(f"bsee_{k}", d)
    charts.bsee_monthly(b["monthly"]); charts.bsee_operators(b["operators"])
    R["volve"] = {"total_oil_bbl": float(v["field_monthly"].oil_bbl.sum()), "first_month": str(v["field_monthly"].month.min().date()), "last_month": str(v["field_monthly"].month.max().date()),
                  "peak_avg_daily_oil_bbl": float(v["field_monthly"].avg_daily_oil_bbl.max()), "wellbores_producing": int(len(v["well_summary"])),
                  "field_decline": v["field_decline"].iloc[0].to_dict()}
    m = b["monthly"]
    R["bsee"] = {"months": int(len(m)), "total_oil_bbl": float(m.oil_bbl.sum()), "total_gas_mcf": float(m.gas_mcf.sum()), "total_water_bbl": float(m.water_bbl.sum()),
                 "operators": int(len(b["operators"])), **b["concentration"].iloc[0].to_dict()}
    write_json(R, config.TABLES_DIR / "real_data_kpi_summary.json")
    return R
