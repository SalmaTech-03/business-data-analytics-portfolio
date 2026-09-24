# Calculated Fields (Tableau)

> Synthetic data (fictional PetroNexa Energy). Specification only; no .twb/.twbx file is provided because none can be produced or verified in the build environment.

| Field | Data source | Formula |
|---|---|---|
| Production Loss % | Well Daily | SUM([production_loss_bbl]) / SUM([potential_production_bbl]) |
| Downtime Share of Loss | Well Daily | SUM([downtime_loss_bbl]) / SUM([production_loss_bbl]) |
| Water Cut % | Well Daily | 100 * SUM([water_production_bbl]) / (SUM([water_production_bbl]) + SUM([oil_production_bbl])) |
| Avg Daily Oil | Well Daily | SUM([oil_production_bbl]) / COUNTD([date]) |
| Maintenance-Associated Downtime % | Well Daily | SUM([maintenance_attributed_downtime_hours]) / SUM([downtime_hours]) |
| Cost per bbl Oil Sold | Field Monthly | SUM([opex_total_usd]) / SUM([oil_sold_bbl]) |
| Cost per BOE | Field Monthly | SUM([opex_total_usd]) / (SUM([oil_sold_bbl]) + SUM([gas_sold_mcf]) / 6) |
| Operating Margin | Field Monthly | SUM([revenue_usd]) - SUM([opex_total_usd]) |
| Fleet Availability % | Equipment Summary | 100 * SUM([operating_hours]) / SUM([period_hours]) |
| Fleet MTBF | Equipment Summary | SUM([operating_hours]) / SUM([failures]) |
| Fleet MTTR | Equipment Summary | SUM([corrective_downtime_hours]) / SUM([failures]) |
| Criticality Weight | Equipment Summary | CASE [criticality] WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END |
| Priority Score | Equipment Summary | [Criticality Weight] * SUM([total_downtime_hours]) |
| Stockout Rate % | Inventory | 100 * SUM([stockout_days]) / SUM([days]) |
| Excess Flag | Inventory | IF [days_of_inventory] > [Excess Days Threshold] THEN "Excess" ELSE "OK" END (parameter default 90) |
| Supplier On-Time % | Supplier Performance | SUM([on_time_pct] * [pos_received]) / SUM([pos_received]) |
| Lead Time Gap | Supplier Performance | AVG([avg_actual_lead_days]) - AVG([avg_quoted_lead_days]) |
| Incident Rate per 200k h | HSE Monthly | SUM([incidents]) * 200000 / SUM([exposure_hours]) |
| LTI Rate per 200k h | HSE Monthly | SUM([lost_time_incidents]) * 200000 / SUM([exposure_hours]) |
| Risk Band | Risk Scores | IF [failure_risk_score_7d] >= [Risk Threshold] THEN "Review" ELSE "Monitor" END (parameter default 0.5; display threshold only) |

Note: Tableau aggregates are computed at the visual level; do not average pre-computed percentages except where a weighted formula is shown.
