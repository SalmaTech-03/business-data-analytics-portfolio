# Interview Preparation — Questions & Answers

All figures quoted below were independently reproduced from the supplied datasets
(`data/raw/p1-customers.xlsx`, `data/raw/p1-mailinglist.xlsx`) by `run_analysis.py`.
Nothing here is estimated or invented. Where a number is an *assumption* rather than a
result, it is labelled as such.

---

### 1. What business problem were you solving?

A company held a mailing list of 250 prospective customers and had to decide whether to
spend money printing and posting a catalog to them. Each catalog costs **$6.50** (a given
business assumption), so the campaign has a known, certain cost of **$1,625.00** and an
uncertain return. Management needed a defensible answer to one question: *is this campaign
expected to make money, and if we run it, who should we prioritise?*

The analysis answers that with a predicted campaign revenue of **$47,224.87**, gross profit
of **$23,612.44** at the stated 50% margin, and net profit of **$21,987.44** — an ROI of
about **13.5x** on catalog spend.

### 2. Why was this a Business Analyst problem rather than a data science problem?

Because the model is the smallest part of the work. The decision required: framing the
question in financial terms, identifying stakeholders and what each needed, writing down
the assumptions that drive the answer (margin, cost per catalog, response behaviour),
defining the KPIs that would later tell us whether the campaign worked, building a decision
rule management could apply, and stress-testing the conclusion against assumptions that
could plausibly be wrong.

The regression is a single, deliberately simple component. Had I handed over only a model
output, management would still not have had a decision. What they needed was the economics
around it and an honest account of where it could break.

### 3. Who were the stakeholders?

Generic roles, since this is a portfolio reconstruction and I won't invent a company:

- **Marketing Manager** — owns the campaign, needs the target list and priority tiers.
- **Finance Manager** — owns the margin and cost assumptions, needs the profit case and the
  sensitivity analysis before releasing budget.
- **Sales / Customer Management** — sanity-checks whether the segment patterns match what
  they see in the field.
- **Marketing Operations** — executes print and distribution, and must capture response data
  at customer level or none of the post-campaign KPIs can be measured.
- **Senior Management** — approves or rejects, and cares about the downside case more than
  the point estimate.

Full analysis in `docs/stakeholder_analysis.md`.

### 4. What were the business requirements?

Fifteen, documented in `docs/business_requirements.md` with rationale, priority and
acceptance criteria. The core ones: determine whether net profit is expected to be positive
(BR-001), estimate campaign revenue (BR-002), compute campaign cost (BR-003), derive gross
profit from the margin assumption (BR-004), identify the characteristics associated with
higher average sales (BR-005), rank customers by expected economic value (BR-006), and
deliver a decision-support summary management can act on without reading code (BR-007).

Each requirement traces forward to a functional requirement and to the artefact that
satisfies it.

### 5. Why did you choose linear regression?

Three reasons, in order of importance:

1. **Explainability.** The coefficients are the business story. Each additional product
   historically purchased is associated with about **+$66.98** in average sale amount, and
   segment membership shifts the baseline by a stated dollar amount. A Marketing Manager can
   act on that. A tree ensemble's feature importances do not tell you *how much* or *in which
   direction*.
2. **Adequate fit.** It explains ~84% of variance, and the relationship between products
   purchased and sale amount is close to linear (correlation 0.856).
3. **Sample size and risk.** The decision hinges on aggregate campaign profit, not on
   individual precision. A simpler model with fewer ways to fail was the right trade.

I did test alternatives honestly: a depth-5 decision tree and a 200-tree random forest both
reached test R² ≈ 0.879 versus 0.832 for linear, with MAE around $79 versus $93. So the
linear model is *not* the most accurate — I retained it deliberately and documented the
trade-off rather than hiding it. If the goal shifted from explanation to per-customer
scoring at scale, I would revisit that choice.

### 6. Why was average sale amount the target?

Because it is the variable that converts directly into money. Revenue per targeted customer
is predicted sale amount × probability of response; multiply by the margin and you have
gross profit. Predicting response alone would tell you *who* buys but not *how much*, and the
segment data shows those are very different questions — the highest-responding group is not
the highest-spending group.

