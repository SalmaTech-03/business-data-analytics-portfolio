# DAX Measures

Only measures supported by the actual model (no time-intelligence
functions, since there's no real date column - see
`docs/assumptions_and_constraints.md`). Each measure mirrors a
function in `src/kpi_calculations.py` so the dashboard and pipeline
never disagree.

```DAX
Total Budget Allocated =
SUM ( budget_records[Budget Allocated] )
```
Mirrors `kpi.total_budget_allocated()`.

```DAX
Total Budget Utilized =
SUM ( budget_records[Budget Utilized] )
```
Mirrors `kpi.total_budget_utilized()`.

```DAX
Utilization Rate =
DIVIDE ( [Total Budget Utilized], [Total Budget Allocated], BLANK() )
```
Sum-of-numerator / sum-of-denominator, matching the Python approach
(not an average of row-level ratios) - mirrors `overall_utilization_rate()`.

```DAX
Budget Variance ($) =
[Total Budget Allocated] - [Total Budget Utilized]
```
Computed directly rather than trusting the raw `Budget_Variance`
column (see data dictionary note on why).

```DAX
Total Revenue Forecast =
SUM ( budget_records[Revenue Forecast] )
```

```DAX
Total Actual Revenue =
SUM ( budget_records[Actual Revenue] )
```

```DAX
Revenue Realization Rate =
DIVIDE ( [Total Actual Revenue], [Total Revenue Forecast], BLANK() )
```
Mirrors `revenue_realization_rate()`.

```DAX
Average Allocation Efficiency =
AVERAGE ( budget_records[Allocation Efficiency] )
```
Mirrors `average_allocation_efficiency()`.

```DAX
Overspent Record Share =
DIVIDE (
    CALCULATE (
        COUNTROWS ( budget_records ),
        budget_records[Budget Utilized] > budget_records[Budget Allocated]
    ),
    COUNTROWS ( budget_records ),
    BLANK()
)
```
Mirrors the `is_overspent` flag in `feature_engineering.py`.

```DAX
Underspent Record Share =
DIVIDE (
    CALCULATE (
        COUNTROWS ( budget_records ),
        budget_records[Budget Utilized] < budget_records[Budget Allocated] * 0.7
    ),
    COUNTROWS ( budget_records ),
    BLANK()
)
```
Mirrors the `is_underspent` flag.

```DAX
Record Count =
COUNTROWS ( budget_records )
```

```DAX
Pct Inefficient Records =
DIVIDE (
    CALCULATE ( COUNTROWS ( budget_records ), budget_records[Budget Status] = "Inefficient" ),
    COUNTROWS ( budget_records ),
    BLANK()
)
```

## Measures intentionally NOT included

- Any `SAMEPERIODLASTYEAR`, `DATEADD`, or YoY/QoQ growth measure -
  the data has no fiscal year, so these would silently produce
  meaningless or misleading results.
- A "Repeat Customer Rate" or similar - no customer dimension exists.
