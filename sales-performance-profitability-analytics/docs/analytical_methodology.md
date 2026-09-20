# Analytical Methodology

## Pipeline architecture

```
Raw Excel (.xls, 3 sheets)
        |
        v
  src/data_loading.py       -- locate + load + validate structure
        |
        v
  src/validation.py         -- business-rule checks (pre-clean)
        |
        v
  src/data_cleaning.py      -- standardize columns, types, document quirks
        |
        v
  src/feature_engineering.py -- date features, order/customer/product rollups
        |
        v
  src/kpi_calculations.py   -- headline KPIs, time-series, growth
        |
        v
  src/visualization.py      -- business-question-driven charts
        |
        v
  run_analysis.py           -- orchestrates all of the above end-to-end,
                                writes de-identified outputs to
                                data/processed/ and outputs/
```

Every stage is independently importable and independently tested. Nothing
in `notebooks/` or `sql/` duplicates logic silently -- notebooks import
directly from `src/`, and every SQL query's result was cross-checked
against the equivalent Python calculation during development.

## Why both SQL and Python

This project deliberately implements the same core KPIs twice: once in SQL
(`sql/02_core_kpis.sql`) and once in Python
(`src/kpi_calculations.py`). This is not redundant -- it's a form of
validation. During development, every SQL query's actual result was
compared against the Python-calculated equivalent (see the "Actual result"
comments inline in each `.sql` file); any mismatch would have signaled a
bug in one implementation or the other. They all matched.

## SQL validation approach

This project's target dialect is PostgreSQL, since that's the most common
production analytics warehouse dialect and the one specified for this
project. The development sandbox used to build this project does not have
network access to provision a PostgreSQL instance, so query **logic** was
validated by loading the cleaned dataset into a local SQLite database and
running equivalent queries (adjusting only dialect-specific syntax --
e.g. SQLite has no `TO_CHAR`/`EXTRACT`/`::numeric` cast syntax, so the
SQLite validation queries use `strftime`/direct division instead). Every
number documented as an "Actual result" comment in the `sql/*.sql` files
was verified this way against the real dataset before being written down.
Before running these files against a live PostgreSQL warehouse, re-confirm
syntax (particularly `TO_CHAR`, `EXTRACT`, `PERCENTILE_CONT`, and `::numeric`
casts) against your specific Postgres version.

## Reproducibility

Running `python run_analysis.py` from the project root reproduces every
table in `outputs/tables/`, every chart in `outputs/figures/`, and the
de-identified dataset in `data/processed/` from the raw file alone. No
manual step or hidden intermediate file is required.

## Testing approach

`tests/` uses `pytest`-style tests (fixtures, `pytest.approx`) covering
three categories:

1. **Data quality** (`test_data_quality.py`) -- structural and business-rule
   checks on the raw/cleaned data.
2. **KPI correctness** (`test_kpi_calculations.py`) -- formula correctness
   against hand-built toy DataFrames, plus internal-consistency checks
   against the real dataset (e.g. `AOV * orders == total revenue`).
3. **Business rules** (`test_business_rules.py`) -- domain logic like
   revenue-contribution percentages summing to 100%, and a hard check that
   no PII column survives the public-output step.

All 36 tests pass against the real dataset (see `reports/project_report.md`
for the full run output and a note on how they were executed in this
environment).
