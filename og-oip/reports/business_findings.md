# Business Findings - PetroNexa Energy (SYNTHETIC)

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.

All figures below are read from generated tables. They describe simulated data and must not be read as statements about real operations. Association statements are correlations in synthetic data, not causal proof.

## 1. Production

- Total oil 13.35 million bbl over 2022-01-01 to 2024-12-31; average portfolio rate 12,183 bbl/day.
- Production loss versus simulated potential: 1.38 million bbl (9.4%). 67% of the loss is downtime-related; the remainder is efficiency loss.
- 93% of well downtime hours are associated with recorded maintenance events (via the equipment-well bridge); the rest is unattributed background shut-ins.
- Estimated lost revenue at realised oil prices: $95.5 million (synthetic).
- Median nominal annual decline across 55 wells with a fit: 15.1% (exponential fit; workovers/downtime contaminate individual fits).

**By field (ranked by loss in barrels):**

| field_id | field_name | oil_bbl | loss_bbl | loss_pct | water_cut_pct | lost_revenue_usd |
|---|---|---|---|---|---|---|
| FIELD-002 | Synthetic Field Bravo | 3,937,987.8 | 447,887.3 | 10.2 | 38.6 | 31,570,569.3 |
| FIELD-001 | Synthetic Field Alpha | 4,358,664.6 | 417,362.0 | 8.7 | 48.6 | 28,821,085.8 |
| FIELD-003 | Synthetic Field Charlie | 2,708,874.3 | 282,290.1 | 9.4 | 36.8 | 18,655,136.1 |
| FIELD-004 | Synthetic Field Delta | 2,346,772.3 | 236,589.4 | 9.2 | 51.5 | 16,497,998.5 |

**Top 5 wells by total loss (rank_by_loss_bbl; loss_pct shown for context):**

| well_id | well_name | field_id | loss_bbl | loss_pct | avg_water_cut_pct |
|---|---|---|---|---|---|
| WELL-0002 | PNX-102 | FIELD-001 | 161,629.3 | 8.3 | 41.9 |
| WELL-0027 | PNX-209 | FIELD-002 | 68,158.1 | 9.5 | 26.3 |
| WELL-0031 | PNX-213 | FIELD-002 | 61,517.9 | 10.9 | 47.6 |
| WELL-0021 | PNX-203 | FIELD-002 | 58,768.5 | 9.7 | 21.2 |
| WELL-0056 | PNX-408 | FIELD-004 | 49,450.6 | 9.6 | 33.7 |

**Spearman associations (well-month level):** (the strong rho for downtime hours is expected by construction - loss is computed from downtime; other rows are the informative ones.)

| target | factor | spearman_rho | p_value | n |
|---|---|---|---|---|
| loss_pct | avg water cut % | -0.046 | 0.041 | 1935 |
| loss_pct | avg pressure psi | 0.029 | 0.203 | 1935 |
| loss_pct | well age (days) | -0.031 | 0.171 | 1935 |
| loss_pct | downtime hours in month | 0.980 | 0.000 | 1935 |
| other_loss_pct | avg water cut % | -0.002 | 0.930 | 1935 |
| other_loss_pct | avg pressure psi | 0.003 | 0.890 | 1935 |
| other_loss_pct | well age (days) | -0.000 | 0.992 | 1935 |
| other_loss_pct | downtime hours in month | -0.220 | 0.000 | 1935 |

## 2. Maintenance and reliability

- 412 corrective events (failures) across 48 units; fleet MTBF 3,030 h, MTTR 25.3 h, availability 98.87%.
- Corrective work is 68% of maintenance cost ($9.68 million). The 10 most expensive units account for 36% of cost.

