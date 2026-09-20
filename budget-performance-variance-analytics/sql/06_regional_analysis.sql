-- ============================================================
-- 06_regional_analysis.sql
-- (This dataset has no geographic/region dimension. As a
-- structural analogue, "regional" analysis is reframed as
-- Department x Fiscal_Quarter, the closest available
-- cross-sectional grouping to a "region x period" breakdown.)
-- ============================================================

SELECT
    department,
    fiscal_quarter,
    SUM(budget_allocated) AS total_allocated,
    SUM(budget_utilized)  AS total_utilized,
    ROUND(SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0), 4) AS utilization_rate,
    ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency
FROM budget_records
GROUP BY department, fiscal_quarter
ORDER BY department, fiscal_quarter;

-- Which department performs best in each quarter label, by
-- allocation efficiency (window function)
SELECT department, fiscal_quarter, avg_allocation_efficiency, rnk
FROM (
    SELECT
        department,
        fiscal_quarter,
        ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency,
        RANK() OVER (
            PARTITION BY fiscal_quarter ORDER BY AVG(allocation_efficiency) DESC
        ) AS rnk
    FROM budget_records
    GROUP BY department, fiscal_quarter
) ranked
WHERE rnk = 1
ORDER BY fiscal_quarter;
