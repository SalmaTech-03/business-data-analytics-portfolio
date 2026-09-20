-- ============================================================
-- 02_core_kpis.sql
-- Business purpose: Headline KPIs management checks first -
-- total budget position and overall revenue forecast accuracy.
-- ============================================================

-- Total Budget Allocated, Utilized, and overall Utilization Rate
SELECT
    SUM(budget_allocated) AS total_budget_allocated,
    SUM(budget_utilized)  AS total_budget_utilized,
    ROUND(SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0), 4) AS overall_utilization_rate,
    SUM(budget_variance)  AS total_budget_variance
FROM budget_records;

-- Total Revenue Forecast vs Actual Revenue, and realization rate
SELECT
    SUM(revenue_forecast) AS total_revenue_forecast,
    SUM(actual_revenue)   AS total_actual_revenue,
    ROUND(SUM(actual_revenue) / NULLIF(SUM(revenue_forecast), 0), 4) AS revenue_realization_rate
FROM budget_records;

-- Average Allocation Efficiency and record/department counts
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT department) AS department_count,
    ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency
FROM budget_records;

-- Budget Status distribution (share of records)
SELECT
    budget_status,
    COUNT(*) AS record_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_records
FROM budget_records
GROUP BY budget_status
ORDER BY record_count DESC;
