# Budget Performance & Variance Analytics

**End-to-End Budget Analytics using SQL, Python & Power BI**

`Python` · `Pandas` · `NumPy` · `SQL (PostgreSQL)` · `Power BI` · `DAX` · `pytest` · `Git`

---

## Executive Summary

An end-to-end analytics workflow that turns 6,780 raw departmental
budget records into validated KPIs, department and expense-category
analysis, and a fully specified Power BI dashboard.

The headline result is a case study in why aggregate metrics mislead:
portfolio-wide budget utilization sits at an apparently on-track **95.99%,**,
but underneath it **46.9% of individual records overspend their
allocation** while **30.1% underspend by more than 30%** — the two
largely cancel out. The analysis identifies three specific
Department × Expense Category combinations worth investigating, rather
than recommending portfolio-wide action that the data doesn't support.

Every number in this repository was calculated by running the pipeline
against the actual dataset. Nothing is estimated or illustrative.

## Business Problem

A fictional multi-department organization allocates quarterly budgets
across 8 departments and 6 expense categories. It holds raw budget,
expense, and revenue-forecast records but has no structured way to
answer:

- Are departments spending within their allocated budgets?
- Which expense categories consume the most budget, and how efficiently?
- How accurate is revenue forecasting, and where is it weakest?
- Which areas warrant management investigation?

## Business Objectives

1. Establish and document data quality honestly before analysing.
2. Build a reproducible pipeline from raw CSV to KPI outputs.
3. Express the same analysis in SQL for cross-validation.
4. Define a tested, auditable KPI framework.
5. Specify a Power BI star-schema model and dashboard.
6. Produce findings grounded strictly in calculated results.

## Dataset

**`Financial_Budgeting_Dataset.csv`** — a **public/sample dataset**
representing a fictional organization. This is not real company data,
and no finding here describes any actual business.

| Property | Value |
|---|---|
| Rows | 6,780 |
| Columns | 20 |
| Grain | One budget record associated with a Department × Expense Category × Fiscal Quarter observation |
| Departments | 8 (Sales, Finance, R&D, Marketing, Logistics, IT, HR, Operations) |
| Expense Categories | 6 (Infrastructure, Maintenance, Operations, Salaries, Technology, Training) |
| Quarter labels | Q1–Q4 (**no fiscal year present**) |
| Missing values | 0 |
| Duplicate records | 0 |

Field-level detail: [`docs/data_dictionary.md`](docs/data_dictionary.md)

> **Scope note.** This project was originally templated around a retail
> Sample Superstore dataset. The dataset actually supplied is a
> departmental budgeting dataset with different dimensions and grain —
> no customer, product, region, discount, or date fields. Rather than
> force retail questions onto data that cannot answer them, the
> business questions, SQL layer, and documentation were re-scoped to
> the real data. Files retaining template names (e.g.
> `sql/04_product_analysis.sql`) state in their headers what they were
> reframed to. Full rationale:
> [`docs/assumptions_and_constraints.md`](docs/assumptions_and_constraints.md)

## Technology Stack

| Layer | Tools |
|---|---|
| Data processing | Python 3.12, pandas, NumPy |
| Analytical SQL | PostgreSQL-compatible SQL (window functions, CTEs, aggregations) |
| Visualization | matplotlib (pipeline), Power BI (dashboard spec) |
| Semantic layer | DAX |
| Testing | pytest (34 tests) | 
| Version control | Git / GitHub |

## Architecture

```
data/raw/Financial_Budgeting_Dataset.csv
    ↓  src/data_loading.py         locate · load · validate columns
    ↓  src/validation.py           structural + domain checks
    ↓  src/data_cleaning.py        standardize · type-convert · report
    ↓  src/feature_engineering.py  derived ratios and flags
    ↓  src/kpi_calculations.py     KPI layer
    ↓  src/visualization.py        business-question charts
    ↓  outputs/tables/ · outputs/figures/
    ↓  Power BI star schema (specified in dashboard/)
```

Orchestrated by `run_analysis.py`. The `sql/` layer mirrors the same
analysis relationally.

## Data Quality

| Check | Result |
|---|---|
| Missing values | 0 |
| Fully duplicated rows | 0 |
| Duplicate `Record_ID` | 0 |
| Negative values in non-negative fields | 0 |
| Categorical domain violations | 0 |
| Rows preserved through cleaning | 6,780 → 6,780 |

**Two issues flagged and disclosed rather than silently corrected:**

1. **258 records (3.8%)** show Budget Utilized exceeding 3× Budget
   Allocated. Raised as a validation warning, retained in the data,
   and disclosed wherever utilization metrics appear.
2. **`Budget_Variance` and `Revenue_Variance` do not reconcile** to
   their component calculations — correlation ~0.005, with the
   supplied budget variance summing to −$360,164 against a genuine
   computed gap of +$40,899,297. Both supplied columns are bounded
   per-record (±$20k / ±$25k) irrespective of record size, indicating
   independently-generated fields. They are excluded from the KPI
   layer and the Power BI model, and the rollup tables expose the two
   quantities under distinct names (`supplied_budget_variance` vs
   `computed_budget_gap`) so they cannot be conflated.

