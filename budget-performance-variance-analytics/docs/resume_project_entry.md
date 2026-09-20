# Resume Entry

**Budget Performance & Variance Analytics**
SQL | Python | Power BI | Pandas | DAX

- Built an end-to-end analytics pipeline (SQL + Python) processing
  6,780 department budget records across 8 departments and 6 expense
  categories, from raw CSV through validation, cleaning, feature
  engineering, and a reusable KPI layer.
- Wrote 8 PostgreSQL-compatible SQL scripts (data quality, core KPIs,
  cross-sectional analysis, window-function rankings, business
  questions) validated against parallel pandas calculations for
  consistency.
- Designed and unit-tested (29 pytest tests) a KPI module covering
  budget utilization rate, revenue realization rate, and allocation
  efficiency, with department- and category-level rollups.
- Documented a Power BI star-schema data model, 12 DAX measures, and
  a 5-page dashboard specification (requirements, data dictionary,
  build guide) ready for implementation.
- Identified and clearly documented data-quality findings, including
  that a supplied variance column does not reconcile to its
  underlying fields and that macro-indicator fields show no
  meaningful correlation with budget outcomes in this dataset -
  avoiding unsupported causal claims in the final report.
