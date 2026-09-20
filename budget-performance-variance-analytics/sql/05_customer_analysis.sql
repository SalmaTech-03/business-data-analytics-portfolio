-- ============================================================
-- 05_customer_analysis.sql
-- (Renamed conceptually from "customer" to "department" - this
-- dataset has no customer dimension. Business purpose: which
-- departments are the largest budget holders, and how efficient
-- are they.)
-- ============================================================

-- Department-level budget and efficiency rollup
SELECT
    department,
    COUNT(*) AS record_count,
    SUM(budget_allocated) AS total_allocated,
    SUM(budget_utilized)  AS total_utilized,
    ROUND(SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0), 4) AS utilization_rate,
    ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency
FROM budget_records
GROUP BY department
ORDER BY total_allocated DESC;

-- Department ranking by average allocation efficiency (window function)
SELECT
    department,
    ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency,
    RANK() OVER (ORDER BY AVG(allocation_efficiency) DESC) AS efficiency_rank
FROM budget_records
GROUP BY department;

-- Departments with the highest share of "Inefficient" records
SELECT
    department,
    COUNT(*) AS total_records,
    SUM(CASE WHEN budget_status = 'Inefficient' THEN 1 ELSE 0 END) AS inefficient_records,
    ROUND(100.0 * SUM(CASE WHEN budget_status = 'Inefficient' THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS pct_inefficient
FROM budget_records
GROUP BY department
ORDER BY pct_inefficient DESC;
