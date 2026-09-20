# Data Dictionary

Source file: `data/raw/Financial_Budgeting_Dataset.csv`
Rows: 6,780  |  Columns: 20  |  Grain: one row = one budget record
(a Department x Expense_Category x Fiscal_Quarter observation)

| Raw Column | Cleaned Column (snake_case) | Type | Description | Observed Range / Values |
|---|---|---|---|---|
| Record_ID | record_id | int | Unique row identifier | 1 - 6,780 (unique, no duplicates) |
| Fiscal_Quarter | fiscal_quarter | category | Quarter label - **no fiscal year present** | Q1, Q2, Q3, Q4 |
| Department | department | category | Owning department | Finance, HR, IT, Logistics, Marketing, Operations, R&D, Sales |
| Expense_Category | expense_category | category | Type of spend | Infrastructure, Maintenance, Operations, Salaries, Technology, Training |
| Budget_Allocated | budget_allocated | float | Budget allocated to this record (USD) | ~1,001 - 249,985 |
| Budget_Utilized | budget_utilized | float | Budget actually spent (USD) | see profiling; some records exceed allocation |
| Monthly_Expense | monthly_expense | float | A monthly expense figure associated with the record (USD) | ~1,000 - 19,995 |
| Revenue_Forecast | revenue_forecast | float | Forecasted revenue associated with the record (USD) | up to ~299,952 |
| Actual_Revenue | actual_revenue | float | Actual revenue associated with the record (USD) | up to ~289,994 |
| Budget_Variance | budget_variance | float | Provided variance figure (USD). **Independent of Budget_Allocated - Budget_Utilized** - see note below | -19,995.81 to +19,998.28 |
| Revenue_Variance | revenue_variance | float | Provided variance figure (USD). **Independent of Actual_Revenue - Revenue_Forecast** - see note below | -24,999.58 to +24,996.98 |
| Expense_Growth_Rate | expense_growth_rate | float | A provided growth-rate figure (%) | roughly -5 to 10 |
| Seasonal_Index | seasonal_index | float | A provided seasonality index | roughly 0.8 - 1.3 |
| Spending_Volatility | spending_volatility | float | A provided volatility measure | roughly 0.05 - 0.45 |
| Rolling_Expense_Mean | rolling_expense_mean | float | A provided rolling-average expense figure | varies |
| Rolling_Revenue_Mean | rolling_revenue_mean | float | A provided rolling-average revenue figure | varies |
| Inflation_Rate | inflation_rate | float | A provided inflation-rate figure (%) | 0 - 7 |
| Market_Index | market_index | float | A provided market index figure | roughly 95 - 130 |
| Allocation_Efficiency | allocation_efficiency | float | A provided efficiency score (0-100 scale) | 70.00 - 97.99 |
| Budget_Status | budget_status | category | Provided status label | Efficient, Moderate, Inefficient |

## Important note on Budget_Variance / Revenue_Variance

During profiling, `Budget_Variance` was checked against
`Budget_Allocated - Budget_Utilized`, and `Revenue_Variance` against
`Actual_Revenue - Revenue_Forecast`. **Neither reconciles**, and the
mismatch is structural rather than a rounding issue:

| Measure | Supplied column (sum) | Computed from components (sum) |
|---|---|---|
| Budget variance | -$360,163.99 | +$40,899,296.68 |
| Revenue variance | +$715,335.38 | -$48,586,332.96 |

Pearson correlation between each supplied column and its apparent
formula is **0.005** for both - effectively zero. The supplied
columns are also bounded (Budget_Variance within +/-$20k,
Revenue_Variance within +/-$25k) regardless of the record's
allocation or forecast size, which is why they sum to near-zero
figures while the genuine gaps run to tens of millions.

**Conclusion:** these are independently-generated fields, not derived
formulas of the other columns. They are reported where they appear in
the source (the `total_variance` column of
`outputs/tables/kpis_by_department.csv` is `SUM(Budget_Variance)` and
is labeled as the supplied measure), but they are **excluded from
every KPI and rate calculation**. `utilization_rate`,
`revenue_realization_rate`, and all variance figures in
`docs/kpi_framework.md` and `docs/findings.md` are computed from
Allocated/Utilized and Forecast/Actual directly.

**Reading the department table:** `total_variance` (supplied) and
`total_allocated - total_utilized` (computed) in
`kpis_by_department.csv` are two different measures and will not
agree. Use the computed difference for any budget-gap question.

## Fields NOT present in this dataset

No Order ID, Customer, Product, Category/Sub-Category, Region,
Discount, Quantity, or any calendar date/year field. Any retail-style
or true time-series analysis is out of scope for this reason.