### 7. How did you select features?

From a candidate set of eleven columns, I used two predictors: average number of products
purchased and customer segment (one-hot encoded, with *Credit Card Only* as the reference
level).

Excluded, with reasons:
- **Customer ID, Address, City, ZIP, Store Number** — identifiers or location fields with no
  causal business rationale; ZIP as a numeric would be meaningless and as a categorical would
  be high-cardinality noise on 2,375 rows.
- **Years as customer** — correlation with sale amount is **0.030**, essentially none.
- **Responded to last catalog** — see question 20; it is confounded and I judged it unsafe.

So: business rationale first, then statistical confirmation, not the reverse.

### 8. What does R² = 0.84 mean?

That the model accounts for approximately **84% of the variance in average sale amount**
across the evaluated data — the remaining ~16% is variation the two predictors do not
capture. It is a measure of explained variation, not of correctness.

Concretely, alongside R² = 0.837 in-sample, the mean absolute error is **$93.07**. On a mean
predicted sale of about $553, that is real, material per-customer error. Validation held up:
a 25% hold-out gave test R² **0.832** and MAE **$93.40**, and 5-fold cross-validation gave
**0.835 ± 0.015**, so the fit is stable rather than a lucky split.

### 9. Why shouldn't R² be called "accuracy"?

Because accuracy is a classification concept — the proportion of correct predictions — and
this is a continuous prediction where no forecast is ever exactly "correct." Saying "84%
accurate" implies each customer's predicted spend is within some 84% tolerance, which is
false and would badly mislead a finance stakeholder sizing risk.

The honest framing is: the model explains 84% of variance, and typical per-customer error is
about $93. Those two statements together are useful; "84% accurate" is neither true nor
useful.

### 10. How did you calculate expected revenue?

Per customer: predicted average sale amount × probability of response, where the response
probability came from the `Score_Yes` field already present in the mailing list dataset. I
did not invent a probability methodology.

Summed across all 250 customers this gives **$47,224.87**. For context, the raw predicted
sales total (before weighting by response probability) is **$138,292.13**, and the mean
response probability across the list is **34.07%**.

### 11. How did you calculate profit?

Gross profit = expected revenue × 50% margin = **$23,612.44**.
Campaign cost = 250 catalogs × $6.50 = **$1,625.00**.
Net profit = gross profit − campaign cost = **$21,987.44**.
ROI = net profit ÷ campaign cost = **13.53x**.

That works out to **$188.90** revenue and **$87.95** net profit per targeted customer.

### 12. What assumptions did you make?

Ten, all documented in `docs/assumptions_and_constraints.md`. The material ones:

- Gross margin is a uniform 50% across products and segments.
- Catalog cost is $6.50 per unit with no volume breaks.
- The supplied response scores are calibrated probabilities.
- Historical purchase behaviour remains predictive of future behaviour.
- The mailing list is drawn from a comparable population to the training data.

That last one deserves flagging, and I raised it rather than buried it: the segment mix
differs sharply between the two datasets. Store Mailing List is 46.7% of training but only
8.0% of the mailing list, while Loyalty Club Only rises from 24.4% to 48.8%. The mailing list
skews toward higher-value segments, so the model is extrapolating across a different mix
than it learned on.

### 13. What would happen if the catalog cost increased?

Very little, and this is the most reassuring finding in the sensitivity analysis. Cost is
only $1,625 against $23,612 of gross profit. At $10 per catalog instead of $6.50, net profit
falls from $21,987 to roughly **$21,112** — about a 4% reduction. The break-even catalog
cost is approximately **$94.45 per unit**, roughly fourteen times the assumed price.

Catalog cost is simply not a decision-relevant risk here. Response behaviour and margin are.

### 14. What would happen if response rates decreased?

This is the real exposure, because revenue scales linearly with it. Applying multipliers to
the response probabilities:

| Response vs. assumed | Net profit | ROI |
|---|---|---|
| 0.6x | $12,542 | 7.7x |
| 0.8x | $17,265 | 10.6x |
| 1.0x (base) | $21,987 | 13.5x |
| 1.2x | $26,320 | 16.2x |

