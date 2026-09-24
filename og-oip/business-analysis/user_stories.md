# User Stories

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.
> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.

## US-01 - Operations Manager
**As a** Operations Manager, **I want to** see monthly oil, gas and water production by field, **so that** I can spot production trends early.

- Business requirements: BR-01
- Functional requirements: FR-05,FR-06
- Delivered by: sql Q01,Q02; charts production_trend_by_field
- Priority: Must

## US-02 - Operations Manager
**As a** Operations Manager, **I want to** rank wells by total loss and by loss percentage, **so that** I know where recovery effort should focus.

- Business requirements: BR-02
- Functional requirements: FR-07
- Delivered by: sql Q03,Q06; analytics.production.by_well
- Priority: Must

## US-03 - Production Engineer
**As a** Production Engineer, **I want to** see production loss split into downtime-related and other loss, **so that** I can target the right lever.

- Business requirements: BR-02
- Functional requirements: FR-05,FR-06
- Delivered by: mart_well_daily; chart loss_decomposition_monthly
- Priority: Must

## US-04 - Production Engineer
**As a** Production Engineer, **I want to** estimate well decline rates, **so that** I can flag wells declining faster than peers.

- Business requirements: BR-01
- Functional requirements: FR-06
- Delivered by: analytics.production.decline_analysis
- Priority: Must

## US-05 - Production Engineer
**As a** Production Engineer, **I want to** track water cut and pressure trends, **so that** I can identify water-management candidates.

- Business requirements: BR-01
- Functional requirements: FR-06
- Delivered by: sql Q07,Q09,Q10
- Priority: Must

## US-06 - Reliability Engineer
**As a** Reliability Engineer, **I want to** see MTBF, MTTR and availability by equipment and type, **so that** I can compare reliability.

- Business requirements: BR-03
- Functional requirements: FR-09
- Delivered by: sql Q12; mart_equipment_summary
- Priority: Must

## US-07 - Reliability Engineer
**As a** Reliability Engineer, **I want to** see failure modes by equipment type, **so that** I can direct root-cause work.

- Business requirements: BR-03
- Functional requirements: FR-09
- Delivered by: sql Q13; maintenance_by_failure_type.csv
- Priority: Must

## US-08 - Maintenance Manager
**As a** Maintenance Manager, **I want to** get a ranked list of priority equipment, **so that** I can plan crews and spares.

- Business requirements: BR-04
- Functional requirements: FR-10
- Delivered by: sql BQ09; critical_equipment_top10.csv
- Priority: Must

## US-09 - Maintenance Manager
**As a** Maintenance Manager, **I want to** compare preventive and corrective cost and downtime, **so that** I can judge the preventive programme.

- Business requirements: BR-04
- Functional requirements: FR-09
- Delivered by: sql Q15,Q16,BQ05
- Priority: Must

## US-10 - Reliability Engineer
**As a** Reliability Engineer, **I want to** identify repeat failures within 30 days, **so that** I can find ineffective repairs.

- Business requirements: BR-03
- Functional requirements: FR-09
- Delivered by: sql Q18,Q19
- Priority: Must

## US-11 - Maintenance Manager
**As a** Maintenance Manager, **I want to** see maintenance cost concentration (Pareto), **so that** I can focus on the costliest units.

- Business requirements: BR-04
- Functional requirements: FR-10
- Delivered by: sql Q17; maintenance_cost_pareto.csv
- Priority: Must

## US-12 - Finance Analyst
**As a** Finance Analyst, **I want to** see revenue, opex and margin by field and year, **so that** I can review profitability.

- Business requirements: BR-05
- Functional requirements: FR-11
- Delivered by: sql Q22; financial_by_field.csv
- Priority: Must

## US-13 - Finance Analyst
**As a** Finance Analyst, **I want to** see cost per barrel and per BOE, **so that** I can track unit economics.

- Business requirements: BR-05
- Functional requirements: FR-11
- Delivered by: sql Q23; kpi_dictionary
- Priority: Must

## US-14 - Finance Analyst
**As a** Finance Analyst, **I want to** see opex by category, **so that** I can see cost drivers.

- Business requirements: BR-05
- Functional requirements: FR-11
- Delivered by: sql Q24; cost_breakdown.csv
- Priority: Must

