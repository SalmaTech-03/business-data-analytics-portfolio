# Interview Discussion Questions & Answers

Answers are specific to this project - what was actually built and
found, not generic textbook answers.

## Business Problem

**1. What business problem does this project solve?**
It builds a repeatable analytics workflow (SQL + Python + Power BI
spec) that turns raw department budget records into KPIs,
department/category rollups, and a documented dashboard design, so
budget performance and revenue-forecast accuracy can be reviewed
systematically instead of ad hoc.

**2. Why did you adapt the project away from its original retail-sales template?**
The dataset I was actually given was a departmental budgeting
dataset, not a Superstore-style retail dataset - no customers,
products, or regions. Rather than force retail questions onto data
that couldn't answer them (which would mean fabricating findings), I
re-scoped the business questions, SQL, and docs to match the real
data. That decision is documented in `assumptions_and_constraints.md`.

**3. What would you do differently with more time/data?**
Request a fiscal-year field so quarter comparisons become a real
trend line instead of a cross-sectional comparison, and add a project
or cost-center dimension so overspend can be traced to a root cause.

## SQL

**4. Why did you write both SQL and pandas for the same analysis?**
To demonstrate the same logic can be expressed relationally and
cross-validate results - e.g. total budget allocated computed in
`sql/02_core_kpis.sql` matches `kpi.total_budget_allocated()` exactly.

**5. Where did you use window functions, and why?**
`RANK() OVER (...)` in `sql/04_product_analysis.sql` and
`sql/05_customer_analysis.sql` to rank expense categories/departments
by utilization or efficiency without a self-join, and a
`PARTITION BY fiscal_quarter` ranking in `sql/06_regional_analysis.sql`
to find the top department per quarter label.

**6. How would you find duplicate records in SQL?**
`GROUP BY <key columns> HAVING COUNT(*) > 1` - see
`sql/01_data_quality.sql`. On this dataset it returns zero rows.

**7. Walk me through a CTE-worthy query in this project.**
The Department x Expense_Category investigation-candidates query
(`sql/08_business_questions.sql`, Q8) could be rewritten with a CTE
that first computes per-combination utilization, then filters/ranks
in an outer query - I kept it as a single aggregated query here
since the dataset is small enough not to need materializing an
intermediate CTE, but I'd introduce one if adding more join logic.

**8. How do you handle division by zero in SQL?**
`NULLIF(denominator, 0)` throughout, e.g.
`budget_utilized / NULLIF(budget_allocated, 0)`.

## Python / Pandas

**9. How is the pipeline structured?**
`data_loading -> validation -> data_cleaning -> feature_engineering ->
kpi_calculations -> visualization`, each in its own `src/` module with
its own tests, orchestrated by `run_analysis.py`.

**10. Why didn't you drop the 258 "extreme utilization" records?**
The cleaning policy in `src/data_cleaning.py` is explicitly
non-destructive - validation flags them as a warning
(`validate_utilization_sanity`), but removing data isn't a decision
an automated pipeline should make silently. It's called out in
`docs/data_quality.md` and `findings.md` instead.

**11. How did you test your KPI functions?**
`tests/test_kpi_calculations.py` uses a small hand-built DataFrame
with known values, so each formula (e.g. utilization rate) can be
checked against an exact expected number, plus a consistency test
that department-level totals sum to the portfolio total.

**12. How do you avoid divide-by-zero errors in pandas?**
`np.where(denominator != 0, numerator/denominator, np.nan)` in
`feature_engineering.py`, tested explicitly in
`test_zero_allocation_does_not_raise_divide_error`.

**13. Why pd.qcut for the efficiency tiers instead of fixed cutoffs (e.g. <70/70-90/>90)?**
Fixed cutoffs assume a known "good" threshold; `qcut` tertiles adapt
to this dataset's actual distribution (70-98 range) so each tier
holds a comparable number of records, which is more meaningful for
relative comparison across departments.

## Data Cleaning

**14. What data quality issues did you find?**
None that required correction - zero nulls, zero duplicates, no
negative values, valid categorical domains. The one flagged item is
the 258 extreme-utilization records (warning, not an error) and the
mismatch between `Budget_Variance`/`Revenue_Variance` and their
"expected" formulas.

**15. How do you decide what counts as an outlier vs. a data error?**
Here, I didn't have ground truth to call the 258 high-utilization
records "errors" - they're within the same numeric type and range as
the rest of the data, just at the tail. I flagged and reported them
rather than assuming causation either way.

## Power BI / DAX

**16. Walk me through your recommended data model.**
A star schema: one fact table (budget_records at the current grain)
and two small dimension tables (Department, Expense_Category), plus a
lightweight Fiscal_Quarter dimension used *only* as a categorical
filter, not a true date table, since there's no year. See
`dashboard/power_bi_build_guide.md`.

**17. Why not use Fiscal_Quarter as a real Power BI date hierarchy?**
Power BI's built-in date intelligence (e.g. `DATEADD`, YoY functions)
requires a contiguous calendar date column. Fiscal_Quarter here is
just 4 category labels with no year, so it's modeled as a plain
dimension, and no time-intelligence DAX (e.g. `SAMEPERIODLASTYEAR`)
is included - see `dashboard/dax_measures.md` for what was
intentionally left out and why.

**18. What DAX measures did you define, and why those?**
Total Budget Allocated/Utilized, Utilization Rate, Revenue
Realization Rate, Average Allocation Efficiency, and Overspent/
Underspent Record Share - directly mirroring the Python KPI layer so
the dashboard and the pipeline never disagree.

**19. How would you validate the Power BI numbers match the Python analysis?**
Compare each DAX measure's total against the corresponding value in
`outputs/tables/kpi_summary.json` after loading the same source data
into Power BI.

## Dashboard Design

**20. Why 5 dashboard pages?**
Executive Overview (headline KPIs), Department Performance, Expense
Category Analysis, Budget Status & Efficiency, and Forecast Accuracy
& Data-Quality Notes - matching the 5 analytical themes actually
present in the data (see `dashboard/dashboard_requirements.md`).

**21. How would a non-technical manager use page 1?**
It surfaces the headline numbers from `findings.md` Finding 1 and 2 -
total allocated/utilized, overall utilization rate, and the
overspent/underspent record share - so they see both the "looks
fine" aggregate and the "actually more nuanced" record-level split
in one view.

## Business Interpretation

**22. What's the single most important finding?**
Finding 2: the near-100% aggregate utilization rate hides that 47% of
records are overspent and 30% are meaningfully underspent - the
portfolio-level number alone would mislead a manager into thinking
budgets are broadly on-track.

**23. What would you tell a manager who wants to know "why" Finance overspends on Operations?**
That this dataset can't answer "why" - it has no project, headcount,
or vendor-level detail. I'd recommend it as the next data source to
request, and frame the current finding as "where to look," not "why
it happens."

## Limitations

**24. What's the biggest limitation of this project?**
No fiscal year, so no real trend/seasonality analysis is possible -
and the dataset shows almost no correlation between fields that
would normally be related (inflation vs. budget outcomes), suggesting
it's synthetic rather than a real operational export.

**25. If this were a real dataset, what would you flag to a stakeholder before they act on it?**
That `Budget_Variance` and `Revenue_Variance` don't reconcile to
their component columns - I'd get clarification on how those two
columns are actually computed before including them in any external
report.
