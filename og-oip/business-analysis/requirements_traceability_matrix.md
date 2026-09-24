# Requirements Traceability Matrix

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.
> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.

BR = business requirement, FR = functional requirement, US = user story. 'UAT only' means the story is verified manually in uat_test_cases.md.

| BR | FR | Story | Implementation artifact | Automated test | UAT case |
|---|---|---|---|---|---|
| BR-01 | FR-05,FR-06 | US-01 | sql Q01,Q02; charts production_trend_by_field | tests/test_kpis.py | UAT-01 |
| BR-02 | FR-07 | US-02 | sql Q03,Q06; analytics.production.by_well | tests/test_kpis.py | UAT-02 |
| BR-02 | FR-05,FR-06 | US-03 | mart_well_daily; chart loss_decomposition_monthly | tests/test_kpis.py | UAT-03 |
| BR-01 | FR-06 | US-04 | analytics.production.decline_analysis | tests/test_kpis.py | UAT-04 |
| BR-01 | FR-06 | US-05 | sql Q07,Q09,Q10 | UAT only | UAT-05 |
| BR-03 | FR-09 | US-06 | sql Q12; mart_equipment_summary | tests/test_kpis.py | UAT-06 |
| BR-03 | FR-09 | US-07 | sql Q13; maintenance_by_failure_type.csv | UAT only | UAT-07 |
| BR-04 | FR-10 | US-08 | sql BQ09; critical_equipment_top10.csv | UAT only | UAT-08 |
| BR-04 | FR-09 | US-09 | sql Q15,Q16,BQ05 | UAT only | UAT-09 |
| BR-03 | FR-09 | US-10 | sql Q18,Q19 | UAT only | UAT-10 |
| BR-04 | FR-10 | US-11 | sql Q17; maintenance_cost_pareto.csv | UAT only | UAT-11 |
| BR-05 | FR-11 | US-12 | sql Q22; financial_by_field.csv | tests/test_kpis.py | UAT-12 |
| BR-05 | FR-11 | US-13 | sql Q23; kpi_dictionary | tests/test_kpis.py | UAT-13 |
| BR-05 | FR-11 | US-14 | sql Q24; cost_breakdown.csv | UAT only | UAT-14 |
| BR-02,BR-05 | FR-12 | US-15 | sql Q25,BQ01 | UAT only | UAT-15 |
| BR-06 | FR-13 | US-16 | sql Q27; inventory_by_category.csv | UAT only | UAT-16 |
| BR-06 | FR-13 | US-17 | sql Q29; low_stock_items.csv | UAT only | UAT-17 |
| BR-06 | FR-13 | US-18 | sql Q33; excess_inventory.csv | UAT only | UAT-18 |
| BR-07 | FR-14 | US-19 | sql Q31,Q32; supplier_performance.csv | UAT only | UAT-19 |
| BR-07 | FR-14 | US-20 | sql Q34 | UAT only | UAT-20 |
| BR-08 | FR-15 | US-21 | sql Q36,Q38 | UAT only | UAT-21 |
| BR-08 | FR-15 | US-22 | sql Q37; mart_hse_monthly | UAT only | UAT-22 |
| BR-10 | FR-17 | US-23 | forecast_next_30d.csv; forecast_backtest_summary.csv | tests/test_forecasting.py | UAT-23 |
| BR-11 | FR-18 | US-24 | ml_latest_equipment_risk.csv; ml_model_metrics_test.csv | tests/test_ml.py | UAT-24 |
| BR-09 | FR-02,FR-03,FR-04 | US-25 | reports/data_quality_report.md | tests/test_validation.py | UAT-25 |
| BR-09 | FR-03 | US-26 | data/processed/cleaning_log.json | tests/test_cleaning.py | UAT-26 |
| BR-12 | FR-19..FR-22 | US-27 | powerbi/*, tableau/*, app/streamlit_app.py, Excel | tests/test_sql_schema.py | UAT-27 |
| BR-13 | FR-23,FR-24 | US-28 | reports/real_data_case_studies.md | tests/test_real_data.py | UAT-28 |

## FR coverage

| FR | Requirement | Implementation |
|---|---|---|
| FR-01 | Generate a relationally consistent synthetic dataset (8 dimension/bridge tables, 9 fact tables) reproducible from a seed | src/og_oip/data_generation/*, scripts/generate_data.py |
| FR-02 | Produce a raw dataset with documented injected defects and a defect log | src/og_oip/data_generation/defects.py, data/reference/defect_injection_log.json |
| FR-03 | Clean raw data into processed tables; quarantine unrepairable rows; log every action | src/og_oip/cleaning/cleaners.py, scripts/clean_data.py |
| FR-04 | Run validation checks (keys, nulls, ranges, dates, referential, domains, units, logic) and publish a data quality report from actual results | src/og_oip/validation/*, reports/data_quality_report.md |
| FR-05 | Build analytical marts (well-day, field-month, equipment, sensor-day, inventory, supplier, HSE) | src/og_oip/transformation/marts.py |
| FR-06 | Report production, loss (downtime vs other), decline and pressure/water-cut trends | src/og_oip/analytics/production.py |
| FR-07 | Rank wells by defined metrics (loss bbl, loss %, avg rate) with explicit definitions | analytics/production.py::by_well |
| FR-08 | Associate downtime with maintenance events through the equipment-well bridge | transformation/marts.py::attributed_downtime |
| FR-09 | Compute MTBF, MTTR, availability, failure counts by equipment and type | analytics/maintenance.py, marts.build_mart_equipment_summary |
| FR-10 | Produce a criticality-weighted maintenance priority ranking with an explicit formula | analytics/maintenance.py::critical_equipment |
| FR-11 | Compute cost per bbl, cost per BOE, margin and cost breakdown by field/year | analytics/financial.py |
| FR-12 | Estimate revenue impact of production loss using realised daily oil price | marts.build_mart_well_daily |
| FR-13 | Compute inventory KPIs: stockout rate, turnover, days of inventory, low stock, excess stock | analytics/inventory.py |
| FR-14 | Compute supplier on-time %, quoted vs actual lead time from purchase orders | marts.build_mart_supplier_performance |
| FR-15 | Compute HSE incident counts, lost-time counts, rates per 200,000 assumed exposure hours, root-cause distribution | analytics/hse.py |
| FR-16 | Quantify associations (Spearman) between operational factors and outcomes, labelled as association not causation | analytics/* |
| FR-17 | Backtest naive, moving-average, exponential-smoothing and AR models with rolling origins; report MAE/RMSE/MAPE/bias | src/og_oip/forecasting/models.py |
| FR-18 | Train and evaluate failure-risk models with time-based splits and real (not fabricated) metrics | src/og_oip/ml/predictive_maintenance.py |
| FR-19 | Provide 40+ PostgreSQL analytical queries, views and a load script | sql/* |
| FR-20 | Provide Power BI and Tableau build specifications (no fabricated binary files) | powerbi/*, tableau/* |
| FR-21 | Provide an Excel workbook with live formulas | excel/OG_OIP_Analysis_Workbook.xlsx |
| FR-22 | Provide a Streamlit exploration app | app/streamlit_app.py |
| FR-23 | Analyse Volve production data separately (conversions, reconciliation, decline, water cut, forecast backtest) | src/og_oip/real_data/volve.py |
| FR-24 | Analyse BSEE OGOR-A data separately (monthly totals, operator concentration, areas, quality checks) | src/og_oip/real_data/bsee.py |
| FR-25 | Provide automated tests for generation, cleaning, validation, KPIs, forecasting, ML, SQL schema, real-data loaders | tests/* |
| FR-26 | Provide reproducible pipeline entry points and documentation of assumptions and limitations | scripts/*, README.md, docs/* |