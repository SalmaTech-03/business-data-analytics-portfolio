# Real-Data Case Studies

These two analyses use REAL datasets supplied by the project author. They are separate from the fictional PetroNexa Energy dataset; no records were merged and no cross-dataset relationships are claimed.

## A. Volve field (Equinor Volve production workbook)

- Producing wellbores in file: 6; monthly aggregate 2008-02-01 to 2016-09-01; total oil 63.1 million bbl (converted from Sm3 at 6.28981 bbl/Sm3).
- Peak monthly-average rate 56,129 bbl/day in 2008-12-01; post-peak exponential fit gives a nominal annual decline of 19.2% (R2 0.42); indicative only.

**Data quality checks:**

| check | value |
|---|---|
| daily rows | 1.56e+04 |
| duplicate (date, wellbore) rows | 0 |
| rows with ON_STREAM_HRS > 24 | 20 |
| rows with negative oil volume | 0 |
| production rows with missing oil volume | 0 |
| production rows with missing on-stream hours | 0 |
| production rows with oil > 0 but on-stream hours == 0 | 1 |
| daily-vs-monthly sheet: matched well-months | 311 |
| daily-vs-monthly sheet: well-months with |oil diff| > 1 Sm3 | 0 |
| daily-vs-monthly sheet: max |oil diff| Sm3 | 1.46e-11 |
| monthly sheet well-months not found in daily | 215 |

**Wellbore summary:**

| wellbore | first_date | last_date | cum_oil_bbl | water_cut_pct | uptime_pct_of_calendar_span | oil_share_pct |
|---|---|---|---|---|---|---|
| 15/9-F-12 | 2008-02-12 | 2016-09-17 | 28,804,873.9 | 59.9 | 86.5 | 45.6 |
| 15/9-F-14 | 2008-02-12 | 2016-09-17 | 24,795,899.0 | 64.4 | 83.3 | 39.3 |
| 15/9-F-11 | 2013-07-08 | 2016-09-17 | 7,219,752.7 | 48.7 | 92.8 | 11.4 |
| 15/9-F-1 C | 2014-04-07 | 2016-04-21 | 1,117,757.9 | 53.8 | 55.8 | 1.8 |
| 15/9-F-15 D | 2014-01-12 | 2016-09-17 | 934,153.5 | 26.1 | 75.8 | 1.5 |
| 15/9-F-5 | 2016-04-11 | 2016-09-17 | 258,892.9 | 24.7 | 77.4 | 0.4 |

**Yearly totals:**

| year | oil_bbl | gas_mcf | water_bbl | water_cut_pct |
|---|---|---|---|---|
| 2,008.0 | 11,097,584.5 | 9,077,240.6 | 147,866.8 | 1.3 |
| 2,009.0 | 16,884,315.9 | 13,277,692.0 | 1,459,888.4 | 8.0 |
| 2,010.0 | 10,629,166.0 | 8,614,963.6 | 11,872,612.5 | 52.8 |
| 2,011.0 | 5,333,541.3 | 4,602,218.6 | 13,778,711.1 | 72.1 |
| 2,012.0 | 3,611,648.7 | 3,185,691.2 | 13,268,993.4 | 78.6 |
| 2,013.0 | 3,509,792.8 | 3,093,136.1 | 16,204,851.3 | 82.2 |
| 2,014.0 | 4,674,004.9 | 3,947,896.5 | 17,083,570.0 | 78.5 |
| 2,015.0 | 5,420,237.9 | 4,535,249.5 | 12,641,422.8 | 70.0 |
| 2,016.0 | 1,971,038.1 | 1,768,176.3 | 9,893,030.9 | 83.4 |

**Monthly-rate forecast backtest (6-month horizon, 4 origins):**

| model | MAE | RMSE | MAPE_pct | mean_bias | origins |
|---|---|---|---|---|---|
| Damped Holt (trend) smoothing | 2,670 | 3,249 | 44 | 1,340 | 4 |
| Naive (last value) | 2,699 | 3,336 | 46 | 1,604 | 4 |
| Simple exponential smoothing | 2,761 | 3,332 | 47 | 1,457 | 4 |
| Moving average (3 months) | 3,003 | 3,534 | 52 | 1,656 | 4 |

Limits: the file has no maintenance, cost or price data, so no reliability or financial KPIs are derived. Rates are as-reported allocations.

## B. BSEE OGOR-A monthly production (2025-01 to 2026-06)

Column names follow the OGOR-A layout as understood by the author (files have no header). Oil/gas/water volume columns were identified by magnitude and behaviour only; verify against the official BSEE data dictionary before publishing. Codes are not decoded. OGOR-B/C files were not used.