The campaign breaks even at roughly **6.9% of the assumed response level** — about a 2.34%
average response rate. Even the severe combined scenario (0.6x response, 40% margin, $10
catalogs) still returns **$8,834** net profit at 3.5x ROI. Across all 80 scenarios tested,
none turned negative. That robustness, not the headline $21,987, is what actually justifies
approving the campaign.

### 15. What were the biggest risks?

From the register in `docs/risks_and_mitigations.md`:

- **Response scores may not be calibrated probabilities.** Everything in the revenue
  calculation rests on them, and their provenance is undocumented.
- **Population shift** between training and mailing list (the segment mix issue above).
- **Margin assumption** — a uniform 50% is a simplification; the mix of products actually
  sold could move it.
- **Per-customer error** of ~$93 MAE, which makes individual prioritisation noisier than the
  aggregate forecast.
- **No response tracking** — if Marketing Operations cannot capture responses at customer
  level, none of the monitoring KPIs can be measured and the next campaign is no better
  informed than this one.

### 16. What would you improve with more data?

- **Product and category-level margins**, to replace the flat 50% assumption — the single
  highest-leverage improvement.
- **Multiple historical campaigns**, enabling a properly fitted response model rather than
  relying on supplied scores, and enabling holdout control groups to measure incremental
  rather than gross response.
- **Recency and frequency fields.** "Years as customer" carries no signal (r = 0.030), but
  recency almost certainly would.
- **Cost of goods per order**, to move from expected profit to true contribution.

### 17. How would you present this to a non-technical manager?

One number first, then the condition, then the risk. "We expect about $22,000 of net profit
on $1,625 of spend. That holds as long as the response estimates are roughly right. Even if
they're 40% worse than assumed and margins fall to 40%, we still make about $8,800."

Then the targeting: 63 customers account for **53.4%** of expected profit, so if budget is
constrained, that is where it goes. Then, honestly, the caveat — the mailing list is skewed
toward better segments than the data the model learned from, so I'd treat the forecast as
directionally sound rather than precise.

No coefficients, no R², unless asked. `reports/executive_summary.md` is written this way.

### 18. What KPIs would you monitor after launch?

Eleven monitoring measures are defined in `docs/kpi_framework.md`. The ones I would put on a
one-page weekly review: actual response rate versus the 34.07% assumed, actual average order
value versus the $553 predicted mean, realised gross margin versus 50%, actual net profit
versus $21,987, and forecast error by segment and by priority tier.

That last one matters most for the *next* campaign: if the High tier does not outperform
Medium, the prioritisation logic is not earning its keep and should be rebuilt.

### 19. What would make you change the recommendation?

Concretely: evidence that the response scores are not calibrated (that would invalidate the
revenue basis entirely, not just scale it); a realised gross margin below about **3.4%**,
which is the mathematical break-even; confirmation that the mailing list population differs
from training in ways beyond segment mix; or a discovery that the 250 contacts were
pre-filtered in a way that makes them unrepresentative.

Note what does *not* change it: moderate cost increases, and response rates anywhere above
about 7% of the assumed level. I'd rather state the conditions under which I'd be wrong than
present a single number as certainty.

### 20. What would you do differently as a Business Analyst?

Three things.

First, I would have interrogated the response variable earlier. Prior responders average
**$156.40** per sale versus **$418.66** for non-responders — the opposite of what anyone
expects. It is a confound: responders are concentrated in the low-value Store Mailing List
segment. A less careful analysis would have either used that feature naively or reported
"responders spend less" as a finding. It is a reminder to check segment composition before
trusting a cross-tab.

Second, I would have pushed for the incrementality question up front. This analysis measures
expected gross response, not lift over doing nothing — some of those customers would have
purchased anyway. A holdout control group costs almost nothing to design in advance and is
impossible to reconstruct afterwards.

Third, I would have agreed the measurement plan with Marketing Operations *before* approval,
not after. The value of this project compounds only if the next campaign has better data than
this one did.
