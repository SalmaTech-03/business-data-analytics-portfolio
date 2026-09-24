# Data Dictionary (processed tables)

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.

Generated from the actual CSV headers in data/processed.

## dim_date

Rows in processed file: 1,096

| Column | Type (inferred) | Description |
|---|---|---|
| date_key | int64 | yyyymmdd integer key |
| date | str | Calendar date |
| year | int64 | Calendar year |
| quarter | int64 | Quarter 1-4 |
| month | int64 | Month number |
| month_name | str | Month name |
| week | int64 | ISO week |
| day | int64 | Day of month |
| day_of_week | int64 | 1=Mon..7=Sun |
| is_weekend | bool | Weekend flag |

## dim_field

Rows in processed file: 4

| Column | Type (inferred) | Description |
|---|---|---|
| field_id | str | Field key (FIELD-nnn) |
| field_name | str | Fictional field name |
| region | str | Synthetic region label |
| basin | str | Synthetic basin label |
| field_type | str | Onshore/Offshore |
| operator | str | Operating company (fictional PetroNexa Energy) |
| commission_date | str | Date put on production |
| status | str | Operational status |

## dim_well

Rows in processed file: 60

| Column | Type (inferred) | Description |
|---|---|---|
| well_id | str | Well key (WELL-nnnn) |
| well_name | str | Well name |
| field_id | str | Field key (FIELD-nnn) |
| well_type | str | Vertical/Directional/Horizontal |
| reservoir | str | Synthetic reservoir label |
| depth_m | int64 | Depth in metres |
| latitude | float64 | Synthetic local grid Y (NOT geographic) |
| longitude | float64 | Synthetic local grid X (NOT geographic) |
| commission_date | str | Date put on production |
| status | str | Operational status |
| primary_equipment_id | str | Primary lift pump serving the well |

## dim_equipment

Rows in processed file: 48

| Column | Type (inferred) | Description |
|---|---|---|
| equipment_id | str | Equipment key (EQ-nnnn) |
| equipment_name | str | Equipment name |
| equipment_type | str | Pump/Compressor/Separator/Generator/Valve/Heat Exchanger/Pipeline Equipment |
| field_id | str | Field key (FIELD-nnn) |
| manufacturer | str | Fictional manufacturer |
| installation_date | str | Installation date |
| criticality | str | Low/Medium/High |
| status | str | Operational status |

## dim_supplier

Rows in processed file: 8

| Column | Type (inferred) | Description |
|---|---|---|
| supplier_id | str | Supplier key |
| supplier_name | str | Fictional supplier name |
| supplier_category | str | Supplier category |
| region | str | Synthetic region label |
| lead_time_days | int64 | Quoted lead time (days) |
| supplier_rating | float64 | Static rating 1-5 (attribute, not measured performance) |

## dim_material

Rows in processed file: 40

| Column | Type (inferred) | Description |
|---|---|---|
| material_id | str | Material key |
| material_name | str | Material name |
| material_category | str | Material category |
| unit | str | Unit of measure |
| unit_cost | float64 | Unit cost USD |
| reorder_level | int64 | Reorder point (units) |
| lead_time_days | int64 | Quoted lead time (days) |
| primary_supplier_id | str | Default supplier |

## dim_warehouse

Rows in processed file: 4

| Column | Type (inferred) | Description |
|---|---|---|
| warehouse_id | str | Warehouse key |
| warehouse_name | str | Warehouse name |
| field_id | str | Field key (FIELD-nnn) |

## bridge_equipment_well

Rows in processed file: 452

| Column | Type (inferred) | Description |
|---|---|---|
| equipment_id | str | Equipment key (EQ-nnnn) |
| well_id | str | Well key (WELL-nnnn) |
| impact_factor | float64 | Share of equipment downtime attributed to the well |

## fact_production

Rows in processed file: 58,642

| Column | Type (inferred) | Description |
|---|---|---|
| date | str | Calendar date |
| well_id | str | Well key (WELL-nnnn) |
| operating_hours | float64 | Hours operating in the period |
| downtime_hours | float64 | Hours down |
| oil_production_bbl | float64 | Oil (bbl) |
| gas_production_mcf | float64 | Gas (mcf) |
| water_production_bbl | float64 | Water (bbl) |
| pressure_psi | float64 | Pressure (psi) |
| temperature_c | float64 | Temperature (C) |
| water_cut_pct | float64 | 100 x water/(oil+water) |
| potential_production_bbl | float64 | SIMULATED unconstrained oil potential (bbl) |
| dq_flag | str | Pipe-separated cleaning flags (imputed/recomputed values) |

