# Business Case: Catalog Campaign Profitability & Customer Targeting

## 1. Situation

The company maintains a direct-mail catalog channel. Marketing has assembled a
mailing list of **250 prospective customers** who have not yet received the
current catalog. Producing and distributing each catalog costs **$6.50**, so the
campaign carries a committed cost of **$1,625** before a single order arrives.

Historically the decision to mail has been made on judgement and segment
intuition. Management has asked for a quantified answer before releasing budget.

## 2. Problem

Catalog spend is committed up front and is unrecoverable. Revenue is uncertain
and arrives only from the subset of recipients who respond. Without an estimate
of expected revenue per recipient, the company cannot tell whether the campaign
creates or destroys value, and cannot rank recipients if the budget is capped.

## 3. Business objective

Produce a defensible, repeatable estimate of the campaign's expected net profit
and return on investment, and rank the 250 prospects by expected economic value
so that budget can be allocated to the highest-value recipients first.

## 4. Scope

**In scope**
- Estimating average sale amount for each of the 250 prospects
- Converting predictions into expected revenue, gross profit, cost, net profit and ROI
- Ranking prospects by expected net profit
- Sensitivity of the decision to the gross-margin, catalog-cost and response assumptions
- A management-facing decision recommendation and monitoring plan

**Out of scope**
- Catalog creative, merchandising and page layout decisions
- Channel mix (email, paid digital, in-store) comparison
- Customer lifetime value modelling beyond the single campaign horizon
- Operational print procurement and logistics
- Any production deployment of the model

## 5. Options considered

| Option | Description | Assessment |
|---|---|---|
| A. Do nothing | Skip the campaign | Zero cost, zero incremental revenue. The baseline against which every other option is measured. |
| B. Mail all 250 | Send a catalog to every name on the list | Simplest to execute; tested directly by this analysis. |
| C. Mail a targeted subset | Mail only prospects above an expected-profit threshold | Reduces cost and raises ROI per catalog, but forgoes profitable volume if every recipient is profitable. |
| D. Judgement-based targeting | Continue segment-intuition selection | No quantified expected value; not auditable; not repeatable. |

This analysis evaluates **Option B** as the primary case and provides the
prioritisation needed to execute **Option C** if budget is constrained.

## 6. Expected benefits

- A quantified expected net profit and ROI for the campaign, replacing judgement
- A ranked target list that lets marketing cut the tail first if budget is cut
- An explicit set of assumptions that can be re-tested against actual results
- A reusable scoring pipeline for subsequent catalog campaigns

## 7. Financial summary

Full detail is in [`reports/executive_summary.md`](../reports/executive_summary.md).
All figures below are computed by the code in this repository from the two
supplied datasets, and reproduce the source project's reported results exactly.

| Measure | Value |
|---|---|
| Customers mailed | 250 |
| Sum of predicted average sale amounts | $138,292.13 |
| Expected revenue (response-weighted) | $47,224.87 |
| Gross profit at 50% margin | $23,612.44 |
| Campaign cost (250 x $6.50) | $1,625.00 |
| **Expected net profit** | **$21,987.44** |
| ROI on campaign spend | 13.5x (1,353%) |

## 8. Cost of inaction

Declining the campaign forgoes an estimated $21,987 of gross contribution while
avoiding $1,625 of committed spend. On the modelled assumptions, inaction is the
more expensive option by a wide margin.

## 9. Decision requested

Approve the mailing of all 250 catalogs, subject to the assumption checks and
the post-campaign monitoring plan set out in
[`decision_framework.md`](decision_framework.md) and
[`implementation_plan.md`](implementation_plan.md).
