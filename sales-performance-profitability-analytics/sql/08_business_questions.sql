-- =============================================================================
-- 08_business_questions.sql
-- =============================================================================
-- Business purpose:
--   One clearly labeled query per major business question from
--   docs/business_questions.md, so a reviewer can map a question directly
--   to the query that answers it. Most of these reuse logic already
--   validated in files 02-07; this file exists for readability/navigation,
--   not to introduce new logic.
--
-- Dialect: PostgreSQL
-- =============================================================================

-- Q1: What is total revenue and total profit?
SELECT SUM(sales) AS total_revenue, SUM(profit) AS total_profit
FROM fact_sales;
-- Actual result: revenue 2,326,534.35 / profit 292,296.81


-- Q2: What is overall profit margin?
SELECT ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS profit_margin
FROM fact_sales;
-- Actual result: 0.1256 (12.56%)


-- Q3: Which category generates the most revenue? The most profit?
SELECT category, SUM(sales) AS revenue, SUM(profit) AS profit
FROM fact_sales
GROUP BY category
ORDER BY revenue DESC;
-- Actual result: Technology leads on BOTH revenue (839,893.28) and profit
-- (146,543.38); Furniture is 2nd on revenue but last on profit.


-- Q4: Which sub-categories perform poorly (negative margin)?
SELECT sub_category, SUM(sales) AS revenue, SUM(profit) AS profit,
       ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin
FROM fact_sales
GROUP BY sub_category
HAVING SUM(profit) < 0
ORDER BY margin ASC;
-- Actual result: 3 of 17 sub-categories are net loss-making, worst margin
-- first: Tables (-8.5% margin, -17,753.21 profit), Bookcases (-3.1% margin,
-- -3,632.07 profit), and Supplies (-2.5% margin, -1,171.39 profit).


-- Q5: Which products contribute the most revenue?
SELECT product_name, SUM(sales) AS revenue
FROM fact_sales
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 5;
-- Actual result: top product is "Canon imageCLASS 2200 Advanced Copier"
-- (61,599.82) -- see 04_product_analysis.sql for full ranked list.


-- Q6: Which products generate weak or negative profit?
SELECT product_name, SUM(sales) AS revenue, SUM(profit) AS profit
FROM fact_sales
GROUP BY product_name
ORDER BY profit ASC
LIMIT 5;
-- Actual result: worst product is "Cubify CubeX 3D Printer Double Head
-- Print" (profit -8,879.97 on revenue of only 11,099.96 -- an 80% loss rate).


-- Q7: Which region performs best?
SELECT region, SUM(sales) AS revenue, SUM(profit) AS profit,
       ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin
FROM fact_sales
GROUP BY region
ORDER BY revenue DESC;
-- Actual result: West leads on both revenue (739,813.61) and margin (14.98%).


-- Q8: Which customer segment generates the most revenue?
SELECT segment, SUM(sales) AS revenue
FROM fact_sales
GROUP BY segment
ORDER BY revenue DESC;
-- Actual result: Consumer (1,170,659.79) -- but see 05_customer_analysis.sql:
-- Consumer also has the lowest margin of the three segments.


-- Q9: What is the Average Order Value?
WITH order_totals AS (
    SELECT order_id, SUM(sales) AS order_sales FROM fact_sales GROUP BY order_id
)
SELECT ROUND(AVG(order_sales)::numeric, 2) AS average_order_value FROM order_totals;
-- Actual result: 455.20


-- Q10: What is the repeat customer rate?
WITH opc AS (SELECT customer_id, COUNT(DISTINCT order_id) AS oc FROM fact_sales GROUP BY customer_id)
SELECT ROUND((SUM(CASE WHEN oc > 1 THEN 1 ELSE 0 END)::numeric / COUNT(*)), 4) AS repeat_rate
FROM opc;
-- Actual result: 0.9851 (98.51%) -- interpret cautiously; see 02_core_kpis.sql caveat.


-- Q11: How does discount relate to profitability?
SELECT CORR(discount, profit / NULLIF(sales, 0)) AS discount_margin_correlation
FROM fact_sales;
-- Actual result: -0.865 (strong negative association; not a causal claim --
-- see 07_discount_profitability.sql).


-- Q12: Which products/categories have high sales but weak margins?
--      (revenue in the top quartile AND margin below the overall average)
WITH product_totals AS (
    SELECT product_id, product_name, SUM(sales) AS revenue,
           SUM(profit) / NULLIF(SUM(sales), 0) AS margin
    FROM fact_sales
    GROUP BY product_id, product_name
),
thresholds AS (
    SELECT
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) AS revenue_p75,
        (SELECT SUM(profit) / NULLIF(SUM(sales), 0) FROM fact_sales) AS overall_margin
    FROM product_totals
)
SELECT p.product_name, p.revenue, p.margin
FROM product_totals p, thresholds t
WHERE p.revenue >= t.revenue_p75 AND p.margin < t.overall_margin
ORDER BY p.revenue DESC
LIMIT 10;
-- Actual result: identifies high-revenue products whose margin trails the
-- 12.56% company-wide average -- e.g. the Cisco TelePresence System EX90
-- (revenue 22,638.48, margin -8.0%) qualifies on both conditions.
-- Full ranked table: outputs/tables/product_summary.csv (sort by
-- revenue_contribution_pct descending, then filter profit_margin < 0.1256).


-- Q13: Where should management investigate further?
--      (states that are simultaneously high-revenue AND net loss-making)
SELECT state_province, SUM(sales) AS revenue, SUM(profit) AS profit
FROM fact_sales
GROUP BY state_province
HAVING SUM(profit) < 0
ORDER BY revenue DESC
LIMIT 5;
-- Actual result: Texas (revenue 170,188.05, profit -25,729.36) is the
-- clearest investigation priority -- it is simultaneously a top-3 state by
-- revenue and the single largest loss-maker in the dataset.