## fact_sensor

Rows in processed file: 105,216

| Column | Type (inferred) | Description |
|---|---|---|
| timestamp | str | Reading time (2 readings/day at 06:00 and 18:00) |
| equipment_id | str | Equipment key (EQ-nnnn) |
| temperature_c | float64 | Temperature (C) |
| pressure_psi | float64 | Pressure (psi) |
| vibration_mm_s | float64 | Vibration (mm/s) |
| flow_rate | float64 | Flow (synthetic m3/h) |
| energy_consumption_kwh | float64 | Energy over the 12h reading window (kWh) |
| operating_hours | float64 | Hours operating in the period |
| dq_flag | str | Pipe-separated cleaning flags (imputed/recomputed values) |

## fact_maintenance

Rows in processed file: 1,107

| Column | Type (inferred) | Description |
|---|---|---|
| maintenance_id | str | Work order key |
| equipment_id | str | Equipment key (EQ-nnnn) |
| date | str | Calendar date |
| maintenance_type | str | Corrective/Preventive/Inspection |
| failure_type | str | Failure mode ('None' if not a failure) |
| downtime_hours | float64 | Hours down |
| labor_cost | float64 | Labour cost USD |
| material_cost | float64 | Material cost USD (= sum quantity x unit_cost) |
| contractor_cost | float64 | Contractor cost USD |
| total_cost | float64 | labor + material + contractor |
| priority | str | Critical/High/Medium/Low |
| work_order_status | str | Completed/In Progress |

## fact_maintenance_material

Rows in processed file: 1,184

| Column | Type (inferred) | Description |
|---|---|---|
| maintenance_id | str | Work order key |
| material_id | str | Material key |
| quantity | int64 | Units |
| warehouse_id | str | Warehouse key |

## fact_sales

Rows in processed file: 4,383

| Column | Type (inferred) | Description |
|---|---|---|
| date | str | Calendar date |
| field_id | str | Field key (FIELD-nnn) |
| oil_volume_bbl | float64 | Oil sold (bbl) |
| gas_volume_mcf | float64 | Gas sold (mcf) |
| oil_price_usd | float64 | Realised oil price USD/bbl |
| gas_price_usd | float64 | Gas price USD/mcf |
| revenue_usd | float64 | oil x price + gas x price |

## fact_operating_cost

Rows in processed file: 30,674

| Column | Type (inferred) | Description |
|---|---|---|
| date | str | Calendar date |
| field_id | str | Field key (FIELD-nnn) |
| cost_category | str | Production/Energy/Labor/Maintenance/Transportation/Utilities/Other |
| cost_amount_usd | float64 | Operating cost USD |

## fact_inventory

Rows in processed file: 87,637

| Column | Type (inferred) | Description |
|---|---|---|
| date | str | Calendar date |
| material_id | str | Material key |
| supplier_id | str | Supplier key |
| warehouse_id | str | Warehouse key |
| opening_stock | float64 | Opening stock (units) |
| receipts | float64 | Units received |
| consumption | float64 | Units consumed |
| closing_stock | float64 | opening + receipts - consumption |
| reorder_level | float64 | Reorder point (units) |
| unit_cost | float64 | Unit cost USD |
| stockout_flag | int64 | 1 if demand exceeded available stock |

## fact_purchase_order

Rows in processed file: 1,965

| Column | Type (inferred) | Description |
|---|---|---|
| po_id | str | Purchase order key |
| order_date | str | Order date |
| material_id | str | Material key |
| supplier_id | str | Supplier key |
| warehouse_id | str | Warehouse key |
| quantity | int64 | Units |
| quoted_lead_time_days | int64 | Quoted lead time |
| promised_date | str | order_date + quoted lead time |
| received_date | str | Receipt date (blank if open) |
| unit_cost | float64 | Unit cost USD |
| status | str | Operational status |

## fact_hse

Rows in processed file: 394

| Column | Type (inferred) | Description |
|---|---|---|
| incident_id | str | Incident key |
| date | str | Calendar date |
| field_id | str | Field key (FIELD-nnn) |
| incident_type | str | Incident type |
| severity | str | Low/Medium/High/Critical |
| lost_time_flag | int64 | 1 if lost-time incident |
| days_lost | int64 | Days lost |
| root_cause | str | Root cause category |
| department | str | Department |
