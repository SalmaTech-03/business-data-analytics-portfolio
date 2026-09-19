# Recommendations

## Primary recommendation

**Proceed with the campaign and mail all 250 catalogs**, conditional on the
three assumption confirmations set out below.

On the stated assumptions the campaign is expected to generate **$47,224.87 in
revenue**, **$23,612.44 in gross profit** against **$1,625 of campaign cost**,
for an **expected net profit of $21,987.44** and an **ROI of 13.5x**.

The recommendation is robust: every one of the 250 prospects is individually
profitable, and the campaign remains profitable under every downside scenario
tested, including the combined case of response at 60% of modelled, a 40% gross
margin and a $10 catalog cost ($8,834 net profit, 3.53x ROI).

## Conditions attached to the recommendation

| # | Condition | Owner | Required before |
|---|---|---|---|
| 1 | Confirm the blended gross margin on the catalog product mix is approximately 50%. | Finance Manager | Budget approval |
| 2 | Confirm the current per-unit print and distribution cost against a live supplier quote. | Marketing Operations | Budget approval |
| 3 | Agree the response-attribution mechanism and the measurement window. | Marketing Operations, Marketing Manager | Mailing |

Condition 3 is a hard gate. Without attribution, the campaign generates revenue
but no learning, and every subsequent campaign decision is made blind.

## Supporting recommendations

### R1 — Mail the full list rather than a targeted subset

The normal reason to target is that some recipients destroy value. Here none do:
the least profitable prospect still returns $5.79 above their catalog cost.
Cutting the bottom of the list would reduce total profit. Targeting becomes
relevant only if the budget is constrained.

### R2 — If the budget is cut, mail in descending expected-profit order

The prioritisation in `outputs/customer_scores.csv` ranks all 250 prospects.
The 63 High-priority prospects account for **$11,746 of expected net profit —
53% of the total from 25% of the catalogs**. Cut from the bottom of the ranking,
never from the middle or by segment convenience.

### R3 — Treat `Loyalty Club and Credit Card` as the priority acquisition segment

That segment averages **$1,116 in predicted sale amount** against $172 for Store
Mailing List, and returns **27.2x ROI** versus 4.1x. It is only 26 of the 250
prospects. Growing this segment is worth more than optimising the mailing list.

### R4 — Build a randomised holdout group into the next campaign

Incrementality is the one assumption that could reverse this conclusion and the
one this analysis cannot test. Withholding a random sample of a few hundred
comparable customers from the next campaign costs a small amount of forgone
profit and converts the largest open question into a measured quantity.

### R5 — Obtain documentation for the response-scoring model

`Score_Yes` drives expected revenue but arrives as a black box. Before the next
campaign, obtain its methodology, training population and calibration so that
assumption A-05 can be validated rather than stress-tested.

### R6 — Apply a contact-frequency cap outside the model

The model will rank the same high-value customers first in every campaign.
Left unchecked, that produces contact fatigue among precisely the customers the
business can least afford to lose. The cap belongs in campaign operations, not
in the scoring logic.

### R7 — Request dated data extracts

Neither source file carries a timestamp, so the age of the training data is
unknown and drift cannot be assessed. Every future extract should carry a
snapshot date.

### R8 — Reconcile the definition of `Years_as_Customer` across systems

The field is an integer in one file and a float on a different scale in the
other. It is excluded from the model for that reason. If tenure genuinely drives
spend, a consistent definition would be worth testing.

## What was deliberately not recommended

- **A more complex model.** A random forest improved held-out R-squared from 0.832 to 0.879 and reduced MAE by about $15 per customer. Against the uncertainty in the response and margin assumptions, that gain is immaterial to the decision, and it costs the interpretability that lets a marketing stakeholder read a coefficient in dollars. The linear model is retained.
- **Excluding high-value outliers.** They are genuine customers in the segment the campaign most wants to reach. Removing them would bias the model against its most valuable targets.
- **A company-specific ROI hurdle.** None was supplied, so none was invented. The decision framework uses an explicitly labelled illustrative figure.
