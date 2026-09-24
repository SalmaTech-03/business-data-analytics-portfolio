# Data Requirements

> All operational data in this project are synthetic. PetroNexa Energy is a FICTIONAL company; stakeholders and roles are illustrative assumptions.

| Entity | Table | Grain | Key | Volume (this build) | Notes |
|---|---|---|---|---|---|
| Date | dim_date | day | date_key | 1,096 | 2022-01-01 to 2024-12-31 |
| Field | dim_field | field | field_id | 4 | fictional names |
| Well | dim_well | well | well_id | 60 | includes primary_equipment_id; coordinates are a synthetic grid |
| Equipment | dim_equipment | unit | equipment_id | 48 | 7 types |
| Supplier / Material / Warehouse | dim_supplier, dim_material, dim_warehouse | item | ids | 8 / 40 / 4 | |
| Equipment-well link | bridge_equipment_well | pair | equipment_id + well_id | 452 | impact_factor |
| Production | fact_production | well-day | well_id + date | ~58.7k | includes SIMULATED potential |
| Sensor | fact_sensor | equipment x 12h reading | equipment_id + timestamp | ~105k | 2 readings/day |
| Maintenance | fact_maintenance, fact_maintenance_material | event | maintenance_id | ~1.1k / ~1.2k | |
| Sales / Opex | fact_sales, fact_operating_cost | field-day (x category) | field_id + date (+category) | ~4.4k / ~30.7k | |
| Inventory / POs | fact_inventory, fact_purchase_order | material-warehouse-day / order | keys | ~87.7k / ~2k | |
| HSE | fact_hse | incident | incident_id | ~394 | |

Exact counts come from data/reference/generation_manifest.json and the cleaning log (quarantined rows reduce processed counts slightly).

## Data quality requirements
Keys unique; not-null on identifiers and core measures; ranges per validation/checks.py; referential integrity; ISO dates in processed data; units: oil bbl, gas mcf, water bbl, pressure psi, temperature C; closing stock = opening + receipts - consumption; total maintenance cost = labor + material + contractor; revenue = volumes x prices.

## Real datasets (separate case studies)
| Dataset | File(s) | Use |
|---|---|---|
| Volve production | Volve_production_data.xlsx (daily 15,634 rows; monthly 527 rows) | Case study A |
| BSEE OGOR-A | ogora2025delimit.txt, ogoradelimit.txt (no header, 85,205 rows, 2025-01 to 2026-06) | Case study B |
| BSEE OGOR-B/C | supplied, NOT used | not analysed |

Users must check the original publishers' terms before redistributing real files.
