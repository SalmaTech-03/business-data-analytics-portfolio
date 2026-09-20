-- =============================================================================
-- 05_customer_analysis.sql
-- =============================================================================
-- Business purpose:
--   Identify top-value customers (by customer_id only -- no names, to keep
--   this file and its output PII-safe for a public repo), order frequency,
--   segment performance, and revenue concentration.
--
-- Dialect: PostgreSQL
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Top customers by revenue (customer_id only -- see data/README.md for why
-- customer_name is excluded from every public query/output in this project)
-- -----------------------------------------------------------------------------
SELECT
    customer_id,
    SUM(sales)                AS revenue,
    SUM(profit)                AS profit,
    COUNT(DISTINCT order_id)   AS orders
FROM fact_sales
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 10;
-- Actual result on this dataset (top 3 of 10 returned):
--   1. SM-20320: revenue 25,043.05 / profit -1,980.74 (loss-making top customer)
--   2. TC-20980: revenue 19,052.22 / profit  8,981.32
--   3. RB-19360: revenue 15,117.34 / profit  6,976.10
-- Reading: the single highest-revenue customer is UNPROFITABLE -- revenue
-- rank and profit rank are not the same thing here.


-- -----------------------------------------------------------------------------
-- Order frequency distribution: how many customers placed N distinct orders
-- -----------------------------------------------------------------------------
WITH orders_per_customer AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM fact_sales
    GROUP BY customer_id
)
SELECT order_count, COUNT(*) AS num_customers
FROM orders_per_customer
GROUP BY order_count
ORDER BY order_count;
-- Actual result on this dataset: distribution ranges from 12 customers with
-- exactly 1 order up to 1 customer with 17 orders; the mode is 5 orders
-- (135 customers). Only 12 of 804 customers (1.5%) are single-order
-- customers, consistent with the 98.51% repeat-customer rate in
-- 02_core_kpis.sql.


-- -----------------------------------------------------------------------------
-- Customer Segment performance
-- -----------------------------------------------------------------------------
SELECT
    segment,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin,
    COUNT(DISTINCT order_id) AS orders
FROM fact_sales
GROUP BY segment
ORDER BY revenue DESC;
-- Actual result on this dataset:
--   Consumer:    revenue 1,170,659.79 / profit 136,371.45 / margin 11.65%
--   Corporate:   revenue   715,806.13 / profit  94,249.64 / margin 13.17%
--   Home Office: revenue   440,068.43 / profit  61,675.73 / margin 14.02%
-- Reading: Consumer drives the most revenue but has the LOWEST margin of
-- the three segments; Home Office is the smallest segment but the most
-- profitable per dollar of revenue.


-- -----------------------------------------------------------------------------
-- Revenue concentration: share of total revenue from the top decile of
-- customers by revenue (NTILE window function)
-- -----------------------------------------------------------------------------
WITH customer_revenue AS (
    SELECT customer_id, SUM(sales) AS revenue
    FROM fact_sales
    GROUP BY customer_id
),
deciled AS (
    SELECT
        customer_id,
        revenue,
        NTILE(10) OVER (ORDER BY revenue DESC) AS revenue_decile
    FROM customer_revenue
)
SELECT
    ROUND(
        (SUM(CASE WHEN revenue_decile = 1 THEN revenue ELSE 0 END)
         / SUM(revenue))::numeric, 4
    ) AS top_decile_revenue_share
FROM deciled;
-- Actual result on this dataset: top_decile_revenue_share = 0.3113 (31.1%)
-- Reading: revenue is only moderately concentrated -- the top 10% of
-- customers (~80 of 804) generate about a third of total revenue, not the
-- 80/20-style concentration sometimes assumed by default.
