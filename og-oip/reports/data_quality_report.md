# Data Quality Report

_Generated 2026-09-24 06:42 UTC from actual validation runs._

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.

## 1. Summary

| Stage | Checks | PASS | FAIL | WARN | Failed rows (sum over checks) |
|---|---|---|---|---|---|
| Raw | 179 | 119 | 60 | 0 | 36,743 |
| Processed | 178 | 178 | 0 | 0 | 0 |

## 2. Failed checks on RAW data

| table | check | column | failed_rows | total_rows | detail |
|---|---|---|---|---|---|
| dim_supplier | primary_key_uniqueness | supplier_id | 6 | 14 |  |
| fact_production | primary_key_uniqueness | date+well_id | 191 | 58862 |  |
| fact_sensor | primary_key_uniqueness | timestamp+equipment_id | 105 | 105321 |  |
| fact_maintenance | primary_key_uniqueness | maintenance_id | 11 | 1136 |  |
| fact_sales | primary_key_uniqueness | date+field_id | 8 | 4392 |  |
| fact_operating_cost | primary_key_uniqueness | date+field_id+cost_category | 34 | 30718 |  |
| fact_inventory | primary_key_uniqueness | date+material_id+warehouse_id | 52 | 87723 |  |
| fact_hse | primary_key_uniqueness | incident_id | 3 | 397 |  |
| fact_production | duplicate_rows | * | 176 | 58862 |  |
| fact_sensor | duplicate_rows | * | 105 | 105321 |  |
| fact_maintenance | duplicate_rows | * | 11 | 1136 |  |
| fact_sales | duplicate_rows | * | 8 | 4392 |  |
| fact_operating_cost | duplicate_rows | * | 30 | 30718 |  |
| fact_inventory | duplicate_rows | * | 43 | 87723 |  |
| fact_hse | duplicate_rows | * | 3 | 397 |  |
| fact_production | null_check | oil_production_bbl | 58 | 58862 |  |
| fact_production | null_check | pressure_psi | 294 | 58862 |  |
| fact_production | null_check | temperature_c | 294 | 58862 |  |
| fact_production | null_check | water_cut_pct | 176 | 58862 |  |
| fact_sensor | null_check | temperature_c | 421 | 105321 |  |
| fact_sensor | null_check | pressure_psi | 421 | 105321 |  |
| fact_sensor | null_check | vibration_mm_s | 420 | 105321 |  |
| fact_sensor | null_check | flow_rate | 420 | 105321 |  |
| fact_sensor | null_check | energy_consumption_kwh | 420 | 105321 |  |
| fact_maintenance | null_check | equipment_id | 7 | 1136 |  |
| fact_inventory | null_check | supplier_id | 876 | 87723 |  |
| fact_inventory | null_check | unit_cost | 440 | 87723 |  |
| fact_sales | null_check | oil_price_usd | 13 | 4392 |  |
| fact_sales | null_check | revenue_usd | 13 | 4392 |  |
| fact_production | range_check | downtime_hours | 29 | 58862 | allowed [0, 24] |
| fact_production | range_check | oil_production_bbl | 29 | 58862 | allowed [0, 10000] |
| fact_sensor | range_check | temperature_c | 31 | 105321 | allowed [-50, 300] |
| fact_sensor | range_check | vibration_mm_s | 52 | 105321 | allowed [0, 50] |
| fact_maintenance | range_check | labor_cost | 3 | 1136 | allowed [0, None] |
| fact_inventory | range_check | consumption | 9 | 87723 | allowed [0, None] |
| fact_operating_cost | range_check | cost_amount_usd | 11 | 30718 | allowed [0, None] |
| fact_production | referential_integrity | well_id | 176 | 58862 | -> well_id in parent |
| fact_hse | referential_integrity | field_id | 26 | 397 | -> field_id in parent |
| fact_production | date_validity | date | 44 | 58862 | parsable and within [2000-01-01, 2030-12-31] |
| fact_production | date_format_consistency | date | 8767 | 58862 | non-ISO formatted values |
| fact_maintenance | date_format_consistency | date | 185 | 1136 | non-ISO formatted values |
| fact_sales | date_validity | date | 1 | 4392 | parsable and within [2000-01-01, 2030-12-31] |
| fact_sales | date_format_consistency | date | 623 | 4392 | non-ISO formatted values |
| fact_operating_cost | date_validity | date | 14 | 30718 | parsable and within [2000-01-01, 2030-12-31] |
| fact_operating_cost | date_format_consistency | date | 4664 | 30718 | non-ISO formatted values |
| fact_inventory | date_validity | date | 43 | 87723 | parsable and within [2000-01-01, 2030-12-31] |
| fact_inventory | date_format_consistency | date | 13272 | 87723 | non-ISO formatted values |
| fact_hse | date_format_consistency | date | 62 | 397 | non-ISO formatted values |
| fact_sensor | date_format_consistency | timestamp | 2045 | 105321 | non-ISO formatted values |
| fact_maintenance | domain_check | maintenance_type | 81 | 1136 | allowed: ['Corrective', 'Inspection', 'Preventive'] |
| fact_operating_cost | domain_check | cost_category | 644 | 30718 | allowed: ['Energy', 'Labor', 'Maintenance', 'Other', 'Production', 'Transportation', 'Utilities'] |
| fact_hse | domain_check | severity | 46 | 397 | allowed: ['Critical', 'High', 'Low', 'Medium'] |
| fact_production | unit_consistency | oil_uom | 253 | 58862 | oil must be reported in bbl |
| fact_sales | unit_consistency | gas_uom | 12 | 4392 | gas must be reported in mcf |
| fact_production | operating_plus_downtime_eq_24 | - | 29 | 58862 |  |
| fact_production | water_cut_consistent_with_volumes | - | 395 | 58862 | tolerance 1 percentage point |
| fact_maintenance | total_cost_eq_components | - | 14 | 1136 |  |
| fact_inventory | closing_eq_open_plus_receipts_minus_consumption | - | 96 | 87723 |  |
| fact_sales | revenue_eq_volume_x_price | - | 12 | 4392 | tolerance $1 |
| dim_supplier | supplier_name_uniqueness_per_id | supplier_name | 16 | 14 | one canonical name per supplier_id |

