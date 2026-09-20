# Interview Discussion Questions & Answers

Answers are specific to this project -- reference actual files, numbers,
and decisions made while building it.

## Business Problem

**1. What problem does this project solve?**
It turns raw Superstore transaction data into a structured analytics
system (SQL layer + Python pipeline + Power BI spec) that can answer
revenue, profitability, product, customer, and regional performance
questions on demand, instead of requiring ad-hoc manual analysis each time.

**2. Why did you pick the Sample Superstore dataset?**
It's realistic enough (10K+ rows, multiple categories/regions/years,
genuine data quirks like the multi-Customer-ID issue) to require real
analytical judgment, while being a well-known public dataset so reviewers
can independently verify my numbers.

**3. What would you do differently with real production data?**
I'd want unit-cost data to calculate true gross margin, marketing-spend
data to evaluate discount ROI properly, and a real "as-of" date to compute
rolling (not lifetime) repeat-customer and retention metrics.

## SQL

**4. Walk me through one of your SQL files.**
`sql/07_discount_profitability.sql` buckets line items into discount
ranges (0%, 0-10%, ..., 50%+), aggregates revenue/profit/margin per
bucket, and separately calculates the Pearson correlation between discount
rate and margin using `CORR()`. The margin turns negative at the 20-30%
bucket and gets progressively worse -- a threshold effect, not a gradual
decline.

**5. Where did you use window functions, and why?**
`sql/03_time_series_analysis.sql` uses `LAG()` to calculate year-over-year
growth without a self-join. `sql/04_product_analysis.sql` uses a running
`SUM() OVER (ORDER BY revenue DESC)` to build a cumulative-revenue-share
(Pareto) column. `sql/05_customer_analysis.sql` uses `NTILE(10)` to bucket
customers into revenue deciles.

**6. How did you handle NULL-related edge cases in SQL (e.g. division by zero)?**
Every division in the SQL files uses `NULLIF(denominator, 0)` to avoid a
divide-by-zero error, matching the same defensive pattern used in the
Python KPI functions (`kpi_calculations.py` uses `.replace(0, pd.NA)` or
an explicit zero-check before dividing).

**7. What's the difference between `RANK()` and `NTILE()`, and why did you pick each?**
`RANK()` (used in `04_product_analysis.sql` and `06_regional_analysis.sql`)
gives each row's ordinal position, with ties sharing a rank -- appropriate
for "who's #1." `NTILE(10)` (used in `05_customer_analysis.sql`) splits
rows into equal-sized buckets -- appropriate for "what share of revenue
comes from the top 10% of customers," which is a group question, not a
ranking question.

**8. Why did you validate SQL logic in SQLite instead of PostgreSQL?**
The development environment had no network access to provision a
PostgreSQL instance. I validated the underlying query *logic* by loading
the cleaned dataset into a local SQLite database and confirming the
results matched the independently-calculated Python KPIs, then wrote the
deliverable `.sql` files in PostgreSQL syntax (documented in
`docs/analytical_methodology.md`). This is disclosed rather than implied
away.

## Python / Pandas

**9. Why is your cleaning pipeline structured as "check and report" rather than "check and fix"?**
Because the actual dataset had zero missing values, zero duplicates, and
zero invalid numeric values at the row level -- there was nothing to
"fix." The pipeline is built to report every check's result (via
`CleaningReport`) and only intervene where a real issue is found, so it
doesn't silently mutate data that's already correct, and it will surface
loudly if a future data refresh introduces real problems.

**10. How do you handle NaN/zero-division risk in your feature engineering?**
`feature_engineering.py`'s `profit_margin` calculation uses
`sales.replace(0, pd.NA)` before dividing, and a dedicated test
(`test_profit_margin_is_only_null_when_sales_is_zero`) asserts that
`profit_margin` is null if and only if `sales` is zero -- catching any
future bug that produces an unexpected null.

**11. What's the difference between your order-level, customer-level, and product-level tables?**
They're three different grains of the same line-item fact table, built by
`feature_engineering.py`'s `build_order_level_table`,
`build_customer_level_table`, and `build_product_level_table`. Each answers
a different class of question (order-size metrics, customer-value metrics,
product-performance metrics) and each has a reconciliation test confirming
its aggregate revenue matches the line-item total exactly.

**12. How did you avoid exposing PII in your Python pipeline?**
`run_analysis.py` explicitly drops `customer_name`, `city`,
`state_province`, and `postal_code` before writing `data/processed/orders_clean.csv`,
and `tests/test_business_rules.py::test_no_pii_columns_in_de_identified_output`
asserts none of those columns are present in that output.

## Data Cleaning

