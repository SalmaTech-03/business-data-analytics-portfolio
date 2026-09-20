-- ============================================================
-- 08_business_questions.sql
-- Clearly labeled queries answering the major business questions
-- for the Budget Performance & Variance Analytics project.
-- ============================================================

-- Q1: What is total budget allocated and utilized?
SELECT SUM(budget_allocated) AS total_allocated, SUM(budget_utilized) AS total_utilized
FROM budget_records;

-- Q2: What is the overall utilization rate?
SELECT ROUND(SUM(budget_utilized) / NULLIF(SUM(budget_allocated), 0), 4) AS overall_utilization_rate
FROM budget_records;

-- Q3: Which departments are over budget on average?
SELECT department,
       ROUND(AVG(budget_utilized / NULLIF(budget_allocated, 0)), 4) AS avg_utilization_rate
FROM budget_records
GROUP BY department
HAVING AVG(budget_utilized / NULLIF(budget_allocated, 0)) > 1
ORDER BY avg_utilization_rate DESC;

-- Q4: Which expense categories consume the largest share of allocated budget?
SELECT expense_category, SUM(budget_allocated) AS total_allocated,
       ROUND(100.0 * SUM(budget_allocated) / SUM(SUM(budget_allocated)) OVER (), 2) AS pct_of_total
FROM budget_records
GROUP BY expense_category
ORDER BY total_allocated DESC;

-- Q5: How accurate is revenue forecasting overall, and by department?
SELECT department,
       SUM(revenue_forecast) AS total_forecast,
       SUM(actual_revenue) AS total_actual,
       ROUND(SUM(actual_revenue) / NULLIF(SUM(revenue_forecast), 0), 4) AS realization_rate
FROM budget_records
GROUP BY department
ORDER BY realization_rate;

-- Q6: Which departments have the best / worst allocation efficiency?
SELECT department, ROUND(AVG(allocation_efficiency), 2) AS avg_efficiency
FROM budget_records
GROUP BY department
ORDER BY avg_efficiency DESC;

-- Q7: What is the distribution of Budget_Status across the portfolio?
SELECT budget_status, COUNT(*) AS record_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM budget_records
GROUP BY budget_status;

-- Q8: Which Department x Expense_Category combinations should
-- management investigate first (highest utilization + Inefficient share)?
SELECT department, expense_category,
       ROUND(AVG(budget_utilized / NULLIF(budget_allocated, 0)), 4) AS avg_utilization_rate,
       ROUND(100.0 * SUM(CASE WHEN budget_status = 'Inefficient' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_inefficient,
       COUNT(*) AS record_count
FROM budget_records
GROUP BY department, expense_category
ORDER BY avg_utilization_rate DESC, pct_inefficient DESC
LIMIT 10;

-- Q9: What KPIs should management monitor going forward? (Answered
-- narratively in docs/kpi_framework.md - not a single query.)
