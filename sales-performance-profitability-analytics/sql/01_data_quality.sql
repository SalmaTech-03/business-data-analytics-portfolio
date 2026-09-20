-- =============================================================================
-- 01_data_quality.sql
-- =============================================================================
-- Business purpose:
--   Profile the fact_sales table before any downstream analysis is trusted.
--   These queries were run against the actual cleaned dataset during
--   development (10,194 rows) -- see docs/data_quality.md for the results.
--
-- Assumed table (see docs/data_dictionary.md for full column list):
--   fact_sales(row_id, order_id, order_date, ship_date, customer_id,
--              segment, region, category, sub_category, product_id,
--              product_name, sales, quantity, discount, profit, ...)
--
-- Dialect: PostgreSQL
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1. Row count
-- Output: single row, total_rows
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS total_rows
FROM fact_sales;
-- Actual result on this dataset: 10,194


-- -----------------------------------------------------------------------------
-- Q2. Null counts per required column
-- Output: one row per column with its null count. All zero on this dataset.
-- -----------------------------------------------------------------------------
SELECT
    SUM(CASE WHEN order_id     IS NULL THEN 1 ELSE 0 END) AS null_order_id,
    SUM(CASE WHEN order_date   IS NULL THEN 1 ELSE 0 END) AS null_order_date,
    SUM(CASE WHEN customer_id  IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN product_id   IS NULL THEN 1 ELSE 0 END) AS null_product_id,
    SUM(CASE WHEN sales        IS NULL THEN 1 ELSE 0 END) AS null_sales,
    SUM(CASE WHEN quantity     IS NULL THEN 1 ELSE 0 END) AS null_quantity,
    SUM(CASE WHEN discount     IS NULL THEN 1 ELSE 0 END) AS null_discount,
    SUM(CASE WHEN profit       IS NULL THEN 1 ELSE 0 END) AS null_profit
FROM fact_sales;
-- Actual result on this dataset: all columns = 0


-- -----------------------------------------------------------------------------
-- Q3. Duplicate Order IDs at the ROW level (full-row duplicates)
-- Output: rows that appear more than once identically. Expected: 0 rows returned.
-- -----------------------------------------------------------------------------
SELECT row_id, order_id, product_id, COUNT(*) AS occurrences
FROM fact_sales
GROUP BY row_id, order_id, product_id
HAVING COUNT(*) > 1;
-- Actual result on this dataset: 0 rows returned


-- -----------------------------------------------------------------------------
-- Q4. Order IDs that map to more than one Customer ID (known data quirk)
-- Output: order_id, count of distinct customer_id
-- -----------------------------------------------------------------------------
SELECT order_id, COUNT(DISTINCT customer_id) AS distinct_customers
FROM fact_sales
GROUP BY order_id
HAVING COUNT(DISTINCT customer_id) > 1;
-- Actual result on this dataset: 2 order_ids returned (CA-2025-121465, CA-2026-130494)
-- Documented in docs/data_quality.md as a known source-system quirk (customer
-- "Harry Olson" has 4 distinct Customer IDs); not corrected, since we do not
-- know which ID is "correct".


-- -----------------------------------------------------------------------------
-- Q5. Invalid numeric values: non-positive sales/quantity, out-of-range discount
-- Output: counts of rows violating each business rule
-- -----------------------------------------------------------------------------
SELECT
    SUM(CASE WHEN sales    <= 0          THEN 1 ELSE 0 END) AS non_positive_sales,
    SUM(CASE WHEN quantity <= 0          THEN 1 ELSE 0 END) AS non_positive_quantity,
    SUM(CASE WHEN discount < 0 OR discount > 1 THEN 1 ELSE 0 END) AS discount_out_of_range
FROM fact_sales;
-- Actual result on this dataset: 0, 0, 0


-- -----------------------------------------------------------------------------
-- Q6. Date range and shipping-date sanity check
-- Output: min/max order date, min/max ship date, count of ship_date < order_date
-- -----------------------------------------------------------------------------
SELECT
    MIN(order_date) AS earliest_order_date,
    MAX(order_date) AS latest_order_date,
    MIN(ship_date)  AS earliest_ship_date,
    MAX(ship_date)  AS latest_ship_date,
    SUM(CASE WHEN ship_date < order_date THEN 1 ELSE 0 END) AS ship_before_order_count
FROM fact_sales;
-- Actual result on this dataset: 2023-01-03 -> 2026-12-30 (orders),
-- 2023-01-07 -> 2027-01-05 (ship), ship_before_order_count = 0


-- -----------------------------------------------------------------------------
-- Q7. Distinct customers, products, orders, categories, sub-categories, regions
-- Output: single-row cardinality summary
-- -----------------------------------------------------------------------------
SELECT
    COUNT(DISTINCT order_id)     AS distinct_orders,
    COUNT(DISTINCT customer_id)  AS distinct_customers,
    COUNT(DISTINCT product_id)   AS distinct_products,
    COUNT(DISTINCT category)     AS distinct_categories,
    COUNT(DISTINCT sub_category) AS distinct_subcategories,
    COUNT(DISTINCT region)       AS distinct_regions
FROM fact_sales;
-- Actual result on this dataset: 5,111 orders / 804 customers / 1,862 products
-- / 3 categories / 17 sub-categories / 4 regions


-- -----------------------------------------------------------------------------
-- Q8. Referential integrity: Returns table Order IDs that don't exist in fact_sales
-- Output: orphaned Order IDs in Returns (expected: 0 rows)
-- -----------------------------------------------------------------------------
SELECT r.order_id
FROM returns r
LEFT JOIN fact_sales f ON f.order_id = r.order_id
WHERE f.order_id IS NULL;
-- Actual result on this dataset: 0 rows returned (all 296 Returns rows
-- reference a real order)
