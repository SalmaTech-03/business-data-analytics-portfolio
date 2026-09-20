# Data Dictionary

Source: **Sample Superstore** dataset (public sample dataset commonly used
for BI/analytics learning; not real transactional data from any real
company). Distributed as `sample_-_superstore.xls`, a legacy Excel 97-2003
workbook with 3 sheets: `Orders`, `People`, `Returns`.

## Orders sheet (fact table source)

10,194 rows x 21 columns. This is the primary analytical table; every
notebook and SQL script joins off of it.

| Source Column     | Standardized Name (`snake_case`) | Type            | Description |
|--------------------|-----------------------------------|-----------------|-------------|
| Row ID             | `row_id`                          | integer         | Line-item primary key, unique per row. |
| Order ID           | `order_id`                        | string          | Groups line items into a single customer order. Not unique per row (one order can have multiple line items). |
| Order Date         | `order_date`                      | date            | Date the order was placed. Range: 2023-01-03 to 2026-12-30. |
| Ship Date          | `ship_date`                       | date            | Date the order shipped. Always >= Order Date in this dataset. |
| Ship Mode          | `ship_mode`                       | string (4 vals) | Standard Class, Second Class, First Class, Same Day. |
| Customer ID        | `customer_id`                     | string          | Customer identifier. **Safe for public output** (no name attached). |
| Customer Name      | `customer_name`                   | string          | **PII -- excluded from every public output** (see `data/README.md`). |
| Segment            | `segment`                         | string (3 vals) | Consumer, Corporate, Home Office. |
| Country/Region     | `country_region`                  | string (2 vals) | United States, Canada. |
| City               | `city`                            | string          | **PII -- excluded from every public output.** |
| State/Province     | `state_province`                  | string          | **PII -- excluded from every public output** (identifies a customer's location in combination with other fields). |
| Postal Code        | `postal_code`                     | string          | **PII -- excluded.** Kept as text (Canadian postal codes are alphanumeric). |
| Region             | `region`                          | string (4 vals) | Central, East, South, West. Safe -- coarser than state. |
| Product ID         | `product_id`                      | string          | Product identifier. 1,862 distinct values. |
| Category           | `category`                        | string (3 vals) | Furniture, Office Supplies, Technology. |
| Sub-Category       | `sub_category`                    | string (17 vals)| e.g. Chairs, Phones, Binders, Tables. |
| Product Name       | `product_name`                    | string          | Free-text product description. 1,849 distinct values (fewer than Product ID due to 32 product IDs having more than one recorded name -- a known source quirk, see `data_quality.md`). |
| Sales              | `sales`                           | float           | Line-item revenue in USD. **This is revenue, not unit price** -- it already reflects quantity and discount. |
| Quantity           | `quantity`                        | integer         | Units sold in this line item. |
| Discount           | `discount`                        | float [0, 1]    | Discount rate applied to this line item. |
| Profit             | `profit`                          | float           | Line-item profit in USD. Can be negative. |

**No unit-cost or unit-price column exists.** `sales` is total line-item
revenue; there is no way to back out a per-unit list price or a
cost-of-goods figure from this dataset. This is why every "margin" in this
project is defined as `profit / sales` (a revenue-based margin) and never
as a cost-based margin.

## People sheet (lookup table)

4 rows x 2 columns: `Regional Manager`, `Region`. Maps each of the 4
regions to a named manager. **`Regional Manager` is treated as PII-adjacent
and excluded from public outputs**, though it's a much smaller privacy
concern than customer PII since it identifies an employee, not a customer.

## Returns sheet (bridge table)

296 rows x 2 columns: `Order ID`, `Returned` (always `"Yes"` in this
dataset -- it is a list of returned orders, not a Yes/No flag on every
order). Every `Order ID` in this sheet was confirmed to exist in `Orders`
(0 orphaned rows). Return rate: 296 distinct returned orders out of 5,111
total orders (5.8% of orders had at least one return).

## Derived columns (created in `src/feature_engineering.py`)

| Column                  | Formula / Definition |
|--------------------------|----------------------|
| `order_year`             | `YEAR(order_date)` |
| `order_quarter`          | `QUARTER(order_date)` (1-4) |
| `order_month`            | `MONTH(order_date)` (1-12) |
| `order_month_name`       | Full month name |
| `order_year_month`       | `"YYYY-MM"` string, for monthly time series |
| `order_year_quarter`     | `"YYYY-QN"` string |
| `profit_margin`          | `profit / sales` (line-item level; revenue-based margin) |
| `is_loss_making`         | `profit < 0` |
| `order_total_sales`      | Sum of `sales` across all line items sharing an `order_id` |
| `order_profit_margin`    | `order_total_profit / order_total_sales` |
| `total_orders` (customer)| `COUNT(DISTINCT order_id)` per `customer_id` |
| `repeat_customer`        | `total_orders > 1` |
| `avg_order_value` (cust.)| `total_sales / total_orders` per customer |
| `revenue_contribution_pct` | Each entity's share of total revenue, as a percentage (sums to ~100% within a table) |
| `profit_contribution_pct`  | Each entity's share of total profit, as a percentage |

## PII classification summary

| Field | Classification | Included in public outputs? |
|---|---|---|
| `customer_id` | Safe identifier | Yes |
| `customer_name` | PII | **No** |
| `city`, `state_province`, `postal_code` | PII (location) | **No** |
| `region`, `country_region` | Coarse geography, safe | Yes |
| `Regional Manager` (People sheet) | Employee-identifying | No (excluded from public outputs; low sensitivity) |
| Everything else | Non-identifying transactional data | Yes |
