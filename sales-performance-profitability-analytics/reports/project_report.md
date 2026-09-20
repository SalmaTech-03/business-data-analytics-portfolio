# Project Report: Sales Performance & Profitability Analytics

## 1. Business Problem

See `docs/business_case.md` for the full write-up. In short: a fictional
retail business has raw transactional sales data but no structured
analytics system to answer revenue, profitability, product, customer, and
regional performance questions.

## 2. Objectives

18 specific business questions, listed and cross-referenced to their
answers in `docs/business_questions.md`.

## 3. Dataset

Public **Sample Superstore** dataset (`sample_-_superstore.xls`), 3
sheets: Orders (10,194 rows x 21 columns), People (4 rows), Returns (296
rows). Full profiling in `docs/data_quality.md`, full schema in
`docs/data_dictionary.md`.

## 4. Data Architecture

Star schema for the analytical layer (both the SQL layer's implied model
and the Power BI model): `FactSales` plus `DimDate`, `DimProduct`,
`DimCustomer`, `DimGeography`. See `dashboard/dashboard_data_dictionary.md`
for the full model and `docs/analytical_methodology.md` for the pipeline
architecture diagram.

## 5. Data Cleaning

`src/data_cleaning.py` implements a "check and report" pipeline (not
"check and silently fix"). Result on the actual dataset: 10,194 rows in,
10,194 rows out -- zero rows dropped, because zero rows violated any
business rule at the row level. Two known quirks were found, documented,
and deliberately left uncorrected (see `docs/data_quality.md`): 2 order
IDs spanning multiple customer IDs (same customer, different source-system
IDs), and 32 product IDs with more than one recorded product name.

## 6. Data Quality

Full validation suite (`src/validation.py`) result:

```
[PASS] required_columns
[PASS] no_missing_values
[PASS] no_full_duplicate_rows
[PASS] row_id_is_unique
[PASS] dates_valid
[PASS] positive_quantity
[PASS] positive_sales
[PASS] discount_in_valid_range
[FAIL] order_maps_to_single_customer   (documented, non-blocking quirk)

8/9 checks passed.
```

## 7. SQL Methodology

8 files (`sql/01_data_quality.sql` through `sql/08_business_questions.sql`),
written in PostgreSQL syntax, using CTEs, window functions (`RANK`,
`NTILE`, `LAG`), `CASE` bucketing, and aggregate functions including
`CORR()`. **Validation approach:** the development sandbox had no network
access to provision PostgreSQL, so every query's logic was validated by
loading the cleaned dataset into a local SQLite database and confirming
results matched independently-calculated Python KPIs exactly (see
`docs/analytical_methodology.md` for the full explanation and the caveat
about dialect-specific syntax like `TO_CHAR`/`EXTRACT`/`::numeric` that
should be re-confirmed against a live PostgreSQL instance before
production use).

## 8. Python Methodology

`src/` package: `data_loading.py`, `data_cleaning.py`,
`feature_engineering.py`, `kpi_calculations.py`, `validation.py`,
`visualization.py`, orchestrated end-to-end by `run_analysis.py`. Five
Jupyter notebooks (`notebooks/01`-`05`) walk through data quality, sales
trends, customer analysis, product profitability, and business insights,
each with markdown narrative, executed code, real tabular output, and
interpretation after every substantive result. All 5 notebooks execute
without error.

## 9. KPI Framework

15 KPIs, each with a formula, business meaning, and actual calculated
value, documented in `docs/kpi_framework.md`. 4 KPI categories
(Customer Lifetime Value, Gross Margin, Marketing ROI, Inventory Turnover)
were deliberately excluded because the source data doesn't support them
without fabricating an input.

## 10. Power BI Architecture

Full specification (no `.pbix` built, per the ground rules of this
project) in `dashboard/`: `dashboard_requirements.md` (5 pages),
`dashboard_data_dictionary.md` (star-schema model), `dax_measures.md` (12
documented measures), `power_bi_build_guide.md` (step-by-step
reconstruction instructions with validation checkpoints against known KPI
values).

## 11. Findings

8 findings, each with cited evidence, in `docs/findings.md`. Headline:
revenue rank and profit rank diverge at the customer, product, and state
level simultaneously -- the top-revenue customer is unprofitable, a top-3
product has negative margin, and Texas (a top-3 revenue state) is the
single largest loss-making state in the dataset.

## 12. Recommendations

5 recommendations, each following Finding -> Evidence -> Business Impact
-> Recommended Action -> Expected KPI Impact -> Limitation, in
`docs/recommendations.md`. The discount-policy recommendation explicitly
flags "observed association; causation is not established" per this
project's ground rules.

## 13. Testing

36 tests across 3 files (`tests/test_data_quality.py`,
`tests/test_kpi_calculations.py`, `tests/test_business_rules.py`), all
passing.

**Environment note:** the sandbox used to build this project has no
network access to `pip install pytest`. Rather than skip testing or claim
untested code works, a minimal pytest-compatible shim (`fixture()`,
`approx()`, and a test collector/runner) was built to execute these
*actual, unmodified* pytest-style test files. Output of the run:

```
tests/test_business_rules.py .......... 9 passed
tests/test_data_quality.py ............ 12 passed
tests/test_kpi_calculations.py ........ 15 passed

TOTAL: 36 passed, 0 failed
```

If you clone this repo somewhere with network access, `pip install -r
requirements.txt` will install real `pytest`, and `pytest` (or `pytest
-v`) will run these same test files directly -- no shim required, since
the tests only use standard `pytest.fixture` and `pytest.approx` features.

## 14. Limitations

See `docs/assumptions_and_constraints.md` for the complete list. The two
most significant: (1) no unit-cost data, so every margin is revenue-based;
(2) the discount-profitability relationship is correlational (-0.865), not
proven causal.

## 15. Future Improvements

- Add unit-cost data (if it becomes available) to calculate true gross
  margin and separate pricing issues from discounting issues.
- Run a controlled discount-policy pilot to test the causal hypothesis
  suggested by Finding 3.
- Build the actual `.pbix` dashboard from the specification in `dashboard/`
  and connect it to a live, refreshable data source.
- Add a `data/raw/README.md`-documented process for handling a real
  incremental data refresh (this project was built against a single static
  snapshot).
