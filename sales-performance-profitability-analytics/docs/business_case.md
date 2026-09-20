# Business Case

## Context

This project is built around a **fictional** retail company (referred to
generically as "the business" throughout) that sells furniture, office
supplies, and technology products across the United States and Canada. It
is **not** a real company, and the underlying data is the public **Sample
Superstore** dataset, widely used for BI and analytics education.

## The problem

The business has years of transactional sales data (line-item orders with
customer, product, geography, discount, and profit fields) but no
structured analytical system for turning that data into decisions.
Questions like "which categories are actually profitable?" or "is our
discounting strategy working?" currently require manually digging through
raw exports, if they can be answered at all.

## What this project delivers

An end-to-end analytics workflow that takes the raw transactional export
and produces:

1. A validated, documented, reproducible **data cleaning pipeline**
   (`src/`, `run_analysis.py`).
2. A **SQL analytics layer** (`sql/`) answering the specific questions
   management would ask, using CTEs, window functions, and aggregate
   queries.
3. **Python notebooks** (`notebooks/`) that walk through data quality,
   sales trends, customer behavior, and product profitability with
   business interpretation attached to every chart.
4. A documented **KPI framework** (`docs/kpi_framework.md`) with a formula,
   business meaning, and SQL/Python implementation for each metric.
5. A **Power BI dashboard specification** (`dashboard/`) detailed enough to
   build the actual `.pbix` file from scratch, including the data model,
   DAX measures, and page-by-page requirements.
6. **Findings and recommendations** (`docs/findings.md`,
   `docs/recommendations.md`) tied explicitly to calculated results, with
   causal claims flagged as such only where the analysis actually supports
   them.

## Why this matters as a portfolio project

It demonstrates the full analytics engineer / BI developer workflow --
not just "make a chart," but data quality validation, reproducible
pipelines, tested KPI logic, a real data model, and business communication
-- on a dataset complex enough (10K+ rows, 2 countries, 17 sub-categories,
804 customers) to require real analytical judgment rather than trivial
aggregation.
