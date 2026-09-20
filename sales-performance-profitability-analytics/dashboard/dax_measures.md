# DAX Measures

All measures below use the star schema in `dashboard_data_dictionary.md`.
Every formula matches the definition in `docs/kpi_framework.md` exactly --
these are the same KPIs, expressed for Power BI, not a reinterpretation.
Create all of these as **measures** (not calculated columns) in a
dedicated `_Measures` table for organization.

## Core KPIs

```dax
Total Revenue = SUM(FactSales[sales])
```
Business meaning: total dollar value of goods sold. Actual value on this
dataset: $2,326,534.35.

```dax
Total Profit = SUM(FactSales[profit])
```
Business meaning: total dollar profit. Actual value: $292,296.81.

```dax
Total Orders = DISTINCTCOUNT(FactSales[order_id])
```
Business meaning: number of distinct customer orders. Actual value: 5,111.

```dax
Total Units = SUM(FactSales[quantity])
```
Business meaning: total units sold. Actual value: 38,654.

```dax
Profit Margin = DIVIDE([Total Profit], [Total Revenue], 0)
```
Business meaning: profit as a percentage of revenue. **Revenue-based
margin** -- no cost data exists to support a cost-based margin (see
`docs/assumptions_and_constraints.md`). `DIVIDE()` returns 0 instead of an
error when revenue is 0 in a filtered context. Actual value: 12.56%.
Format as a percentage in the visual.

```dax
Average Order Value =
DIVIDE(
    [Total Revenue],
    [Total Orders],
    0
)
```
Business meaning: average dollar size of an order. This correctly computes
the order-grain average (total revenue / distinct orders) matching
`src/kpi_calculations.py::average_order_value`. Actual value: $455.20.

```dax
Average Units per Order = DIVIDE([Total Units], [Total Orders], 0)
```
Actual value: 7.56.

## Customer KPIs

```dax
Customer Count = DISTINCTCOUNT(FactSales[customer_id])
```
Actual value: 804.

```dax
Revenue per Customer = DIVIDE([Total Revenue], [Customer Count], 0)
```
Actual value: $2,893.70.

```dax
Repeat Customer Rate =
VAR CustomerOrderCounts =
    SUMMARIZE(
        FactSales,
        FactSales[customer_id],
        "OrderCount", DISTINCTCOUNT(FactSales[order_id])
    )
VAR RepeatCustomers =
    COUNTROWS(FILTER(CustomerOrderCounts, [OrderCount] > 1))
VAR TotalCustomers =
    COUNTROWS(CustomerOrderCounts)
RETURN
    DIVIDE(RepeatCustomers, TotalCustomers, 0)
```
Business meaning: share of customers with more than one distinct order.
**This is a dataset-lifetime rate, not a rolling rate** -- present it with
that caveat on the dashboard (see `dashboard_requirements.md` Page 3).
Actual value: 98.51%.

## Time-Intelligence KPIs

These require `DimDate` to be marked as the official Date table (see
`dashboard_data_dictionary.md`).

```dax
Revenue Growth YoY =
VAR CurrentRevenue = [Total Revenue]
VAR PriorYearRevenue =
    CALCULATE(
        [Total Revenue],
        SAMEPERIODLASTYEAR(DimDate[Date])
    )
RETURN
    DIVIDE(CurrentRevenue - PriorYearRevenue, PriorYearRevenue)
```
Actual values by year: 2024 -4.26%, 2025 +29.80%, 2026 +21.44% (2023 has
no prior year in the dataset, so this returns BLANK for 2023).

```dax
Profit Growth YoY =
VAR CurrentProfit = [Total Profit]
VAR PriorYearProfit =
    CALCULATE(
        [Total Profit],
        SAMEPERIODLASTYEAR(DimDate[Date])
    )
RETURN
    DIVIDE(CurrentProfit - PriorYearProfit, PriorYearProfit)
```
Actual values by year: 2024 +20.00%, 2025 +33.29%, 2026 +16.04%.

## Contribution / Share Measures

```dax
Revenue Contribution % =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL(FactSales)),
    0
)
```
Business meaning: each filtered context's (e.g. a selected category's)
share of total company revenue. Use on a table/matrix visual with Category
or Sub-Category on rows.

```dax
Profit Contribution % =
DIVIDE(
    [Total Profit],
    CALCULATE([Total Profit], ALL(FactSales)),
    0
)
```

## Discount/Profitability Measures

```dax
Avg Discount Rate = AVERAGE(FactSales[discount])
```

```dax
Discount-Margin Correlation =
-- Power BI's native DAX has no built-in CORR() function (unlike SQL's
-- CORR() used in sql/07_discount_profitability.sql). If an exact
-- correlation coefficient is needed on the dashboard, calculate it once
-- in Python/SQL (already done: -0.865, see docs/findings.md) and display
-- it as a static reference value in a card/text box on Page 5, rather
-- than attempting a full DAX reimplementation of Pearson's r.
```

## Measure formatting reference

| Measure | Format |
|---|---|
| Total Revenue, Total Profit, Revenue per Customer, Average Order Value | Currency, 2 decimals |
| Profit Margin, Repeat Customer Rate, Revenue Growth YoY, Profit Growth YoY, Revenue Contribution %, Profit Contribution %, Avg Discount Rate | Percentage, 1-2 decimals |
| Total Orders, Total Units, Customer Count | Whole number, thousands separator |
