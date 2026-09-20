# Findings

Every finding below cites the exact SQL file, notebook, or output table
where the number was calculated. No figure here was estimated or invented.

---

### Finding 1: Overall business performance is healthy and growing

**Evidence:** Total revenue $2,326,534.35, total profit $292,296.81, overall
profit margin 12.56%, across 5,111 orders and 804 customers
(`sql/02_core_kpis.sql`). Revenue grew year-over-year in 3 of the last 4
years: 2024 -4.26%, 2025 +29.80%, 2026 +21.44%
(`sql/03_time_series_analysis.sql`).

**Business meaning:** The business is on a growth trajectory, with the
2024 dip being the only interruption in an otherwise accelerating trend.

---

### Finding 2: Furniture drives significant revenue but very little profit

**Evidence:** Category performance (`sql/04_product_analysis.sql`):

| Category | Revenue | Profit | Margin |
|---|---|---|---|
| Technology | $839,893.28 | $146,543.38 | 17.4% |
| Furniture | $754,747.76 | $19,729.996 | **2.6%** |
| Office Supplies | $731,893.31 | $126,023.44 | 17.2% |

**Business meaning:** Furniture is almost as large as the other two
categories by revenue but generates roughly one-seventh their profit. This
is a margin problem within Furniture, not a demand problem -- customers are
buying it; the business isn't keeping much of what they pay.

---

### Finding 3: Discount levels above ~20% are strongly associated with negative margins

**Evidence:** Margin by discount bucket (`sql/07_discount_profitability.sql`):

| Discount | Margin |
|---|---|
| 0% | 29.6% |
| 0-10% | 16.6% |
| 10-20% | 11.5% |
| 20-30% | **-10.1%** |
| 30-40% | -19.4% |
| 40-50% | -35.7% |
| 50%+ | -118.7% |

Correlation between discount rate and line-item margin: **-0.865**.

**Business meaning:** There's a threshold effect, not a gradual decline --
margin stays positive through 20% discount and turns negative at every
level beyond that. Office Supplies shows the widest full-price-to-deep-discount
margin swing (36.8% at 0% discount vs. -121.6% above 30%).

**Observed association; causation is not established.** Discounts may be
applied selectively to already-low-margin or slow-moving products, which
would produce this same pattern without discounting itself causing the
margin loss. This project's data does not include the information needed
(e.g. discount approval reason, inventory age) to distinguish these
explanations.

---

### Finding 4: Revenue rank and profit rank frequently diverge

**Evidence:**
- The single highest-revenue customer (`SM-20320`, $25,043.05) is
  **unprofitable overall** (-$1,980.74 profit) (`sql/05_customer_analysis.sql`).
- The #3 product by revenue (Cisco TelePresence System EX90 Videoconferencing
  Unit, $22,638.48) has a **-8.0% margin** (`sql/04_product_analysis.sql`).
- Texas is the **3rd-highest-revenue state** ($170,188.05) and
  simultaneously the **single largest loss-making state** in the entire
  dataset (-$25,729.36) (`sql/06_regional_analysis.sql`).

**Business meaning:** Any decision-making process that ranks customers,
products, or regions by revenue alone will systematically misidentify
priorities. Profit-aware ranking is necessary at every level of this
business.

---

### Finding 5: Three sub-categories are net loss-making

**Evidence:** Sub-category margins (`sql/04_product_analysis.sql`,
`outputs/tables/subcategory_summary.csv`):

| Sub-Category | Revenue | Profit | Margin |
|---|---|---|---|
| Tables | $208,020.18 | -$17,753.21 | **-8.5%** |
| Bookcases | $115,361.20 | -$3,632.07 | -3.1% |
| Supplies | $46,725.50 | -$1,171.39 | -2.5% |

**Business meaning:** Tables is the clear outlier -- it loses money at
meaningful scale ($208K in revenue, an 8.5% loss rate), while Bookcases and
Supplies are smaller, marginal losses.

---

### Finding 6: Customer revenue is only moderately concentrated

**Evidence:** The top 10% of customers by revenue (~80 of 804) generate
31.13% of total revenue (`sql/05_customer_analysis.sql`, NTILE window
function).

**Business meaning:** Growth is broad-based rather than dependent on a
handful of large accounts -- there is no single "whale" customer whose
loss would be catastrophic (the top customer is, in fact, unprofitable --
see Finding 4).

---

### Finding 7: The Consumer segment drives the most revenue but has the lowest margin

**Evidence:** Segment performance (`sql/05_customer_analysis.sql`):

| Segment | Revenue | Profit | Margin |
|---|---|---|---|
| Consumer | $1,170,659.79 | $136,371.45 | 11.65% |
| Corporate | $715,806.13 | $94,249.64 | 13.17% |
| Home Office | $440,068.43 | $61,675.73 | **14.02%** |

**Business meaning:** Home Office is the smallest segment by revenue but
the most efficient per dollar sold. Consumer's scale advantage comes with a
margin cost.

---

### Finding 8: The repeat customer rate is very high, but the metric needs context

**Evidence:** 98.51% of customers placed more than one order across the
dataset's ~4-year span (`sql/02_core_kpis.sql`). Only 12 of 804 customers
placed exactly one order.

**Business meaning:** This figure is a *dataset-lifetime* rate, not a
rolling 12-month loyalty rate -- over a 4-year window, most active
customers will naturally order more than once. It should not be presented
to stakeholders as a "98.5% loyalty rate" without that caveat (see
`docs/assumptions_and_constraints.md`).
