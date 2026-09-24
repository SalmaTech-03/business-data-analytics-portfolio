# Page 5 - Inventory & Suppliers

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

**Audience:** Supply Chain Analyst, Procurement Lead

## Layout
| Visual | Fields / measures |
|---|---|
| Cards | [Stockout Rate %], [Inventory Value (USD, latest)], [Inventory Turnover (annualised)], [Supplier On-Time %], [Open POs] |
| Bar: stockout rate by material category | dim_material[material_category], [Stockout Rate %] |
| Table: items at or below reorder | dim_material[material_name], dim_warehouse[warehouse_name], closing_stock, reorder_level (filter closing <= reorder, latest date) |
| Bar: supplier on-time % | dim_supplier[supplier_name], [Supplier On-Time %] |
| Clustered bar: quoted vs actual lead time | dim_supplier[supplier_name], [Avg Quoted Lead Time (d)], [Avg Actual Lead Time (d)] |
| Column: consumption value by category | [Consumption Value (USD)] |

## Filters
Warehouse, Material category, Supplier, Date

## Insight questions
1. Which categories stock out most? 2. Which suppliers are late? 3. Where is stock excessive?
