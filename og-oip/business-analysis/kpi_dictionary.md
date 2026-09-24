# KPI Dictionary

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.
> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.

| KPI | Definition | Formula | Grain | Source | Caveat |
|---|---|---|---|---|---|
| Oil production (bbl) | Reported oil volume | SUM(oil_production_bbl) | well-day | fact_production | Imputed rows flagged in dq_flag |
| Production potential (bbl) | SIMULATED unconstrained rate from decline curve | SUM(potential_production_bbl) | well-day | fact_production | Synthetic construct, no real-world equivalent |
| Production loss (bbl) | Potential minus actual, floored at 0 | SUM(MAX(potential - oil, 0)) | well-day | mart_well_daily | Depends on the simulated potential |
| Production loss % | Loss share of potential | SUM(loss) / SUM(potential) | any | mart_well_daily |  |
| Downtime loss (bbl) | Loss attributable to hours down | MIN(potential x downtime_hours/24, loss) | well-day | mart_well_daily | Remaining loss is 'other (efficiency) loss' |
| Maintenance-associated downtime share | Well downtime hours explained by maintenance events | SUM(attributed hours) / SUM(downtime_hours) | any | mart_well_daily | Assumes downtime starts on maintenance date and spills at <=24 h/day |
| Water cut % | Water share of liquids | 100 x water / (water + oil) | any (volume-weighted) | fact_production | Never average row-level percentages for aggregates |
| Nominal annual decline % | Exponential decline from log-linear fit of monthly mean rate | 100 x (1 - exp(12 x slope)) | well | well_decline_analysis.csv | Workovers and downtime contaminate the fit |
| Failure | Corrective maintenance event | COUNT(maintenance_type = 'Corrective') | equipment | fact_maintenance |  |
| Availability % | Share of period not in maintenance downtime | 100 x (period_hours - downtime_hours) / period_hours | equipment | fact_maintenance | Period = 1096 days x 24 h |
| MTBF (h) | Mean operating hours between failures | (period_hours - downtime_hours) / failures | equipment / type | fact_maintenance | Blank when failures = 0 |
| MTTR (h) | Mean corrective downtime per failure | corrective downtime_hours / failures | equipment / type | fact_maintenance |  |
| Priority score | Criticality-weighted downtime | weight(High 3, Medium 2, Low 1) x total downtime_hours | equipment | mart_equipment_summary | Weights are an assumption |
| Opex (USD) | Operating cost | SUM(cost_amount_usd) | field-day-category | fact_operating_cost | Synthetic cost model |
| Cost per bbl oil sold | Unit cost | opex / oil_volume_bbl | field-month | v_field_financial_monthly | Gas revenue not netted |
| Cost per BOE sold | Unit cost per BOE | opex / (oil bbl + gas mcf / 6) | field-month | mart_field_monthly | 6 mcf = 1 BOE convention |
| Operating margin (USD) | Revenue less opex | revenue_usd - opex | field-month | mart_field_monthly | No capex, tax or royalty |
| Estimated lost revenue (USD) | Loss valued at realised price | production_loss_bbl x oil_price_usd | well-day | mart_well_daily | Estimate |
| Stockout rate % | Share of item-warehouse-days with unmet demand | 100 x SUM(stockout_flag) / COUNT(rows) | any | fact_inventory |  |
| Inventory turnover (annualised) | Consumption value over average stock value | consumption_value / avg_stock_value / years | material-warehouse | mart_inventory |  |
| Days of inventory | Cover at average consumption | avg closing stock / avg daily consumption | material-warehouse | mart_inventory | Infinite/blank if no consumption |
| Supplier on-time % | Received on or before promised date | 100 x AVG(received_date <= promised_date) | supplier | fact_purchase_order | Received orders only |
| Lead-time gap (d) | Actual minus quoted lead time | AVG(received - order) - AVG(quoted_lead_time_days) | supplier | fact_purchase_order |  |
| Incident rate per 200k h | Incidents normalised by exposure | incidents x 200000 / exposure_hours | field-month | mart_hse_monthly | Exposure = 30 h x producing well-days (assumption) |
| Lost-time incident rate | Lost-time incidents normalised | LTI x 200000 / exposure_hours | field-month | mart_hse_monthly | Same exposure assumption |
| Failure risk score (7d) | Model probability of corrective failure within 7 days | model.predict_proba | equipment-day | ml_latest_equipment_risk.csv | Synthetic sensors; moderate precision/recall |
| Forecast error (MAE/RMSE/MAPE/bias) | Backtest accuracy | rolling-origin, 30-day horizon | portfolio-day | forecast_backtest_summary.csv | Level shifts from new wells not anticipated |