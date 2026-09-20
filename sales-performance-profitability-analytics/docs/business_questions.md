# Business Questions

Every question below is answered somewhere in this project with an actual
calculated result -- not a hypothesis. Each row links to where the answer
lives.

| # | Question | Answered in |
|---|---|---|
| 1 | What is total revenue and total profit? | `sql/02_core_kpis.sql`, `notebooks/02_sales_exploration.ipynb` |
| 2 | What is overall profit margin? | `sql/02_core_kpis.sql` |
| 3 | How are revenue and profit changing over time? | `sql/03_time_series_analysis.sql`, `notebooks/02_sales_exploration.ipynb` |
| 4 | Which categories generate the most revenue? | `sql/04_product_analysis.sql` |
| 5 | Which categories generate the most profit? | `sql/04_product_analysis.sql` |
| 6 | Which sub-categories perform poorly? | `sql/04_product_analysis.sql`, `notebooks/04_product_profitability.ipynb` |
| 7 | Which products contribute the most revenue? | `sql/04_product_analysis.sql` |
| 8 | Which products generate weak or negative profit? | `sql/04_product_analysis.sql`, `notebooks/04_product_profitability.ipynb` |
| 9 | Which regions perform best? | `sql/06_regional_analysis.sql` |
| 10 | Which customer segments generate the most revenue? | `sql/05_customer_analysis.sql` |
| 11 | What is the Average Order Value? | `sql/02_core_kpis.sql` |
| 12 | What is the repeat customer rate? | `sql/02_core_kpis.sql`, `sql/05_customer_analysis.sql` |
| 13 | How does discount relate to profitability? | `sql/07_discount_profitability.sql`, `notebooks/02_sales_exploration.ipynb` |
| 14 | Which products/categories have high sales but weak margins? | `notebooks/04_product_profitability.ipynb`, `sql/08_business_questions.sql` (Q12) |
| 15 | Which products/categories have lower sales but stronger margins? | `notebooks/04_product_profitability.ipynb` |
| 16 | Where should management investigate further? | `docs/findings.md`, `docs/recommendations.md` |
| 17 | What KPIs should management monitor? | `docs/kpi_framework.md` |
| 18 | Who are the highest-value customers? | `sql/05_customer_analysis.sql` (by `customer_id` only -- no names) |

## Scope note

These are the questions this project answers with the data available. It
does **not** answer questions that would require data not present in the
Sample Superstore export -- for example, unit cost, marketing spend,
customer acquisition channel, or inventory levels. See
`docs/assumptions_and_constraints.md` for the full list of what's out of
scope and why.
