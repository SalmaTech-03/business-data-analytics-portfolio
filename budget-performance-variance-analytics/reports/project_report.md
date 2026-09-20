# Project Report

**Budget Performance & Variance Analytics**
End-to-End Budget Analytics using SQL, Python & Power BI

---

## 1. Business Problem

A fictional multi-department organization allocates quarterly budgets
across 8 departments and 6 expense categories. Leadership holds raw
budget, expense, and revenue-forecast records but has no analytical
layer to answer whether departments spend within budget, which areas
overspend, how efficiently budget is allocated, or how reliable
revenue forecasts are. This project builds that layer.

The dataset is a **public/sample dataset** representing a fictional
organization. No claim is made about any real company.

## 2. Objectives

1. Establish data quality and document the dataset honestly.
2. Build a reproducible Python pipeline from raw CSV to KPIs.
3. Express the same analysis in SQL for cross-validation.
4. Define a KPI framework with tested, auditable formulas.
5. Specify a Power BI star-schema model and dashboard.
6. Produce findings and recommendations grounded strictly in
   calculated results.

## 3. Dataset

`data/raw/Financial_Budgeting_Dataset.csv` — 6,780 rows × 20 columns.
Grain: one row per Department × Expense Category × Fiscal Quarter
budget record.

**Dimensions available:** Department (8 values), Expense Category
(6 values), Fiscal Quarter (Q1–Q4 labels, no year), Budget Status
(Efficient / Moderate / Inefficient).

**Measures available:** Budget Allocated, Budget Utilized, Monthly
Expense, Revenue Forecast, Actual Revenue, Allocation Efficiency,
Spending Volatility, Inflation Rate, Market Index, and several
provided derived fields.

**Not present:** Order ID, Customer, Product, Category/Sub-Category,
Region, Discount, Quantity, or any calendar date. Full field-level
detail: `docs/data_dictionary.md`.

### Scope adaptation

This repository was originally scoped around a retail Sample
Superstore dataset. The dataset actually supplied is a departmental
budgeting dataset with different dimensions and grain. Rather than
force retail questions (top products, regional sales, discount vs.
profit, repeat customer rate) onto data that cannot answer them, the
business questions, SQL layer, notebooks, and documentation were
re-scoped to the real data. Where a file retains its original
template name (e.g. `sql/04_product_analysis.sql`), its header states
what it was reframed to. Full rationale: `docs/assumptions_and_constraints.md`.

## 4. Data Architecture

```
data/raw/Financial_Budgeting_Dataset.csv
    ↓  src/data_loading.py        (locate, load, validate columns)
    ↓  src/validation.py          (structural + domain checks)
    ↓  src/data_cleaning.py       (standardize, type-convert, report)
    ↓  src/feature_engineering.py (derived ratios and flags)
    ↓  src/kpi_calculations.py    (KPI layer)
    ↓  src/visualization.py       (business-question charts)
    ↓  outputs/tables/ + outputs/figures/
    ↓  Power BI star schema (documented in dashboard/)
```

Orchestrated by `run_analysis.py`. The SQL layer in `sql/` mirrors the
same analysis relationally for cross-validation.

## 5. Data Cleaning

Implemented in `src/data_cleaning.py` under a strict
**non-destructive policy**: the pipeline never silently drops or
alters records. It standardizes column names to snake_case, coerces
numeric and categorical types, and returns a `CleaningReport`
documenting everything it found.

On this dataset cleaning is row-count-preserving — 6,780 rows in,
6,780 rows out — verified by
`tests/test_data_quality.py::test_cleaning_does_not_drop_rows`.

Cleaning decisions are recorded in the `CLEANING_DECISIONS` constant
and surfaced in the report object, so the rationale travels with the
code.

## 6. Data Quality

| Check | Result |
|---|---|
| Rows / columns | 6,780 / 20 |
| Missing values | 0 |
| Fully duplicated rows | 0 |
| Duplicate Record_ID | 0 |
| Negative values in non-negative fields | 0 |
| Categorical domain violations | 0 |

**Two items flagged, neither corrected:**

1. **258 records (3.8%)** show Budget Utilized exceeding 3× Budget
   Allocated. Raised as a validation *warning*, retained in the data,
   and disclosed wherever utilization metrics appear.
2. **`Budget_Variance` and `Revenue_Variance` do not reconcile** to
   `Allocated − Utilized` and `Actual − Forecast` respectively —
   mean absolute discrepancy in the tens of thousands of dollars.
   These columns are excluded from the KPI layer and the Power BI
   model; variance is computed independently from its components.

Full report: `docs/data_quality.md`.

## 7. SQL Methodology

Eight PostgreSQL-compatible scripts in `sql/`, each with a stated
business purpose, commented queries, and an explanation of output:

| File | Purpose |
|---|---|
| `01_data_quality.sql` | Row counts, nulls, duplicates, domain checks, ranges |
| `02_core_kpis.sql` | Headline budget and revenue KPIs |
| `03_time_series_analysis.sql` | Quarter-label comparison (explicitly *not* a trend) |
| `04_product_analysis.sql` | Expense category performance, `RANK()` window functions |
| `05_customer_analysis.sql` | Department performance and efficiency ranking |
| `06_regional_analysis.sql` | Department × Quarter, `RANK() OVER (PARTITION BY ...)` |
| `07_discount_profitability.sql` | Inflation-band and volatility association analysis |
| `08_business_questions.sql` | Labeled queries answering each business question |