**13. What data-quality issues did you actually find, and how did you handle each?**
Two real quirks: (1) 2 order IDs map to 4 different Customer IDs, all
belonging to the same customer name -- documented as a source-system
artifact and left uncorrected because there's no reliable way to know
which ID is canonical; (2) 32 product IDs have more than one recorded
product name -- documented, and the product-level table groups by ID+name
together rather than guessing which name is correct. See
`docs/data_quality.md`.

**14. How do you know your cleaning pipeline didn't silently drop data it shouldn't have?**
`CleaningReport.rows_in` and `rows_out` are logged on every run --
`run_analysis.py` prints "10,194 rows in -> 10,194 rows out (no rows
dropped)" every time, making any unintended row loss immediately visible.

## Power BI / DAX

**15. Walk me through your data model.**
A star schema built from the single Orders table: `FactSales` at the
center, with `DimDate`, `DimProduct`, `DimGeography`, and `DimCustomer`
(customer_id/segment only -- no name) as dimension tables, all with
1-to-many relationships filtering into the fact table. See
`dashboard/dashboard_data_dictionary.md` for the full schema.

**16. Why build a separate DimDate table instead of using Order Date directly?**
A dedicated date table supports proper time-intelligence DAX (e.g.
`SAMEPERIODLASTYEAR`), lets you mark it as the official Date table in Power
BI (required for many time-intelligence functions to work correctly), and
decouples "the calendar" from "the fact table's date column," which
matters if a second date field (like Ship Date) is ever needed for
analysis.

**17. How would you calculate Profit Margin in DAX, and why that formula specifically?**
`DIVIDE(SUM(FactSales[profit]), SUM(FactSales[sales]))` -- using `DIVIDE()`
instead of `/` to avoid a division-by-zero error in a filtered context
with no rows. This is the same revenue-based margin formula used
everywhere else in the project, since no cost data exists to support a
cost-based margin.

**18. What's the difference between a measure and a calculated column, and where did you use each?**
A measure recalculates dynamically based on filter context (used for
every KPI in `dashboard/dax_measures.md` -- Total Revenue, Profit Margin,
etc.); a calculated column is computed once and stored per-row. This
project avoids calculated columns where a measure would work, per Power BI
star-schema best practice, since measures are more memory-efficient and
correctly respond to slicers/filters.

**19. How would you implement Revenue Growth YoY in DAX?**
Using a time-intelligence pattern:
`VAR CurrentRevenue = [Total Revenue]`
`VAR PriorYearRevenue = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(DimDate[Date]))`
`RETURN DIVIDE(CurrentRevenue - PriorYearRevenue, PriorYearRevenue)`
-- documented in full in `dashboard/dax_measures.md`.

## Dashboard Design

**20. Why 5 dashboard pages instead of 1?**
Each page serves a different audience/question: Executive Overview for a
5-second health check, Product Performance and Customer Analytics for
category/account managers, Regional Analysis for territory decisions, and
Profitability & Discount Analysis for the discount-policy question
specifically. Combining them into one page would overload any single
viewer with irrelevant detail.

**21. How did you decide what NOT to put on the dashboard?**
Anything requiring data this dataset doesn't have (CLV, marketing ROI,
inventory turnover) was excluded rather than approximated -- see
`docs/kpi_framework.md`'s "KPIs deliberately NOT included" section.

## Business Interpretation

**22. What's the single most important insight from this analysis?**
That revenue rank and profit rank diverge at every level of this business
-- the top-revenue customer is unprofitable, a top-3-revenue product has
negative margin, and a top-3-revenue state is the single biggest
loss-maker. Any revenue-only decision process would misallocate attention.

**23. You found a strong negative correlation between discount and margin. Does that mean discounting hurts profit?**
Not necessarily -- it's an association, not a proven causal relationship.
Discounts might be applied selectively to products that were already
low-margin or slow-moving, which would produce the same statistical
pattern without discounting being the cause. I'd want experimental data
(A/B testing different discount policies) to establish causation.

**24. If you had one more data source to add, what would it be, and why?**
Unit cost. It would let me calculate a true gross margin instead of a
revenue-based margin, and separate "this product is underpriced" from
"this product is being discounted too aggressively" -- right now those two
explanations are indistinguishable.

## Limitations

**25. What are the biggest limitations of this analysis?**
(1) No unit-cost data, so margin is revenue-based only; (2) no marketing
or acquisition-channel data, so nothing about *why* customers bought can
be established; (3) the discount-margin relationship is correlational, not
causal; (4) SQL logic was validated in SQLite rather than a live
PostgreSQL instance due to environment constraints, though results were
cross-checked against independently calculated Python KPIs. All of these
are documented explicitly in `docs/assumptions_and_constraints.md` rather
than glossed over.
