# Executive Dashboard — Requirements Specification

## Scope and honesty note

This is a **design specification**, not a built dashboard. No Power BI file is
included in this repository and no screenshots are presented. What is provided is
the specification below plus the CSV extracts in `outputs/` that a developer can
import directly to build it.

## Purpose

Give Marketing, Finance and Senior Management a single view that answers:

1. Should we approve this campaign?
2. Where does the value come from?
3. What would have to change for the answer to be different?
4. Once the campaign runs, is it performing as forecast?

## Audience and usage

| Audience | Primary page | Typical use |
|---|---|---|
| Senior Management | Executive Overview | 60-second approval decision |
| Marketing Manager | Customer Targeting | Building and cutting the mail file |
| Finance Manager | Scenario Analysis | Challenging the assumptions |
| Data / Analytics | Model Performance | Monitoring drift after launch |

## Data sources

| File | Grain | Refresh |
|---|---|---|
| `outputs/customer_scores.csv` | One row per prospect (250) | Per campaign scoring run |
| `outputs/campaign_summary.csv` | One row — the campaign total | Per campaign scoring run |
| `outputs/segment_summary.csv` | One row per segment (4) | Per campaign scoring run |
| `outputs/priority_summary.csv` | One row per priority tier | Per campaign scoring run |
| `outputs/sensitivity_analysis.csv` | One row per scenario (80) | Per campaign scoring run |

Schema detail is in [`dashboard_data_dictionary.md`](dashboard_data_dictionary.md).

---

## Page 1 — Executive Overview

### KPI cards

| Card | Value | Source | Format | Notes |
|---|---|---|---|---|
| Expected Revenue | $47,224.87 | `campaign_summary.expected_revenue` | Currency, 0 dp | |
| Expected Gross Profit | $23,612.44 | `campaign_summary.gross_profit` | Currency, 0 dp | Subtitle: "at 50% margin" |
| Campaign Cost | $1,625.00 | `campaign_summary.campaign_cost` | Currency, 0 dp | Subtitle: "250 x $6.50" |
| **Expected Net Profit** | **$21,987.44** | `campaign_summary.net_profit` | Currency, 0 dp | Largest card. Conditional colour: green above zero, red at or below |
| ROI | 13.5x | `campaign_summary.roi` | Decimal, 1 dp, suffix "x" | |
| Customer Count | 250 | `campaign_summary.customers` | Whole number | |

### Charts

| # | Visual | Type | Axes / fields | Business question |
|---|---|---|---|---|
| 1 | Expected profit by customer segment | Horizontal bar | Segment vs `Expected_Net_Profit`, sorted descending | Which segments carry the campaign? |
| 2 | Revenue vs campaign cost | Waterfall | Expected revenue → COGS → gross profit → campaign cost → net profit | How does revenue become profit? |
| 3 | Predicted sales distribution | Histogram | `Predicted_Sale_Amount`, 20 bins | How concentrated is customer value? |
| 4 | Customer segment comparison | Clustered bar | Segment vs customer count and average predicted sale (dual axis) | Are we mailing volume or value? |
| 5 | Expected profit by customer | Bar, top 20 | `Customer_ID` vs `Expected_Net_Profit`, descending | Who are the highest-value targets? |

### Management Decision panel

A static text panel, updated each scoring run:

> **Recommendation: PROCEED.** Expected net profit of $21,987 on $1,625 of
> campaign spend (13.5x ROI). All 250 prospects are individually profitable. The
> campaign remains profitable under every downside scenario tested, including
> response 40% below forecast combined with a 40% margin and a $10 catalog cost.
>
> **Conditional on:** Finance confirming the 50% gross margin; Operations
> confirming the $6.50 unit cost; response attribution being in place before
> mailing.
>
> **Largest unquantified risk:** incrementality. Without a control group, it is
> not possible to establish how many of these orders would have occurred anyway.

---

## Page 2 — Customer Targeting

