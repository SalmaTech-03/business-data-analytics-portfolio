# Dashboard Data Dictionary

Fields exposed to the Power BI model, and how they map to the
underlying columns. See `docs/data_dictionary.md` for the full source
data dictionary; this file lists only what's actually surfaced in the
dashboard.

## Fact table: `budget_records`

| Field (Power BI) | Source Column | Type | Notes |
|---|---|---|---|
| Record ID | record_id | Whole Number | Not shown on visuals; used as a key |
| Department (FK) | department | Text | Links to Dim_Department |
| Expense Category (FK) | expense_category | Text | Links to Dim_ExpenseCategory |
| Fiscal Quarter | fiscal_quarter | Text | Category filter only - not a date hierarchy |
| Budget Allocated | budget_allocated | Decimal | USD |
| Budget Utilized | budget_utilized | Decimal | USD |
| Monthly Expense | monthly_expense | Decimal | USD |
| Revenue Forecast | revenue_forecast | Decimal | USD |
| Actual Revenue | actual_revenue | Decimal | USD |
| Allocation Efficiency | allocation_efficiency | Decimal | 0-100 scale |
| Spending Volatility | spending_volatility | Decimal | provided metric |
| Inflation Rate | inflation_rate | Decimal | % |
| Market Index | market_index | Decimal | provided index |
| Budget Status | budget_status | Text | Efficient / Moderate / Inefficient |

**Not loaded into the dashboard model:** `Budget_Variance` and
`Revenue_Variance` as supplied - since they don't reconcile to their
component columns (see `docs/data_dictionary.md`), the dashboard
computes variance via DAX measures from Allocated/Utilized and
Forecast/Actual directly, so the dashboard's variance numbers are
internally consistent and auditable.

## Dim_Department
| Field | Values |
|---|---|
| Department | Sales, Finance, R&D, Marketing, Logistics, IT, HR, Operations |

## Dim_ExpenseCategory
| Field | Values |
|---|---|
| Expense Category | Infrastructure, Maintenance, Operations, Salaries, Technology, Training |
