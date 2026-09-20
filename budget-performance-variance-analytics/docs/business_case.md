# Business Case

## Context

This project uses a **public/sample dataset** (`Financial_Budgeting_Dataset.csv`)
that simulates departmental budgeting and expense-tracking records for
a fictional multi-department organization. **This is not a real
company**, and no findings in this repo should be read as describing
any actual business.

## The problem, as framed for this project

A fictional organization allocates quarterly budgets across 8
departments (Sales, Finance, R&D, Marketing, Logistics, IT, HR,
Operations) and 6 expense categories (Infrastructure, Operations,
Technology, Training, Maintenance, Salaries). Leadership currently
has raw budget/expense/revenue records but no structured analytical
layer to answer:

- Are departments spending within their allocated budgets?
- Which expense categories consume the most budget, and how
  efficiently?
- How accurate is revenue forecasting?
- Which department x expense-category combinations warrant a closer
  look?

## Analytical workflow

```
Raw Data (CSV)
  -> Data Quality Checks
  -> Clean Data
  -> SQL Analysis Layer
  -> Python Analysis (pandas)
  -> KPI Layer
  -> Power BI Data Model
  -> Dashboard
  -> Business Insights
  -> Recommendations
```

## Scope note

The originally planned project template for this repo assumed a
retail sales dataset (Sample Superstore: orders, customers, products,
regions). The dataset actually supplied is a **financial budgeting**
dataset with a different grain and different dimensions (department,
expense category, fiscal quarter label - no customer, product, or
region fields, and no calendar year). The project was adapted to fit
the actual data rather than forcing retail-style questions onto data
that can't answer them. See `assumptions_and_constraints.md` for the
specific limitations this creates.
