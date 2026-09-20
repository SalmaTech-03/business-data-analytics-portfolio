-- ============================================================
-- 03_time_series_analysis.sql
-- Business purpose: Compare Q1-Q4 activity.
-- IMPORTANT: The source data has NO fiscal year column - only a
-- Q1/Q2/Q3/Q4 label. These queries therefore report a CROSS-
-- SECTIONAL comparison of quarter labels pooled across the whole
-- dataset, NOT a chronological trend. True month-over-month or
-- year-over-year growth cannot be computed from this file.
-- (See docs/assumptions_and_constraints.md.)
-- ============================================================

-- Budget allocated/utilized/utilization rate by fiscal quarter label
SELECT
    fiscal_quarter,
    SUM(budget_allocated) AS total_allocated,
    SUM(budget_utilized)  AS total_utilized,
    ROUND(SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0), 4) AS utilization_rate,
    COUNT(*) AS record_count
FROM budget_records
GROUP BY fiscal_quarter
ORDER BY fiscal_quarter;

-- Revenue forecast vs actual by fiscal quarter label
SELECT
    fiscal_quarter,
    SUM(revenue_forecast) AS total_forecast,
    SUM(actual_revenue)   AS total_actual,
    ROUND(SUM(actual_revenue) / NULLIF(SUM(revenue_forecast), 0), 4) AS realization_rate
FROM budget_records
GROUP BY fiscal_quarter
ORDER BY fiscal_quarter;

-- Average allocation efficiency by quarter label
SELECT
    fiscal_quarter,
    ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency,
    ROUND(AVG(spending_volatility), 3)   AS avg_spending_volatility
FROM budget_records
GROUP BY fiscal_quarter
ORDER BY fiscal_quarter;
