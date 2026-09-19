# Project Report

**Catalog Campaign Profitability & Customer Targeting Analysis**

---

## Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Context](#2-business-context)
3. [Problem Statement](#3-problem-statement)
4. [Business Objectives](#4-business-objectives)
5. [Stakeholders](#5-stakeholders)
6. [Requirements](#6-requirements)
7. [Data Understanding](#7-data-understanding)
8. [Data Quality](#8-data-quality)
9. [Exploratory Analysis](#9-exploratory-analysis)
10. [Predictive Modelling](#10-predictive-modelling)
11. [Model Validation](#11-model-validation)
12. [Campaign Economics](#12-campaign-economics)
13. [Customer Prioritisation](#13-customer-prioritisation)
14. [Sensitivity Analysis](#14-sensitivity-analysis)
15. [Risks](#15-risks)
16. [Limitations](#16-limitations)
17. [Recommendation](#17-recommendation)
18. [Implementation Plan](#18-implementation-plan)
19. [Monitoring KPIs](#19-monitoring-kpis)
20. [Conclusion](#20-conclusion)

---

## 1. Executive Summary

A catalog campaign targeting 250 prospective customers is expected to generate
**$47,224.87 in revenue** and **$23,612.44 in gross profit** against **$1,625 in
campaign cost**, producing an **expected net profit of $21,987.44** and a **13.5x
return** on campaign spend.

Every one of the 250 prospects is individually profitable, so no part of the list
warrants exclusion. Value is concentrated: the top quarter of the list carries
53% of the expected profit, which matters if the budget is reduced.

Customer value is driven by two things — average basket size and the depth of the
customer's relationship with the company. A customer holding both a loyalty
membership and a store credit card is worth roughly seven times a store-mailing-list
customer. Tenure has no measurable effect.

The model explains approximately **84% of the variation** in average sale amount,
with a held-out mean absolute error of **$93.40** per customer. More importantly,
the recommendation survives every downside scenario tested, including response
40% below forecast combined with a 40% margin and a $10 catalog cost, which still
returns $8,834 of net profit.

**Recommendation: proceed**, conditional on Finance confirming the margin
assumption, Operations confirming the unit cost, and response tracking being in
place before mailing.

---

## 2. Business Context

The company sells through a direct-mail catalog channel alongside its retail
stores. It maintains customer relationships through a loyalty programme and a
store credit card, and customers are classified into four segments by which of
these they hold.

Catalog campaigns require committed upfront spend: printing and distribution are
paid whether or not the recipient buys. Historically the decision of whom to mail
has been made on segment intuition rather than expected value, which is neither
auditable nor repeatable.

Marketing has assembled a list of 250 prospective recipients and asked for a
quantified assessment before releasing budget.

---

## 3. Problem Statement

> The company must decide whether to spend $1,625 mailing catalogs to 250
> prospective customers, without knowing how much revenue those customers will
> generate. Campaign cost is committed and unrecoverable; revenue is uncertain and
> arises only from those who respond. Without an estimate of expected value per
> recipient, management cannot determine whether the campaign creates value, and
> cannot rank recipients if the budget is constrained.

### Primary business question

**"Is the proposed catalog campaign financially attractive, and which customers
should receive the highest campaign priority?"**

### Secondary questions and where each is answered

| # | Question | Section |
|---|---|---|
| 1 | What customer characteristics are associated with higher average sales? | 9, 10 |
| 2 | Which customer segments generate higher expected value? | 12 |
| 3 | What is the expected revenue from the 250-customer campaign? | 12 |
| 4 | What is the expected gross profit? | 12 |
| 5 | What is the campaign cost? | 12 |
| 6 | What is the expected net profit? | 12 |
| 7 | What is the expected ROI? | 12 |
| 8 | Which customers have the highest predicted economic value? | 13 |
| 9 | What assumptions could materially change the decision? | 14, 16 |
| 10 | What should management monitor after campaign execution? | 19 |

---

## 4. Business Objectives

| # | Objective | Success measure |
|---|---|---|
| 1 | Quantify the campaign's expected net profit and ROI | A single defensible figure with every input traceable to a formula |
| 2 | Rank prospects by expected economic value | All 250 prospects ranked with documented tier thresholds |
| 3 | Identify what drives customer value | Quantified, dollar-denominated effect of each characteristic |
| 4 | Establish how robust the decision is | Break-even points stated for every assumption |
| 5 | Provide a decision-support product management can act on | One-page summary plus BI-ready extracts |
| 6 | Define how success will be measured after launch | KPI set with owners and data sources agreed pre-launch |

---

## 5. Stakeholders

| Role | Interest | Influence | What they need |
|---|---|---|---|
| Marketing Manager | Owns budget and the mail decision | High | Target list and expected return |
| Finance Manager | Validates margin, cost and ROI | High | Assumption register and sensitivity analysis |
| Senior Management | Approves discretionary spend | High | One-page recommendation |
| Sales / Customer Management | Owns the customer relationship | Medium | Segment targeting, contact-frequency controls |
| Marketing Operations | Executes print and distribution | Medium | Prioritised mail file, unit-cost confirmation |
| Data / Analytics | Builds and maintains the model | Medium | Methodology and monitoring plan |
| IT / Data Engineering | Provides data access | Low | Refresh requirements |

Full register: [`../docs/stakeholder_analysis.md`](../docs/stakeholder_analysis.md).

---

## 6. Requirements

Fifteen business requirements (BR-001 to BR-015) and twenty functional
requirements (FR-001 to FR-020) were defined, each traced to the artefact that
satisfies it. The critical path runs through BR-001 (is net profit positive),
BR-006 (prioritise by economic value) and BR-009 (show what would change the
decision).

Full detail: [`../docs/business_requirements.md`](../docs/business_requirements.md)
and [`../docs/functional_requirements.md`](../docs/functional_requirements.md).

---

## 7. Data Understanding

| File | Rows | Purpose |
|---|---|---|
| `p1-customers.xlsx` | 2,375 | Historical customers with known average sale amount. Model training. |
| `p1-mailinglist.xlsx` | 250 | Campaign prospects. Model scoring. |

**Target variable:** `Avg_Sale_Amount` — the average dollar value of a customer's
purchases. Chosen because campaign revenue from a responder is the size of the
order they place.

**Predictors retained:** `Avg_Num_Products_Purchased` (numeric) and
`Customer_Segment` (categorical, four levels, one-hot encoded with
`Credit Card Only` as the reference).

**Variables excluded and why:**

| Variable | Reason |
|---|---|
| `Years_as_Customer` | Correlation of 0.03 with the target; inconsistent type and scale between the two files |
| `Responded_to_Last_Catalog` | Absent from the mailing list — the model would be unscoreable |
| `Customer_ID`, `Store_Number`, `ZIP` | Numeric labels, not quantities |
| `Name`, `Address`, `City`, `State` | Personally identifying; no predictive content |

**Response probability:** the mailing list carries `Score_Yes`, a supplied
probability of catalog response. The model that produced it is not included with
this project.

Full field-level detail: [`../docs/data_dictionary.md`](../docs/data_dictionary.md).

---

## 8. Data Quality

All checks were executed in code rather than asserted.

| Check | Result |
|---|---|
| Missing values | 0 across both files |
| Duplicate rows / IDs | 0 across both files |
| Invalid target values | 0 non-positive sale amounts |
| Probability range violations | 0; `Score_Yes + Score_No = 1` for every row |
| Category consistency | Exactly the four expected segments in both files |
| Outliers in target | 58 of 2,375 (2.4%) beyond the 1.5x IQR fence — retained as genuine high-value customers |

Three issues were identified and addressed: `ZIP` stored as an integer (cast to a
padded string, excluded from modelling); `#_Years_as_Customer` inconsistently
typed and scaled across files (excluded); and `Responded_to_Last_Catalog` present
only in the training file (excluded under BRule-06).

**Verdict: both files are fit for purpose.** The issues found are definitional
rather than corruption.

Full assessment: [`../docs/data_quality.md`](../docs/data_quality.md).

---

## 9. Exploratory Analysis

### Distribution of the target

Average sale amount is strongly right-skewed: mean $399.77 against a median
$281.32, ranging from $1.22 to $2,963.49. A small group of high-value customers
accounts for a disproportionate share of revenue, which is the core argument for
scoring customers individually rather than planning on an average.

### Products purchased is the strongest driver

Correlation of **r = 0.86** with average sale amount, with a near-linear
relationship that supports a linear model.

*Caveat:* both fields are averages over the same purchase history, so part of the
correlation is arithmetic rather than a discovered behavioural driver.

### Segments separate sharply

| Segment | n (training) | Mean sale | Median sale |
|---|---|---|---|
| Loyalty Club and Credit Card | 194 | $1,074.16 | $1,015.66 |
| Credit Card Only | 494 | $682.68 | $698.60 |
| Loyalty Club Only | 579 | $396.33 | $384.76 |
| Store Mailing List | 1,108 | $157.36 | $166.92 |

Confidence intervals do not overlap between adjacent segments. Segment carries
information independent of basket size.

### Tenure does not matter

Correlation of 0.03 with average sale amount. A useful negative finding that
removes a variable stakeholders commonly assume should be included.

### Prior catalog response is confounded with segment

Customers who responded to the last catalog have a **lower** mean sale amount
($156) than those who did not ($419). The effect disappears once segment is
accounted for — prior response is concentrated in the lowest-spending segment.
Targeting on past response alone would systematically select the least valuable
customers.

### The campaign list is not like the training population

| Segment | Training share | Mailing-list share |
|---|---|---|
| Store Mailing List | 46.7% | 8.0% |
| Loyalty Club Only | 24.4% | 48.8% |
| Credit Card Only | 20.8% | 32.8% |
| Loyalty Club and Credit Card | 8.2% | 10.4% |

Not an error, but it means the forecast leans on parts of the model estimated
from a smaller share of the training data. Registered as constraint C-04.

### Response probability is flat across segments

Segment means range only from 33.7% to 35.9%. Segment predicts *how much* a
customer spends but not *whether* they respond — which is what makes ranking on
the product of the two worthwhile.

Detail: [`../notebooks/01_exploratory_data_analysis.ipynb`](../notebooks/01_exploratory_data_analysis.ipynb).

---

## 10. Predictive Modelling

### Why linear regression

The business question is not "what is the most accurate possible prediction" but
"which characteristics move average sale amount, and by how much in dollars".
Linear regression answers both, produces coefficients a marketing stakeholder can
read directly, and can be reproduced by Finance with a calculator. EDA confirmed
the underlying relationship is close to linear.

### The fitted model

```
Predicted Average Sale Amount =
      $303.46                                        (intercept)
    + $66.98  x  Average Number of Products Purchased
    + $281.84  if  Loyalty Club and Credit Card
    - $149.36  if  Loyalty Club Only
    - $245.42  if  Store Mailing List
    +   $0.00  if  Credit Card Only                  (reference level)
```

### Interpretation

| Term | Business reading |
|---|---|
| $66.98 per product | Each additional product in the average basket is associated with about $67 more per sale |
| +$281.84 | A dual-relationship customer is associated with $282 more per sale than a credit-card-only customer |
| -$149.36 | Loyalty membership alone is associated with $149 *less* per sale — membership by itself is not a value marker |
| -$245.42 | Store-list customers spend least even after accounting for basket size |

These are associations, not causal effects. Moving a customer between segments
would not automatically change their basket.

Detail: [`../notebooks/02_predictive_model.ipynb`](../notebooks/02_predictive_model.ipynb).

---

## 11. Model Validation

| Metric | Fitted (n=2,375) | Held-out test (n=594) |
|---|---|---|
| R-squared | 0.8369 | 0.8316 |
| MAE | $93.07 | $93.40 |
| RMSE | $137.34 | $140.19 |

5-fold cross-validated R-squared: **0.8351 (std 0.0145)**.

### What R-squared means here

The model explains approximately **84% of the variation** in average sale amount
across the customers evaluated. **This is not an accuracy rate.** It does not mean
predictions are correct 84% of the time, nor that individual predictions fall
within 16% of the truth. R-squared compares the model's errors against the errors
you would make by predicting the overall mean for everyone.

The figure that describes individual reliability is MAE: a typical prediction is
off by about **$93** on a mean predicted sale of $553, roughly 17% in either
direction. RMSE exceeding MAE indicates a minority of large errors, consistent
with the high-value outliers identified in EDA.

### Generalisation

Train and test R-squared differ by less than one point and cross-validation folds
cluster tightly. **The model is not overfitting.**

### Residual diagnostics

Residuals centre on zero with no systematic bias, which is what makes the
campaign-level total trustworthy. Two departures from ideal behaviour: spread
widens at higher predicted values, and the tails are heavier than normal. Both
reflect the retained high-value outliers. The model under-predicts the highest
spenders, making the forecast conservative at the top of the range.

**Why aggregate error is acceptable here.** The forecast is a sum across 250
customers, not 250 individual promises. Opposing errors offset. The same error
structure would be unacceptable if the campaign selected a small number of
customers for expensive individual treatment.

### Benchmark against alternatives

| Model | Test R-squared | Test MAE |
|---|---|---|
| Linear Regression (baseline) | 0.832 | $93.40 |
| Decision Tree (depth 5) | 0.879 | $79.13 |
| Random Forest (200 trees) | 0.879 | $78.76 |

The flexible models do perform better. **The linear model was retained anyway**,
for three reasons: the improvement is worth about $1,875 of gross profit against
an expected net profit of $21,987; it is smaller than the swing from a five-point
change in the margin assumption; and the interpretability feeds list-building and
segment strategy in a way a feature-importance score does not.

This trade-off should be revisited if the model moves into automated per-customer
targeting at scale.

---

## 12. Campaign Economics

### Formulas

```
Expected Revenue (customer) = Predicted Sale Amount x P(response)
Gross Profit     (customer) = Expected Revenue x Gross Margin
Net Profit       (customer) = Gross Profit - Cost per Catalog
Campaign Cost               = Number of Catalogs x Cost per Catalog
Campaign ROI                = Net Profit / Campaign Cost
```

### Assumptions applied

| Assumption | Value | ID |
|---|---|---|
| Cost per catalog | $6.50 | A-01 |
| Gross margin | 50% | A-02 |
| Response probability | Supplied `Score_Yes`, mean 34.1% | A-05 |

### Results

| Measure | Value |
|---|---|
| Customers mailed | 250 |
| Sum of predicted sale amounts | $138,292.13 |
| Average response probability | 34.1% |
| Expected revenue | $47,224.87 |
| Gross profit (50%) | $23,612.44 |
| Campaign cost | $1,625.00 |
| **Expected net profit** | **$21,987.44** |
| Campaign ROI | 13.53x (1,353%) |
| Revenue per customer mailed | $188.90 |
| Net profit per customer mailed | $87.95 |

### Validation against the source project

The original *Predicting Catalog Demand* analysis reported predicted average
sales of $138,292.13, predicted revenue of $47,224.87 and predicted profit of
$21,987.44. Because the underlying datasets were available, all three were
**independently recomputed** rather than quoted. All three reproduce to within
rounding.

### Every prospect pays for itself

At the average response probability, a catalog breaks even at a predicted sale of
**$38.16**. The lowest predicted sale on the list is **$125.02**. **No prospect on
this list destroys value**, so there is no case for trimming the tail.

### Value by segment

| Segment | Prospects | Expected revenue | Net profit | ROI |
|---|---|---|---|---|
| Credit Card Only | 82 | $19,076.83 | $9,005.42 | 16.9x |
| Loyalty Club Only | 122 | $17,285.48 | $7,849.74 | 9.9x |
| Loyalty Club and Credit Card | 26 | $9,543.21 | $4,602.61 | 27.2x |
| Store Mailing List | 20 | $1,319.35 | $529.68 | 4.1x |

Volume and efficiency diverge. Credit Card Only contributes the most total profit
because it is a large slice of the list. Loyalty Club and Credit Card is by far
the most efficient — 10% of the list producing 21% of the profit at 27.2x return.
Store Mailing List remains profitable at 4.1x but is the obvious first cut if
budget is constrained.

**Strategic implication:** the highest-return lever is not better targeting within
this list. It is growing the dual-relationship segment.

Detail: [`../notebooks/03_campaign_profitability.ipynb`](../notebooks/03_campaign_profitability.ipynb).

---

## 13. Customer Prioritisation

### Threshold logic

Arbitrary cut-offs go stale as soon as the model or assumptions change. Tiers are
derived from the profit distribution itself (BRule-08):

| Tier | Rule |
|---|---|
| **Low** | Expected net profit at or below zero — the catalog does not pay for itself |
| **High** | Profitable and at or above the 75th percentile of profitable customers |
| **Medium** | Profitable, below the 75th percentile |

### Results

| Tier | Customers | Expected revenue | Net profit | ROI | Share of profit |
|---|---|---|---|---|---|
| High (≥ $111.99) | 63 | $24,310.59 | $11,745.79 | 28.7x | 53.4% |
| Medium | 187 | $22,914.28 | $10,241.64 | 8.4x | 46.6% |
| Low | 0 | — | — | — | — |

**63 prospects — 25% of the list — carry 53% of the expected profit.**

No prospect falls into the Low tier. The tier is retained in the framework rather
than removed, because the rule must still work on a future list that does contain
value-destroying names.

### Profit concentration

| Top n% of ranked prospects | Share of expected profit |
|---|---|
| 10% | 29.6% |
| 25% | 52.9% |
| 50% | 77.6% |
| Bottom 25% | 7.4% |

If the budget were halved, mailing the top 125 names retains roughly
three-quarters of the profit at half the cost — higher ROI, lower absolute return.
Cuts should be made from the bottom of the ranking, never by segment convenience.

### Why ranking on a single input would be wrong

The most valuable prospects are neither the highest predicted spenders nor the
most likely responders, but those where both are reasonably high. A prospect with
a $2,000 predicted sale at 18% response probability is worth less than one with an
$800 sale at 70%. Only the product identifies the right targets.

---

## 14. Sensitivity Analysis

Eighty scenarios across gross margin (40%-60%), catalog cost ($5-$10) and
response level (60%-120% of modelled).

### Break-even points

| Assumption | Base case | Break-even |
|---|---|---|
| Response level | 100% of modelled | 6.9% of modelled (~2.3% campaign response rate) |
| Gross margin | 50% | ~3.44% |
| Cost per catalog | $6.50 | ~$94.45 |
| Average predicted sale | $553.17 | $38.06 |

### Margin vs cost (response held at modelled level)

| Gross margin \ Cost | $5.00 | $6.50 | $8.00 | $10.00 |
|---|---|---|---|---|
| 40% | $17,640 | $17,265 | $16,890 | $16,390 |
| 45% | $20,001 | $19,626 | $19,251 | $18,751 |
| **50%** | $22,362 | **$21,987** | $21,612 | $21,112 |
| 55% | $24,724 | $24,349 | $23,974 | $23,474 |
| 60% | $27,085 | $26,710 | $26,335 | $25,835 |

*Only the 50% / $6.50 cell is the base case. All others are hypothetical.*

Gross margin matters roughly **seven times more** than catalog cost — a $9,400
swing against $1,250. Effort belongs with Finance confirming the margin, not with
renegotiating print costs.

### Response scenarios (margin 50%, cost $6.50)

| Scenario | Expected revenue | Net profit | ROI |
|---|---|---|---|
| 60% of modelled | $28,334.92 | $12,542.46 | 7.7x |
| 80% of modelled | $37,779.90 | $17,264.95 | 10.6x |
| **100% — base case** | **$47,224.87** | **$21,987.44** | **13.5x** |
| 120% of modelled | $55,890.15 | $26,320.07 | 16.2x |

### Combined downside

| Scenario | Response | Margin | Cost | Net profit | ROI |
|---|---|---|---|---|---|
| Best case | 120% | 60% | $5.00 | $32,284 | 25.8x |
| **Base case** | **100%** | **50%** | **$6.50** | **$21,987** | **13.5x** |
| Mild downside | 80% | 45% | $8.00 | $15,001 | 7.5x |
| Severe downside | 60% | 40% | $10.00 | $8,834 | 3.5x |

**Every one of the 80 scenarios is profitable.**

### What the grid cannot test

Sensitivity varies the assumptions. It cannot test non-incrementality (whether
orders would have occurred anyway) or a structural break in customer behaviour.
Those are the two ways this recommendation could still be wrong.

Detail: [`../notebooks/04_sensitivity_analysis.ipynb`](../notebooks/04_sensitivity_analysis.ipynb).

---

## 15. Risks

Twelve risks are registered. The three with greatest exposure:

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **R-02 Response probabilities are wrong.** Supplied by a model that cannot be validated here. | High | Medium | Stress-tested across 60%-120%; break-even published; measured after launch (M-01) |
| **R-10 Non-incremental revenue.** Orders would have occurred anyway. | High | Medium | Acknowledged as A-08; randomised holdout recommended for the next campaign |
| **R-09 Insufficient tracking.** Orders cannot be attributed to the catalog. | High | Medium | Attribution agreed as a go/no-go gate in Phase 3 |

Full register: [`../docs/risks_and_mitigations.md`](../docs/risks_and_mitigations.md).

---

## 16. Limitations

Stated plainly, because a recommendation is only as good as its declared weaknesses.

1. **Only two predictors were available.** No recency, frequency, product category, channel or seasonality data exists. About 16% of the variation in spend is unexplained by anything available.
2. **The response model is a black box.** `Score_Yes` drives half the expected-revenue calculation and its methodology cannot be inspected.
3. **Incrementality is untestable with this design.** No control group exists, so true causal lift cannot be separated from orders that would have happened anyway.
4. **The model under-predicts high-value customers.** Linear fit pulls extremes toward the centre; the most profitable prospects are likely worth more than stated.
5. **Population mismatch.** The mailing list skews towards segments that are a smaller share of the training data; the dual-relationship coefficient rests on 194 records.
6. **Coefficients are associations, not levers.** Moving a customer between segments would not add $282 to their basket.
7. **Part of the fit is arithmetic.** Products purchased and sale amount are both averages over the same history.
8. **No timestamps.** The age of the training data is unknown, so drift cannot be assessed against elapsed time.
9. **Single geography.** `State` is effectively constant; findings should not be generalised to other markets.
10. **Single-campaign horizon.** No customer lifetime value is modelled, so a campaign that acquires long-term customers is undervalued.

---

## 17. Recommendation

**Proceed with the campaign and mail all 250 catalogs**, conditional on:

| # | Condition | Owner |
|---|---|---|
| 1 | Confirm the blended gross margin is approximately 50% | Finance Manager |
| 2 | Confirm the current per-unit print and distribution cost | Marketing Operations |
| 3 | **Agree response attribution and the measurement window before mailing** | Marketing Operations |

Condition 3 is a hard gate. Without attribution the campaign may make money, but
the organisation will learn nothing and the next decision will be made just as
blind.

### Supporting recommendations

- **Mail the full list**, since every prospect is profitable and trimming reduces total profit.
- **If budget is cut, mail in descending expected-profit order.** Cut from the bottom, never by segment convenience.
- **Treat the dual-relationship segment as the priority for growth** — 27.2x return against 4.1x for store-list customers.
- **Build a randomised holdout into the next campaign** to settle the incrementality question.
- **Obtain documentation for the response-scoring model** so A-05 can be validated rather than stress-tested.
- **Apply a contact-frequency cap outside the model**, since it will rank the same customers first every time.

Full detail: [`../docs/recommendations.md`](../docs/recommendations.md).

---

## 18. Implementation Plan

Eight phases from data preparation through to future campaign optimisation, with
responsible roles at each stage. The critical gate is Phase 3, where response
attribution must be tested end to end before catalogs are released.

Phase 7 contains the sharpest test of whether this analysis was worth doing:
**if the High-priority tier does not outperform the Medium tier on response and
profit, the prioritisation added no value** and the ranking approach must be
reconsidered.

Full plan: [`../docs/implementation_plan.md`](../docs/implementation_plan.md).

---

## 19. Monitoring KPIs

| ID | KPI | Compare against |
|---|---|---|
| M-01 | Actual response rate | 34.1% |
| M-02 | Actual average order value | $553.17 predicted mean |
| M-03 | Actual campaign revenue | $47,224.87 |
| M-04 | Actual campaign cost | $1,625.00 |
| M-05 | Realised gross margin | 50% assumption |
| M-06 | Actual net profit | $21,987.44 |
| M-07 | Actual ROI | 13.53x |
| M-08 | Forecast error (MAE) | $93.40 held-out MAE |
| M-09 | Response rate by priority tier | High should beat Medium |
| M-10 | Profit by segment | `outputs/segment_summary.csv` |
| M-11 | Opt-out / complaint rate | Watch for contact fatigue |

Full definitions: [`../docs/kpi_framework.md`](../docs/kpi_framework.md).

---

## 20. Conclusion

The campaign is expected to return **$21,987 of net profit on $1,625 of spend**,
a 13.5x return. Every prospect on the list is individually profitable, and the
conclusion survives every downside scenario the available data supports —
including response 40% below forecast combined with an adverse margin and an
inflated catalog cost.

Two questions remain open, and both are stated rather than glossed over. The
response probabilities come from a model that could not be validated here, and
incrementality cannot be measured without a control group. Neither undermines the
recommendation at the margins involved, but both should be closed before the next
campaign — the first by obtaining documentation, the second by holding back a
randomised group.

The analysis also produces a finding beyond the immediate decision: customer value
is driven by relationship depth, not tenure, and the dual-relationship segment
returns nearly seven times what the store-mailing-list segment does. **The highest
-return action available is not optimising this campaign. It is growing that
segment.**
