# KPI Framework

Each KPI below is implemented in `src/kpi_calculations.py`, unit
tested in `tests/test_kpi_calculations.py`, and mirrored in SQL in
`sql/02_core_kpis.sql`. Formulas are stated explicitly so results are
reproducible and auditable.

| KPI | Formula | Actual Result (full dataset) |
|---|---|---|
| Total Budget Allocated | SUM(Budget_Allocated) | $1,019,783,032.04 |
| Total Budget Utilized | SUM(Budget_Utilized) | $978,883,735.36 |
| Overall Utilization Rate | Total Utilized / Total Allocated | 95.99% |
| Computed Budget Gap | Total Allocated - Total Utilized | $40,899,296.68 |
| *Supplied Budget_Variance (provenance only, not used in analysis)* | SUM(Budget_Variance) | *-$360,163.99* |
| Total Revenue Forecast | SUM(Revenue_Forecast) | $1,250,614,857.82 |
| Total Actual Revenue | SUM(Actual_Revenue) | $1,202,028,524.86 |
| Revenue Realization Rate | Total Actual Revenue / Total Revenue Forecast | 96.12% |
| Record Count | COUNT(*) | 6,780 |
| Department Count | COUNT(DISTINCT Department) | 8 |
| Average Allocation Efficiency | AVG(Allocation_Efficiency) | 84.04 / 100 |
| Budget Status Mix | share of records per Budget_Status | Efficient 34.0% / Inefficient 33.4% / Moderate 32.6% |

> **Two variance quantities, deliberately kept apart.** The source
> `Budget_Variance` column does not reconcile to
> `Allocated - Utilized` (correlation ~0.005, sums differ by $41.3M).
> Rollup tables expose both under distinct names -
> `supplied_budget_variance` and `computed_budget_gap` - so they can
> never be mistaken for each other. All analysis uses the computed
> figure. See `docs/data_dictionary.md`.
| Overspent Record Share | share of records where Utilized > Allocated | 46.9% |
| Underspent Record Share | share of records where Utilized < 70% of Allocated | 30.1% |

## Department- and category-level KPIs

`kpis_by_department()` and `kpis_by_expense_category()` compute the
same allocated/utilized/utilization-rate/avg-efficiency rollup at
each grain - see `findings.md` for the actual per-department and
per-category numbers.

## KPIs management should monitor going forward

1. **Overall Utilization Rate** - trending toward >100% signals
   systemic overspend risk.
2. **Overspent Record Share** - currently 46.9% of records exceed
   their allocation; tracking this share over time is more
   actionable than the aggregate rate alone, since the aggregate can
   mask offsetting over/under-spend.
3. **Revenue Realization Rate** by department - Operations (93.4%)
   and Finance (94.7%) currently show the weakest forecast accuracy.
4. **% Inefficient records** by department - flags where budget
   discipline is weakest at the operational level, not just the
   aggregate level.
5. **Allocation Efficiency** distribution (not just the average) -
   the tertile split (`efficiency_tier`) shows how much of the
   portfolio sits in the bottom third.