| equipment_type | units | failures | mtbf_hours | mttr_hours | availability_pct | cost_usd |
|---|---|---|---|---|---|---|
| Pump | 16 | 199 | 2,086.3 | 22.6 | 98.6 | 3,367,911.4 |
| Compressor | 8 | 80 | 2,582.2 | 36.7 | 98.2 | 2,850,340.2 |
| Separator | 8 | 43 | 4,852.3 | 27.6 | 99.2 | 1,459,745.2 |
| Generator | 4 | 35 | 2,978.9 | 18.7 | 99.1 | 497,843.7 |
| Valve | 4 | 22 | 4,760.2 | 8.9 | 99.5 | 631,304.6 |
| Pipeline Equipment | 4 | 19 | 5,494.3 | 28.3 | 99.2 | 475,140.2 |
| Heat Exchanger | 4 | 14 | 7,465.2 | 30.2 | 99.3 | 398,038.6 |

**Priority equipment (score = criticality weight x downtime hours):**

| equipment_id | equipment_name | criticality | failures | total_downtime_hours | priority_score |
|---|---|---|---|---|---|
| EQ-0018 | Compressor 002-06 | High | 12 | 631.9 | 1,895.6 |
| EQ-0005 | Compressor 001-05 | High | 11 | 518.3 | 1,554.8 |
| EQ-0006 | Compressor 001-06 | High | 10 | 513.5 | 1,540.4 |
| EQ-0030 | Compressor 003-06 | High | 10 | 506.1 | 1,518.4 |
| EQ-0039 | Pump 004-03 | High | 20 | 456.9 | 1,370.8 |

## 3. Financial (synthetic assumptions)

- Revenue $956M, operating cost $314M, operating margin $642M. Cost per bbl of oil sold $23.88 (all opex / oil bbl; gas revenue not netted); per BOE $20.29.
- Price and cost levels are simulation parameters; margin levels should not be benchmarked against real companies.

| category | usd | share_pct |
|---|---|---|
| Production | 124,138,221.2 | 39.5 |
| Labor | 79,120,370.4 | 25.2 |
| Transportation | 39,473,932.2 | 12.6 |
| Utilities | 26,313,492.0 | 8.4 |
| Other | 21,357,390.2 | 6.8 |
| Energy | 14,105,024.9 | 4.5 |
| Maintenance | 9,728,183.5 | 3.1 |

| year | revenue_usd | opex_usd | oil_sold_bbl | lost_revenue_usd | cost_per_bbl | revenue_per_bbl |
|---|---|---|---|---|---|---|
| 2,022.00 | 255,766,831.14 | 89,036,144.85 | 3,338,085.80 | 24,456,472.51 | 26.67 | 76.62 |
| 2,023.00 | 344,972,393.84 | 110,800,641.14 | 4,929,572.80 | 34,783,121.36 | 22.48 | 69.98 |
| 2,024.00 | 355,409,770.59 | 114,399,828.50 | 4,891,720.90 | 36,305,195.88 | 23.39 | 72.66 |

## 4. Inventory and suppliers

- Stockout rate 2.14% of item-warehouse-days; annualised turnover 10.7; median days of inventory 34; 31 item-warehouse pairs at/below reorder level on the last day.
- Overall on-time delivery 74% (received purchase orders). Supplier on-time % vs stockout days: Spearman rho -0.68 (p=0.062, n=8 suppliers - low statistical power).

| material_category | stockout_rate_pct | avg_inventory_value_usd | consumption_value_usd |
|---|---|---|---|
| Lubricants | 6.59 | 65,234.03 | 3,693,010.71 |
| Chemicals | 5.69 | 69,795.37 | 3,874,541.34 |
| Seals | 1.11 | 20,308.12 | 752,893.38 |
| Filters | 1.02 | 17,988.18 | 718,067.66 |
| Bearings | 0.89 | 62,801.38 | 1,703,649.82 |
| Piping | 0.61 | 80,330.47 | 1,727,705.99 |
| Valves | 0.61 | 139,692.99 | 2,394,045.05 |
| Electrical | 0.58 | 44,603.68 | 1,217,652.14 |

