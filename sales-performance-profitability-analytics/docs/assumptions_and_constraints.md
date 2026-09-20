# Assumptions and Constraints

## Hard constraints imposed by the data

1. **No unit-cost or cost-of-goods column exists.** The dataset provides
   `sales` (line-item revenue) and `profit` (line-item profit) directly,
   but no per-unit price or cost basis. Every "margin" figure in this
   project is therefore `profit / sales` (a **revenue-based margin**), and
   this is never confused with or presented as a cost-based margin. This
   also means gross-margin-style analysis (e.g. "how much did we mark this
   product up?") is not possible with this dataset.

2. **No marketing spend, acquisition channel, or campaign data exists.**
   Any statement about *why* revenue grew or a customer converted is out of
   scope -- this dataset only shows what was sold, not what drove the sale.

3. **No inventory or stock-level data exists.** "Weak performance" for a
   product in this project always means weak *revenue or profit*, never
   weak sell-through rate against available stock (which isn't knowable
   from this data).

4. **Customer identity is limited to a `customer_id`, `customer_name`,
   `segment`, and derived order history.** There is no demographic,
   loyalty-program, or lifetime-value-beyond-this-dataset information.
   "Customer Lifetime Value" as a formal metric is not calculated in this
   project, since it usually requires assumptions (retention curves,
   discount rates) this dataset can't support with real data -- calculating
   it would mean fabricating an input, which this project's ground rules
   explicitly prohibit.

## Definitions adopted (and why)

- **Repeat customer** = a `customer_id` with more than one distinct
  `order_id` in the dataset. This is the only defensible definition given
  the columns available; it is a *dataset-lifetime* rate, not a rolling
  12-month rate, because the analysis doesn't have a "today" to roll from
  other than the dataset's own date range.
- **Average Order Value (AOV)** = total revenue / total distinct orders,
  computed by first summing revenue within each `order_id`, then averaging
  across orders. This is the order-grain definition, not the line-item-grain
  average.
- **Profit Margin** = total profit / total revenue, always. Never a
  cost-based calculation (see constraint #1).

## Interpretive cautions (see also `docs/findings.md`)

- **Discount vs. margin is a correlation, not a proven causal
  relationship.** A strong negative correlation (-0.865) exists between
  discount rate and profit margin, but discounts may be applied
  selectively to products that were already low-margin or slow-moving --
  which would produce the same statistical pattern without discounting
  itself being the cause. Every place this relationship is mentioned in
  this project explicitly says "association, not causation."
- **The dataset's date range (2023-2026) extends beyond the analysis's
  reference date.** All 4 calendar years have complete 12-month data, so
  year-over-year growth figures compare whole years to whole years and are
  not distorted by an in-progress final year.
- **"Repeat customer rate" of 98.5% should not be read as a strong loyalty
  signal on its own.** Over a ~4-year window, most active customers will
  naturally place more than one order; this figure says more about the
  time horizon than about loyalty-program effectiveness.

## What this project deliberately does NOT do

- Does not claim this is a real company or real business results.
- Does not fabricate a percentage, dollar figure, or trend that wasn't
  actually calculated from the data (every number with a specific value
  anywhere in `docs/`, `reports/`, or `README.md` was computed in
  `run_analysis.py`, a notebook, or a SQL query, and can be reproduced).
- Does not claim a production deployment, a live dashboard connection, or
  business impact for a company that doesn't exist.
- Does not expose customer names, cities, states, postal codes, or exact
  addresses in any file intended for the public repository.
