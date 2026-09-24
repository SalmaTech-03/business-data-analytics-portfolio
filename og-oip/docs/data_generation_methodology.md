# Data Generation Methodology (SYNTHETIC)

All PetroNexa Energy data are simulated. This document lists every relationship that was **built into the generator**, so nothing simulated can be mistaken for a discovery. Seed = 42; `data/reference/generation_manifest.json` stores row counts and content hashes.

## Scale
4 fields, 60 wells, 48 equipment units (12 per field, 7 types), 8 suppliers, 40 materials (8 categories), 4 warehouses, 2022-01-01 to 2024-12-31 (1,096 days). About 291k fact rows before defects.

## Order of simulation
1. Dimensions (`dimensions.py`). Wells receive an Arps decline parameter set (qi, initial decline, b), water-cut curve, GOR, pressure, optional workover uplift (parameters in `data/reference/well_generation_parameters.csv`). `bridge_equipment_well` says which wells an equipment failure affects: pump -> its wells (1.0); compressor/separator -> all field wells (0.6); generator (0.8); pipeline equipment (0.5); valve/heat exchanger -> 4 wells (0.7).
2. Maintenance (`operations.py`): preventive every 85-125 days; inspections (35% alongside PM); corrective events from a daily hazard = base annual rate by type x (1+0.04 x age) x (1+0.6 x min(days since PM/120, 2)) x criticality factor / 1.4. Downtime lognormal by type. Costs: labour = downtime x crew x 85 USD/h; contractor cost with type-dependent probability; material lines drawn from materials stocked in the field's warehouse (so `material_cost = sum(quantity x unit_cost)` exactly).
3. Downtime spill: hours spread from the event day at <=24 h/day; well downtime = hours x impact_factor, plus 2% random background shut-ins of 1-8 h.
4. Sensors: 2 readings/day per unit; baselines by type; AR(1) noise; slow age drift; **75% of failures have a degradation ramp over 4-14 days** (vibration, temperature, pressure, flow, energy); ~1.5 false-alarm ramps per unit; readings reflect downtime.
5. Production: potential = Arps hyperbolic rate x workover uplift x (1+N(0,3%)); actual oil = potential x operating_hours/24 x efficiency (N(0.97,0.03) clipped 0.85-1.0, reduced on pressure dips); water from a logistic-style water-cut curve; gas = oil x GOR (rising 4%/year).
6. Sales: oil sold = 98.5% of produced, gas sold = 92%; prices from mean-reverting monthly random walks (oil ~72, gas ~3.2) with field differentials and daily noise.
7. Operating cost (field-day-category): production (per producing well + per bbl), energy (sensor kWh x 0.09 USD x seasonal tariff), labour (per well + per corrective event), maintenance (equals the field's maintenance costs that day), transportation (per bbl), utilities, other.
8. HSE: Poisson incidents per field-day with rate 0.09 x (wells/16) x (1 + 0.15 x corrective events in last 7 days); type/severity/root-cause distributions with a higher share of equipment-failure/maintenance root causes within 3 days after a corrective event. (The resulting monthly association is weak and was not detected in tests - reported honestly.)
9. Inventory: routine Poisson demand + maintenance material use; reorder point = mean demand x quoted lead time x 1.25 + 1; order quantity = 35 days of demand; supplier lateness with a hidden on-time probability (55%-95%) and 2-14 day delays. Unmet demand is assumed covered by an emergency purchase outside the ledger; stockouts do not feed back into downtime (a simplification).

## Injected defects (raw data)
`defects.py` injects: mixed date formats and invalid dates, missing values, exact and business duplicates, oil in m3 (production) and gas in MMCF (sales), negative values, outliers (x10 oil, downtime > 24 h, sensor spikes of 999/-999), naming variants (well ids, maintenance types, cost categories, severity, field ids, supplier names), missing keys, cost/closing-stock/revenue inconsistencies. Counts are logged in `data/reference/defect_injection_log.json`.

## Cleaning rules and their limits
See `src/og_oip/cleaning/cleaners.py` and section 4/6 of `reports/data_quality_report.md`. Unrecoverable rows (invalid dates, unknown keys) are quarantined. Oil imputation = potential x uptime x the well's median efficiency (flagged `oil_imputed`); sensor/pressure/temperature gaps interpolated within unit/well (flagged). Residual: a few injected x10 outliers on very low-output days fall below the 1.25 x potential detection threshold (the test suite bounds this).

## What the analyses can and cannot show
Because relationships are simulated, findings such as "downtime drives loss" or "vibration precedes failure" are properties of the generator. Their value is to demonstrate method and pipeline correctness, KPI definitions, and honest evaluation.
