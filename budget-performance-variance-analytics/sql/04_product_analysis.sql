-- ============================================================
-- 04_product_analysis.sql
-- (Renamed conceptually from "product" to "expense category" -
-- this dataset has no product dimension. Business purpose:
-- which expense categories consume budget, and how efficiently.)
-- ============================================================

-- Total allocated/utilized/variance by expense category
SELECT
    expense_category,
    SUM(budget_allocated) AS total_allocated,
    SUM(budget_utilized)  AS total_utilized,
    SUM(budget_variance)  AS total_variance,
    ROUND(SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0), 4) AS utilization_rate,
    ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency
FROM budget_records
GROUP BY expense_category
ORDER BY total_allocated DESC;

-- Rank expense categories by utilization rate (window function)
SELECT
    expense_category,
    ROUND(SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0), 4) AS utilization_rate,
    RANK() OVER (
        ORDER BY SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0) DESC
    ) AS utilization_rank
FROM budget_records
GROUP BY expense_category;

-- Department x Expense Category matrix (top 10 combinations by
-- average utilization rate - candidates for investigation)
SELECT
    department,
    expense_category,
    ROUND(AVG(budget_utilized / NULLIF(budget_allocated, 0)), 4) AS avg_utilization_rate,
    COUNT(*) AS record_count
FROM budget_records
GROUP BY department, expense_category
ORDER BY avg_utilization_rate DESC
LIMIT 10;
