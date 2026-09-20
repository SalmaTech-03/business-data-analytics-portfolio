# Data Quality Report

Generated from actually running `src/data_cleaning.py` and
`src/validation.py` against `data/raw/Financial_Budgeting_Dataset.csv`.

## Summary

| Check | Result |
|---|---|
| Row count | 6,780 |
| Column count | 20 |
| Fully duplicated rows | 0 |
| Duplicate `Record_ID` values | 0 |
| Missing values (any column) | 0 |
| Negative values in non-negative fields (Budget_Allocated, Budget_Utilized, Monthly_Expense, Revenue_Forecast, Actual_Revenue, Inflation_Rate, Allocation_Efficiency) | 0 |
| Categorical domains (Fiscal_Quarter, Department, Expense_Category, Budget_Status) | All values in-domain, no unexpected labels |
| Unique departments | 8 |
| Unique expense categories | 6 |
| Fiscal quarter labels | Q1, Q2, Q3, Q4 (no year - not a true date field) |

## Warning flagged by validation (not a hard failure)

`src/validation.py::validate_utilization_sanity` flags **258 records
(3.8% of the dataset)** where `Budget_Utilized` is more than 3x
`Budget_Allocated`. These are not removed - they are legitimate data
points in a synthetic dataset with a wide utilization range - but
they are worth knowing about before treating "utilization rate" as a
tightly-bounded metric. They are visible in the long right tail of
`outputs/figures/utilization_rate_by_department.png`-style analysis
and are called out explicitly in `findings.md` and
`assumptions_and_constraints.md`.

## Formula-consistency check

`Budget_Variance` and `Revenue_Variance` were checked against the
values you'd expect if they were simple derived columns
(`Allocated - Utilized` and `Actual - Forecast` respectively).
**Neither reconciles**, and the mismatch is structural, not rounding:

| Measure | Supplied column (sum) | Computed from components (sum) | Correlation |
|---|---|---|---|
| Budget variance | -$360,163.99 | +$40,899,296.68 | 0.005 |
| Revenue variance | +$715,335.38 | -$48,586,332.96 | 0.005 |

Both supplied columns are bounded per-record (+/-$20k and +/-$25k
respectively) regardless of the record's allocation or forecast size,
which is why they sum to near-zero while the genuine gaps run to tens
of millions. They are independently-generated fields.

This is documented, not silently corrected. The KPI layer computes
its own variance and exposes the two quantities under distinct names
(`supplied_budget_variance` vs `computed_budget_gap`) so they cannot
be conflated. Locked in by
`tests/test_kpi_calculations.py::test_supplied_variance_and_computed_gap_are_different_quantities`.

## Conclusion

The dataset is structurally clean (no nulls, no duplicates, valid
categorical domains) and required no destructive cleaning. The
cleaning pipeline (`src/data_cleaning.py`) is row-count-preserving on
this data (6,780 rows in, 6,780 rows out) - confirmed by
`tests/test_data_quality.py::test_cleaning_does_not_drop_rows`.