## 3. Failed checks on PROCESSED data (residual issues)

All checks passed on processed data.

## 4. Cleaning actions (counts from the cleaning run)

| table | action | count |
|---|---|---|
| dim_supplier | rows_in | 14 |
| dim_supplier | name_variants_standardised | 5 |
| dim_supplier | duplicate_suppliers_removed | 6 |
| dim_supplier | rows_out | 8 |
| dim_supplier | rows_quarantined | 0 |
| dim_date | rows_in | 1096 |
| dim_date | rows_out | 1096 |
| dim_date | rows_quarantined | 0 |
| dim_field | rows_in | 4 |
| dim_field | rows_out | 4 |
| dim_field | rows_quarantined | 0 |
| dim_well | rows_in | 60 |
| dim_well | rows_out | 60 |
| dim_well | rows_quarantined | 0 |
| dim_equipment | rows_in | 48 |
| dim_equipment | rows_out | 48 |
| dim_equipment | rows_quarantined | 0 |
| dim_material | rows_in | 40 |
| dim_material | rows_out | 40 |
| dim_material | rows_quarantined | 0 |
| dim_warehouse | rows_in | 4 |
| dim_warehouse | rows_out | 4 |
| dim_warehouse | rows_quarantined | 0 |
| bridge_equipment_well | rows_in | 452 |
| bridge_equipment_well | rows_out | 452 |
| bridge_equipment_well | rows_quarantined | 0 |
| fact_maintenance_material | rows_in | 1192 |
| fact_maintenance_material | rows_out | 1184 |
| fact_maintenance_material | rows_quarantined | 8 |
| fact_purchase_order | rows_in | 1965 |
| fact_purchase_order | rows_out | 1965 |
| fact_purchase_order | rows_quarantined | 0 |
| fact_production | rows_in | 58862 |
| fact_production | well_id_normalised | 176 |
| fact_production | quarantined_invalid_date | 44 |
| fact_production | oil_m3_to_bbl_converted | 252 |
| fact_production | duplicates_removed | 176 |
| fact_production | negative_oil_set_missing | 29 |
| fact_production | outlier_oil_set_missing | 58 |
| fact_production | downtime_clipped | 29 |
| fact_production | operating_hours_recomputed | 66 |
| fact_production | oil_imputed | 144 |
| fact_production | water_cut_missing_before | 176 |
| fact_production | pressure_psi_imputed | 293 |
| fact_production | temperature_c_imputed | 293 |
| fact_production | rows_out | 58642 |
| fact_production | rows_quarantined | 44 |
| fact_sensor | rows_in | 105321 |
| fact_sensor | duplicates_removed | 105 |
| fact_sensor | spikes_set_missing | 83 |
| fact_sensor | temperature_c_imputed | 451 |
| fact_sensor | pressure_psi_imputed | 420 |
| fact_sensor | vibration_mm_s_imputed | 471 |
| fact_sensor | flow_rate_imputed | 420 |
| fact_sensor | energy_consumption_kwh_imputed | 420 |
| fact_sensor | rows_out | 105216 |
| fact_sensor | rows_quarantined | 0 |
| fact_maintenance | rows_in | 1136 |
| fact_maintenance | type_names_standardised | 81 |
| fact_maintenance | duplicate_ids_removed | 11 |
| fact_maintenance | business_duplicates_removed | 11 |
| fact_maintenance | labor_cost_sign_corrected | 3 |
| fact_maintenance | material_cost_sign_corrected | 0 |
| fact_maintenance | contractor_cost_sign_corrected | 0 |
| fact_maintenance | total_cost_recomputed | 11 |
| fact_maintenance | rows_out | 1107 |
| fact_maintenance | rows_quarantined | 7 |
| fact_inventory | rows_in | 87723 |
| fact_inventory | quarantined_invalid_date | 43 |
| fact_inventory | duplicates_removed | 43 |
| fact_inventory | supplier_id_filled_from_material | 876 |
| fact_inventory | unit_cost_filled_from_material | 438 |
| fact_inventory | negative_consumption_sign_corrected | 9 |
| fact_inventory | closing_stock_recomputed | 87 |
| fact_inventory | rows_out | 87637 |
| fact_inventory | rows_quarantined | 43 |
| fact_sales | rows_in | 4392 |
| fact_sales | duplicates_removed | 8 |
| fact_sales | gas_mmcf_to_mcf_converted | 12 |
| fact_sales | oil_price_filled_month_median | 13 |
| fact_sales | revenue_recomputed | 26 |
| fact_sales | rows_out | 4383 |
| fact_sales | rows_quarantined | 1 |
| fact_operating_cost | rows_in | 30718 |
| fact_operating_cost | category_names_standardised | 644 |
| fact_operating_cost | duplicates_removed | 30 |
| fact_operating_cost | negative_amount_sign_corrected | 11 |
| fact_operating_cost | rows_out | 30674 |
| fact_operating_cost | rows_quarantined | 14 |
| fact_hse | rows_in | 397 |
| fact_hse | severity_standardised | 46 |
| fact_hse | field_id_standardised | 26 |
| fact_hse | duplicates_removed | 3 |
| fact_hse | rows_out | 394 |
| fact_hse | rows_quarantined | 0 |

