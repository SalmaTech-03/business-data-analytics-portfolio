-- 02_core_kpis.sql
-- Core KPI calculations for Sales Performance & Profitability Analytics
-- Assumption: fact_sales contains the cleaned sales dataset.

-- 1. Revenue, Profit, Units and Profit Margin
SELECT
    SUM(sales) AS total_revenue,
    SUM(profit) AS total_profit,
    SUM(quantity) AS total_units,
    ROUND(
        (SUM(profit) / NULLIF(SUM(sales), 0))::numeric,
        4
    ) AS profit_margin
FROM fact_sales;

-- 2. Distinct Orders and Customers
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers
FROM fact_sales;

-- 3. Average Order Value
SELECT
    ROUND(
        (SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0))::numeric,
        2
    ) AS average_order_value
FROM fact_sales;

-- 4. Average Profit per Order
SELECT
    ROUND(
        (SUM(profit) / NULLIF(COUNT(DISTINCT order_id), 0))::numeric,
        2
    ) AS average_profit_per_order
FROM fact_sales;

-- 5. Repeat Customer Rate
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM fact_sales
    GROUP BY customer_id
)
SELECT
    ROUND(
        (
            COUNT(*) FILTER (WHERE order_count > 1)::numeric
            / NULLIF(COUNT(*), 0)
        ),
        4
    ) AS repeat_customer_rate
FROM customer_orders;
