# Assumptions and Constraints

## 1. This dataset is not a retail sales dataset

The project brief this repo originated from assumed a Sample
Superstore-style retail dataset (orders, customers, products,
regions, discounts). The dataset actually provided
(`Financial_Budgeting_Dataset.csv`) is a **departmental budgeting**
dataset. The project structure, SQL files, and business questions
were adapted to the real data rather than forcing a retail framing
onto fields that don't exist. Several SQL/doc files explicitly note
where a section (e.g. "regional analysis", "product analysis") was
reframed to the closest available analog (see `sql/06_regional_analysis.sql`
and `sql/04_product_analysis.sql` headers).

## 2. No true calendar time series

`Fiscal_Quarter` contains only `Q1`-`Q4` labels with **no fiscal
year**. This means:
- Records labeled `Q1` are NOT necessarily chronologically before
  records labeled `Q2` - they may span different, unstated years.
- All "by quarter" analysis in this project (`sql/03_time_series_analysis.sql`,
  `kpis_by_quarter()`) is a **cross-sectional comparison of quarter
  labels**, not a trend line, and no growth rate or month-over-month
  change is computed.
- If a real fiscal year field becomes available, this is the first
  place to extend the analysis into genuine time-series work.

## 3. No customer, product, or region dimension

There is no way to compute customer-level metrics (repeat customer
rate, customer lifetime value), product-level metrics (top/bottom
SKUs), or region-level metrics. Department and Expense_Category are
the only two categorical dimensions available, and are used
throughout as the primary analytical cuts.

## 4. Budget_Variance / Revenue_Variance do not equal simple derived formulas

As documented in `data_dictionary.md` and `data_quality.md`, the
supplied `Budget_Variance` and `Revenue_Variance` columns do not
match `Allocated - Utilized` / `Actual - Forecast`. This project
therefore computes its own variance from first principles rather than
relying on the supplied columns, and does not attempt to explain the
discrepancy (which would require information not present in the
file).

## 5. No causal claims

Correlation analysis between `inflation_rate`, `spending_volatility`,
`market_index`, and budget/efficiency outcomes found **negligible
pairwise correlation (|r| < 0.03 for every pair tested)**. This
project does not claim inflation, market conditions, or spending
volatility drive budget or efficiency outcomes in this dataset - the
data does not support that claim. Any relationships reported (e.g.
in `sql/07_discount_profitability.sql`) are framed as observed
cross-sectional patterns only.

## 6. Dataset appears synthetically generated

The combination of (a) zero missing values, (b) zero duplicates,
(c) variance columns that don't reconcile to their component columns,
and (d) near-zero correlation between fields that would normally be
related in real financial data (e.g. inflation and cost growth)
suggests this is a synthetic/generated dataset rather than an export
of real transactional records. This project treats it accordingly -
suitable for demonstrating a full analytics workflow, but findings
should not be read as reflecting real-world financial dynamics.

## 7. Utilization outliers

258 of 6,780 records (3.8%) show Budget_Utilized more than 3x
Budget_Allocated. These are retained (not dropped) per the
non-destructive cleaning policy, but they do widen the tails of any
utilization-based metric and are called out in `findings.md`.
