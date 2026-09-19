# KPI Framework

Two groups of KPIs. **Forecast KPIs** are produced by this analysis before the
campaign runs. **Monitoring KPIs** are measured after launch and compared back
to the forecast.

All forecast values below are computed by `run_analysis.py` from the supplied
datasets. Monitoring KPIs have no values yet — they are definitions, and the
value column is deliberately empty until actual campaign results exist.

---

## Forecast KPIs

### KPI-01 — Predicted Average Sale Amount

| Field | Detail |
|---|---|
| **Definition** | The model's estimate of the average dollar value of a purchase, for a single prospect. |
| **Formula** | `303.46 + 66.98 x Avg_Num_Products_Purchased + segment adjustment` |
| **Business meaning** | What this customer is worth per purchase occasion if they buy. The building block for every other financial figure. |
| **Data required** | `Avg_Num_Products_Purchased`, `Customer_Segment` |
| **Computed by** | `src/modeling.py::TrainedModel.predict` |
| **Forecast value** | Sum across 250 prospects = **$138,292.13**; mean = $553.17 |
| **Decision relevance** | Drives customer ranking. A customer whose predicted sale amount is too low cannot cover the catalog cost at any plausible response rate. |

### KPI-02 — Expected Response Rate

| Field | Detail |
|---|---|
| **Definition** | The probability-weighted share of recipients expected to place an order. |
| **Formula** | `mean(Score_Yes)` across the mailed population |
| **Business meaning** | How much of the list is expected to convert. |
| **Data required** | `Score_Yes` |
| **Computed by** | `src/profitability.py::campaign_summary` |
| **Forecast value** | **34.1%** (range across individuals: 18.6% to 100.0%) |
| **Decision relevance** | The single most uncertain input. Its provenance is external to this project, so it is stress-tested across a 60%-120% band in the sensitivity analysis. |

### KPI-03 — Expected Revenue

| Field | Detail |
|---|---|
| **Definition** | Revenue the campaign is expected to generate, weighted by each prospect's probability of responding. |
| **Formula** | `sum(Predicted_Sale_Amount x Response_Probability)` |
| **Business meaning** | Gross top-line the campaign should produce. |
| **Data required** | KPI-01, KPI-02 |
| **Computed by** | `src/profitability.py::expected_revenue` |
| **Forecast value** | **$47,224.87** ($188.90 per customer mailed) |
| **Decision relevance** | The top of the profit calculation and the figure Finance will challenge first. |

### KPI-04 — Campaign Cost

| Field | Detail |
|---|---|
| **Definition** | Total printing and distribution cost of the mailing. |
| **Formula** | `Number of Catalogs x Cost per Catalog` |
| **Business meaning** | The committed, unrecoverable spend. |
| **Data required** | Catalog count; unit cost assumption (A-01) |
| **Computed by** | `src/profitability.py::campaign_cost` |
| **Forecast value** | **$1,625.00** (250 x $6.50) |
| **Decision relevance** | The only certain number in the model and the hurdle the campaign must clear. |

### KPI-05 — Gross Profit

| Field | Detail |
|---|---|
| **Definition** | Contribution remaining after cost of goods sold, before campaign cost. |
| **Formula** | `Expected Revenue x Gross Margin` |
| **Business meaning** | The portion of revenue actually available to pay for the campaign. |
| **Data required** | KPI-03; gross-margin assumption (A-02) |
| **Computed by** | `src/profitability.py::gross_profit` |
| **Forecast value** | **$23,612.44** at a 50% margin |
| **Decision relevance** | Using revenue instead of gross profit would overstate campaign value by a factor of two. |

### KPI-06 — Net Campaign Profit

| Field | Detail |
|---|---|
| **Definition** | Gross profit less campaign cost. |
| **Formula** | `Gross Profit - Campaign Cost` |
| **Business meaning** | The value the campaign creates. The primary decision metric. |
| **Data required** | KPI-05, KPI-04 |
| **Computed by** | `src/profitability.py::net_profit` |
| **Forecast value** | **$21,987.44** |
| **Decision relevance** | BR-001 is satisfied if and only if this figure is positive. |

### KPI-07 — ROI

