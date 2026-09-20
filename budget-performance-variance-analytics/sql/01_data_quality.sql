-- ============================================================
-- 01_data_quality.sql
-- Business purpose: Confirm the raw budget_records table is fit
-- for analysis before any KPI or business-question query runs.
-- Dialect: PostgreSQL-compatible.
-- Assumed table: budget_records (loaded from Financial_Budgeting_Dataset.csv)
-- ============================================================

-- Row count
SELECT COUNT(*) AS total_rows FROM budget_records;

-- Null counts per column (run individually or via UNION as below)
SELECT
    SUM(CASE WHEN record_id IS NULL THEN 1 ELSE 0 END)          AS null_record_id,
    SUM(CASE WHEN fiscal_quarter IS NULL THEN 1 ELSE 0 END)     AS null_fiscal_quarter,
    SUM(CASE WHEN department IS NULL THEN 1 ELSE 0 END)         AS null_department,
    SUM(CASE WHEN expense_category IS NULL THEN 1 ELSE 0 END)   AS null_expense_category,
    SUM(CASE WHEN budget_allocated IS NULL THEN 1 ELSE 0 END)   AS null_budget_allocated,
    SUM(CASE WHEN budget_utilized IS NULL THEN 1 ELSE 0 END)    AS null_budget_utilized,
    SUM(CASE WHEN revenue_forecast IS NULL THEN 1 ELSE 0 END)   AS null_revenue_forecast,
    SUM(CASE WHEN actual_revenue IS NULL THEN 1 ELSE 0 END)     AS null_actual_revenue,
    SUM(CASE WHEN budget_status IS NULL THEN 1 ELSE 0 END)      AS null_budget_status
FROM budget_records;

-- Duplicate record_id values
SELECT record_id, COUNT(*) AS occurrences
FROM budget_records
GROUP BY record_id
HAVING COUNT(*) > 1;

-- Fully duplicated rows (all columns identical)
SELECT department, expense_category, fiscal_quarter, budget_allocated,
       budget_utilized, COUNT(*) AS occurrences
FROM budget_records
GROUP BY department, expense_category, fiscal_quarter, budget_allocated, budget_utilized
HAVING COUNT(*) > 1;

-- Invalid / out-of-domain categorical values
SELECT DISTINCT fiscal_quarter FROM budget_records
WHERE fiscal_quarter NOT IN ('Q1','Q2','Q3','Q4');

SELECT DISTINCT budget_status FROM budget_records
WHERE budget_status NOT IN ('Efficient','Moderate','Inefficient');

-- Negative values in fields that should be non-negative
SELECT COUNT(*) AS negative_budget_allocated FROM budget_records WHERE budget_allocated < 0;
SELECT COUNT(*) AS negative_budget_utilized  FROM budget_records WHERE budget_utilized  < 0;
SELECT COUNT(*) AS negative_revenue_forecast FROM budget_records WHERE revenue_forecast < 0;
SELECT COUNT(*) AS negative_actual_revenue   FROM budget_records WHERE actual_revenue   < 0;

-- Distinct departments and expense categories (used to confirm the
-- expected dimension values for the star schema in Power BI)
SELECT DISTINCT department FROM budget_records ORDER BY 1;
SELECT DISTINCT expense_category FROM budget_records ORDER BY 1;

-- Numeric range sanity check
SELECT
    MIN(budget_allocated) AS min_allocated, MAX(budget_allocated) AS max_allocated,
    MIN(allocation_efficiency) AS min_efficiency, MAX(allocation_efficiency) AS max_efficiency
FROM budget_records;
