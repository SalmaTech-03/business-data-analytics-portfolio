# Recommendations

Format: **Finding -> Evidence -> Business Implication -> Recommended
Action -> KPI to Monitor -> Limitation.** These are written as if
advising the fictional organization behind the sample dataset - they
are illustrative, not real business advice.

---

## 1. Investigate Finance's Operations and Training spend, and IT's Salaries spend

- **Finding:** These are the 3 highest average-utilization
  Department x Expense_Category combinations (Finance/Operations
  130.0%, IT/Salaries 126.1%, Finance/Training 125.9%).
- **Evidence:** `outputs/tables/top_utilization_combinations.csv`.
- **Business Implication:** These combinations consistently exceed
  their allocated budget by roughly a quarter, more than any other
  pairing in the portfolio.
- **Recommended Action:** Route these three combinations to a
  targeted budget review before the next allocation cycle, rather
  than adjusting budgets portfolio-wide.
- **KPI to Monitor:** Department x Expense_Category utilization rate,
  reviewed quarterly per combination (not just per department).
- **Limitation:** The dataset has no explanatory fields (e.g. project
  codes, headcount changes) that would explain *why* these
  combinations run over - this flags where to look, not why.

---

## 2. Don't rely on the aggregate 96% utilization rate as a health signal

- **Finding:** 46.9% of records are overspent and 30.1% are
  underspent by 30%+, despite a near-100% aggregate rate.
- **Evidence:** Findings 1-2, `outputs/tables/kpis_by_department.csv`.
- **Business Implication:** A single portfolio-level utilization
  number can look healthy while masking significant record-level
  variance in both directions.
- **Recommended Action:** Report utilization distribution (e.g. %
  overspent, % underspent) alongside the aggregate rate in any
  management dashboard - implemented as a KPI card in
  `dashboard/dashboard_requirements.md`.
- **KPI to Monitor:** Overspent Record Share and Underspent Record
  Share, tracked alongside Overall Utilization Rate.
- **Limitation:** Without a time dimension, it's not possible to say
  whether over/underspend is worsening or improving.

---

## 3. Improve revenue forecasting for Operations and Finance

- **Finding:** Operations (93.35%) and Finance (94.73%) have the
  weakest revenue realization rates of the 8 departments.
- **Evidence:** Finding 5, department revenue rollup.
- **Business Implication:** These two departments' forecasts are
  furthest from actuals, which could distort planning that depends on
  their forecasts.
- **Recommended Action:** Review the forecasting method used for
  Operations and Finance specifically, rather than adjusting the
  company-wide forecasting process.
- **KPI to Monitor:** Revenue Realization Rate by department,
  reviewed each forecasting cycle.
- **Limitation:** The dataset doesn't indicate the forecasting method
  used, so this recommendation identifies *where* accuracy is
  weakest, not a specific fix.

---

## 4. Do not use Inflation_Rate, Market_Index, or Spending_Volatility as budget-outcome predictors in this dataset

- **Finding:** All pairwise correlations between these fields and
  budget/efficiency outcomes are below |r| = 0.03.
- **Evidence:** Finding 8, `sql/07_discount_profitability.sql`.
- **Business Implication:** Any model or narrative that assumes these
  macro fields explain budget performance would not be supported by
  this data.
- **Recommended Action:** If macro-driver analysis is a priority, it
  would need a dataset where these fields are populated from a real
  source (vs. what appears to be independently-generated synthetic
  values here) - see `assumptions_and_constraints.md`.
- **KPI to Monitor:** N/A for this dataset; re-evaluate if a
  real-world data source replaces the current file.
- **Limitation:** Absence of correlation in this sample doesn't prove
  absence of relationship in real operations - it's a property of
  this specific (likely synthetic) dataset.

---

## 5. Add a fiscal year field before attempting trend analysis

- **Finding:** Fiscal_Quarter has no year, so no valid trend line can
  be computed.
- **Evidence:** `assumptions_and_constraints.md`, item 2.
- **Business Implication:** Leadership cannot currently answer "is
  Q3 performance improving year over year" from this data.
- **Recommended Action:** If this were a real data pipeline, request
  a fiscal-year field be added to the source extract before building
  any quarter-over-quarter or year-over-year dashboard visual.
- **KPI to Monitor:** N/A until the field exists.
- **Limitation:** This is a data-availability gap, not something
  analysis can work around without fabricating a year.
