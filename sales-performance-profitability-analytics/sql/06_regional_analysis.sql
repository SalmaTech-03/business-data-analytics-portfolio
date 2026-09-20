-- =============================================================================
-- 06_regional_analysis.sql
-- =============================================================================
-- Business purpose:
--   Answer "Which regions/states perform best?" and surface any region or
--   state that is high-revenue but low- or negative-profit.
--
-- Dialect: PostgreSQL
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Revenue, Profit, and Margin by Region
-- -----------------------------------------------------------------------------
SELECT
    region,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin,
    COUNT(DISTINCT order_id) AS orders
FROM fact_sales
GROUP BY region
ORDER BY revenue DESC;
-- Actual result on this dataset:
--   West:    revenue 739,813.61 / profit 110,798.82 / margin 14.98%
--   East:    revenue 691,828.17 / profit  94,883.26 / margin 13.71%
--   Central: revenue 503,170.67 / profit  39,865.31 / margin  7.92%  <- lowest margin
--   South:   revenue 391,721.91 / profit  46,749.43 / margin 11.93%


-- -----------------------------------------------------------------------------
-- State-level performance, ranked by revenue
-- -----------------------------------------------------------------------------
SELECT
    state_province,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin
FROM fact_sales
GROUP BY state_province
ORDER BY revenue DESC
LIMIT 10;
-- Actual result on this dataset (top 3 of 10 returned):
--   California: revenue 457,687.63 / profit 76,381.39 (best combination of scale and profit)
--   New York:   revenue 310,876.27 / profit 74,038.55
--   Texas:      revenue 170,188.05 / profit -25,729.36  <- 3rd-highest revenue, but the SINGLE
--               biggest loss-making state in the entire dataset


-- -----------------------------------------------------------------------------
-- States with negative total profit (loss-making states)
-- -----------------------------------------------------------------------------
SELECT
    state_province,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit
FROM fact_sales
GROUP BY state_province
HAVING SUM(profit) < 0
ORDER BY profit ASC;
-- Actual result on this dataset: 12 of 59 states/provinces are net
-- loss-making. The four worst are Texas (-25,729.36), Ohio (-16,971.38),
-- Pennsylvania (-15,559.96), and Illinois (-12,607.89) -- all large,
-- high-revenue states, which is why this matters more than a small state
-- with a small loss would.


-- -----------------------------------------------------------------------------
-- Regional revenue rank by year (window function) -- has the #1 region changed?
-- -----------------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM order_date) AS order_year,
    region,
    SUM(sales) AS revenue,
    RANK() OVER (
        PARTITION BY EXTRACT(YEAR FROM order_date)
        ORDER BY SUM(sales) DESC
    ) AS revenue_rank_in_year
FROM fact_sales
GROUP BY EXTRACT(YEAR FROM order_date), region
ORDER BY order_year, revenue_rank_in_year;
-- Actual result on this dataset: East led in revenue in 2024 only; West was
-- #1 in 2023, 2025, and 2026. South has ranked #4 (last) in every single
-- year of the dataset.
