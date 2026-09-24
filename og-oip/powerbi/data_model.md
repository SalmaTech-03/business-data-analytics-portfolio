# Power BI Data Model

> Synthetic data (fictional PetroNexa Energy). This folder contains SPECIFICATIONS to build the report; no .pbix file is included because none can be produced or verified in the build environment.

## Tables (source: data/processed unless noted)
| Table | Type | Grain | Key |
|---|---|---|---|
| dim_date | Dimension | day | date (mark as date table) |
| dim_field | Dimension | field | field_id |
| dim_well | Dimension | well | well_id |
| dim_equipment | Dimension | unit | equipment_id |
| dim_supplier | Dimension | supplier | supplier_id |
| dim_material | Dimension | material | material_id |
| dim_warehouse | Dimension | warehouse | warehouse_id |
| bridge_equipment_well | Bridge | equipment x well | equipment_id + well_id (hide from report view) |
| fact_production | Fact | well-day | well_id + date |
| fact_sensor | Fact | equipment x reading | equipment_id + timestamp (+ calculated column date) |
| fact_maintenance | Fact | work order | maintenance_id |
| fact_maintenance_material | Fact | work order x material | maintenance_id + material_id |
| fact_sales | Fact | field-day | field_id + date |
| fact_operating_cost | Fact | field-day-category | field_id + date + cost_category |
| fact_inventory | Fact | material-warehouse-day | material_id + warehouse_id + date |
| fact_purchase_order | Fact | PO | po_id |
| fact_hse | Fact | incident | incident_id |
| mart_well_daily (data/marts) | Optional | well-day | for loss decomposition already computed in Python |
| forecast_next_30d, ml_latest_equipment_risk, ml_model_metrics_test, forecast_backtest_summary (reports/tables) | Output tables | see files | disconnected or joined on equipment_id |

## Relationships (single direction, one-to-many, dimension filters fact)
| From (one) | To (many) |
|---|---|
| dim_date[date] | fact_production[date], fact_maintenance[date], fact_sales[date], fact_operating_cost[date], fact_inventory[date], fact_hse[date], fact_sensor[date], fact_purchase_order[order_date] |
| dim_field[field_id] | dim_well[field_id], dim_equipment[field_id], dim_warehouse[field_id], fact_sales[field_id], fact_operating_cost[field_id], fact_hse[field_id] |
| dim_well[well_id] | fact_production[well_id] |
| dim_equipment[equipment_id] | fact_maintenance[equipment_id], fact_sensor[equipment_id], ml_latest_equipment_risk[equipment_id] |
| dim_material[material_id] | fact_inventory[material_id], fact_maintenance_material[material_id], fact_purchase_order[material_id] |
| dim_supplier[supplier_id] | fact_inventory[supplier_id], fact_purchase_order[supplier_id], dim_material[primary_supplier_id] (inactive) |
| dim_warehouse[warehouse_id] | fact_inventory[warehouse_id], fact_purchase_order[warehouse_id] |
| fact_maintenance[maintenance_id] | fact_maintenance_material[maintenance_id] |

Only one active date relationship per fact table. Well-to-field for production visuals flows dim_field -> dim_well -> fact_production.

## Calculated columns / Power Query columns
- fact_sensor[date] = DateTime.Date([timestamp]) (Power Query).
- fact_purchase_order[on_time] = 1 if received_date <= promised_date, 0 if later, null if open (Power Query).
- fact_purchase_order[actual_lead_days] = Duration.Days(received_date - order_date).

## Modelling notes
- Import mode; about 290k fact rows in total, comfortably within Import limits.
- Avoid averaging water_cut_pct across rows; use the volume-weighted measure.
- Hide technical columns (dq_flag optional to show in a data-quality page).
- Set number formats: bbl and mcf whole numbers, USD with thousands separators.
