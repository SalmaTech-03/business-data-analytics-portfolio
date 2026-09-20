# Business Recommendations

Each recommendation follows: Finding -> Evidence -> Business Impact ->
Recommended Action -> Expected KPI Impact -> Limitation. See
`docs/findings.md` for the full evidence detail behind each finding
summarized here.

---

## Recommendation 1: Review discount authorization above 20%, starting with Office Supplies

**Finding:** Margin turns negative at discount levels of 20% and above,
and stays increasingly negative through 50%+.

**Evidence:** Margin by discount bucket ranges from +11.5% (10-20%
discount) to -118.7% (50%+ discount); correlation of -0.865 between
discount and margin (`sql/07_discount_profitability.sql`). Office Supplies
shows the widest full-price-to-deep-discount swing (36.8% -> -121.6%).

**Business Impact:** The four discount buckets from 20% upward (20-30%
through 50%+) combine for -$136,020.69 in total losses
(-10,513.45 + -25,477.51 + -22,999.54 + -77,030.19) on $364,760.15 of
revenue in those buckets*.

**Recommended Action:** Introduce a discount-approval threshold at 20% --
discounts above that level should require explicit sign-off, starting with
Office Supplies given its widest margin swing.

**Expected KPI Impact:** Overall Profit Margin (currently 12.56%);
Category-level margin for Office Supplies specifically.

**Limitation:** **Observed association; causation is not established.**
This dataset cannot distinguish "discounting causes margin loss" from
"already-low-margin or slow-moving products get discounted more" -- both
would produce this exact pattern. Any policy change should be piloted and
measured, not assumed to work based on this correlation alone.

*(Note: the -$136,020.69 figure recomputes the sum of the four negative-margin
buckets' profit directly from `sql/07_discount_profitability.sql`'s
per-bucket results; it is not a new calculation.)*

---

## Recommendation 2: Investigate the Furniture category's cost/pricing structure, starting with Tables

**Finding:** Furniture generates $754,747.76 in revenue (2nd of 3
categories) but only $19,729.996 in profit (2.6% margin, far below
Technology's 17.4% and Office Supplies' 17.2%).

**Evidence:** Category performance table (`sql/04_product_analysis.sql`).
Within Furniture, the Tables sub-category alone is responsible for
-$17,753.21 in losses on $208,020.18 of revenue (-8.5% margin) --
`docs/findings.md` Finding 5.

**Business Impact:** If Furniture's margin matched even the lower of the
other two categories (Office Supplies, 17.2%), it would generate roughly
$129,959 in profit on its current revenue -- about $110,229 more than its
actual current profit of $19,730. This is illustrative math showing the
scale of the gap, not a projection of what's achievable.

**Recommended Action:** Conduct a pricing/discount review specifically for
the Tables sub-category before addressing Furniture broadly -- it is the
single largest driver of the category's weak margin.

**Expected KPI Impact:** Furniture category Profit Margin; Tables
sub-category Profit.

**Limitation:** This dataset has no unit-cost data, so it's not possible
to determine whether Tables' poor margin comes from pricing, shipping
cost, discounting, or product mix -- only that the poor margin exists and
is concentrated there.

---

## Recommendation 3: Build a profit-aware ranking view for customers, products, and states -- not a revenue-only one

**Finding:** Revenue rank and profit rank diverge at every level of this
business.

**Evidence:** The top-revenue customer is unprofitable; a top-3 revenue
product has -8.0% margin; Texas is a top-3 revenue state and the single
largest loss-making state (`docs/findings.md` Finding 4).

**Business Impact:** Any account-management, product-assortment, or
territory-planning decision made from a revenue-only leaderboard risks
prioritizing loss-making entities.

**Recommended Action:** Add profit and margin columns alongside revenue in
every "top N" report management uses (a version of this already exists in
`outputs/tables/customer_summary.csv` and `product_summary.csv`, and is
built into Dashboard Page 3 -- see `dashboard/dashboard_requirements.md`).

**Expected KPI Impact:** No single KPI -- this is a reporting-practice
change intended to prevent future misallocation of attention/incentives.

**Limitation:** This is a process recommendation, not something with a
directly measurable "before/after" KPI in this dataset.

---

## Recommendation 4: Prioritize Texas, Ohio, Pennsylvania, and Illinois for a state-level profitability review

**Finding:** 12 of 59 states/provinces are net loss-making; the four
worst (Texas, Ohio, Pennsylvania, Illinois) combine for -$70,868.58 in
losses despite all four being mid-to-large states by revenue.

**Evidence:** `sql/06_regional_analysis.sql` state-level breakdown.

**Business Impact:** -$70,868.58 in combined losses across 4 states,
concentrated enough to be worth investigating as a group rather than
one-by-one.

**Recommended Action:** Review product mix, discount rates, and shipping
costs specifically in these four states, since they are large enough
(unlike small-loss states like Oregon at -$1,190) for a fix to matter at
the company level.

**Expected KPI Impact:** Central region Profit Margin (currently the
lowest of the 4 regions at 7.92%) and state-level profit for the four
named states.

**Limitation:** State-level loss could stem from many causes not visible
in this dataset (local competition, shipping distance/cost, regional
discount policy) -- this recommendation is "investigate," not "here is the
fix."

---

## Recommendation 5: Treat the 98.51% repeat-customer rate as a baseline, not an achievement, when reporting to stakeholders

**Finding:** 98.51% of customers ordered more than once across the
dataset's ~4-year window.

**Evidence:** `sql/02_core_kpis.sql`.

**Business Impact:** None directly -- this is a communication/reporting
recommendation to prevent an overstated interpretation of the metric.

**Recommended Action:** When this KPI is presented (e.g. on Dashboard Page
3), pair it with the order-frequency distribution
(`sql/05_customer_analysis.sql`) so stakeholders see the full distribution,
not just the headline rate.

**Expected KPI Impact:** None -- this improves how an existing KPI is
communicated, not the KPI's value.

**Limitation:** N/A -- this is a presentation recommendation, not an
analytical claim requiring a caveat beyond what's already stated in
`docs/assumptions_and_constraints.md`.
