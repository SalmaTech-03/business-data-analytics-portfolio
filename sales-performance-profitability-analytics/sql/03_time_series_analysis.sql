-- =============================================================================
-- 03_time_series_analysis.sql
-- =============================================================================
-- Business purpose:
--   Answer "How is revenue changing over time?" at monthly, quarterly, and
--   yearly grain, and calculate year-over-year growth using a window function.
--
-- Caveat: the dataset's Order Date range is 2023-01-03 to 2026-12-30. Every
-- calendar year in that range (2023-2026) has a full 12 months of data, so
-- the year-over-year growth figures below compare complete years to complete
-- years -- they are not distorted by a partial final year.
--
-- Dialect: PostgreSQL
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Monthly Revenue, Profit, Orders
-- -----------------------------------------------------------------------------
SELECT
    TO_CHAR(order_date, 'YYYY-MM') AS year_month,
    SUM(sales)                     AS revenue,
    SUM(profit)                    AS profit,
    COUNT(DISTINCT order_id)       AS orders
FROM fact_sales
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY year_month;
-- Actual result on this dataset: 48 monthly rows (Jan 2023 - Dec 2026).
-- Full table saved to outputs/tables/revenue_by_month.csv


-- -----------------------------------------------------------------------------
-- Quarterly Revenue and Profit
-- -----------------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM order_date)    AS order_year,
    EXTRACT(QUARTER FROM order_date) AS order_quarter,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit
FROM fact_sales
GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(QUARTER FROM order_date)
ORDER BY order_year, order_quarter;
-- Actual result on this dataset (selected rows):
--   2023 Q1: revenue 75,971.86 / profit 4,095.15
--   2025 Q4: revenue 236,745.24 / profit 38,194.55  (highest-profit quarter)
--   2026 Q4: revenue 287,104.32 / profit 29,018.46  (highest-revenue quarter)


-- -----------------------------------------------------------------------------
-- Yearly Revenue, Profit, and Year-over-Year Growth (window function)
-- Formula: YoY growth = (current_year_revenue - prior_year_revenue) / prior_year_revenue
-- -----------------------------------------------------------------------------
WITH yearly AS (
    SELECT
        EXTRACT(YEAR FROM order_date) AS order_year,
        SUM(sales)  AS revenue,
        SUM(profit) AS profit
    FROM fact_sales
    GROUP BY EXTRACT(YEAR FROM order_date)
)
SELECT
    order_year,
    revenue,
    profit,
    ROUND(
        ((revenue - LAG(revenue) OVER (ORDER BY order_year))
         / NULLIF(LAG(revenue) OVER (ORDER BY order_year), 0))::numeric, 4
    ) AS revenue_yoy_growth,
    ROUND(
        ((profit - LAG(profit) OVER (ORDER BY order_year))
         / NULLIF(LAG(profit) OVER (ORDER BY order_year), 0))::numeric, 4
    ) AS profit_yoy_growth
FROM yearly
ORDER BY order_year;
-- Actual result on this dataset:
--   2023: revenue 494,040.21 / profit  51,684.30 / growth: n/a (first year)
--   2024: revenue 472,993.03 / profit  62,020.97 / revenue -4.26% / profit +20.00%
--   2025: revenue 613,933.58 / profit  82,665.20 / revenue +29.80% / profit +33.29%
--   2026: revenue 745,567.53 / profit  95,926.35 / revenue +21.44% / profit +16.04%
-- Reading: 2024 is the only year with a revenue decline despite a profit
-- increase -- worth a note in docs/findings.md, but this query only
-- describes the pattern; it does not explain the cause.
