-- =============================================================================
-- 04_product_analysis.sql
-- =============================================================================
-- Business purpose:
--   Answer "Which categories/sub-categories/products generate the most
--   revenue and profit?" and "Which have weak or negative margin?"
--
-- Dialect: PostgreSQL
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Category performance
-- -----------------------------------------------------------------------------
SELECT
    category,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin
FROM fact_sales
GROUP BY category
ORDER BY revenue DESC;
-- Actual result on this dataset:
--   Technology:      revenue 839,893.28 / profit 146,543.38 / margin 17.4%
--   Furniture:       revenue 754,747.76 / profit  19,729.996 / margin  2.6%
--   Office Supplies: revenue 731,893.31 / profit 126,023.44 / margin 17.2%
-- Reading: Furniture has almost as much revenue as the other two categories
-- but a fraction of the profit -- a margin problem, not a volume problem.


-- -----------------------------------------------------------------------------
-- Sub-category performance, ranked by revenue (window function)
-- -----------------------------------------------------------------------------
SELECT
    sub_category,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin,
    RANK() OVER (ORDER BY SUM(sales) DESC) AS revenue_rank
FROM fact_sales
GROUP BY sub_category
ORDER BY revenue DESC;
-- Actual result on this dataset (17 sub-categories) -- top and bottom by margin:
--   Highest margin:  Labels (43.9%), Paper (43.4%), Envelopes (42.3%), Copiers (37.2%)
--   Negative margin: Tables (-8.5%), Supplies (-2.5%), Bookcases (-3.1%)
-- Full table saved to outputs/tables/subcategory_summary.csv


-- -----------------------------------------------------------------------------
-- Product-level revenue and profit contribution with cumulative share
-- (Pareto-style view -- identifies the small set of products driving revenue)
-- -----------------------------------------------------------------------------
WITH product_totals AS (
    SELECT
        product_id,
        product_name,
        category,
        sub_category,
        SUM(sales)    AS revenue,
        SUM(profit)   AS profit,
        SUM(quantity) AS units
    FROM fact_sales
    GROUP BY product_id, product_name, category, sub_category
)
SELECT
    product_name,
    category,
    sub_category,
    revenue,
    profit,
    ROUND((profit / NULLIF(revenue, 0))::numeric, 4) AS margin,
    ROUND(
        (SUM(revenue) OVER (ORDER BY revenue DESC)
         / SUM(revenue) OVER ())::numeric, 4
    ) AS cumulative_revenue_share
FROM product_totals
ORDER BY revenue DESC
LIMIT 20;
-- Actual result on this dataset (top 3 of 20 returned):
--   1. Canon imageCLASS 2200 Advanced Copier - revenue 61,599.82, margin 40.9%, cum. share 2.6%
--   2. Fellowes PB500 Electric Punch Plastic Comb Binding Machine - revenue 27,453.38, margin 28.2%, cum. share 3.8%
--   3. Cisco TelePresence System EX90 Videoconferencing Unit - revenue 22,638.48, margin -8.0% (loss-making despite being a top-3 revenue product)
-- Full table saved to outputs/tables/product_summary.csv


-- -----------------------------------------------------------------------------
-- Products with the worst total profit (weak/negative-profit products)
-- -----------------------------------------------------------------------------
SELECT
    product_name,
    category,
    sub_category,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin
FROM fact_sales
GROUP BY product_name, category, sub_category
ORDER BY profit ASC
LIMIT 10;
-- Actual result on this dataset: the worst product by total profit is
-- "Cubify CubeX 3D Printer Double Head Print" (revenue 11,099.96, profit
-- -8,879.97, margin -80%). 6 of the bottom 10 products are in the Technology
-- "Machines" sub-category or Furniture "Tables" sub-category.
-- Full table saved to outputs/tables/product_summary.csv
