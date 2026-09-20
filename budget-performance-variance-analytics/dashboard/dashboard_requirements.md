# Power BI Dashboard Requirements

**No .pbix file has been built in this environment.** This document
specifies exactly what to build so the dashboard can be created
directly from it in Power BI Desktop. Pages and KPIs are adapted to
what this dataset can actually support (no product/region/customer
dimension - see `docs/assumptions_and_constraints.md`).

## Data source
`data/raw/Financial_Budgeting_Dataset.csv` (or the cleaned/featured
output of `run_analysis.py`), loaded as a single fact table plus two
small lookup/dimension tables built from its distinct values
(Department, Expense_Category) - see `power_bi_build_guide.md` for
the modeling steps.

## Page 1 - Executive Overview

**KPI cards:**
- Total Budget Allocated ($1,019,783,032 on full data)
- Total Budget Utilized ($978,883,735)
- Overall Utilization Rate (95.99%)
- Overspent Record Share (46.9%) and Underspent Record Share (30.1%)
- Revenue Realization Rate (96.12%)
- Average Allocation Efficiency (84.04 / 100)

**Charts:**
- Clustered column: Budget Allocated vs. Utilized by Department
- Bar: Utilization Rate by Department (reference line at 100%)
- Donut: Budget Status distribution (Efficient / Moderate / Inefficient)
- Column: Revenue Forecast vs. Actual by Department

## Page 2 - Department Performance

- Table: Department x total allocated, total utilized, utilization
  rate, avg allocation efficiency, record count
- Bar: Avg Allocation Efficiency by Department (ranked)
- Stacked bar: Budget Status mix (%) by Department
- Matrix: Department x Expense_Category utilization rate heatmap

## Page 3 - Expense Category Analysis

- Bar: Total Budget Allocated by Expense_Category
- Bar: Utilization Rate by Expense_Category (ranked)
- Scatter: Avg Allocation Efficiency (x) vs. Utilization Rate (y) by
  Expense_Category, sized by total allocated - flags
  high-spend/low-efficiency categories
- Table: Top 10 Department x Expense_Category combinations by
  utilization rate (investigation candidates)

## Page 4 - Budget Status & Efficiency

- Histogram: Allocation Efficiency distribution
- Box/violin equivalent (or banded bar): Spending Volatility by
  Budget Status
- Table: % Inefficient records by Department
- Slicer: Fiscal_Quarter label (with a visible note that it carries
  no year - cross-sectional filter only)

## Page 5 - Forecast Accuracy & Data Notes

- Bar: Revenue Realization Rate by Department (ranked, reference line
  at 100%)
- Card: correlation disclosure - "No meaningful correlation (|r| <
  0.03) found between Inflation_Rate/Market_Index/Spending_Volatility
  and budget outcomes in this dataset"
- Text box: data-quality notes (no fiscal year; Budget_Variance and
  Revenue_Variance do not reconcile to their component columns; 258
  records show extreme utilization) - pulled from `docs/data_quality.md`

## Interactivity requirements
- Department and Expense_Category slicers on every page.
- Cross-filtering enabled between all visuals on a page.
- Page 1 KPI cards should NOT be affected by page-level slicers
  (use a separate, unfiltered measure or a "reset context" bookmark)
  so the headline numbers always show the full-portfolio total.
