# Power BI Build Guide

Step-by-step instructions to build the dashboard specified in
`dashboard_requirements.md` from scratch in Power BI Desktop.

## 1. Get data
`Home > Get Data > Text/CSV` -> select
`data/raw/Financial_Budgeting_Dataset.csv` (or an exported cleaned
CSV from `outputs/` if you've run `run_analysis.py` first).

## 2. Transform (Power Query)
- Promote headers, confirm data types (dates: none exist; numeric
  columns as Decimal Number; text columns as Text).
- Rename columns to friendly names matching
  `dashboard_data_dictionary.md` (e.g. `Budget_Allocated` -> `Budget Allocated`).
- Do **not** parse `Fiscal_Quarter` as a date - keep it as Text.
- Close & Apply.

## 3. Build the star schema
1. Reference the main query twice (or use `Table.Distinct`) to build:
   - `Dim_Department`: one column, `Department`, distinct values.
   - `Dim_ExpenseCategory`: one column, `Expense Category`, distinct
     values.
2. In Model view, create relationships:
   - `Dim_Department[Department]` (1) -> `budget_records[Department]` (*)
   - `Dim_ExpenseCategory[Expense Category]` (1) -> `budget_records[Expense Category]` (*)
3. Set both relationships to single-direction filtering (dimension ->
   fact), the standard star-schema pattern.
4. Do **not** build a Date table - there is no date field. Use
   `Fiscal_Quarter` as a plain slicer on the fact table.

## 4. Add DAX measures
Create a dedicated measures table (`_Measures`, no data, used only to
hold measures for organization) and paste in every measure from
`dax_measures.md`.

## 5. Build each page
Follow the page-by-page KPI/chart list in `dashboard_requirements.md`
exactly - each visual is already tied to a specific business
question, so there's no need to add extra decorative visuals.

## 6. Set up the "always full portfolio" KPI cards on Page 1
Use **Edit Interactions** (Format ribbon) to turn off filtering from
page-level slicers onto the Page 1 KPI card visuals specifically, so
they always reflect the full portfolio regardless of what a user has
filtered elsewhere on the page - satisfies the requirement in
`dashboard_requirements.md`.

## 7. Validate against the Python pipeline
Run `python run_analysis.py`, open `outputs/tables/kpi_summary.json`,
and confirm each DAX measure's total matches the corresponding JSON
value (e.g. `Total Budget Allocated` should read $1,019,783,032.04).
This is the manual QA step - there is no automated Power BI test in
this repo.

## 8. Export / share
`File > Export > PDF` for a static leave-behind, or publish to Power
BI Service if you have a workspace. Neither step has been performed
in this environment - both are manual next steps for you to do
locally with Power BI Desktop installed.
