# Acceptance Criteria

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.
> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.

## US-01
1. Given processed data, when I view monthly production by field, then totals equal the sum of well-day rows
2. Each field appears for every month with production
3. Units (bbl, mcf) are labelled

## US-02
1. Both rank metrics are defined in the output columns
2. Ranks are deterministic for ties (method=min)

## US-03
1. downtime_loss + other_loss = production_loss for every row
2. Loss is never negative

## US-04
1. Output includes months used, R-squared and p-value
2. Wells with fewer than 18 months are excluded and stated

## US-05
1. Water cut is volume-weighted at field level
2. Values stay within 0-100%

## US-06
1. MTBF = operating hours / failures; MTTR = corrective downtime / failures
2. Units with zero failures show blank MTBF, not zero

## US-07
1. Only corrective events count as failures
2. Counts reconcile with total failure KPI

## US-08
1. Score = criticality weight x downtime hours (weights High 3, Medium 2, Low 1)
2. Formula is displayed next to the ranking

## US-09
1. Shares sum to 100%
2. Corrective and preventive are never mixed in one bucket

## US-10
1. Repeat interval is measured between consecutive corrective events on the same equipment

## US-11
1. Cumulative share reaches 100% at the last unit

## US-12
1. margin = revenue - opex
2. Currency and synthetic status are stated

## US-13
1. Cost per bbl = total opex / oil bbl sold (gas not netted)
2. BOE uses 6 mcf per BOE

## US-14
1. Category shares sum to 100%

## US-15
1. Uses the realised oil price of the same field and day
2. Method is documented as an estimate

## US-16
1. Stockout rate = stockout item-days / item-warehouse-days

## US-17
1. List is evaluated on the last inventory date

## US-18
1. Threshold (90 days of inventory) is an explicit assumption

## US-19
1. Only received purchase orders are scored
2. On time means received on or before promised date

## US-20
1. Open orders have no received date

## US-21
1. Severity uses the controlled list Low/Medium/High/Critical

## US-22
1. Exposure hours assumption is stated with the metric

## US-23
1. Backtest uses rolling origins without look-ahead
2. MAE, RMSE, MAPE and bias are reported per model

## US-24
1. Split is time-based
2. Threshold is chosen on validation data only
3. Report states data are synthetic

## US-25
1. Report numbers come from validation results
2. Quarantined rows are counted

## US-26
1. Each action has a count
2. Raw files are never modified

## US-27
1. Specifications define measures and page layouts
2. Synthetic-data notice is visible on every page

## US-28
1. No real record is merged into PetroNexa tables
2. Assumptions about BSEE column meaning are stated
