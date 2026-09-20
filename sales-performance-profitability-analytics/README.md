# Sales Performance & Profitability Analytics

### End-to-End Sales Analytics using SQL, Python & Power BI

*Built on the public Sample Superstore dataset for portfolio purposes.
This is not a real company, and no business results below are for a real
business -- see [Limitations](#limitations).*

---

## Executive Summary

An end-to-end analytics pipeline that turns 10,194 raw retail transactions
into a validated, tested, documented analytical system: a Python
data-cleaning and KPI pipeline, an 8-file PostgreSQL analytics layer, 5
Jupyter notebooks, a Power BI dashboard specification, and findings/
recommendations tied to real calculated results. Headline numbers:
**$2,326,534.35 revenue, $292,296.81 profit (12.56% margin), 5,111 orders,
804 customers** -- every figure in this README is reproducible by running
`python run_analysis.py`.

## Business Problem

The business has years of transactional sales data but no structured way
to answer: which products/categories are actually profitable, which
regions underperform, whether discounting helps or hurts margin, and who
the highest-value customers really are (revenue and profit rank turn out
to diverge -- see [Key Findings](#key-findings)). Full detail:
[`docs/business_case.md`](docs/business_case.md).

## Business Objectives

18 specific business questions, each answered with a real calculated
result and cross-referenced to the file it's answered in:
[`docs/business_questions.md`](docs/business_questions.md).

## Dataset

Public **Sample Superstore** dataset. 10,194 order line items, 2023-2026,
2 countries, 4 regions, 3 categories, 17 sub-categories, 804 customers,
1,862 products. Full profiling: [`docs/data_quality.md`](docs/data_quality.md).
Full schema: [`docs/data_dictionary.md`](docs/data_dictionary.md).

## Technology Stack

Python (Pandas, NumPy, Matplotlib, Seaborn) | SQL (PostgreSQL dialect) |
Power BI (DAX, star-schema modeling) | pytest | Git/GitHub

## Architecture

```
Raw Excel -> Load -> Validate -> Clean -> Engineer Features -> KPIs
    -> Analysis Tables -> Visualizations -> De-identified Outputs
```

Full diagram and explanation: [`docs/analytical_methodology.md`](docs/analytical_methodology.md).

## Data Quality

The dataset is clean at the row level: **0 missing values, 0 duplicate
rows, 0 invalid numeric values** across 10,194 rows. One known,
low-impact data quirk (2 order IDs spanning multiple customer IDs, traced
to a single customer issued 4 source-system IDs) is documented and
deliberately left uncorrected rather than guessed at. Full report:
[`docs/data_quality.md`](docs/data_quality.md).

## SQL Analysis

8 files in [`sql/`](sql/), using CTEs, window functions (`RANK`, `NTILE`,
`LAG`), `CASE`-based bucketing, and `CORR()`. Every query's result was
cross-validated against independently-calculated Python output during
development (see [`docs/analytical_methodology.md`](docs/analytical_methodology.md)
for the validation methodology, including an honest note on why SQLite was
used for logic validation instead of a live PostgreSQL instance).

## Python Analysis

Modular pipeline in [`src/`](src/) (data loading, cleaning, feature
engineering, KPI calculation, validation, visualization), orchestrated by
[`run_analysis.py`](run_analysis.py). 5 Jupyter notebooks in
[`notebooks/`](notebooks/), each executed with real output embedded (data
quality, sales exploration, customer analysis, product profitability,
business insights).

## KPI Framework

15 KPIs with formula, business meaning, and actual value:
[`docs/kpi_framework.md`](docs/kpi_framework.md).

| KPI | Value |
|---|---|
| Total Revenue | $2,326,534.35 |
| Total Profit | $292,296.81 |
| Profit Margin | 12.56% |
| Total Orders | 5,111 |
| Average Order Value | $455.20 |
| Repeat Customer Rate | 98.51% |

## Power BI Dashboard

Full specification (no `.pbix` file is claimed to exist -- this is
documentation detailed enough to build one):
[`dashboard/dashboard_requirements.md`](dashboard/dashboard_requirements.md)
(5 pages), [`dashboard/dashboard_data_dictionary.md`](dashboard/dashboard_data_dictionary.md)
(star-schema model), [`dashboard/dax_measures.md`](dashboard/dax_measures.md)
(12 documented measures), [`dashboard/power_bi_build_guide.md`](dashboard/power_bi_build_guide.md)
(step-by-step build instructions with validation checkpoints).

## Key Findings

Full detail with evidence: [`docs/findings.md`](docs/findings.md).

1. Revenue grew in 3 of the last 4 years (2025 +29.8%, 2026 +21.4% YoY).
2. Furniture generates $754,748 in revenue but only 2.6% margin, versus
   ~17% for the other two categories.
3. Margin turns negative at every discount level of 20% and above
   (correlation: -0.865) -- **an association, not proven causation**.
4. **Revenue rank and profit rank diverge**: the top-revenue customer is
   unprofitable, a top-3-revenue product has -8.0% margin, and Texas (a
   top-3 revenue state) is the single largest loss-making state
   (-$25,729).
5. Revenue is only moderately concentrated: the top 10% of customers
   generate 31.1% of revenue.

## Business Recommendations

5 recommendations, each following Finding -> Evidence -> Business Impact
-> Recommended Action -> Expected KPI Impact -> Limitation:
[`docs/recommendations.md`](docs/recommendations.md). No causal claim is
made where the data only supports a correlation.

## Testing

36 automated tests (pytest-style) across 3 files -- data quality, KPI
formula correctness, and business-rule consistency (e.g. no PII column
survives the de-identification step). All 36 pass. See
[`reports/project_report.md`](reports/project_report.md) section 13 for
the full run output and an honest note on the test-execution environment.

## Limitations

- **No unit-cost data exists** -- every "margin" figure is `profit / sales`
  (revenue-based), never a cost-based margin.
- **The discount-profitability relationship is correlational, not causal**
  -- stated explicitly everywhere it's discussed.
- **No `.pbix` file is included** -- `dashboard/` is a build specification,
  not a claim that a working dashboard file exists in this repo.
- **This is not a real company** and no finding here reflects real
  business impact.

Full list: [`docs/assumptions_and_constraints.md`](docs/assumptions_and_constraints.md).

## Project Structure

```
sales-performance-profitability-analytics/
├── data/
│   ├── raw/                  (gitignored -- see data/README.md)
│   ├── processed/            (regenerated by run_analysis.py)
│   └── README.md
├── sql/                      8 files, 01_data_quality.sql -> 08_business_questions.sql
├── notebooks/                5 executed Jupyter notebooks
├── src/                      data_loading, data_cleaning, feature_engineering,
│                             kpi_calculations, validation, visualization
├── dashboard/                Power BI requirements, data model, DAX, build guide
├── outputs/
│   ├── figures/              7 charts
│   └── tables/                10 aggregated CSVs
├── reports/
│   ├── executive_summary.md
│   └── project_report.md
├── docs/                      10 documentation files (data dictionary, quality,
│                             KPI framework, findings, recommendations, etc.)
├── tests/                     36 tests across 3 files
├── README.md
├── requirements.txt
├── pytest.ini
├── run_analysis.py
└── .gitignore
```

## How to Run

```bash
# 1. Clone and enter the repo
git clone <this-repo-url>
cd sales-performance-profitability-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place the raw dataset (not included in this repo -- see data/README.md)
#    at data/raw/sample_-_superstore.xlsx or .xls

# 4. Run the full pipeline
python run_analysis.py

# 5. Run the tests
pytest

# 6. Explore the notebooks
jupyter notebook notebooks/
```