| Element | Type | Detail |
|---|---|---|
| Priority tier summary | Three cards | Customer count, expected profit and profit share per tier |
| Prospect table | Table | `Profit_Rank`, `Customer_ID`, `Customer_Segment`, `City`, `Predicted_Sale_Amount`, `Response_Probability`, `Expected_Revenue`, `Expected_Net_Profit`, `Priority`. Sorted by rank. Exportable. |
| Value map | Scatter | X: `Predicted_Sale_Amount`, Y: `Response_Probability`, size: `Expected_Net_Profit`, colour: `Priority` |
| Cumulative profit curve | Line | X: cumulative share of customers (ranked), Y: cumulative share of profit. Shows how much profit survives a budget cut |
| Profit by store | Bar | `Store_Number` vs expected net profit |

---

## Page 3 — Scenario Analysis

| Element | Type | Detail |
|---|---|---|
| Scenario banner | Text | **"All figures on this page are hypothetical scenarios, not forecasts."** Required by BRule-14 |
| Margin vs cost heatmap | Matrix | Rows: `Gross_Margin`; columns: `Cost_Per_Catalog`; values: `Net_Profit`; diverging colour scale centred on the base case |
| Response scenario bars | Bar | `Response_Multiplier` vs `Net_Profit`, base case highlighted in a distinct colour |
| Tornado chart | Bar | Net-profit swing per assumption, sorted by magnitude |
| Break-even cards | Three cards | Break-even response level, break-even margin, break-even catalog cost |
| Assumption selectors | Slicers | Gross margin, cost per catalog, response multiplier — drive all visuals on this page |

---

## Page 4 — Post-Campaign Performance

**Not populated until the campaign has run.** Included so that the measurement
design is agreed before launch rather than improvised afterwards.

| Element | Metric | Comparison |
|---|---|---|
| Response rate | Actual vs forecast (34.1%) | M-01 |
| Average order value | Actual vs predicted ($553.17) | M-02 |
| Revenue | Actual vs forecast ($47,224.87) | M-03 |
| Net profit | Actual vs forecast ($21,987.44) | M-06 |
| ROI | Actual vs forecast (13.5x) | M-07 |
| Lift by priority tier | Response rate, High vs Medium | M-09 — the sharpest test of whether the prioritisation added value |
| Forecast error | Actual MAE vs held-out MAE ($93.40) | M-08 |
| Opt-out rate | Actual by tier | M-11 |

---

## Global filters

| Filter | Field | Applies to |
|---|---|---|
| Customer Segment | `Customer_Segment` | Pages 1, 2, 4 |
| Customer Priority | `Priority` | Pages 1, 2, 4 |
| Customer Location | `City`, `ZIP` | Page 2 |
| Store | `Store_Number` | Page 2 |
| Gross Margin | `Gross_Margin` | Page 3 |
| Cost per Catalog | `Cost_Per_Catalog` | Page 3 |
| Response Multiplier | `Response_Multiplier` | Page 3 |

## Design standards

| Rule | Reason |
|---|---|
| Currency to whole dollars on cards, two decimals in tables | Executives read magnitude; analysts need precision |
| ROI as a multiple ("13.5x"), not a percentage | Easier to compare against other spend |
| Green for profit, red for loss, blue for neutral | Consistent, colour-blind-safe palette |
| Every scenario visual carries a "hypothetical" label | BRule-14 — prevents scenario figures being quoted as forecasts |
| Every page footer names the scoring run date and model version | Auditability (NFR-006) |
| No visual without a stated business question | Charts justify their space or are removed |

## Measures required (DAX-equivalent)

```
Expected Revenue      = SUM(customer_scores[Expected_Revenue])
Gross Profit          = SUM(customer_scores[Gross_Profit])
Campaign Cost         = COUNTROWS(customer_scores) * [Cost Per Catalog]
Net Profit            = [Gross Profit] - [Campaign Cost]
ROI                   = DIVIDE([Net Profit], [Campaign Cost])
Avg Revenue per Cust  = DIVIDE([Expected Revenue], COUNTROWS(customer_scores))
Profit per Catalog    = DIVIDE([Net Profit], COUNTROWS(customer_scores))
High Priority Profit  = CALCULATE([Net Profit], customer_scores[Priority] = "High")
Profit Concentration  = DIVIDE([High Priority Profit], [Net Profit])
```

`Cost Per Catalog` should be a parameter, not a hard-coded constant, so the
assumption can be changed without editing the model.
