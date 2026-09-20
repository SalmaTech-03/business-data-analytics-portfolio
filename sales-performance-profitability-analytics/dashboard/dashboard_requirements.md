# Power BI Dashboard Requirements

**Status: specification only.** No `.pbix` file has been created as part
of this project -- this document (plus `dashboard_data_dictionary.md` and
`dax_measures.md`) contains everything needed to build one in Power BI
Desktop. See `power_bi_build_guide.md` for step-by-step build instructions.

## Data source

`data/processed/orders_clean.csv` (the de-identified output of
`run_analysis.py`) -- 10,194 rows, no `customer_name`/`city`/
`state_province`/`postal_code` columns. Import this file, not the raw
Excel workbook, into Power BI.

## Page 1 -- Executive Overview

**Audience:** Leadership; a 5-second health check.

KPI cards (top row):
- Total Revenue -- `[Total Revenue]`
- Total Profit -- `[Total Profit]`
- Profit Margin -- `[Profit Margin]`
- Total Orders -- `[Total Orders]`
- Total Units Sold -- `[Total Units]`
- Average Order Value -- `[Average Order Value]`

Charts:
- Revenue trend (line chart, monthly, `DimDate[YearMonth]` on axis)
- Profit trend (line chart, monthly)
- Revenue by Category (bar chart)
- Revenue by Region (bar chart or map)
- Profit by Category (bar chart)

Filters/slicers: Year, Region, Category (all pages should share these via
"Sync Slicers" for a consistent filter experience).

## Page 2 -- Product Performance

**Audience:** Category/product managers.

- Top 10 products by revenue (bar chart, horizontal)
- Bottom 10 products by profit (bar chart, horizontal, highlight negative)
- Category performance (revenue, profit, margin -- table or matrix)
- Sub-category performance (matrix with conditional formatting on margin)
- Revenue vs. Profit scatter plot (one point per product, to visually spot
  high-revenue/low-margin outliers -- this directly visualizes Finding 4
  in `docs/findings.md`)
- Margin distribution (histogram or box plot by category)

Tooltip page (optional): hovering a product shows its full name, category,
sub-category, revenue, profit, and margin without needing to click through.

## Page 3 -- Customer Analytics

**Audience:** Account/segment managers.

**Privacy constraint: use `customer_id` only. Never add `customer_name` to
this dashboard if it's rebuilt from a source file that still contains it.**

- Customer Count (KPI card)
- Repeat Customer Rate (KPI card, with a tooltip/note reminding viewers
  this is a dataset-lifetime rate, not a rolling rate -- see
  `docs/assumptions_and_constraints.md`)
- Revenue per Customer (KPI card)
- Top 10 customers by revenue (table, by `customer_id`, include Profit
  column alongside Revenue -- so the divergence in Finding 4 is visible,
  not hidden)
- Segment performance (Consumer / Corporate / Home Office -- revenue,
  profit, margin)
- Customer revenue distribution (Pareto-style chart: bar for individual
  customer revenue + line for cumulative %, ranked by revenue with no
  names shown)

## Page 4 -- Regional Analysis

**Audience:** Territory/regional managers.

- Revenue by Region (bar chart)
- Profit by Region (bar chart)
- Margin by Region (bar chart or KPI matrix)
- Orders by Region (bar chart)
- State-level performance (filled map or table, colored by profit --
  Texas, Ohio, Pennsylvania, Illinois should visually stand out as
  loss-making despite high revenue)
- Regional revenue trend (line chart, one line per region, over time)

## Page 5 -- Profitability & Discount Analysis

**Audience:** Pricing/discount policy owners.

- Discount vs. Margin (bar chart, one bar per discount bucket: 0%, 0-10%,
  10-20%, 20-30%, 30-40%, 40-50%, 50%+ -- color negative bars red)
- Revenue vs. Profit by Category (grouped bar, repeated from Page 1 for
  context)
- High-sales/low-margin product table (products in the top revenue
  quartile with below-average margin -- see notebook 04's definition)
- Sub-category profitability ranking (table, sorted by margin ascending,
  so Tables/Bookcases/Supplies appear at the top)
- Key findings & recommendations (text box, summarizing
  `docs/findings.md`/`docs/recommendations.md` -- this is the one page
  where static text belongs alongside visuals)

## Interactivity requirements (all pages)

- Drill-down: Category -> Sub-Category -> Product on any product-related
  visual.
- Cross-filtering: clicking a bar/segment on any chart should filter the
  other visuals on the same page.
- Tooltips: every chart should show exact values (not just visual
  position) on hover.
- Slicers: Year, Region, Category, Segment -- synced across pages where it
  makes sense (e.g. Year and Region make sense on every page; Segment
  mainly matters on Pages 1 and 3).