| Field | Detail |
|---|---|
| **Definition** | Return per dollar of campaign spend. |
| **Formula** | `Net Profit / Campaign Cost` |
| **Business meaning** | Lets this campaign be compared against other uses of the same marketing budget. |
| **Data required** | KPI-06, KPI-04 |
| **Computed by** | `src/profitability.py::roi` |
| **Forecast value** | **13.53x (1,353%)** |
| **Decision relevance** | Compared against the organisation's required threshold. No such threshold is supplied with this project; `docs/decision_framework.md` uses an explicitly labelled example. |

### KPI-08 — Average Revenue per Customer

| Field | Detail |
|---|---|
| **Definition** | Expected revenue divided by the number of catalogs mailed. |
| **Formula** | `Expected Revenue / Number of Catalogs` |
| **Business meaning** | Revenue yield of a single catalog. |
| **Data required** | KPI-03, catalog count |
| **Computed by** | `src/profitability.py::campaign_summary` |
| **Forecast value** | **$188.90** |
| **Decision relevance** | Directly comparable to the $6.50 unit cost, which makes the economics legible without any modelling background. |

### KPI-09 — Expected Profit per Customer

| Field | Detail |
|---|---|
| **Definition** | Net profit attributable to a single mailed catalog. |
| **Formula** | `(Predicted Sale Amount x Response Probability x Gross Margin) - Cost per Catalog` |
| **Business meaning** | Whether an individual catalog pays for itself. |
| **Data required** | KPI-01, KPI-02, A-01, A-02 |
| **Computed by** | `src/profitability.py::build_customer_economics` |
| **Forecast value** | **$87.95** on average; every one of the 250 prospects is positive; range $5.79 to $396.16 |
| **Decision relevance** | The ranking variable for the prioritisation framework. |

### KPI-10 — Break-even Response Level

| Field | Detail |
|---|---|
| **Definition** | The fraction of the modelled response level at which net profit falls to exactly zero. |
| **Formula** | `Campaign Cost / Gross Profit` |
| **Business meaning** | How wrong the response assumption can be before the campaign stops creating value. |
| **Data required** | KPI-04, KPI-05 |
| **Computed by** | `src/profitability.py::campaign_summary` |
| **Forecast value** | **0.069** — response would have to collapse to about 6.9% of the modelled level (roughly a 2.3% campaign response rate) before the campaign breaks even |
| **Decision relevance** | The clearest single expression of how much margin for error the decision carries. |

---

## Monitoring KPIs (measured after launch)

| ID | KPI | Formula | Owner | Data source | Target / comparison |
|---|---|---|---|---|---|
| M-01 | Actual response rate | Responders / catalogs mailed | Marketing Operations | Order system, campaign code | Compare to 34.1% forecast |
| M-02 | Actual average order value | Campaign revenue / responders | Finance Manager | Order system | Compare to $553.17 predicted mean |
| M-03 | Actual campaign revenue | Sum of attributed orders | Finance Manager | Order system | Compare to $47,224.87 |
| M-04 | Actual campaign cost | Invoiced print plus postage | Marketing Operations | Supplier invoice | Compare to $1,625.00 |
| M-05 | Actual gross margin realised | (Revenue - COGS) / Revenue | Finance Manager | Finance ledger | Compare to the 50% assumption |
| M-06 | Actual net profit | Actual gross profit - actual cost | Finance Manager | Derived | Compare to $21,987.44 |
| M-07 | Actual ROI | Actual net profit / actual cost | Marketing Manager | Derived | Compare to 13.53x |
| M-08 | Forecast accuracy (MAE) | Mean absolute difference between predicted and actual sale amount for responders | Data / Analytics | Order system plus scores | Compare to the $93.40 held-out MAE |
| M-09 | Response rate by priority tier | Responders / mailed, within tier | Marketing Manager | Order system plus scores | High tier should outperform Medium; if not, the ranking has no lift |
| M-10 | Profit contribution by segment | Net profit summed within segment | Marketing Manager | Derived | Compare to `outputs/segment_summary.csv` |
| M-11 | Opt-out / complaint rate | Opt-outs / catalogs mailed | Sales / Customer Management | CRM | Watch for contact-frequency damage (risk R-08) |
