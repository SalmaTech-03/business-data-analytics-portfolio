# UAT Test Cases

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.
> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.

These are prepared scripts. No business user has executed them; automated tests are listed in the traceability matrix.

## UAT-01 (US-01)
- **Objective:** verify that the Operations Manager can see monthly oil, gas and water production by field.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q01,Q02; charts production_trend_by_field; check each acceptance criterion in acceptance_criteria.md for US-01.
- **Expected result:** totals equal the sum of well-day rows; Each field appears for every month with production; Units (bbl, mcf) are labelled.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-02 (US-02)
- **Objective:** verify that the Operations Manager can rank wells by total loss and by loss percentage.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q03,Q06; analytics.production.by_well; check each acceptance criterion in acceptance_criteria.md for US-02.
- **Expected result:** Both rank metrics are defined in the output columns; Ranks are deterministic for ties (method=min).
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-03 (US-03)
- **Objective:** verify that the Production Engineer can see production loss split into downtime-related and other loss.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open mart_well_daily; chart loss_decomposition_monthly; check each acceptance criterion in acceptance_criteria.md for US-03.
- **Expected result:** downtime_loss + other_loss = production_loss for every row; Loss is never negative.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-04 (US-04)
- **Objective:** verify that the Production Engineer can estimate well decline rates.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open analytics.production.decline_analysis; check each acceptance criterion in acceptance_criteria.md for US-04.
- **Expected result:** Output includes months used, R-squared and p-value; Wells with fewer than 18 months are excluded and stated.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-05 (US-05)
- **Objective:** verify that the Production Engineer can track water cut and pressure trends.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q07,Q09,Q10; check each acceptance criterion in acceptance_criteria.md for US-05.
- **Expected result:** Water cut is volume-weighted at field level; Values stay within 0-100%.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-06 (US-06)
- **Objective:** verify that the Reliability Engineer can see MTBF, MTTR and availability by equipment and type.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q12; mart_equipment_summary; check each acceptance criterion in acceptance_criteria.md for US-06.
- **Expected result:** MTBF = operating hours / failures; MTTR = corrective downtime / failures; Units with zero failures show blank MTBF, not zero.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-07 (US-07)
- **Objective:** verify that the Reliability Engineer can see failure modes by equipment type.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q13; maintenance_by_failure_type.csv; check each acceptance criterion in acceptance_criteria.md for US-07.
- **Expected result:** Only corrective events count as failures; Counts reconcile with total failure KPI.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-08 (US-08)
- **Objective:** verify that the Maintenance Manager can get a ranked list of priority equipment.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql BQ09; critical_equipment_top10.csv; check each acceptance criterion in acceptance_criteria.md for US-08.
- **Expected result:** Score = criticality weight x downtime hours (weights High 3, Medium 2, Low 1); Formula is displayed next to the ranking.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-09 (US-09)
- **Objective:** verify that the Maintenance Manager can compare preventive and corrective cost and downtime.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q15,Q16,BQ05; check each acceptance criterion in acceptance_criteria.md for US-09.
- **Expected result:** Shares sum to 100%; Corrective and preventive are never mixed in one bucket.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-10 (US-10)
- **Objective:** verify that the Reliability Engineer can identify repeat failures within 30 days.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q18,Q19; check each acceptance criterion in acceptance_criteria.md for US-10.
- **Expected result:** Repeat interval is measured between consecutive corrective events on the same equipment.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-11 (US-11)
- **Objective:** verify that the Maintenance Manager can see maintenance cost concentration (Pareto).
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q17; maintenance_cost_pareto.csv; check each acceptance criterion in acceptance_criteria.md for US-11.
- **Expected result:** Cumulative share reaches 100% at the last unit.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-12 (US-12)
- **Objective:** verify that the Finance Analyst can see revenue, opex and margin by field and year.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q22; financial_by_field.csv; check each acceptance criterion in acceptance_criteria.md for US-12.
- **Expected result:** margin = revenue - opex; Currency and synthetic status are stated.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-13 (US-13)
- **Objective:** verify that the Finance Analyst can see cost per barrel and per BOE.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q23; kpi_dictionary; check each acceptance criterion in acceptance_criteria.md for US-13.
- **Expected result:** Cost per bbl = total opex / oil bbl sold (gas not netted); BOE uses 6 mcf per BOE.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-14 (US-14)
- **Objective:** verify that the Finance Analyst can see opex by category.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q24; cost_breakdown.csv; check each acceptance criterion in acceptance_criteria.md for US-14.
- **Expected result:** Category shares sum to 100%.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-15 (US-15)
- **Objective:** verify that the Finance Analyst can estimate revenue lost to production loss.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q25,BQ01; check each acceptance criterion in acceptance_criteria.md for US-15.
- **Expected result:** Uses the realised oil price of the same field and day; Method is documented as an estimate.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-16 (US-16)
- **Objective:** verify that the Supply Chain Analyst can see stockout rate by material category.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q27; inventory_by_category.csv; check each acceptance criterion in acceptance_criteria.md for US-16.
- **Expected result:** Stockout rate = stockout item-days / item-warehouse-days.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-17 (US-17)
- **Objective:** verify that the Supply Chain Analyst can list items at or below reorder level.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q29; low_stock_items.csv; check each acceptance criterion in acceptance_criteria.md for US-17.
- **Expected result:** List is evaluated on the last inventory date.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-18 (US-18)
- **Objective:** verify that the Supply Chain Analyst can identify excess inventory.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q33; excess_inventory.csv; check each acceptance criterion in acceptance_criteria.md for US-18.
- **Expected result:** Threshold (90 days of inventory) is an explicit assumption.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-19 (US-19)
- **Objective:** verify that the Procurement Lead can compare supplier on-time delivery and lead time.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q31,Q32; supplier_performance.csv; check each acceptance criterion in acceptance_criteria.md for US-19.
- **Expected result:** Only received purchase orders are scored; On time means received on or before promised date.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-20 (US-20)
- **Objective:** verify that the Procurement Lead can see open purchase orders past promise date.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q34; check each acceptance criterion in acceptance_criteria.md for US-20.
- **Expected result:** Open orders have no received date.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-21 (US-21)
- **Objective:** verify that the HSE Lead can see incidents by field, severity and root cause.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q36,Q38; check each acceptance criterion in acceptance_criteria.md for US-21.
- **Expected result:** Severity uses the controlled list Low/Medium/High/Critical.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-22 (US-22)
- **Objective:** verify that the HSE Lead can see incident rates per 200,000 exposure hours.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open sql Q37; mart_hse_monthly; check each acceptance criterion in acceptance_criteria.md for US-22.
- **Expected result:** Exposure hours assumption is stated with the metric.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-23 (US-23)
- **Objective:** verify that the Planning Analyst can get a 30-day production forecast with backtest errors.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open forecast_next_30d.csv; forecast_backtest_summary.csv; check each acceptance criterion in acceptance_criteria.md for US-23.
- **Expected result:** Backtest uses rolling origins without look-ahead; MAE, RMSE, MAPE and bias are reported per model.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-24 (US-24)
- **Objective:** verify that the Reliability Engineer can see equipment failure-risk scores.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open ml_latest_equipment_risk.csv; ml_model_metrics_test.csv; check each acceptance criterion in acceptance_criteria.md for US-24.
- **Expected result:** Split is time-based; Threshold is chosen on validation data only; Report states data are synthetic.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-25 (US-25)
- **Objective:** verify that the Data Steward can see a data quality report with defects found, fixed and residual.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open reports/data_quality_report.md; check each acceptance criterion in acceptance_criteria.md for US-25.
- **Expected result:** Report numbers come from validation results; Quarantined rows are counted.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-26 (US-26)
- **Objective:** verify that the Data Steward can trace every cleaning action.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open data/processed/cleaning_log.json; check each acceptance criterion in acceptance_criteria.md for US-26.
- **Expected result:** Each action has a count; Raw files are never modified.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-27 (US-27)
- **Objective:** verify that the Executive can open a dashboard with KPIs across production, maintenance, finance, inventory and HSE.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open powerbi/*, tableau/*, app/streamlit_app.py, Excel; check each acceptance criterion in acceptance_criteria.md for US-27.
- **Expected result:** Specifications define measures and page layouts; Synthetic-data notice is visible on every page.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).

## UAT-28 (US-28)
- **Objective:** verify that the Portfolio Reviewer can see Volve and BSEE analyses kept separate from the fictional company.
- **Preconditions:** pipeline executed (`scripts/run_all.py`); outputs in reports/tables and data/marts.
- **Steps:** open reports/real_data_case_studies.md; check each acceptance criterion in acceptance_criteria.md for US-28.
- **Expected result:** No real record is merged into PetroNexa tables; Assumptions about BSEE column meaning are stated.
- **Status:** Not executed by a business user (no real UAT was performed for this portfolio project).
