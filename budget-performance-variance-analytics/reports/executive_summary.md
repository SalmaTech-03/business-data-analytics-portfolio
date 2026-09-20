# Executive Summary

*Written for a non-technical reader. All figures are calculated from
the actual dataset; see `docs/findings.md` for evidence behind each
point.*

## Executive Summary

An analytics workflow was built to turn 6,780 raw departmental budget
records into a set of reviewable KPIs, department and expense-category
breakdowns, and a dashboard specification. At the portfolio level,
budget spend tracks closely to allocation (96.0% utilization) and
revenue comes in slightly under forecast (96.1% realization). The more
useful finding sits underneath those headline numbers: nearly half of
individual budget records overspend their allocation, and roughly a
third underspend significantly — the two largely cancel out in the
aggregate.

## Business Problem

A fictional organization allocates budget across 8 departments and 6
expense categories but has no structured way to answer basic
questions: are departments spending within budget, which areas
overspend, and how reliable are revenue forecasts? This project
builds that analytical layer.

## Dataset

A **public/sample dataset** (`Financial_Budgeting_Dataset.csv`),
6,780 rows × 20 columns. It is not real company data. Each row is one
Department × Expense Category × Fiscal Quarter budget record. The
dataset contains no customer, product, or geographic information, and
no calendar year — which limits what can be concluded (see
Limitations).

## Key KPIs

| KPI | Value |
|---|---|
| Total Budget Allocated | $1,019,783,032 |
| Total Budget Utilized | $978,883,735 |
| Overall Utilization Rate | 95.99% |
| Total Revenue Forecast | $1,250,614,858 |
| Total Actual Revenue | $1,202,028,525 |
| Revenue Realization Rate | 96.12% |
| Average Allocation Efficiency | 84.04 / 100 |
| Records Overspent | 46.9% |
| Records Underspent (>30% below allocation) | 30.1% |

## Key Findings

1. **The healthy-looking aggregate hides wide variance.** A 96.0%
   utilization rate sounds on-track, but 46.9% of records exceed their
   allocation while 30.1% fall more than 30% short. Offsetting
   over- and underspend produces a reassuring average.
2. **Three combinations stand out for review.** Finance/Operations
   (130.0% utilization), IT/Salaries (126.1%), and Finance/Training
   (125.9%) are the highest-utilization Department × Expense Category
   pairings.
3. **Revenue forecasting is weakest in Operations and Finance**
   (93.4% and 94.7% realization). Logistics is the only department
   where actual revenue exceeded forecast (101.1%).
4. **No department is a systemic problem.** The share of records
   labeled "Inefficient" ranges narrowly from 32.2% to 34.7% across
   all eight departments, and average efficiency scores differ by
   less than one point.
5. **Macro indicators explain nothing here.** Inflation rate, market
   index, and spending volatility show negligible correlation
   (|r| < 0.03) with budget outcomes.

## Business Implications

Management reporting that relies on a single portfolio-level
utilization figure would give a misleading impression of budget
discipline. The actionable signal is at the Department × Expense
Category grain, not the department level — where differences are
too small to act on. Revenue forecasting accuracy is a separate,
department-specific issue worth addressing on its own.

## Recommendations

1. Review the three high-utilization combinations individually rather
   than adjusting budgets across the board.
2. Report overspend/underspend share alongside the aggregate
   utilization rate in all management dashboards.
3. Examine forecasting methodology specifically for Operations and
   Finance.
4. Do not build predictive models on the macro-indicator fields in
   this dataset.
5. Request a fiscal year field before attempting any trend analysis.

Full detail with evidence and limitations per recommendation:
`docs/recommendations.md`.

## Limitations

- **No fiscal year.** Quarter labels (Q1–Q4) carry no year, so no
  genuine trend, seasonality, or growth analysis is possible. All
  quarter comparisons are cross-sectional.
- **No customer, product, or region dimension.** Retail-style
  analysis is out of scope.
- **Supplied variance columns don't reconcile.** `Budget_Variance`
  and `Revenue_Variance` do not equal their component calculations;
  this project computes variance independently and flags the
  discrepancy rather than explaining it.
- **The dataset appears synthetic.** Zero missing values, zero
  duplicates, and near-zero correlation between naturally-related
  fields all point to generated rather than operational data.
  Findings demonstrate analytical method, not real-world financial
  dynamics.
- **No causal claims.** Everything reported is an observed
  cross-sectional pattern.

## Next Steps

1. Build the Power BI dashboard from `dashboard/power_bi_build_guide.md`
   and validate its measures against `outputs/tables/kpi_summary.json`.
2. Source a fiscal year field to unlock time-series analysis.
3. Source project- or cost-center-level detail to move from "where to
   look" to "why it happens" on the flagged combinations.
