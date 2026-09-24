"""Generate the business-analysis document set from ONE source of truth (keeps IDs consistent across documents)."""
import _bootstrap  # noqa: F401
from pathlib import Path

from og_oip import config

OUT = config.ROOT / "business-analysis"
NOTE = f"> {config.SYNTHETIC_NOTICE}\n> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.\n"

BR = [
 ("BR-01", "Monitor production performance by field and well", "Operations Manager sees oil, gas, water and water cut trends at field/well level."),
 ("BR-02", "Quantify production loss versus potential and separate downtime from other loss", "Production Engineer can size and rank losses."),
 ("BR-03", "Track equipment reliability (MTBF, MTTR, availability, failure modes)", "Reliability Engineer can compare equipment types and units."),
 ("BR-04", "Prioritise maintenance effort by downtime, cost and criticality", "Maintenance Manager gets a ranked, explainable priority list."),
 ("BR-05", "Understand operating cost, unit cost per barrel and margin", "Finance Analyst can track opex and unit economics by field."),
 ("BR-06", "Monitor inventory, stockouts and reorder exposure", "Supply Chain Analyst can see stockout and excess stock."),
 ("BR-07", "Evaluate supplier delivery performance and lead times", "Procurement can compare suppliers on-time and lead-time gaps."),
 ("BR-08", "Monitor HSE incidents, severity and rates", "HSE Lead can track incidents, lost time and root causes."),
 ("BR-09", "Ensure trusted data via validation, cleaning and lineage", "Data Steward can see defects found, fixed and quarantined."),
 ("BR-10", "Provide short-term production forecasts with honest accuracy measures", "Planning can use baseline forecasts with backtest errors."),
 ("BR-11", "Provide early-warning failure risk scoring", "Reliability Engineer gets ranked equipment risk with documented limits."),
 ("BR-12", "Deliver self-service analytics (SQL, dashboards specs, Streamlit, Excel)", "Executives and analysts can explore KPIs without code."),
 ("BR-13", "Demonstrate methods on separate real datasets (Volve, BSEE OGOR-A) without mixing them into the synthetic company", "Portfolio reviewers see real-data rigour and clear separation."),
]
FR = [  # id, text, BR, artifact
 ("FR-01", "Generate a relationally consistent synthetic dataset (8 dimension/bridge tables, 9 fact tables) reproducible from a seed", "BR-09,BR-12", "src/og_oip/data_generation/*, scripts/generate_data.py"),
 ("FR-02", "Produce a raw dataset with documented injected defects and a defect log", "BR-09", "src/og_oip/data_generation/defects.py, data/reference/defect_injection_log.json"),
 ("FR-03", "Clean raw data into processed tables; quarantine unrepairable rows; log every action", "BR-09", "src/og_oip/cleaning/cleaners.py, scripts/clean_data.py"),
 ("FR-04", "Run validation checks (keys, nulls, ranges, dates, referential, domains, units, logic) and publish a data quality report from actual results", "BR-09", "src/og_oip/validation/*, reports/data_quality_report.md"),
 ("FR-05", "Build analytical marts (well-day, field-month, equipment, sensor-day, inventory, supplier, HSE)", "BR-01..BR-08", "src/og_oip/transformation/marts.py"),
 ("FR-06", "Report production, loss (downtime vs other), decline and pressure/water-cut trends", "BR-01,BR-02", "src/og_oip/analytics/production.py"),
 ("FR-07", "Rank wells by defined metrics (loss bbl, loss %, avg rate) with explicit definitions", "BR-02", "analytics/production.py::by_well"),
 ("FR-08", "Associate downtime with maintenance events through the equipment-well bridge", "BR-02,BR-04", "transformation/marts.py::attributed_downtime"),
 ("FR-09", "Compute MTBF, MTTR, availability, failure counts by equipment and type", "BR-03", "analytics/maintenance.py, marts.build_mart_equipment_summary"),
 ("FR-10", "Produce a criticality-weighted maintenance priority ranking with an explicit formula", "BR-04", "analytics/maintenance.py::critical_equipment"),
 ("FR-11", "Compute cost per bbl, cost per BOE, margin and cost breakdown by field/year", "BR-05", "analytics/financial.py"),
 ("FR-12", "Estimate revenue impact of production loss using realised daily oil price", "BR-02,BR-05", "marts.build_mart_well_daily"),
 ("FR-13", "Compute inventory KPIs: stockout rate, turnover, days of inventory, low stock, excess stock", "BR-06", "analytics/inventory.py"),
 ("FR-14", "Compute supplier on-time %, quoted vs actual lead time from purchase orders", "BR-07", "marts.build_mart_supplier_performance"),
 ("FR-15", "Compute HSE incident counts, lost-time counts, rates per 200,000 assumed exposure hours, root-cause distribution", "BR-08", "analytics/hse.py"),
 ("FR-16", "Quantify associations (Spearman) between operational factors and outcomes, labelled as association not causation", "BR-02,BR-08", "analytics/*"),
 ("FR-17", "Backtest naive, moving-average, exponential-smoothing and AR models with rolling origins; report MAE/RMSE/MAPE/bias", "BR-10", "src/og_oip/forecasting/models.py"),
 ("FR-18", "Train and evaluate failure-risk models with time-based splits and real (not fabricated) metrics", "BR-11", "src/og_oip/ml/predictive_maintenance.py"),
 ("FR-19", "Provide 40+ PostgreSQL analytical queries, views and a load script", "BR-12", "sql/*"),
 ("FR-20", "Provide Power BI and Tableau build specifications (no fabricated binary files)", "BR-12", "powerbi/*, tableau/*"),
 ("FR-21", "Provide an Excel workbook with live formulas", "BR-12", "excel/OG_OIP_Analysis_Workbook.xlsx"),
 ("FR-22", "Provide a Streamlit exploration app", "BR-12", "app/streamlit_app.py"),
 ("FR-23", "Analyse Volve production data separately (conversions, reconciliation, decline, water cut, forecast backtest)", "BR-13", "src/og_oip/real_data/volve.py"),
 ("FR-24", "Analyse BSEE OGOR-A data separately (monthly totals, operator concentration, areas, quality checks)", "BR-13", "src/og_oip/real_data/bsee.py"),
 ("FR-25", "Provide automated tests for generation, cleaning, validation, KPIs, forecasting, ML, SQL schema, real-data loaders", "BR-09", "tests/*"),
 ("FR-26", "Provide reproducible pipeline entry points and documentation of assumptions and limitations", "BR-09,BR-12", "scripts/*, README.md, docs/*"),
]
STORIES = [  # id, persona, want, so that, BRs, FRs, artifact, ACs
 ("US-01", "Operations Manager", "see monthly oil, gas and water production by field", "I can spot production trends early", "BR-01", "FR-05,FR-06", "sql Q01,Q02; charts production_trend_by_field", ["Given processed data, when I view monthly production by field, then totals equal the sum of well-day rows", "Each field appears for every month with production", "Units (bbl, mcf) are labelled"]),
 ("US-02", "Operations Manager", "rank wells by total loss and by loss percentage", "I know where recovery effort should focus", "BR-02", "FR-07", "sql Q03,Q06; analytics.production.by_well", ["Both rank metrics are defined in the output columns", "Ranks are deterministic for ties (method=min)"]),
 ("US-03", "Production Engineer", "see production loss split into downtime-related and other loss", "I can target the right lever", "BR-02", "FR-05,FR-06", "mart_well_daily; chart loss_decomposition_monthly", ["downtime_loss + other_loss = production_loss for every row", "Loss is never negative"]),
 ("US-04", "Production Engineer", "estimate well decline rates", "I can flag wells declining faster than peers", "BR-01", "FR-06", "analytics.production.decline_analysis", ["Output includes months used, R-squared and p-value", "Wells with fewer than 18 months are excluded and stated"]),
 ("US-05", "Production Engineer", "track water cut and pressure trends", "I can identify water-management candidates", "BR-01", "FR-06", "sql Q07,Q09,Q10", ["Water cut is volume-weighted at field level", "Values stay within 0-100%"]),
 ("US-06", "Reliability Engineer", "see MTBF, MTTR and availability by equipment and type", "I can compare reliability", "BR-03", "FR-09", "sql Q12; mart_equipment_summary", ["MTBF = operating hours / failures; MTTR = corrective downtime / failures", "Units with zero failures show blank MTBF, not zero"]),
 ("US-07", "Reliability Engineer", "see failure modes by equipment type", "I can direct root-cause work", "BR-03", "FR-09", "sql Q13; maintenance_by_failure_type.csv", ["Only corrective events count as failures", "Counts reconcile with total failure KPI"]),
 ("US-08", "Maintenance Manager", "get a ranked list of priority equipment", "I can plan crews and spares", "BR-04", "FR-10", "sql BQ09; critical_equipment_top10.csv", ["Score = criticality weight x downtime hours (weights High 3, Medium 2, Low 1)", "Formula is displayed next to the ranking"]),
 ("US-09", "Maintenance Manager", "compare preventive and corrective cost and downtime", "I can judge the preventive programme", "BR-04", "FR-09", "sql Q15,Q16,BQ05", ["Shares sum to 100%", "Corrective and preventive are never mixed in one bucket"]),
 ("US-10", "Reliability Engineer", "identify repeat failures within 30 days", "I can find ineffective repairs", "BR-03", "FR-09", "sql Q18,Q19", ["Repeat interval is measured between consecutive corrective events on the same equipment"]),
 ("US-11", "Maintenance Manager", "see maintenance cost concentration (Pareto)", "I can focus on the costliest units", "BR-04", "FR-10", "sql Q17; maintenance_cost_pareto.csv", ["Cumulative share reaches 100% at the last unit"]),
 ("US-12", "Finance Analyst", "see revenue, opex and margin by field and year", "I can review profitability", "BR-05", "FR-11", "sql Q22; financial_by_field.csv", ["margin = revenue - opex", "Currency and synthetic status are stated"]),
 ("US-13", "Finance Analyst", "see cost per barrel and per BOE", "I can track unit economics", "BR-05", "FR-11", "sql Q23; kpi_dictionary", ["Cost per bbl = total opex / oil bbl sold (gas not netted)", "BOE uses 6 mcf per BOE"]),
 ("US-14", "Finance Analyst", "see opex by category", "I can see cost drivers", "BR-05", "FR-11", "sql Q24; cost_breakdown.csv", ["Category shares sum to 100%"]),
 ("US-15", "Finance Analyst", "estimate revenue lost to production loss", "I can prioritise by value", "BR-02,BR-05", "FR-12", "sql Q25,BQ01", ["Uses the realised oil price of the same field and day", "Method is documented as an estimate"]),
 ("US-16", "Supply Chain Analyst", "see stockout rate by material category", "I can adjust reorder policy", "BR-06", "FR-13", "sql Q27; inventory_by_category.csv", ["Stockout rate = stockout item-days / item-warehouse-days"]),
 ("US-17", "Supply Chain Analyst", "list items at or below reorder level", "I can trigger orders", "BR-06", "FR-13", "sql Q29; low_stock_items.csv", ["List is evaluated on the last inventory date"]),
 ("US-18", "Supply Chain Analyst", "identify excess inventory", "I can release working capital", "BR-06", "FR-13", "sql Q33; excess_inventory.csv", ["Threshold (90 days of inventory) is an explicit assumption"]),
 ("US-19", "Procurement Lead", "compare supplier on-time delivery and lead time", "I can manage suppliers", "BR-07", "FR-14", "sql Q31,Q32; supplier_performance.csv", ["Only received purchase orders are scored", "On time means received on or before promised date"]),
 ("US-20", "Procurement Lead", "see open purchase orders past promise date", "I can chase deliveries", "BR-07", "FR-14", "sql Q34", ["Open orders have no received date"]),
 ("US-21", "HSE Lead", "see incidents by field, severity and root cause", "I can target safety actions", "BR-08", "FR-15", "sql Q36,Q38", ["Severity uses the controlled list Low/Medium/High/Critical"]),
 ("US-22", "HSE Lead", "see incident rates per 200,000 exposure hours", "I can normalise across fields", "BR-08", "FR-15", "sql Q37; mart_hse_monthly", ["Exposure hours assumption is stated with the metric"]),
 ("US-23", "Planning Analyst", "get a 30-day production forecast with backtest errors", "I can use it with known accuracy", "BR-10", "FR-17", "forecast_next_30d.csv; forecast_backtest_summary.csv", ["Backtest uses rolling origins without look-ahead", "MAE, RMSE, MAPE and bias are reported per model"]),
 ("US-24", "Reliability Engineer", "see equipment failure-risk scores", "I can plan inspections", "BR-11", "FR-18", "ml_latest_equipment_risk.csv; ml_model_metrics_test.csv", ["Split is time-based", "Threshold is chosen on validation data only", "Report states data are synthetic"]),
 ("US-25", "Data Steward", "see a data quality report with defects found, fixed and residual", "I can trust the analytics", "BR-09", "FR-02,FR-03,FR-04", "reports/data_quality_report.md", ["Report numbers come from validation results", "Quarantined rows are counted"]),
 ("US-26", "Data Steward", "trace every cleaning action", "I can audit changes", "BR-09", "FR-03", "data/processed/cleaning_log.json", ["Each action has a count", "Raw files are never modified"]),
 ("US-27", "Executive", "open a dashboard with KPIs across production, maintenance, finance, inventory and HSE", "I get one view of performance", "BR-12", "FR-19..FR-22", "powerbi/*, tableau/*, app/streamlit_app.py, Excel", ["Specifications define measures and page layouts", "Synthetic-data notice is visible on every page"]),
 ("US-28", "Portfolio Reviewer", "see Volve and BSEE analyses kept separate from the fictional company", "I can judge real-data methodology", "BR-13", "FR-23,FR-24", "reports/real_data_case_studies.md", ["No real record is merged into PetroNexa tables", "Assumptions about BSEE column meaning are stated"]),
]
KPIS = [  # name, definition, formula, grain, source, caveat
 ("Oil production (bbl)", "Reported oil volume", "SUM(oil_production_bbl)", "well-day", "fact_production", "Imputed rows flagged in dq_flag"),
 ("Production potential (bbl)", "SIMULATED unconstrained rate from decline curve", "SUM(potential_production_bbl)", "well-day", "fact_production", "Synthetic construct, no real-world equivalent"),
 ("Production loss (bbl)", "Potential minus actual, floored at 0", "SUM(MAX(potential - oil, 0))", "well-day", "mart_well_daily", "Depends on the simulated potential"),
 ("Production loss %", "Loss share of potential", "SUM(loss) / SUM(potential)", "any", "mart_well_daily", ""),
 ("Downtime loss (bbl)", "Loss attributable to hours down", "MIN(potential x downtime_hours/24, loss)", "well-day", "mart_well_daily", "Remaining loss is 'other (efficiency) loss'"),
 ("Maintenance-associated downtime share", "Well downtime hours explained by maintenance events", "SUM(attributed hours) / SUM(downtime_hours)", "any", "mart_well_daily", "Assumes downtime starts on maintenance date and spills at <=24 h/day"),
 ("Water cut %", "Water share of liquids", "100 x water / (water + oil)", "any (volume-weighted)", "fact_production", "Never average row-level percentages for aggregates"),
 ("Nominal annual decline %", "Exponential decline from log-linear fit of monthly mean rate", "100 x (1 - exp(12 x slope))", "well", "well_decline_analysis.csv", "Workovers and downtime contaminate the fit"),
 ("Failure", "Corrective maintenance event", "COUNT(maintenance_type = 'Corrective')", "equipment", "fact_maintenance", ""),
 ("Availability %", "Share of period not in maintenance downtime", "100 x (period_hours - downtime_hours) / period_hours", "equipment", "fact_maintenance", "Period = 1096 days x 24 h"),
 ("MTBF (h)", "Mean operating hours between failures", "(period_hours - downtime_hours) / failures", "equipment / type", "fact_maintenance", "Blank when failures = 0"),
 ("MTTR (h)", "Mean corrective downtime per failure", "corrective downtime_hours / failures", "equipment / type", "fact_maintenance", ""),
 ("Priority score", "Criticality-weighted downtime", "weight(High 3, Medium 2, Low 1) x total downtime_hours", "equipment", "mart_equipment_summary", "Weights are an assumption"),
 ("Opex (USD)", "Operating cost", "SUM(cost_amount_usd)", "field-day-category", "fact_operating_cost", "Synthetic cost model"),
 ("Cost per bbl oil sold", "Unit cost", "opex / oil_volume_bbl", "field-month", "v_field_financial_monthly", "Gas revenue not netted"),
 ("Cost per BOE sold", "Unit cost per BOE", "opex / (oil bbl + gas mcf / 6)", "field-month", "mart_field_monthly", "6 mcf = 1 BOE convention"),
 ("Operating margin (USD)", "Revenue less opex", "revenue_usd - opex", "field-month", "mart_field_monthly", "No capex, tax or royalty"),
 ("Estimated lost revenue (USD)", "Loss valued at realised price", "production_loss_bbl x oil_price_usd", "well-day", "mart_well_daily", "Estimate"),
 ("Stockout rate %", "Share of item-warehouse-days with unmet demand", "100 x SUM(stockout_flag) / COUNT(rows)", "any", "fact_inventory", ""),
 ("Inventory turnover (annualised)", "Consumption value over average stock value", "consumption_value / avg_stock_value / years", "material-warehouse", "mart_inventory", ""),
 ("Days of inventory", "Cover at average consumption", "avg closing stock / avg daily consumption", "material-warehouse", "mart_inventory", "Infinite/blank if no consumption"),
 ("Supplier on-time %", "Received on or before promised date", "100 x AVG(received_date <= promised_date)", "supplier", "fact_purchase_order", "Received orders only"),
 ("Lead-time gap (d)", "Actual minus quoted lead time", "AVG(received - order) - AVG(quoted_lead_time_days)", "supplier", "fact_purchase_order", ""),
 ("Incident rate per 200k h", "Incidents normalised by exposure", "incidents x 200000 / exposure_hours", "field-month", "mart_hse_monthly", "Exposure = 30 h x producing well-days (assumption)"),
 ("Lost-time incident rate", "Lost-time incidents normalised", "LTI x 200000 / exposure_hours", "field-month", "mart_hse_monthly", "Same exposure assumption"),
 ("Failure risk score (7d)", "Model probability of corrective failure within 7 days", "model.predict_proba", "equipment-day", "ml_latest_equipment_risk.csv", "Synthetic sensors; moderate precision/recall"),
 ("Forecast error (MAE/RMSE/MAPE/bias)", "Backtest accuracy", "rolling-origin, 30-day horizon", "portfolio-day", "forecast_backtest_summary.csv", "Level shifts from new wells not anticipated"),
]