## US-15 - Finance Analyst
**As a** Finance Analyst, **I want to** estimate revenue lost to production loss, **so that** I can prioritise by value.

- Business requirements: BR-02,BR-05
- Functional requirements: FR-12
- Delivered by: sql Q25,BQ01
- Priority: Must

## US-16 - Supply Chain Analyst
**As a** Supply Chain Analyst, **I want to** see stockout rate by material category, **so that** I can adjust reorder policy.

- Business requirements: BR-06
- Functional requirements: FR-13
- Delivered by: sql Q27; inventory_by_category.csv
- Priority: Must

## US-17 - Supply Chain Analyst
**As a** Supply Chain Analyst, **I want to** list items at or below reorder level, **so that** I can trigger orders.

- Business requirements: BR-06
- Functional requirements: FR-13
- Delivered by: sql Q29; low_stock_items.csv
- Priority: Must

## US-18 - Supply Chain Analyst
**As a** Supply Chain Analyst, **I want to** identify excess inventory, **so that** I can release working capital.

- Business requirements: BR-06
- Functional requirements: FR-13
- Delivered by: sql Q33; excess_inventory.csv
- Priority: Must

## US-19 - Procurement Lead
**As a** Procurement Lead, **I want to** compare supplier on-time delivery and lead time, **so that** I can manage suppliers.

- Business requirements: BR-07
- Functional requirements: FR-14
- Delivered by: sql Q31,Q32; supplier_performance.csv
- Priority: Must

## US-20 - Procurement Lead
**As a** Procurement Lead, **I want to** see open purchase orders past promise date, **so that** I can chase deliveries.

- Business requirements: BR-07
- Functional requirements: FR-14
- Delivered by: sql Q34
- Priority: Must

## US-21 - HSE Lead
**As a** HSE Lead, **I want to** see incidents by field, severity and root cause, **so that** I can target safety actions.

- Business requirements: BR-08
- Functional requirements: FR-15
- Delivered by: sql Q36,Q38
- Priority: Must

## US-22 - HSE Lead
**As a** HSE Lead, **I want to** see incident rates per 200,000 exposure hours, **so that** I can normalise across fields.

- Business requirements: BR-08
- Functional requirements: FR-15
- Delivered by: sql Q37; mart_hse_monthly
- Priority: Must

## US-23 - Planning Analyst
**As a** Planning Analyst, **I want to** get a 30-day production forecast with backtest errors, **so that** I can use it with known accuracy.

- Business requirements: BR-10
- Functional requirements: FR-17
- Delivered by: forecast_next_30d.csv; forecast_backtest_summary.csv
- Priority: Should

## US-24 - Reliability Engineer
**As a** Reliability Engineer, **I want to** see equipment failure-risk scores, **so that** I can plan inspections.

- Business requirements: BR-11
- Functional requirements: FR-18
- Delivered by: ml_latest_equipment_risk.csv; ml_model_metrics_test.csv
- Priority: Should

## US-25 - Data Steward
**As a** Data Steward, **I want to** see a data quality report with defects found, fixed and residual, **so that** I can trust the analytics.

- Business requirements: BR-09
- Functional requirements: FR-02,FR-03,FR-04
- Delivered by: reports/data_quality_report.md
- Priority: Should

## US-26 - Data Steward
**As a** Data Steward, **I want to** trace every cleaning action, **so that** I can audit changes.

- Business requirements: BR-09
- Functional requirements: FR-03
- Delivered by: data/processed/cleaning_log.json
- Priority: Should

## US-27 - Executive
**As a** Executive, **I want to** open a dashboard with KPIs across production, maintenance, finance, inventory and HSE, **so that** I get one view of performance.

- Business requirements: BR-12
- Functional requirements: FR-19..FR-22
- Delivered by: powerbi/*, tableau/*, app/streamlit_app.py, Excel
- Priority: Should

## US-28 - Portfolio Reviewer
**As a** Portfolio Reviewer, **I want to** see Volve and BSEE analyses kept separate from the fictional company, **so that** I can judge real-data methodology.

- Business requirements: BR-13
- Functional requirements: FR-23,FR-24
- Delivered by: reports/real_data_case_studies.md
- Priority: Should
