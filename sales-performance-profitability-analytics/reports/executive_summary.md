# Executive Summary

*Written for a non-technical audience. This project is built on the
public Sample Superstore dataset for portfolio/demonstration purposes --
it is not a real company or real business results.*

## Business Problem

The business had years of raw sales transaction data but no structured way
to answer basic performance questions: which products are actually
profitable, which regions are underperforming, and whether the discount
strategy is helping or hurting the bottom line.

## Dataset

10,194 sales transactions from 2023-2026, covering 804 customers, 1,862
products across 3 categories and 17 sub-categories, in 4 U.S./Canadian
regions.

## Key KPIs

| Metric | Value |
|---|---|
| Total Revenue | $2,326,534.35 |
| Total Profit | $292,296.81 |
| Profit Margin | 12.56% |
| Total Orders | 5,111 |
| Average Order Value | $455.20 |
| Customers | 804 |

## Key Findings

1. **The business is growing** -- revenue is up in 3 of the last 4 years,
   with 2025 and 2026 both showing 20%+ growth.
2. **Furniture sells well but barely makes money** -- it's the
   2nd-largest category by revenue but generates only 2.6% margin, versus
   ~17% for the other two categories.
3. **Deep discounting (20%+) is strongly linked to losses** -- margin
   turns negative at every discount level from 20% up. This is a strong
   pattern, but the analysis can't yet prove discounting *causes* the
   loss versus discounts being applied to already-weak products.
4. **Revenue leaders aren't always profit leaders** -- the top-revenue
   customer, a top-3 product, and a top-3 state are each, individually,
   unprofitable or loss-making. Ranking by revenue alone hides this.

## Business Implications

Decisions based only on revenue -- which customers to prioritize, which
states to expand in, which products to keep pushing -- risk reinforcing
loss-making activity. The business needs profit-aware, not just
revenue-aware, reporting at every level.

## Recommendations

1. Add a discount-approval threshold around 20%, starting with Office
   Supplies.
2. Investigate Furniture's margin problem, especially the Tables
   sub-category.
3. Always report profit alongside revenue in "top customer/product/state"
   views.
4. Review Texas, Ohio, Pennsylvania, and Illinois specifically -- together
   they account for nearly $71K in losses despite being sizeable markets.

(Full detail with evidence for each: `docs/findings.md`,
`docs/recommendations.md`.)

## Limitations

No cost-per-unit data exists, so "margin" here means profit as a share of
revenue, not a true cost-based margin. The discount-profitability link is
a correlation, not proven causation. See
`docs/assumptions_and_constraints.md` for the complete list.

## Next Steps

1. Build the Power BI dashboard from the specification in `dashboard/`.
2. Pilot a discount-approval threshold and measure the actual margin
   impact (moving from correlation to a controlled comparison).
3. Conduct a Furniture-category pricing/cost review.