| supplier_id | supplier_name | pos_received | on_time_pct | avg_quoted_lead_days | avg_actual_lead_days |
|---|---|---|---|---|---|
| SUP-001 | Aurelia Industrial Supply | 229 | 61.1 | 16.8 | 19.2 |
| SUP-002 | Borealis Machine Parts | 248 | 92.3 | 12.4 | 12.1 |
| SUP-003 | Cobalt Valve & Fitting Co | 173 | 87.9 | 25.0 | 25.3 |
| SUP-004 | Delmar Lubricants & Chemicals | 347 | 61.4 | 6.0 | 8.5 |
| SUP-005 | Everglen Filtration Systems | 269 | 80.3 | 11.8 | 12.6 |
| SUP-006 | Fulcrum Electrical Works | 225 | 73.3 | 20.8 | 22.2 |
| SUP-007 | Granite Pipe & Flange Ltd | 214 | 83.2 | 26.8 | 27.2 |
| SUP-008 | Helix Chemical Trading | 228 | 58.8 | 7.7 | 10.7 |

## 5. HSE

- 394 incidents, 29 lost-time, 170 days lost; incident rate 44.8 per 200,000 assumed exposure hours (exposure is an ASSUMPTION: 30 h per producing well-day).
- Field-month association between corrective events and incident counts: rho -0.04 (p=0.65) - no meaningful monthly association detected in this dataset.
- Share of incidents within 3 days after a corrective event in the same field: 33.2% versus 32.0% of field-days in such windows - no clear clustering.

## 6. Forecasting

Rolling-origin backtest (6 origins, 30-day horizon) on portfolio daily oil. Lowest MAE: **Moving average (30d)**. ARIMA not included (statsmodels unavailable).

| model | MAE | RMSE | MAPE_pct | mean_bias | origins |
|---|---|---|---|---|---|
| Moving average (30d) | 942.65 | 1,162.62 | 8.06 | 263.79 | 6 |
| Moving average (7d) | 965.83 | 1,176.41 | 8.15 | 25.33 | 6 |
| Simple exponential smoothing | 1,083.75 | 1,312.92 | 9.02 | -52.48 | 6 |
| Damped Holt (trend) smoothing | 1,084.49 | 1,313.69 | 9.03 | -53.21 | 6 |
| Autoregression AR(7) OLS | 1,167.46 | 1,434.39 | 10.07 | 929.14 | 6 |
| Naive (last value) | 1,351.53 | 1,617.52 | 11.16 | -91.70 | 6 |

The portfolio series has level shifts from wells coming online, which simple methods cannot anticipate; treat forecasts as short-term baselines.

## 7. Predictive maintenance (synthetic sensors)

Time-based split: train to 2023-01-31, validation to 2023-06-30, test from 2023-07-15. Test positive rate 5.8% (a random model's PR-AUC equals this).

| model | roc_auc | pr_auc | precision | recall | f1 | threshold | tp | fp | fn | tn |
|---|---|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.808 | 0.464 | 0.616 | 0.421 | 0.500 | 0.802 | 620 | 386 | 852 | 23534 |
| Random Forest | 0.797 | 0.496 | 0.706 | 0.457 | 0.555 | 0.540 | 673 | 280 | 799 | 23640 |
| Gradient Boosting (HistGB) | 0.782 | 0.449 | 0.630 | 0.399 | 0.489 | 0.348 | 588 | 345 | 884 | 23575 |
| Rule baseline: 3-day vibration ratio | 0.752 | 0.378 | 0.645 | 0.393 | 0.488 | 1.163 | 578 | 318 | 894 | 23602 |

Best model by PR-AUC: Random Forest. Event-level: 72% of 198 failure windows raised at least one alert; 4.0 false-alert days per equipment-year.
Caveat: the precursor signal was simulated (75% of failures have a detectable ramp), so these metrics show the pipeline works, not how a real fleet would perform.

## 8. Recommendations (conditional on the synthetic evidence)

1. Prioritise the top-ranked equipment by priority score for reliability review; the fields with the largest barrel loss give the largest recovery upside.
2. Investigate the unattributed downtime share before assuming all downtime is maintenance-driven.
3. Review reorder points for the categories with the highest stockout rate and for suppliers with the lowest on-time delivery.
4. Use the risk-scoring output as a ranked inspection list, not an automatic trigger, given the moderate precision/recall.