The cleaning pipeline operates under a **non-destructive policy** — it
never silently drops or alters records.

Full report: [`docs/data_quality.md`](docs/data_quality.md)

## SQL Analysis

Eight PostgreSQL-compatible scripts, each with stated business purpose,
commented queries, and output explanation:

| File | Purpose |
|---|---|
| `01_data_quality.sql` | Row counts, nulls, duplicates, domain checks, ranges |
| `02_core_kpis.sql` | Headline budget and revenue KPIs |
| `03_time_series_analysis.sql` | Quarter-label comparison (explicitly *not* a trend) |
| `04_product_analysis.sql` | Expense category performance with `RANK()` |
| `05_customer_analysis.sql` | Department performance and efficiency ranking |
| `06_regional_analysis.sql` | Department × Quarter with `RANK() OVER (PARTITION BY …)` |
| `07_discount_profitability.sql` | Inflation-band and volatility association analysis |
| `08_business_questions.sql` | Labeled queries per business question |

Techniques: aggregate functions, `GROUP BY … HAVING` duplicate
detection, `NULLIF` safe division, `CASE` bucketing, and window
functions for rankings and percent-of-total without self-joins.

## Python Analysis

Six single-purpose modules under `src/`, plus five executed Jupyter
notebooks under `notebooks/`. Notable decisions:

- Rates computed as **sum-of-numerator ÷ sum-of-denominator**, not
  average-of-ratios — the correct approach across unequal group sizes.
- Division guarded throughout, with an explicit zero-denominator test.
- Efficiency tiers built from **`pd.qcut` tertiles of the actual
  distribution**, not arbitrary fixed thresholds.
- Every chart function documents the business question it answers.

## KPI Framework

| KPI | Value |
|---|---|
| Total Budget Allocated | $1,019,783,032.04 |
| Total Budget Utilized | $978,883,735.36 |
| Overall Utilization Rate | 95.99% |
| Total Revenue Forecast | $1,250,614,857.82 |
| Total Actual Revenue | $1,202,028,524.86 |
| Revenue Realization Rate | 96.12% |
| Average Allocation Efficiency | 84.04 / 100 |
| Records Overspent | 46.9% |
| Records Underspent (>30% below allocation) | 30.1% |
| Budget Status mix | Efficient 34.0% · Inefficient 33.4% · Moderate 32.6% |

Each KPI has an explicit formula, a docstring, unit tests, and a
matching DAX measure. Detail: [`docs/kpi_framework.md`](docs/kpi_framework.md)

## Power BI Dashboard


**Model:** star schema — one fact table plus `Dim_Department` and
`Dim_ExpenseCategory`, single-direction filtering.

**No date table** — Power BI time intelligence requires a contiguous
calendar column, and `Fiscal_Quarter` is four labels with no year. All
time-intelligence DAX is deliberately omitted rather than included in
a form that would silently produce meaningless results.

**Five pages:** Executive Overview · Department Performance · Expense
Category Analysis · Budget Status & Efficiency · Forecast Accuracy &
Data Notes.

**Twelve DAX measures**, each annotated with the Python function it
mirrors, validated against `outputs/tables/kpi_summary.json`.

- [`dashboard/dashboard_requirements.md`](dashboard/dashboard_requirements.md)
- [`dashboard/dashboard_data_dictionary.md`](dashboard/dashboard_data_dictionary.md)
- [`dashboard/dax_measures.md`](dashboard/dax_measures.md)
- [`dashboard/power_bi_build_guide.md`](dashboard/power_bi_build_guide.md)

## Key Findings

1. **Overall utilization is 95.99%** — close to but under allocation.
2. **The aggregate hides wide variance** — 46.9% of records overspend,
   30.1% underspend by >30%; they largely offset.
3. **Three combinations stand out** — Finance/Operations (130.0%),
   IT/Salaries (126.1%), Finance/Training (125.9%).
4. **Department-level efficiency is narrowly clustered** (83.66–84.32
   on a 0–100 scale) — no departmental outlier.
5. **Revenue forecasting is weakest in Operations (93.4%) and Finance
   (94.7%)**; Logistics alone exceeds forecast at 101.1%.
6. **Budget Status is evenly distributed** — "Inefficient" share
   ranges only 32.2%–34.7% across all departments.
7. **Spending volatility does not differentiate Budget Status** —
   group means differ by ~0.004 against a within-group SD of ~0.115.
8. **Macro fields show negligible linear correlation with the measured budget outcomes** — every pairwise correlation
   between inflation, market index, volatility, and budget outcomes is
   below |r| = 0.03.

Each finding is documented as Finding → Evidence → Business Meaning in
[`docs/findings.md`](docs/findings.md).

## Business Recommendations

