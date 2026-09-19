# Dashboard Data Dictionary

Schema of the CSV extracts in `outputs/`, produced by `python run_analysis.py`.

## `customer_scores.csv` — one row per campaign prospect (250 rows)

The primary fact table.

| Field | Type | Description | Example | Dashboard use |
|---|---|---|---|---|
| `Customer_ID` | Integer | Unique prospect identifier | `2213` | Key; table display |
| `Name` | String | Prospect name | `A Giametti` | Mail-file production only. Exclude from any shared dashboard. |
| `Customer_Segment` | String | One of four relationship segments | `Loyalty Club Only` | Primary filter and grouping dimension |
| `City` | String | City of residence | `Centennial` | Location filter |
| `State` | String | State | `CO` | Location filter (effectively constant) |
| `ZIP` | String | Zero-padded 5-character postal code | `80015` | Location filter; map visual |
| `Store_Number` | Integer | Associated store | `105` | Grouping dimension. Not a quantity — never aggregate. |
| `Avg_Num_Products_Purchased` | Integer | Average products per purchase | `3` | Model input; drill-through detail |
| `Years_as_Customer` | Float | Tenure. **Not a model input** (constraint C-05) | `0.2` | Display only |
| `Predicted_Sale_Amount` | Float | Model estimate of average sale value | `672.40` | Histogram; scatter X-axis |
| `Response_Probability` | Float 0-1 | Probability of responding, from supplied `Score_Yes` | `0.3050` | Scatter Y-axis |
| `Expected_Revenue` | Float | `Predicted_Sale_Amount x Response_Probability` | `205.09` | Revenue measures |
| `Gross_Profit` | Float | `Expected_Revenue x 0.50` | `102.55` | Profit measures |
| `Catalog_Cost` | Float | Cost of one catalog | `6.50` | Constant at the row grain |
| `Expected_Net_Profit` | Float | `Gross_Profit - Catalog_Cost` | `96.05` | Primary ranking measure; bubble size |
| `Customer_ROI` | Float | `Expected_Net_Profit / Catalog_Cost` | `14.78` | Efficiency measure. Average across rows; do not sum. |
| `Priority` | String | `High`, `Medium` or `Low` per BRule-08 | `High` | Filter; scatter colour |
| `Profit_Rank` | Integer | Rank by expected net profit, 1 is highest | `17` | Table sort order |

## `campaign_summary.csv` — one row, campaign totals

| Field | Type | Description | Value |
|---|---|---|---|
| `customers` | Integer | Catalogs mailed | `250` |
| `predicted_sales_total` | Float | Sum of predicted sale amounts | `138292.13` |
| `expected_revenue` | Float | Response-weighted revenue | `47224.87` |
| `gross_margin` | Float | Margin assumption applied | `0.50` |
| `gross_profit` | Float | Revenue x margin | `23612.44` |
| `campaign_cost` | Float | Catalogs x unit cost | `1625.00` |
| `net_profit` | Float | Gross profit - campaign cost | `21987.44` |
| `roi` | Float | Net profit / campaign cost | `13.53` |
| `avg_response_probability` | Float | Mean response probability | `0.3407` |
| `revenue_per_customer` | Float | Revenue / catalogs | `188.90` |
| `net_profit_per_customer` | Float | Net profit / catalogs | `87.95` |
| `breakeven_response_multiplier` | Float | Fraction of modelled response at which profit reaches zero | `0.0688` |

**Note on `predicted_sales_total`.** This is the sum of predicted sale amounts
*before* response weighting. It is a model diagnostic, not a revenue forecast,
and must never be presented as expected revenue on a dashboard.

## `segment_summary.csv` — one row per segment (4 rows)

| Field | Type | Description |
|---|---|---|
| `Customer_Segment` | String | Segment name |
| `Customers` | Integer | Prospects in this segment |
| `Avg_Predicted_Sale` | Float | Mean predicted sale amount |
| `Avg_Response_Prob` | Float | Mean response probability |
| `Expected_Revenue` | Float | Segment revenue total |
| `Gross_Profit` | Float | Segment gross profit total |
| `Expected_Net_Profit` | Float | Segment net profit total |
| `Campaign_Cost` | Float | Customers x $6.50 |
| `ROI` | Float | Segment net profit / segment cost |

## `priority_summary.csv` — one row per priority tier

| Field | Type | Description |
|---|---|---|
| `Priority` | String | `High`, `Medium` or `Low` |
| `Customers` | Integer | Prospects in the tier |
| `Expected_Revenue` | Float | Tier revenue total |
| `Expected_Net_Profit` | Float | Tier net profit total |
| `Min_Profit` / `Max_Profit` | Float | Profit range within the tier |
| `Campaign_Cost` | Float | Tier cost |
| `ROI` | Float | Tier return |
| `Share_of_profit` | Float | Tier share of total expected profit |

**Note.** Tiers with no members are absent from this file. In the current run no
prospect falls into `Low`, so only `High` and `Medium` appear. A dashboard should
not assume three rows.

## `sensitivity_analysis.csv` — one row per scenario (80 rows)

| Field | Type | Description |
|---|---|---|
| `Response_Multiplier` | Float | Fraction of modelled response applied (0.6, 0.8, 1.0, 1.2) |
| `Gross_Margin` | Float | Margin applied (0.40 to 0.60) |
| `Cost_Per_Catalog` | Float | Unit cost applied (5.00 to 10.00) |
| `Expected_Revenue` | Float | Scenario revenue |
| `Gross_Profit` | Float | Scenario gross profit |
| `Campaign_Cost` | Float | Scenario campaign cost |
| `Net_Profit` | Float | Scenario net profit |
| `ROI` | Float | Scenario return |

**The base case is the single row where `Response_Multiplier = 1.0`,
`Gross_Margin = 0.50` and `Cost_Per_Catalog = 6.50`.** Every other row is
hypothetical and must be labelled as such wherever it is displayed (BRule-14).

## Relationships

```
campaign_summary  (1 row, no key — card values only)

customer_scores   (250 rows, grain: Customer_ID)
    |-- Customer_Segment --> segment_summary.Customer_Segment   (many-to-one)
    |-- Priority         --> priority_summary.Priority          (many-to-one)

sensitivity_analysis  (80 rows, standalone — no relationship to the fact table)
```

## Aggregation rules

| Measure | Correct aggregation | Common mistake |
|---|---|---|
| `Expected_Revenue`, `Gross_Profit`, `Expected_Net_Profit` | SUM | — |
| `Catalog_Cost` | SUM (or COUNT x 6.50) | — |
| `Customer_ROI` | AVERAGE, or recompute as SUM(profit)/SUM(cost) | Summing ROI across rows is meaningless |
| `Response_Probability` | AVERAGE | Summing probabilities |
| `Predicted_Sale_Amount` | AVERAGE for reporting | Summing and presenting the total as revenue |
| `Store_Number`, `ZIP`, `Customer_ID` | COUNT or DISTINCTCOUNT only | Summing or averaging an identifier |
