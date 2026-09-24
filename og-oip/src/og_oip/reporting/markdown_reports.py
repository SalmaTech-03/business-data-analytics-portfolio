"""Generate narrative reports whose numbers come ONLY from computed tables (reports/tables)."""
from __future__ import annotations

import pandas as pd

from og_oip import config
from og_oip.utils.io import df_to_md, read_json

T = config.TABLES_DIR


def _t(n):
    return pd.read_csv(T / f"{n}.csv")


def build_findings() -> str:
    K = read_json(T / "kpi_summary.json"); p, m, f, i, h = K["production"], K["maintenance"], K["financial"], K["inventory"], K["hse"]
    bf, bw, bt, ce = _t("production_by_field"), _t("production_by_well_ranking"), _t("maintenance_by_equipment_type"), _t("critical_equipment_top10")
    cb, fy, ft = _t("cost_breakdown"), _t("financial_by_year"), _t("maintenance_by_failure_type")
    la, ic, sp = _t("loss_associations"), _t("inventory_by_category"), _t("supplier_performance")
    ml, mlk = _t("ml_model_metrics_test"), K["ml"]
    fb = _t("forecast_backtest_summary")
    L = ["# Business Findings - PetroNexa Energy (SYNTHETIC)", "", f"> {config.SYNTHETIC_NOTICE}", "",
         "All figures below are read from generated tables. They describe simulated data and must not be read as statements about real operations. "
         "Association statements are correlations in synthetic data, not causal proof.", "",
         "## 1. Production", "",
         f"- Total oil {p['total_oil_bbl']/1e6:.2f} million bbl over {K['period'][0]} to {K['period'][1]}; average portfolio rate {p['avg_daily_oil_bbl_portfolio']:,.0f} bbl/day.",
         f"- Production loss versus simulated potential: {p['production_loss_bbl']/1e6:.2f} million bbl ({p['production_loss_pct']:.1f}%). {p['downtime_share_of_loss_pct']:.0f}% of the loss is downtime-related; the remainder is efficiency loss.",
         f"- {p['maintenance_associated_downtime_share_pct']:.0f}% of well downtime hours are associated with recorded maintenance events (via the equipment-well bridge); the rest is unattributed background shut-ins.",
         f"- Estimated lost revenue at realised oil prices: ${p['estimated_lost_revenue_usd']/1e6:.1f} million (synthetic).",
         f"- Median nominal annual decline across {p['wells_with_decline_fit']} wells with a fit: {p['median_nominal_annual_decline_pct']:.1f}% (exponential fit; workovers/downtime contaminate individual fits).", "",
         "**By field (ranked by loss in barrels):**", "", df_to_md(bf[["field_id", "field_name", "oil_bbl", "loss_bbl", "loss_pct", "water_cut_pct", "lost_revenue_usd"]], floatfmt=",.1f"), "",
         "**Top 5 wells by total loss (rank_by_loss_bbl; loss_pct shown for context):**", "", df_to_md(bw.head(5)[["well_id", "well_name", "field_id", "loss_bbl", "loss_pct", "avg_water_cut_pct"]], floatfmt=",.1f"), "",
         "**Spearman associations (well-month level):** (the strong rho for downtime hours is expected by construction - loss is computed from downtime; other rows are the informative ones.)", "", df_to_md(la, floatfmt=".3f"), "",
         "## 2. Maintenance and reliability", "",
         f"- {m['failure_count']} corrective events (failures) across 48 units; fleet MTBF {m['fleet_mtbf_hours']:,.0f} h, MTTR {m['fleet_mttr_hours']:.1f} h, availability {m['fleet_availability_pct']:.2f}%.",
         f"- Corrective work is {m['corrective_cost_share_pct']:.0f}% of maintenance cost (${m['total_maintenance_cost_usd']/1e6:.2f} million). The 10 most expensive units account for {m['top10_equipment_cost_share_pct']:.0f}% of cost.", "",
         df_to_md(bt[["equipment_type", "units", "failures", "mtbf_hours", "mttr_hours", "availability_pct", "cost_usd"]], floatfmt=",.1f"), "",
         "**Priority equipment (score = criticality weight x downtime hours):**", "", df_to_md(ce.head(5)[["equipment_id", "equipment_name", "criticality", "failures", "total_downtime_hours", "priority_score"]], floatfmt=",.1f"), "",
         "## 3. Financial (synthetic assumptions)", "",
         f"- Revenue ${f['revenue_usd_synthetic']/1e6:.0f}M, operating cost ${f['operating_cost_usd']/1e6:.0f}M, operating margin ${f['operating_margin_usd']/1e6:.0f}M. Cost per bbl of oil sold ${f['cost_per_bbl_oil_sold']:.2f} (all opex / oil bbl; gas revenue not netted); per BOE ${f['cost_per_boe_sold']:.2f}.",
         "- Price and cost levels are simulation parameters; margin levels should not be benchmarked against real companies.", "",
         df_to_md(cb, floatfmt=",.1f"), "", df_to_md(fy, floatfmt=",.2f"), "",
         "## 4. Inventory and suppliers", "",
         f"- Stockout rate {i['stockout_rate_pct']:.2f}% of item-warehouse-days; annualised turnover {i['annualised_inventory_turnover']:.1f}; median days of inventory {i['avg_days_of_inventory']:.0f}; {i['low_stock_items_at_end']} item-warehouse pairs at/below reorder level on the last day.",
         f"- Overall on-time delivery {i['overall_on_time_delivery_pct']:.0f}% (received purchase orders). Supplier on-time % vs stockout days: Spearman rho {i['supplier_association']['spearman_rho_ontime_vs_stockout_days']:.2f} (p={i['supplier_association']['p_value']:.3f}, n=8 suppliers - low statistical power).", "",
         df_to_md(ic[["material_category", "stockout_rate_pct", "avg_inventory_value_usd", "consumption_value_usd"]], floatfmt=",.2f"), "",
         df_to_md(sp[["supplier_id", "supplier_name", "pos_received", "on_time_pct", "avg_quoted_lead_days", "avg_actual_lead_days"]], floatfmt=",.1f"), "",
         "## 5. HSE", "",
         f"- {h['incident_count']} incidents, {h['lost_time_incidents']} lost-time, {h['days_lost']} days lost; incident rate {h['portfolio_incident_rate_per_200k_h']:.1f} per 200,000 assumed exposure hours (exposure is an ASSUMPTION: {config.EXPOSURE_HOURS_PER_ACTIVE_WELL_DAY:.0f} h per producing well-day).",
         f"- Field-month association between corrective events and incident counts: rho {h['maintenance_association']['spearman_rho_failures_vs_incidents']:.2f} (p={h['maintenance_association']['p_value']:.2f}) - no meaningful monthly association detected in this dataset.",
         f"- Share of incidents within {h['post_failure_window']['window_days']} days after a corrective event in the same field: {h['post_failure_window']['incident_share_in_window_pct']:.1f}% versus {h['post_failure_window']['field_day_share_in_window_pct']:.1f}% of field-days in such windows - no clear clustering.", "",
         "## 6. Forecasting", "",
         f"Rolling-origin backtest ({K['forecast']['backtest_origins']} origins, {K['forecast']['horizon_days']}-day horizon) on portfolio daily oil. Lowest MAE: **{K['forecast']['best_model_by_MAE']}**. ARIMA not included (statsmodels unavailable).", "",
         df_to_md(fb, floatfmt=",.2f"), "",
         "The portfolio series has level shifts from wells coming online, which simple methods cannot anticipate; treat forecasts as short-term baselines.", "",
         "## 7. Predictive maintenance (synthetic sensors)", "",
         f"Time-based split: train to {mlk['dataset']['split']['train_end']}, validation to {mlk['dataset']['split']['val_end']}, test from {mlk['dataset']['split']['test_start']}. Test positive rate {mlk['dataset']['test_positive_rate_pct']:.1f}% (a random model's PR-AUC equals this).", "",
         df_to_md(ml, floatfmt=".3f"), "",
         f"Best model by PR-AUC: {mlk['best_model_by_test_pr_auc']}. Event-level: {mlk['event_level']['failure_windows_with_alert_pct']:.0f}% of {mlk['event_level']['failure_windows']} failure windows raised at least one alert; {mlk['event_level']['false_alert_days_per_equipment_year']:.1f} false-alert days per equipment-year.",
         "Caveat: the precursor signal was simulated (75% of failures have a detectable ramp), so these metrics show the pipeline works, not how a real fleet would perform.", "",
         "## 8. Recommendations (conditional on the synthetic evidence)", "",
         "1. Prioritise the top-ranked equipment by priority score for reliability review; the fields with the largest barrel loss give the largest recovery upside.",
         "2. Investigate the unattributed downtime share before assuming all downtime is maintenance-driven.",
         "3. Review reorder points for the categories with the highest stockout rate and for suppliers with the lowest on-time delivery.",
         "4. Use the risk-scoring output as a ranked inspection list, not an automatic trigger, given the moderate precision/recall."]
    return "\n".join(L)


