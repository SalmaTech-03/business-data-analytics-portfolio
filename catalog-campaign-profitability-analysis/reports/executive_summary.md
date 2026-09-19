# Executive Summary

**Catalog Campaign Profitability & Customer Targeting Analysis**

*Prepared for: Marketing Director, Finance Manager, Senior Management*

---

## The decision

Marketing has a list of **250 prospective customers** and wants to know whether
to send them a catalog. Each catalog costs **$6.50** to print and distribute, so
the campaign commits **$1,625** before a single order arrives.

The question is simple: **does the expected return justify the spend, and if the
budget is tight, who should receive a catalog first?**

---

## What we did

We used the company's existing customer records — 2,375 customers whose spending
is already known — to establish what kinds of customers spend more. We then
applied that pattern to the 250 prospects to estimate what each is likely to
spend, weighted it by how likely they are to respond at all, and worked through
the economics.

Nothing here is a new business theory. It is the company's own purchase history,
applied consistently to a list of names, so the decision rests on evidence
instead of judgement.

---

## What we found

### 1. The campaign is expected to be strongly profitable

| | |
|---|---|
| Expected revenue | **$47,224.87** |
| Less cost of goods (50% margin) | -$23,612.43 |
| Gross profit | **$23,612.44** |
| Less campaign cost (250 x $6.50) | -$1,625.00 |
| **Expected net profit** | **$21,987.44** |
| **Return on campaign spend** | **13.5x** |

Every dollar spent on catalogs is expected to return about **$13.50 in profit**.
The average catalog costs $6.50 and is expected to generate **$188.90 in
revenue**.

### 2. Every single prospect is worth mailing

All 250 names are individually profitable. The least attractive still clears
their own catalog cost by $5.79. **There is no part of this list worth cutting.**

### 3. Value is concentrated, which matters if the budget is cut

The **top 63 prospects — a quarter of the list — account for 53% of the expected
profit**. If the budget were halved, mailing the top 125 names would retain
roughly three-quarters of the profit at half the cost. A ranked list is provided
so cuts can be made from the bottom rather than at random.

### 4. Two things drive customer value

**How many products a customer typically buys**, and **what kind of relationship
they have with the company**. Tenure turns out not to matter at all — long-standing
customers do not spend more per purchase than recent ones.

The relationship effect is large:

| Customer type | Average spend per sale |
|---|---|
| Loyalty club **and** credit card | $1,074 |
| Credit card only | $683 |
| Loyalty club only | $396 |
| Store mailing list only | $157 |

A customer with both a loyalty membership and a store credit card is worth about
**seven times** a store-mailing-list customer. Notably, **loyalty membership on
its own is not a marker of high value** — it is the combination that matters.

### 5. A finding worth knowing before someone suggests it

Customers who responded to the *last* catalog actually spend **less** on average
($156) than those who did not ($419). The instinct to "target our past
responders" would systematically select the lowest-value customers. The effect is
explained by segment mix, not by response behaviour itself.

---

## How confident should you be?

**The estimate is well supported but it is an estimate.**

The model explains about **84% of the variation** in how much customers spend.
That is a good result for two pieces of information about a customer — but it is
**not an accuracy rate**. A typical individual prediction is off by around **$93**
in one direction or the other, on an average predicted sale of $553.

Why that is acceptable here: the campaign forecast is a **total across 250
customers**, and individual errors in opposite directions largely cancel out. The
total is far more reliable than any single customer's prediction.

**More importantly, the decision does not depend on the model being right.** We
tested what happens when the assumptions fail:

| If this happened | Net profit |
|---|---|
| Everything as forecast | $21,987 |
| Response comes in 20% below forecast | $17,265 |
| Response comes in 40% below forecast | $12,542 |
| Margin turns out to be 40% instead of 50% | $17,265 |
| Catalogs cost $10 instead of $6.50 | $21,112 |
| **All three go wrong at once** | **$8,834** |

**The campaign pays under every scenario we could construct.** Response would
have to collapse to about a **2.3% response rate** — roughly one order per 43
catalogs, against a forecast of one in three — before the campaign merely broke
even.

---

## Risks to be aware of

**1. The response estimate is the weakest link.** The probability that each
prospect responds came with the data, produced by a model we do not have access
to and cannot verify. It is the single biggest driver of the revenue figure. The
reassurance is the wide margin for error shown above.

**2. We cannot tell how many of these orders would have happened anyway.**
Some recipients might have bought without the catalog. If so, the campaign's true
incremental profit is lower than the headline figure. **This is the one risk that
could genuinely change the conclusion**, and it cannot be resolved with the
current campaign design — only by holding back a randomised comparison group in a
future campaign.

**3. The prospect list differs from the customers we learned from.** It skews
towards higher-value relationship types. That is sensible for a curated list, but
it means the forecast leans on parts of the pattern supported by less data.

**4. Contact fatigue.** The model will rank the same high-value customers first
in every campaign. Left unchecked, that risks irritating exactly the customers the
business can least afford to lose.

---

## Recommendation

**Proceed with the campaign and mail all 250 catalogs**, subject to three
confirmations before the budget is released:

| # | Confirmation needed | Owner |
|---|---|---|
| 1 | That the blended gross margin on the catalog product mix is close to 50% | Finance Manager |
| 2 | That the current print and postage cost is still $6.50 per unit | Marketing Operations |
| 3 | **That response tracking is in place before catalogs are mailed** | Marketing Operations |

Point 3 is the one to insist on. Without a way to attribute orders back to the
catalog, the campaign may well make money — but the organisation will learn
nothing from it, and the next campaign decision will be made just as blind as this
one was.

---

## What to measure after launch

| Measure | Forecast to compare against |
|---|---|
| Response rate | 34.1% |
| Average order value | $553 |
| Campaign revenue | $47,225 |
| Net profit | $21,987 |
| ROI | 13.5x |
| **Response rate: high-priority vs medium-priority names** | High should beat Medium |
| Opt-out and complaint rate | Watch for contact fatigue |

The second-to-last one is the real test. **If the high-priority group does not
outperform the medium-priority group, the targeting added no value** and the
ranking approach should be reconsidered. That is the honest test of whether this
analysis was worth doing, and it should be run.

---

## Next step

Approve the campaign, confirm the three items above, and schedule a post-campaign
review four weeks after the response window closes.

For the next campaign, hold back a randomised group of comparable customers. The
small amount of forgone profit buys the answer to the one question this analysis
could not settle.

---

*Supporting detail: [`project_report.md`](project_report.md) for the full
analysis; [`../docs/assumptions_and_constraints.md`](../docs/assumptions_and_constraints.md)
for every assumption; [`../docs/risks_and_mitigations.md`](../docs/risks_and_mitigations.md)
for the risk register.*