def w(name, text):
    (OUT / name).write_text(text, encoding="utf-8")

def main():
    OUT.mkdir(exist_ok=True)
    w("user_stories.md", "# User Stories\n\n" + NOTE + "\n" + "\n".join(
        f"## {s[0]} - {s[1]}\n**As a** {s[1]}, **I want to** {s[2]}, **so that** {s[3]}.\n\n- Business requirements: {s[4]}\n- Functional requirements: {s[5]}\n- Delivered by: {s[6]}\n- Priority: {'Must' if i < 22 else 'Should'}\n" for i, s in enumerate(STORIES)))
    w("acceptance_criteria.md", "# Acceptance Criteria\n\n" + NOTE + "\n" + "\n".join(f"## {s[0]}\n" + "\n".join(f"{k}. {a}" for k, a in enumerate(s[7], 1)) + "\n" for s in STORIES))
    tests = {"US-01": "tests/test_kpis.py", "US-02": "tests/test_kpis.py", "US-03": "tests/test_kpis.py", "US-04": "tests/test_kpis.py", "US-06": "tests/test_kpis.py", "US-12": "tests/test_kpis.py", "US-13": "tests/test_kpis.py", "US-23": "tests/test_forecasting.py", "US-24": "tests/test_ml.py", "US-25": "tests/test_validation.py", "US-26": "tests/test_cleaning.py", "US-28": "tests/test_real_data.py", "US-27": "tests/test_sql_schema.py"}
    rows = "\n".join(f"| {s[4]} | {s[5]} | {s[0]} | {s[6]} | {tests.get(s[0], 'UAT only')} | UAT-{i + 1:02d} |" for i, s in enumerate(STORIES))
    w("requirements_traceability_matrix.md", "# Requirements Traceability Matrix\n\n" + NOTE + "\nBR = business requirement, FR = functional requirement, US = user story. 'UAT only' means the story is verified manually in uat_test_cases.md.\n\n| BR | FR | Story | Implementation artifact | Automated test | UAT case |\n|---|---|---|---|---|---|\n" + rows + "\n\n## FR coverage\n\n| FR | Requirement | Implementation |\n|---|---|---|\n" + "\n".join(f"| {f[0]} | {f[1]} | {f[3]} |" for f in FR))
    w("BRD.md", f"""# Business Requirements Document (BRD)

{NOTE}
## 1. Purpose
PetroNexa Energy (fictional) wants one analytics platform that links production, maintenance, finance, inventory, HSE and sensor data so managers can find where production and money are lost and where risk is concentrated.

## 2. Business context and problem statement
Operational data live in separate systems (production allocation, maintenance work orders, ERP costs, warehouse stock, HSE logs, sensor historian). Reports are assembled manually, definitions differ between teams, and data quality issues (duplicates, unit mix-ups, missing values, naming variants) erode trust. As a result leaders cannot answer basic questions consistently, such as how much production is lost to downtime and what it costs.

## 3. Objectives
1. Provide governed KPI definitions and a single relational model (BR-01 to BR-08).
2. Make data quality visible and repeatable (BR-09).
3. Provide baseline forecasting and failure-risk scoring with honest accuracy reporting (BR-10, BR-11).
4. Provide self-service outputs: SQL, dashboard specifications, Excel, Streamlit (BR-12).
5. Demonstrate the same analytical methods on separate real datasets without mixing them into the fictional company (BR-13).

## 4. Business requirements
| ID | Requirement | Success statement |
|---|---|---|
""" + "\n".join(f"| {b[0]} | {b[1]} | {b[2]} |" for b in BR) + """

## 5. Scope
**In scope:** synthetic PetroNexa dataset (4 fields, 60 wells, 48 equipment units, 3 years daily), data quality pipeline, KPIs, analytics, forecasting baseline, failure-risk model, PostgreSQL model and queries, BI specifications, Excel, Streamlit app, real-data case studies (Volve, BSEE OGOR-A).

**Out of scope:** real-time streaming, reservoir simulation, economic evaluation with capex/tax/royalty, integration with production systems, real company data, use of OGOR-B/C files.

## 6. Success criteria (measurable in this project)
- Processed data passes 100% of the implemented validation checks (see data quality report).
- Every KPI in the KPI dictionary is reproducible in Python and SQL.
- Tests pass and every claimed metric is produced by code (no manually typed results).

## 7. Constraints, assumptions, risks
See assumptions_and_constraints.md and risk_register.md.

## 8. Approval
This is a portfolio document; there is no real sign-off. Stakeholders are illustrative (see stakeholder_analysis.md).
""")
    w("FRD.md", "# Functional Requirements Document (FRD)\n\n" + NOTE + "\n| ID | Functional requirement | Supports | Implementation |\n|---|---|---|---|\n" + "\n".join(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} |" for f in FR) + """

## Non-functional requirements
| ID | Requirement |
|---|---|
| NFR-01 | Reproducibility: fixed seed 42; regenerating gives identical content hashes (data/reference/generation_manifest.json) |
| NFR-02 | No credentials in code; database settings via environment variables |
| NFR-03 | Full pipeline runs on a single CPU in minutes with pandas/numpy/scikit-learn/scipy/matplotlib |
| NFR-04 | Every synthetic output carries a synthetic-data notice; every real-data output carries a real-data label |
| NFR-05 | Raw data are never overwritten by cleaning |
""")
    w("kpi_dictionary.md", "# KPI Dictionary\n\n" + NOTE + "\n| KPI | Definition | Formula | Grain | Source | Caveat |\n|---|---|---|---|---|---|\n" + "\n".join("| " + " | ".join(k) + " |" for k in KPIS))

    uat = []
    for i, s in enumerate(STORIES, 1):
        uat.append(f"## UAT-{i:02d} ({s[0]})\n- **Objective:** verify that the {s[1]} can {s[2]}.\n- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.\n- **Steps:** open {s[6]}; check each acceptance criterion in acceptance_criteria.md for {s[0]}.\n- **Expected result:** " + "; ".join(a.split(", then ")[-1] if ", then " in a else a for a in s[7]) + ".\n- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).\n")
    w("uat_test_cases.md", "# UAT Test Cases\n\n" + NOTE + "\nThese are prepared scripts. No business user has executed them; automated tests are listed in the traceability matrix.\n\n" + "\n".join(uat))

if __name__ == "__main__":
    main()
