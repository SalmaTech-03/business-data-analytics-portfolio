# Analytical Methodology

## Pipeline

`data_loading -> validation -> data_cleaning -> feature_engineering ->
kpi_calculations -> visualization`, orchestrated by `run_analysis.py`
and mirrored analytically in `sql/`.

## Tools and why

- **pandas / numpy**: primary analysis engine for a 6,780-row tabular
  dataset - no need for a distributed engine.
- **SQL (PostgreSQL-compatible)**: demonstrates the same analysis
  expressed relationally (aggregations, window functions, CASE
  bucketing) - the SQL and Python answers are cross-checked to agree.
- **matplotlib**: kept dependency-light; every chart is tied to a
  specific business question (see docstrings in `src/visualization.py`).
- **pytest**: 29 tests across data quality, KPI correctness (using
  hand-computed toy data), and business-rule/feature-engineering
  behavior.
- **Power BI (documented, not built)**: the project provides a full
  build specification (`dashboard/`) rather than claiming a `.pbix`
  file exists that wasn't actually built in this environment.

## Statistical approach

- Ratios (utilization rate, realization rate) are computed as
  **sum-of-numerator / sum-of-denominator** at the aggregate level
  (not an average-of-ratios), which is the standard, non-misleading
  way to report a rate across unequal-sized groups.
- `efficiency_tier` (Low/Medium/High) is built from **tertiles of the
  actual data** (`pd.qcut`), not arbitrary fixed cutoffs, so each tier
  represents roughly a third of records regardless of the underlying
  distribution's shape.
- Cross-sectional groupings (department, expense category, fiscal
  quarter) are reported as-is; no trend line or growth rate is
  computed across fiscal quarters, because the data has no year field
  to order them chronologically (see `assumptions_and_constraints.md`).
- Associations reported in `sql/07_discount_profitability.sql` and
  `findings.md` (e.g. inflation rate vs. budget variance) are
  described as observed associations only. A correlation matrix was
  computed (`inflation_rate`, `spending_volatility`,
  `allocation_efficiency`, `budget_variance_pct`, `market_index`) and
  all pairwise correlations were negligible (|r| < 0.03), so this
  project explicitly does NOT claim any of these fields drive budget
  outcomes in this dataset.

## Reproducibility

`python run_analysis.py` from the project root re-runs the entire
pipeline from raw CSV to saved tables/figures. `pytest` re-runs all
29 tests. Both were executed for this repo and the actual results are
what's reported in `findings.md` - no numbers here are hypothetical.