Techniques used: aggregate functions, `GROUP BY ... HAVING` for
duplicate detection, `NULLIF` for safe division, `CASE` bucketing,
and window functions (`RANK()`, `SUM() OVER ()`) for rankings and
percent-of-total without self-joins.

## 8. Python Methodology

Six modules under `src/`, each single-purpose and independently
testable. Key decisions:

- **Rates are computed as sum-of-numerator over sum-of-denominator**,
  not as an average of row-level ratios — the correct approach when
  aggregating across unequally-sized groups.
- **Division is guarded throughout** via
  `np.where(denominator != 0, ...)`, with an explicit test for the
  zero-denominator case.
- **Efficiency tiers use `pd.qcut` tertiles** derived from the actual
  distribution rather than arbitrary fixed thresholds.
- **matplotlib only**, with `Agg` backend for headless pipeline runs.
  Every chart function's docstring states the business question it
  answers.

## 9. KPI Framework

Eleven headline KPIs plus department-, category-, and quarter-level
rollups, each with an explicit formula, a docstring, and unit tests.
Each Python KPI has a matching DAX measure so the dashboard and the
pipeline cannot diverge.

Actual computed values and the recommended monitoring set:
`docs/kpi_framework.md`.

## 10. Power BI Architecture

**No `.pbix` file exists in this repository.** The dashboard is fully
specified for implementation rather than claimed as built.

**Model:** star schema — one fact table (`budget_records` at source
grain) plus `Dim_Department` and `Dim_ExpenseCategory`, with
single-direction filtering from dimension to fact.

**No date table.** Power BI time intelligence requires a contiguous
calendar column; `Fiscal_Quarter` is four category labels with no
year, so it is modeled as a plain slicer and all time-intelligence
DAX is deliberately omitted.

**Five pages:** Executive Overview, Department Performance, Expense
Category Analysis, Budget Status & Efficiency, Forecast Accuracy &
Data Notes.

**Twelve DAX measures**, each annotated with the Python function it
mirrors. Validation step: compare each measure against
`outputs/tables/kpi_summary.json`.

Specification: `dashboard/dashboard_requirements.md`,
`dashboard/dashboard_data_dictionary.md`, `dashboard/dax_measures.md`,
`dashboard/power_bi_build_guide.md`.

## 11. Findings

Nine findings, each structured as Finding → Evidence → Business
Meaning in `docs/findings.md`. Summary:

1. Overall utilization is 95.99% — close to but under allocation.
2. 46.9% of records overspend, 30.1% underspend by >30%; the
   aggregate masks both.
3. Finance/Operations (130.0%), IT/Salaries (126.1%), and
   Finance/Training (125.9%) are the highest-utilization combinations.
4. Department-level efficiency is narrowly clustered (83.66–84.32).
5. Revenue realization is weakest in Operations (93.4%) and Finance
   (94.7%); Logistics alone exceeds forecast (101.1%).
6. Budget Status is evenly distributed with no departmental outlier.
7. Spending volatility does not differentiate Budget Status.
8. All macro-field correlations are negligible (|r| < 0.03).
9. Q2 leads marginally on utilization and efficiency — a label-level
   observation, not a seasonal trend.

## 12. Recommendations

Five recommendations in `docs/recommendations.md`, each following
Finding → Evidence → Business Implication → Recommended Action →
KPI to Monitor → Limitation. No recommendation asserts causation.

## 13. Testing

29 pytest tests across three files, **all passing**:

- `test_data_quality.py` (12) — load success, required columns,
  duplicates, nulls, categorical domains, negative values,
  row-preservation, column standardization.
- `test_kpi_calculations.py` (11) — every KPI formula verified
  against a hand-built DataFrame with known values, plus a
  consistency test that department totals sum to the portfolio total
  and a zero-denominator guard test.
- `test_business_rules.py` (6) — feature-engineering flags,
  utilization-rate correctness, zero-revenue handling, tier labels,
  and an end-to-end validation pass on the real dataset.

Tests assert meaningful properties; none are trivial tautologies.

Run with `pytest` from the project root.

## 14. Limitations

1. **No fiscal year** — no trend, growth, or seasonality analysis is
   possible. This is the single largest constraint.
2. **No customer, product, or region dimension** — limits the
   analysis to two categorical cuts.
3. **Unreconciled variance columns** — cause unknown; excluded from
   the KPI layer.
4. **Dataset appears synthetic** — zero nulls, zero duplicates, and
   near-zero correlation between naturally-related fields. Findings
   demonstrate method, not real-world financial behavior.
5. **No explanatory fields** — the analysis can identify *where* to
   investigate but never *why* an overrun occurred.
6. **No causal inference** — all results are cross-sectional
   associations.
7. **Power BI dashboard is specified, not built.**

## 15. Future Improvements

1. Add a fiscal year field to enable genuine time-series analysis,
   YoY comparison, and Power BI time intelligence.
2. Add project or cost-center granularity to trace overruns to root
   causes.
3. Clarify the derivation of the supplied variance columns with the
   data owner.
4. Build and validate the Power BI dashboard against the pipeline
   outputs.
5. Add a CI workflow (GitHub Actions) to run pytest on every push.
6. If a real dataset replaces this one, revisit the macro-indicator
   correlation analysis, which may behave very differently.
