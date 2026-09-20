# Resume Project Entry

## Sales Performance & Profitability Analytics
**SQL | Python (Pandas) | Power BI | DAX | pytest**

- Built an end-to-end analytics pipeline in Python (Pandas) that loads,
  validates, cleans, and transforms 10K+ retail transaction records into
  order-, customer-, and product-level analytical tables, with zero rows
  dropped and every cleaning decision logged in a reproducible report.
- Wrote an 8-file PostgreSQL analytics layer using CTEs, window functions
  (`RANK`, `NTILE`, `LAG`), and aggregate queries to answer revenue,
  profitability, customer, and regional performance questions, cross-validating
  every query's output against independently calculated Python results.
- Designed a star-schema Power BI data model (fact + 4 dimension tables)
  with documented DAX measures for revenue, profit margin, YoY growth, and
  customer retention KPIs across a 5-page interactive dashboard specification.
- Delivered findings and recommendations tied directly to calculated
  results (e.g. identifying that a top-3-revenue state was the single
  largest loss-making state), explicitly distinguishing correlation from
  causation where the data didn't support a causal claim.
- Enforced data privacy throughout: built a de-identification step into
  the pipeline and covered it with an automated test, ensuring no
  customer-identifying fields reach any public-facing output.
- Validated the pipeline with 36 automated tests (pytest-style) covering
  data quality, KPI formula correctness, and business-rule consistency.
