-- =============================================================================
-- 07_discount_profitability.sql
-- =============================================================================
-- Business purpose:
--   Examine how discount level relates to revenue and profitability.
--
-- IMPORTANT: these queries show an ASSOCIATION between discount level and
-- margin. They do NOT establish that discounting CAUSES margin to fall --
-- discounts may be applied selectively to already-low-margin or slow-moving
-- products, which would produce the same pattern without discounting being
-- the cause. See docs/findings.md and docs/recommendations.md, where this
-- caveat is repeated explicitly.
--
-- Dialect: PostgreSQL
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Revenue, Profit, and Margin by Discount Bucket
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN discount = 0     THEN '0%'
        WHEN discount <= 0.1  THEN '0-10%'
        WHEN discount <= 0.2  THEN '10-20%'
        WHEN discount <= 0.3  THEN '20-30%'
        WHEN discount <= 0.4  THEN '30-40%'
        WHEN discount <= 0.5  THEN '40-50%'
        ELSE '50%+'
    END AS discount_bucket,
    SUM(sales)  AS revenue,
    SUM(profit) AS profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0))::numeric, 4) AS margin,
    COUNT(DISTINCT order_id) AS orders
FROM fact_sales
GROUP BY discount_bucket
ORDER BY MIN(discount);
-- Actual result on this dataset:
--   0%:     revenue 1,105,323.79 / profit 326,718.59 / margin 29.6%
--   0-10%:  revenue    54,952.50 / profit   9,099.97 / margin 16.6%
--   10-20%: revenue   801,497.92 / profit  92,498.94 / margin 11.5%
--   20-30%: revenue   104,474.07 / profit -10,513.45 / margin -10.1%  <- turns negative here
--   30-40%: revenue   130,991.22 / profit -25,477.51 / margin -19.4%
--   40-50%: revenue    64,403.51 / profit -22,999.54 / margin -35.7%
--   50%+:   revenue    64,891.35 / profit -77,030.19 / margin -118.7%
-- Reading: margin is positive at every discount level up to 20%, and
-- negative at every level from 20% upward -- a clear threshold pattern,
-- not a gradual decline.


-- -----------------------------------------------------------------------------
-- Correlation check: line-item discount vs line-item profit margin
-- (Pearson correlation coefficient)
-- -----------------------------------------------------------------------------
SELECT
    CORR(discount, profit / NULLIF(sales, 0)) AS discount_margin_correlation
FROM fact_sales;
-- Actual result on this dataset: -0.865 (strong negative linear association).
-- Again: this is a correlation, not evidence of causation.


-- -----------------------------------------------------------------------------
-- Average discount rate and margin split (0% vs >30%) by category
-- -----------------------------------------------------------------------------
SELECT
    category,
    ROUND(AVG(discount)::numeric, 4) AS avg_discount_rate,
    ROUND(AVG(CASE WHEN discount = 0 THEN profit / NULLIF(sales, 0) END)::numeric, 4) AS avg_margin_no_discount,
    ROUND(AVG(CASE WHEN discount > 0.3 THEN profit / NULLIF(sales, 0) END)::numeric, 4) AS avg_margin_deep_discount
FROM fact_sales
GROUP BY category;
-- Actual result on this dataset:
--   Furniture:       avg discount 17.3% | margin@0%: 29.5% | margin@>30%: -59.3%
--   Office Supplies: avg discount 15.6% | margin@0%: 36.8% | margin@>30%: -121.6%  <- most extreme swing
--   Technology:      avg discount 13.1% | margin@0%: 29.0% | margin@>30%: -28.2%
-- Reading: Office Supplies shows the widest gap between full-price and
-- deep-discount margin, making it the category most worth reviewing for
-- discount policy first.
