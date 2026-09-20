# Business Questions

Adapted from the original retail-analytics question template to fit
the actual dataset (department/expense budgeting, not retail sales).
Each question is answered with real, calculated results in
`findings.md`; the SQL that answers it lives in `sql/08_business_questions.sql`.

1. What is total budget allocated and utilized?
2. What is the overall utilization rate (utilized / allocated)?
3. How is the budget changing across fiscal-quarter labels
   (Q1-Q4, cross-sectional - no year in the data)?
4. Which expense categories consume the largest share of budget?
5. Which expense categories have the highest / lowest average
   allocation efficiency?
6. Which departments are, on average, over budget (utilization > 100%)?
7. Which departments have the strongest / weakest allocation
   efficiency?
8. What is the overall revenue realization rate (actual / forecast)?
9. How does revenue forecast accuracy vary by department?
10. What is the distribution of Budget_Status (Efficient / Moderate /
    Inefficient) across the whole dataset?
11. Does Budget_Status vary meaningfully by department?
12. Which Department x Expense_Category combinations have the
    highest average utilization rate - candidates for investigation?
13. Is there an observable relationship between spending volatility
    and Budget_Status?
14. Is there an observable relationship between inflation rate and
    budget variance / allocation efficiency?
15. What data-quality issues, if any, affect the reliability of these
    answers (e.g. the extreme-utilization outlier records)?
16. What KPIs should management monitor going forward?

Note: the original template's retail-specific questions (top
products, regional sales, discount-vs-profit, repeat customer rate)
are not answerable from this dataset - there is no product, region,
or customer dimension - and are intentionally omitted rather than
answered with fabricated substitutes.
