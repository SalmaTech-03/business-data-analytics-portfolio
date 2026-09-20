-- ============================================================
-- 07_discount_profitability.sql
-- (This dataset has no discount field. Reframed as the closest
-- available cost-pressure analogue: Inflation_Rate vs. budget
-- variance / allocation efficiency. We report the association
-- found in the data without claiming causation.)
-- ============================================================

-- Bucket records into inflation bands and compare outcomes
SELECT
    CASE
        WHEN inflation_rate < 3  THEN 'Low (<3%)'
        WHEN inflation_rate < 5  THEN 'Moderate (3-5%)'
        WHEN inflation_rate < 7  THEN 'Elevated (5-7%)'
        ELSE 'High (7%+)'
    END AS inflation_band,
    COUNT(*) AS record_count,
    ROUND(AVG(budget_utilized / NULLIF(budget_allocated, 0)), 4) AS avg_utilization_rate,
    ROUND(AVG(allocation_efficiency), 2) AS avg_allocation_efficiency,
    ROUND(AVG(budget_variance), 2) AS avg_budget_variance
FROM budget_records
GROUP BY 1
ORDER BY 1;

-- Spending volatility vs. budget status - do more volatile
-- spending patterns associate with worse budget status?
SELECT
    budget_status,
    ROUND(AVG(spending_volatility), 3) AS avg_spending_volatility,
    COUNT(*) AS record_count
FROM budget_records
GROUP BY budget_status
ORDER BY avg_spending_volatility DESC;

-- NOTE: These are cross-sectional associations only. No causal
-- claim (e.g. "inflation causes budget overruns") is supported by
-- this query alone - see docs/assumptions_and_constraints.md.
