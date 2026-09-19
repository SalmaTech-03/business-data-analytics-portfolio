# Assumptions and Constraints

## Assumptions register

Every assumption carries a source, an impact rating and a validation route.
"Source project" means the assumption was stated in the original *Predicting
Catalog Demand* analysis and is carried forward unchanged.

| ID | Assumption | Source | Impact if wrong | Validation route |
|---|---|---|---|---|
| A-01 | Catalog printing and distribution costs **$6.50 per unit**, flat, with no volume tiers or fixed setup fee. | Source project | Low. Cost is a small fraction of gross profit; doubling it to $13 still leaves the campaign strongly profitable. Tested in the sensitivity analysis. | Confirm with Marketing Operations against the current supplier quote before mailing. |
| A-02 | Average **gross margin is 50%** and applies uniformly across all products and customers. | Source project | High. Gross profit scales linearly with this figure. A 40% margin reduces net profit by roughly $4,700. | Finance Manager confirms the blended margin on the catalog product mix. |
| A-03 | `Avg_Sale_Amount` is the correct measure of campaign revenue per responder — that is, a responder's order resembles their historical average purchase. | Source project | Medium. If catalog orders are systematically larger or smaller than a customer's typical purchase, revenue is biased in that direction. | Compare actual campaign order values against predictions after launch (KPI M-02). |
| A-04 | The relationship between customer characteristics and spend observed in the 2,375 historical customers **holds for the 250 prospects**. | Analytical | Medium-high. The mailing list has a materially different segment mix from the training population (see Constraints). | Compare realised sale amounts by segment against predictions after launch. |
| A-05 | The supplied `Score_Yes` values are **valid probabilities of catalog response**. | Supplied with the data | High. This is the most uncertain input in the model and the one whose provenance cannot be checked here. | Stress-tested across 60%-120% of the supplied values. Validate against actual response after launch (M-01). |
| A-06 | Responses are **independent** — one customer's decision does not affect another's. | Analytical | Low. Reasonable for direct mail to individual households. | No practical validation route; accepted. |
| A-07 | All 250 catalogs are **successfully delivered**. No returns, bad addresses or undeliverables. | Analytical | Low. Undeliverables reduce both cost and revenue roughly proportionally, so ROI is largely unaffected. | Address hygiene check before the mail file is released. |
| A-08 | There is **no cannibalisation** — catalog orders are incremental rather than purchases the customer would have made anyway. | Analytical | Medium. If a share of orders would have happened regardless, true incremental profit is lower than forecast. A holdout group is the only clean way to measure this. | Hold out a randomised control group in a future campaign. |
| A-09 | Revenue is recognised **within the campaign measurement window**; no material lag pushes orders outside the tracking period. | Analytical | Low-medium. A lag understates measured performance without changing true value. | Define the response window before launch (see implementation plan, Phase 5). |
| A-10 | One catalog is mailed **per customer**, not per household, so no duplicate mailings occur within a household. | Analytical | Low. Would slightly overstate cost. | Deduplicate on address during mail-file preparation. |

## Constraints

| ID | Constraint | Consequence for the analysis |
|---|---|---|
| C-01 | The mailing list contains exactly **250 prospects**. The campaign cannot be scaled up without a new list. | Campaign cost is capped at $1,625. All totals are fixed to this population. |
| C-02 | `Responded_to_Last_Catalog` exists in the training file but **not** in the mailing list. | Excluded from the feature set (BRule-06), even though it is available historically. |
| C-03 | The model behind `Score_Yes` is **not supplied**. Its methodology, training data and calibration cannot be inspected. | Treated as a given input (A-05) and stress-tested rather than validated. |
| C-04 | The **segment mix of the mailing list differs sharply from the training population**. Store Mailing List is 47% of training customers but only 8% of the mailing list; Credit Card Only is 21% of training but 33% of the list. | The mailing list skews towards higher-value segments. Predictions rely on the model extrapolating a segment balance it was not dominated by. Documented as a limitation. |
| C-05 | `Years_as_Customer` is an **integer in the training file and a float on a different scale in the mailing list**. | Cannot be used as a predictor without reconciling the definitions with the data owner. Excluded. |
| C-06 | No **product-level, order-level or time-series** data is available. Only customer-level aggregates. | Prevents basket analysis, seasonality adjustment and lifetime-value modelling. |
| C-07 | No **control group** exists in this campaign design. | Incrementality (A-08) cannot be measured. Only gross performance can be reported. |
| C-08 | The organisation's **required ROI threshold** is not supplied. | The decision framework uses an explicitly labelled example threshold rather than inventing a company standard. |
| C-09 | The data has **no timestamp**. The recency of the historical customer file is unknown. | Model drift cannot be assessed against elapsed time. Raised as risk R-07. |
| C-10 | `State` is effectively **constant** and `City` values are concentrated in one metropolitan area. | Findings should not be generalised to other geographies without revalidation. |
