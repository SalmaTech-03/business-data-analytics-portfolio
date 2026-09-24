# Data Source Schema (Tableau)

> Synthetic data (fictional PetroNexa Energy). Specification only; no .twb/.twbx file is provided because none can be produced or verified in the build environment.

## Recommended sources (CSV marts, already joined and typed)
| Data source | File | Grain | Key columns |
|---|---|---|---|
| Well Daily | data/marts/mart_well_daily.csv | well-day | date, well_id, field_id, month |
| Field Monthly | data/marts/mart_field_monthly.csv | field-month | field_id, month |
| Equipment Summary | data/marts/mart_equipment_summary.csv | equipment | equipment_id |
| Equipment Monthly | data/marts/mart_equipment_monthly.csv | equipment-month | equipment_id, month |
| Sensor Daily | data/marts/mart_sensor_daily.csv | equipment-day | equipment_id, date |
| Inventory | data/marts/mart_inventory.csv | material-warehouse | material_id, warehouse_id |
| Supplier Performance | data/marts/mart_supplier_performance.csv | supplier | supplier_id |
| HSE Monthly | data/marts/mart_hse_monthly.csv | field-month | field_id, month |
| Risk Scores | reports/tables/ml_latest_equipment_risk.csv | equipment | equipment_id |
| Forecast | reports/tables/forecast_next_30d.csv | day | date |

## Key columns (from the actual marts)
- mart_well_daily: date, well_id, well_name, field_id, well_type, reservoir, operating_hours, downtime_hours, oil_production_bbl, gas_production_mcf, water_production_bbl, pressure_psi, temperature_c, water_cut_pct, potential_production_bbl, production_loss_bbl, downtime_loss_bbl, other_loss_bbl, maintenance_attributed_downtime_hours, unattributed_downtime_hours, oil_price_usd, estimated_lost_revenue_usd, well_age_days, month.
- mart_field_monthly: field_id, month, oil_bbl, gas_mcf, water_bbl, potential_bbl, loss_bbl, loss_pct, downtime_hours, revenue_usd, oil_sold_bbl, gas_sold_mcf, cost_*_usd (production, energy, labor, maintenance, transportation, utilities, other), opex_total_usd, cost_per_bbl_oil_sold, cost_per_boe_sold, operating_margin_usd, lost_revenue_usd.
- mart_equipment_summary: equipment_id, equipment_name, equipment_type, field_id, criticality, failures, total_downtime_hours, corrective_downtime_hours, maintenance_cost_usd, period_hours, operating_hours, availability_pct, mtbf_hours, mttr_hours, failures_per_year.
- mart_hse_monthly: field_id, month, exposure_hours, incidents, lost_time_incidents, days_lost, incident_rate_per_200k_h, ltir_per_200k_h.

## Relationships (logical layer)
Well Daily.field_id = Field Monthly.field_id and Well Daily.month = Field Monthly.month (many-to-many, use only for filtering by field/month). Equipment Summary.equipment_id = Risk Scores.equipment_id. Use a shared Field and Month parameter/filters across data sources rather than blending high-cardinality keys.

## Data types
Dates: date; month columns: date (first of month); ids: string; measures: decimal.