- 18 months, 49.0 operators. Reported oil 1,077 million bbl, gas 1,144 million mcf, water 618 million bbl.
- Concentration: top 5 operators hold 72.2% of reported oil, top 10 hold 86.5%; HHI 1395 (0-10,000 scale).

**Data quality checks:**

| check | value |
|---|---|
| rows | 85205 |
| distinct months | 18 |
| unparsable month | 0 |
| non-numeric oil/gas/water values | 0 |
| negative oil/gas/water values | 0 |
| days_on_production > 31 | 0 |
| rows repeated on (lease, completion, month, API, interval) | 0 |
| rows with all three volumes = 0 | 54656 |
| rows with volumes > 0 but days_on_production == 0 | 0 |
| rows with days_on_production > 0 but all volumes = 0 | 1207 |

**Top 10 operators by oil:**

| operator_name | oil_bbl | oil_share_pct | water_to_oil_ratio |
|---|---|---|---|
| SHELL OFFSHORE INC. | 285342168 | 26.5 | 0.3 |
| BP EXPLORATION & PRODUCTION INC | 212773207 | 19.8 | 0.5 |
| CHEVRON USA INC | 124948634 | 11.6 | 0.3 |
| ANADARKO PETROLEUM CORPORATION | 101074973 | 9.4 | 0.4 |
| MURPHY EXPLORATION & PRODUCTION COMPANY - USA | 52696765 | 4.9 | 0.3 |
| LLOG EXPLORATION OFFSHORE LLC | 43249085 | 4.0 | 0.3 |
| UNION OIL COMPANY OF CALIFORNIA | 30839477 | 2.9 | 0.1 |
| BOE EXPLORATION & PRODUCTION LLC | 28160532 | 2.6 | 0.0 |
| HESS CORPORATION | 27217951 | 2.5 | 0.5 |
| TALOS QN EXPLORATION LLC | 24888253 | 2.3 | 0.5 |

**Top area-block prefixes by oil:**

| area_prefix | oil_bbl | oil_share_pct |
|---|---|---|
| MC | 431674465 | 40.1 |
| GC | 320270896 | 29.7 |
| WR | 122836929 | 11.4 |
| AC | 68932860 | 6.4 |
| KC | 33857584 | 3.1 |
| GB | 18575123 | 1.7 |
| EW | 17608016 | 1.6 |
| DC | 10864800 | 1.0 |

**Monthly totals:**

| month | oil_bbl | gas_mcf | water_bbl | completions | operators | water_to_oil_ratio |
|---|---|---|---|---|---|---|
| 2025-01-01 | 56034961 | 58090056 | 32822461 | 5075 | 47 | 0.59 |
| 2025-02-01 | 49673730 | 52394411 | 30629985 | 4963 | 47 | 0.62 |
| 2025-03-01 | 56155887 | 60550399 | 34408007 | 4927 | 47 | 0.61 |
| 2025-04-01 | 54903761 | 58559171 | 31204625 | 4907 | 46 | 0.57 |
| 2025-05-01 | 57137177 | 61281528 | 32561877 | 4821 | 46 | 0.57 |
| 2025-06-01 | 58469587 | 62339306 | 34784264 | 4834 | 46 | 0.59 |
| 2025-07-01 | 59986591 | 65722676 | 33682184 | 4799 | 46 | 0.56 |
| 2025-08-01 | 62996525 | 67957109 | 35333713 | 4760 | 44 | 0.56 |
| 2025-09-01 | 61931894 | 65699914 | 35378355 | 4746 | 44 | 0.57 |
| 2025-10-01 | 66501289 | 70337281 | 36845224 | 4737 | 43 | 0.55 |
| 2025-11-01 | 62095590 | 65830080 | 34001719 | 4728 | 43 | 0.55 |
| 2025-12-01 | 65078743 | 69976474 | 35983223 | 4707 | 43 | 0.55 |
| 2026-01-01 | 64971130 | 69341977 | 36910252 | 4673 | 43 | 0.57 |
| 2026-02-01 | 56956960 | 60786988 | 34002303 | 4663 | 43 | 0.60 |
| 2026-03-01 | 62994915 | 67624590 | 36329221 | 4637 | 43 | 0.58 |
| 2026-04-01 | 63955183 | 67772745 | 36340066 | 4430 | 42 | 0.57 |
| 2026-05-01 | 59380671 | 60611083 | 33692840 | 4433 | 41 | 0.57 |
| 2026-06-01 | 57419970 | 59456793 | 32601816 | 4365 | 40 | 0.57 |

Limits: 18 months is too short for decline or seasonality conclusions; operator names are as reported (no merger/name reconciliation); the completion count decline across the period may reflect reporting changes as well as operations.