## 5. Injected defects (generator ground truth)

These counts are what the synthetic generator injected into the RAW files; they document what the pipeline should detect.

| defect | injected |
|---|---|
| production_nonstandard_date_format | 8756 |
| production_invalid_date | 44 |
| production_oil_reported_in_m3 | 253 |
| production_missing_pressure_psi | 293 |
| production_missing_temperature_c | 293 |
| production_missing_water_cut_pct | 176 |
| production_missing_oil_production_bbl | 58 |
| production_oil_outliers_x10 | 58 |
| production_negative_oil | 29 |
| production_downtime_gt_24 | 29 |
| production_well_id_naming | 176 |
| production_exact_duplicates | 176 |
| sensor_nonstandard_timestamp | 2041 |
| sensor_missing_temperature_c | 420 |
| sensor_missing_pressure_psi | 420 |
| sensor_missing_vibration_mm_s | 420 |
| sensor_missing_flow_rate | 420 |
| sensor_missing_energy_consumption_kwh | 420 |
| sensor_vibration_spikes_999 | 52 |
| sensor_temperature_spikes_minus999 | 31 |
| sensor_exact_duplicates | 105 |
| maintenance_nonstandard_date_format | 183 |
| maintenance_invalid_date | 0 |
| maintenance_type_naming_variants | 79 |
| maintenance_missing_equipment_id | 7 |
| maintenance_negative_labor_cost | 3 |
| maintenance_total_cost_mismatch | 11 |
| maintenance_exact_duplicates | 11 |
| maintenance_business_duplicates_new_id | 11 |
| inventory_nonstandard_date_format | 13273 |
| inventory_invalid_date | 43 |
| inventory_missing_supplier_id | 876 |
| inventory_missing_unit_cost | 438 |
| inventory_negative_consumption | 9 |
| inventory_closing_stock_mismatch | 87 |
| inventory_exact_duplicates | 43 |
| supplier_name_variant_rows | 6 |
| sales_nonstandard_date_format | 622 |
| sales_invalid_date | 1 |
| sales_gas_reported_in_mmcf | 12 |
| sales_missing_oil_price_usd | 13 |
| sales_missing_revenue_usd | 13 |
| sales_exact_duplicates | 8 |
| opcost_nonstandard_date_format | 4661 |
| opcost_invalid_date | 14 |
| opcost_category_naming_variants | 643 |
| opcost_negative_amount | 15 |
| opcost_exact_duplicates | 30 |
| hse_nonstandard_date_format | 61 |
| hse_invalid_date | 0 |
| hse_severity_case_variants | 46 |
| hse_field_id_variants | 26 |
| hse_exact_duplicates | 3 |

## 6. Limitations

- Rows with unparsable dates or unknown keys are quarantined (data/processed/quarantine), not repaired; they reduce row counts versus the generator truth.
- Imputation is method-based (interpolation, potential-based estimate) and always flagged in `dq_flag` where the schema carries it.
- Range thresholds are project assumptions, not engineering standards.