# KPI Framework

Every KPI below has an implementation in `src/kpi_calculations.py`
(Python, unit-tested in `tests/test_kpi_calculations.py`), a matching SQL
query in `sql/02_core_kpis.sql`, and where relevant a DAX measure in
`dashboard/dax_measures.md`. The "Actual value" column is the real,
calculated result from this dataset (see `docs/data_quality.md` for the
underlying row counts).

| KPI | Formula | Business Meaning | Actual Value |
|---|---|---|---|
| Total Revenue | `SUM(sales)` | Total dollar value of goods sold. | $2,326,534.35 |
| Total Profit | `SUM(profit)` | Total dollar profit after cost, discount, etc. as recorded in the source data. | $292,296.81 |
| Total Orders | `COUNT(DISTINCT order_id)` | Number of distinct customer orders. | 5,111 |
| Total Units Sold | `SUM(quantity)` | Total units shipped across all orders. | 38,654 |
| Profit Margin | `Total Profit / Total Revenue` | Percentage of revenue retained as profit. **Revenue-based, not cost-based** (no cost data exists -- see `docs/assumptions_and_constraints.md`). | 12.56% |
| Average Order Value (AOV) | `Total Revenue / Total Orders` (order-grain) | Average dollar size of a single order. | $455.20 |
| Average Units per Order | `Total Units / Total Orders` | Average number of items per order. | 7.56 |
| Customer Count | `COUNT(DISTINCT customer_id)` | Total distinct customers in the dataset's history. | 804 |
| Revenue per Customer | `Total Revenue / Customer Count` | Average lifetime (within-dataset) revenue per customer. | $2,893.70 |
| Repeat Customer Rate | `(customers with >1 order) / (all customers)` | Share of customers who ordered more than once. Dataset-lifetime rate, not a rolling rate (see caveat in `assumptions_and_constraints.md`). | 98.51% |
| Revenue Growth Rate (YoY) | `(current_year_revenue - prior_year_revenue) / prior_year_revenue` | Year-over-year revenue growth. | 2024: -4.26% \| 2025: +29.80% \| 2026: +21.44% |
| Profit Growth Rate (YoY) | `(current_year_profit - prior_year_profit) / prior_year_profit` | Year-over-year profit growth. | 2024: +20.00% \| 2025: +33.29% \| 2026: +16.04% |
| Category Contribution % | Each category's `SUM(sales)` as a % of total revenue | Which categories drive overall revenue. | Technology 36.1% \| Furniture 32.4% \| Office Supplies 31.5% |
| Regional Contribution % | Each region's `SUM(sales)` as a % of total revenue | Which regions drive overall revenue. | West 31.8% \| East 29.7% \| Central 21.6% \| South 16.8% |
| Discount Rate (avg, by category) | `AVG(discount)` per category | How aggressively each category is discounted on average. | Furniture 17.3% \| Office Supplies 15.6% \| Technology 13.1% |

## KPIs deliberately NOT included, and why

- **Customer Lifetime Value (CLV):** would require assumptions (churn
  rate, discount rate, retention curve) not supported by real data in this
  dataset -- calculating it would mean fabricating an input.
- **Gross Margin / Markup %:** requires a unit-cost figure that does not
  exist in this dataset (see `docs/assumptions_and_constraints.md`).
- **Marketing ROI / CAC:** no marketing spend or acquisition-channel data
  exists in this dataset.
- **Inventory turnover / sell-through rate:** no inventory or stock-level
  data exists in this dataset.

## Power BI implementation

Every KPI in the table above has a corresponding DAX measure documented in
`dashboard/dax_measures.md`, using the same formula shown here -- the DAX
is not a reinterpretation, it is the same calculation expressed for the
Power BI data model.