1. Review the three high-utilization combinations individually rather
   than adjusting budgets portfolio-wide.
2. Report overspend/underspend share alongside the aggregate
   utilization rate — the aggregate alone misleads.
3. Examine forecasting methodology specifically for Operations and
   Finance.
4. Do not treat the macro-indicator fields as 
   established predictors based on this dataset alone.
5. Request a fiscal year field before attempting trend analysis.

Each follows Finding → Evidence → Business Implication → Recommended
Action → KPI to Monitor → Limitation, with no causal claims:
[`docs/recommendations.md`](docs/recommendations.md)

## Testing

**34 pytest tests, all passing.**

```
tests/test_data_quality.py       12 passed
tests/test_kpi_calculations.py   16 passed
tests/test_business_rules.py      6 passed
============================== 34 passed ==============================
```

KPI formulas are verified against a hand-built DataFrame with known
values, not against the pipeline's own output. Tests also cover
row-preservation through cleaning, zero-denominator guards, and a
cross-check that department-level totals sum to the portfolio total.

## Limitations

1. **No fiscal year** — no trend, growth, or seasonality analysis is
   possible. All quarter comparisons are cross-sectional. This is the
   single largest constraint.
2. **No customer, product, or region dimension** — two categorical
   cuts only.
3. **Unreconciled variance columns** — cause unknown; excluded from
   the KPI layer.
4. **The dataset appears synthetic** — zero nulls, zero duplicates,
   and near-zero correlation between naturally-related fields.
   Findings demonstrate analytical method, not real-world financial
   behaviour.
5. **No explanatory fields** — the analysis identifies *where* to
   investigate, never *why*.
6. **No causal inference** — all results are cross-sectional
   associations.
7. **The Power BI dashboard is specified, not built.**
8. **Not a production deployment** — this is a portfolio project
   demonstrating an analytical workflow.

## Project Structure

```
budget-performance-variance-analytics/
├── data/
│   ├── raw/              # git-ignored — place the CSV here
│   ├── processed/
│   └── README.md         # privacy rationale
├── sql/                  # 8 PostgreSQL analysis scripts
├── notebooks/            # 5 executed Jupyter notebooks
├── src/                  # 6 pipeline modules
├── dashboard/            # Power BI specification (4 docs)
├── outputs/
│   ├── figures/          # 6 generated charts
│   └── tables/           # aggregated CSV + KPI JSON
├── reports/
│   ├── executive_summary.md
│   └── project_report.md
├── docs/                 # 11 documentation files
├── tests/                # 34 pytest tests
├── README.md
├── requirements.txt
├── pytest.ini
├── run_analysis.py
├── PORTFOLIO_QUALITY_CHECKLIST.md
└── .gitignore
```

## How to Run

```bash
# 1. Clone and enter the repository
git clone <your-repo-url>
cd budget-performance-variance-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place the dataset
#    Put Financial_Budgeting_Dataset.csv in data/raw/
#    (this folder is git-ignored — see data/README.md)

# 4. Run the full pipeline
python run_analysis.py

# 5. Run the test suite
pytest
```

The pipeline prints a KPI summary and writes aggregated tables to
`outputs/tables/` and charts to `outputs/figures/`.

**SQL:** load the CSV into a PostgreSQL table named `budget_records`
with snake_case column names, then run the scripts in `sql/` in order.

**Power BI:** follow
[`dashboard/power_bi_build_guide.md`](dashboard/power_bi_build_guide.md).

## Privacy

This dataset contains **no personal data** — records are departmental
budget entries with no customer names, addresses, emails, or
individual-level information.

The raw data folder is nevertheless git-ignored on principle, so the
rule holds consistently for any future dataset and nobody has to
re-verify safety before a push. Only **aggregated outputs**
(group-by tables, summary JSON, charts) are committed — no row-level
records. Rationale: [`data/README.md`](data/README.md)


## Resume Version

**Budget Performance & Variance Analytics**
`SQL` · `Python` · `Power BI` · `Pandas` · `DAX`

- Built an end-to-end analytics pipeline (SQL + Python) processing
  6,780 department budget records across 8 departments and 6 expense
  categories, from raw CSV through validation, cleaning, feature
  engineering, and a reusable KPI layer.
- Wrote 8 PostgreSQL-compatible SQL scripts (data quality, core KPIs,
  cross-sectional analysis, window-function rankings, business
  questions) validated against parallel pandas calculations.
- Designed and unit-tested (34 pytest tests) a KPI module covering
  budget utilization rate, revenue realization rate, and allocation
  efficiency, with department- and category-level rollups.
- Documented a Power BI star-schema data model, 12 DAX measures, and a
  5-page dashboard specification ready for implementation.
- Identified and documented data-quality findings — including a
  supplied variance column that failed reconciliation and macro
  indicators with no meaningful correlation to outcomes — avoiding
  unsupported causal claims in the final report.

---

*Portfolio project built on a public/sample dataset representing a
fictional organization. Not a production system; no real business
impact is claimed.*
