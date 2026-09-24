# Page 4 - Financial

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

**Audience:** Finance Analyst

## Layout
| Visual | Fields / measures |
|---|---|
| Cards | [Revenue (USD)], [Opex (USD)], [Operating Margin (USD)], [Cost per bbl Oil Sold], [Cost per BOE Sold] |
| Line: cost per bbl and average realised price by month | month, [Cost per bbl Oil Sold], [Avg Realised Oil Price] |
| Stacked column: opex by category | month, fact_operating_cost[cost_category], [Opex (USD)] |
| Bar: margin by field | dim_field[field_name], [Operating Margin (USD)] |
| Card: [Estimated Lost Revenue (USD)] | with note: estimate using same-day realised price |

## Filters
Field, Cost category, Date

## Insight questions
1. Is unit cost improving? 2. Which cost category dominates? 3. What is the value of lost production?