def build_real_report() -> str:
    R = read_json(T / "real_data_kpi_summary.json"); v, b = R["volve"], R["bsee"]
    vq, vw, vy = _t("volve_data_quality"), _t("volve_well_summary"), _t("volve_yearly")
    bq, bm, bo, ba = _t("bsee_data_quality"), _t("bsee_monthly"), _t("bsee_operators"), _t("bsee_areas")
    vf = _t("volve_forecast_backtest_summary")
    L = ["# Real-Data Case Studies", "",
         "These two analyses use REAL datasets supplied by the project author. They are separate from the fictional PetroNexa Energy dataset; no records were merged and no cross-dataset relationships are claimed.", "",
         "## A. Volve field (Equinor Volve production workbook)", "",
         f"- Producing wellbores in file: {v['wellbores_producing']}; monthly aggregate {v['first_month']} to {v['last_month']}; total oil {v['total_oil_bbl']/1e6:.1f} million bbl (converted from Sm3 at {config.BBL_PER_M3} bbl/Sm3).",
         f"- Peak monthly-average rate {v['peak_avg_daily_oil_bbl']:,.0f} bbl/day in {v['field_decline']['peak_month']}; post-peak exponential fit gives a nominal annual decline of {v['field_decline']['nominal_annual_decline_pct']:.1f}% (R2 {v['field_decline']['r_squared']:.2f}); indicative only.", "",
         "**Data quality checks:**", "", df_to_md(vq, floatfmt=",.3g"), "",
         "**Wellbore summary:**", "", df_to_md(vw[["wellbore", "first_date", "last_date", "cum_oil_bbl", "water_cut_pct", "uptime_pct_of_calendar_span", "oil_share_pct"]], floatfmt=",.1f"), "",
         "**Yearly totals:**", "", df_to_md(vy, floatfmt=",.1f"), "",
         "**Monthly-rate forecast backtest (6-month horizon, 4 origins):**", "", df_to_md(vf, floatfmt=",.0f"), "",
         "Limits: the file has no maintenance, cost or price data, so no reliability or financial KPIs are derived. Rates are as-reported allocations.", "",
         "## B. BSEE OGOR-A monthly production (2025-01 to 2026-06)", "",
         "Column names follow the OGOR-A layout as understood by the author (files have no header). Oil/gas/water volume columns were identified by magnitude and behaviour only; verify against the official BSEE data dictionary before publishing. Codes are not decoded. OGOR-B/C files were not used.", "",
         f"- {b['months']} months, {b['operators']} operators. Reported oil {b['total_oil_bbl']/1e6:,.0f} million bbl, gas {b['total_gas_mcf']/1e6:,.0f} million mcf, water {b['total_water_bbl']/1e6:,.0f} million bbl.",
         f"- Concentration: top 5 operators hold {b['top5_oil_share_pct']:.1f}% of reported oil, top 10 hold {b['top10_oil_share_pct']:.1f}%; HHI {b['hhi_oil (0-10000)']:.0f} (0-10,000 scale).", "",
         "**Data quality checks:**", "", df_to_md(bq, floatfmt=",.0f"), "",
         "**Top 10 operators by oil:**", "", df_to_md(bo.head(10)[["operator_name", "oil_bbl", "oil_share_pct", "water_to_oil_ratio"]], floatfmt=",.1f"), "",
         "**Top area-block prefixes by oil:**", "", df_to_md(ba.head(8)[["area_prefix", "oil_bbl", "oil_share_pct"]], floatfmt=",.1f"), "",
         "**Monthly totals:**", "", df_to_md(bm[["month", "oil_bbl", "gas_mcf", "water_bbl", "completions", "operators", "water_to_oil_ratio"]], floatfmt=",.2f"), "",
         "Limits: 18 months is too short for decline or seasonality conclusions; operator names are as reported (no merger/name reconciliation); the completion count decline across the period may reflect reporting changes as well as operations."]
    return "\n".join(L)
