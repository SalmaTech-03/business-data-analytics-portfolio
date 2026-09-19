"""Campaign economics: revenue, gross profit, cost, net profit and ROI.

All formulas are stated once here and reused by the notebooks, the tests and
the dashboard extract, so the repository cannot drift into two versions of the
same number.

    Expected Revenue (customer) = Predicted Sale Amount x P(response)
    Gross Profit     (customer) = Expected Revenue x Gross Margin
    Catalog Cost     (customer) = Cost per Catalog
    Net Profit       (customer) = Gross Profit - Catalog Cost
    ROI              (campaign) = Net Profit / Campaign Cost
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Business assumptions carried over unchanged from the source project.
COST_PER_CATALOG = 6.50
GROSS_MARGIN = 0.50


@dataclass(frozen=True)
class CampaignAssumptions:
    """The three levers that drive the whole financial model."""

    cost_per_catalog: float = COST_PER_CATALOG
    gross_margin: float = GROSS_MARGIN
    response_multiplier: float = 1.0  # 1.0 = use model response scores as-is

    def __post_init__(self) -> None:
        if self.cost_per_catalog < 0:
            raise ValueError("cost_per_catalog cannot be negative")
        if not 0 <= self.gross_margin <= 1:
            raise ValueError("gross_margin must be between 0 and 1")
        if self.response_multiplier < 0:
            raise ValueError("response_multiplier cannot be negative")


def expected_revenue(
    predicted_sale_amount: float | np.ndarray | pd.Series,
    response_probability: float | np.ndarray | pd.Series = 1.0,
) -> float | np.ndarray | pd.Series:
    """Probability-weighted revenue per customer."""
    return predicted_sale_amount * response_probability


def gross_profit(revenue, gross_margin: float = GROSS_MARGIN):
    """Contribution left after cost of goods, before campaign cost."""
    if not 0 <= gross_margin <= 1:
        raise ValueError("gross_margin must be between 0 and 1")
    return revenue * gross_margin


def campaign_cost(n_catalogs: int, cost_per_catalog: float = COST_PER_CATALOG) -> float:
    """Total printing and distribution cost for the mailing."""
    if n_catalogs < 0:
        raise ValueError("n_catalogs cannot be negative")
    if cost_per_catalog < 0:
        raise ValueError("cost_per_catalog cannot be negative")
    return n_catalogs * cost_per_catalog


def net_profit(gross, cost):
    """Gross profit less the cost of sending the catalogs."""
    return gross - cost


def roi(net, cost):
    """Return on campaign spend. Undefined (NaN) when nothing is spent."""
    cost_arr = np.asarray(cost, dtype=float)
    net_arr = np.asarray(net, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(cost_arr > 0, net_arr / cost_arr, np.nan)
    return float(result) if result.ndim == 0 else result


def build_customer_economics(
    scored: pd.DataFrame,
    assumptions: CampaignAssumptions | None = None,
    prediction_col: str = "Predicted_Sale_Amount",
    response_col: str | None = "Score_Yes",
) -> pd.DataFrame:
    """Return a per-customer economics table for the mailing list.

    If `response_col` is None the function falls back to a deterministic
    100%-response view. That fallback is documented as a limitation rather than
    presented as a forecast.
    """
    a = assumptions or CampaignAssumptions()
    out = scored.copy()

    if response_col and response_col in out.columns:
        prob = out[response_col].astype(float) * a.response_multiplier
        prob = prob.clip(upper=1.0)
        out["Response_Probability"] = prob
        out["Response_Basis"] = "Model score (Score_Yes)"
    else:
        out["Response_Probability"] = 1.0
        out["Response_Basis"] = "Not available - deterministic 100% assumption"

    out["Expected_Revenue"] = expected_revenue(
        out[prediction_col], out["Response_Probability"]
    )
    out["Gross_Profit"] = gross_profit(out["Expected_Revenue"], a.gross_margin)
    out["Catalog_Cost"] = a.cost_per_catalog
    out["Expected_Net_Profit"] = net_profit(out["Gross_Profit"], out["Catalog_Cost"])
    out["Customer_ROI"] = roi(out["Expected_Net_Profit"], out["Catalog_Cost"])
    return out


def campaign_summary(
    economics: pd.DataFrame, assumptions: CampaignAssumptions | None = None
) -> dict:
    """Roll the per-customer table up to the campaign-level KPI set."""
    a = assumptions or CampaignAssumptions()
    n = len(economics)
    revenue = float(economics["Expected_Revenue"].sum())
    gross = float(economics["Gross_Profit"].sum())
    cost = campaign_cost(n, a.cost_per_catalog)
    net = net_profit(gross, cost)
    return {
        "customers": n,
        "predicted_sales_total": float(economics["Predicted_Sale_Amount"].sum()),
        "expected_revenue": revenue,
        "gross_margin": a.gross_margin,
        "gross_profit": gross,
        "campaign_cost": cost,
        "net_profit": net,
        "roi": roi(net, cost),
        "avg_response_probability": float(economics["Response_Probability"].mean()),
        "revenue_per_customer": revenue / n if n else float("nan"),
        "net_profit_per_customer": net / n if n else float("nan"),
        "breakeven_response_multiplier": (
            cost / gross if gross > 0 else float("nan")
        ),
    }


def prioritise_customers(
    economics: pd.DataFrame, profit_col: str = "Expected_Net_Profit"
) -> pd.DataFrame:
    """Assign High / Medium / Low priority from the profit distribution.

    Rules (see docs/business_rules.md, BRule-08):
      * Low       - expected net profit <= 0 (the catalog does not pay for itself)
      * High      - profitable and in the top quartile of profitable customers
      * Medium    - profitable, below the top quartile
    The threshold is derived from the data, not chosen by hand, so it moves with
    the model rather than becoming stale.
    """
    out = economics.copy()
    profitable = out[out[profit_col] > 0][profit_col]
    high_cut = float(profitable.quantile(0.75)) if len(profitable) else float("inf")

    def label(v: float) -> str:
        if v <= 0:
            return "Low"
        return "High" if v >= high_cut else "Medium"

    out["Priority"] = out[profit_col].apply(label)
    out["Priority_Threshold_High"] = high_cut
    out["Profit_Rank"] = out[profit_col].rank(ascending=False, method="min").astype(int)
    return out


def sensitivity_grid(
    economics: pd.DataFrame,
    gross_margins: list[float],
    catalog_costs: list[float],
    response_multipliers: list[float] | None = None,
) -> pd.DataFrame:
    """Recompute campaign economics across an assumption grid."""
    response_multipliers = response_multipliers or [1.0]
    rows = []
    base_pred = economics["Predicted_Sale_Amount"]
    base_prob = economics["Response_Probability"]
    n = len(economics)
    for rm in response_multipliers:
        prob = (base_prob * rm).clip(upper=1.0)
        revenue = float((base_pred * prob).sum())
        for gm in gross_margins:
            gross = revenue * gm
            for cost_each in catalog_costs:
                cost = campaign_cost(n, cost_each)
                net = gross - cost
                rows.append({
                    "Response_Multiplier": rm,
                    "Gross_Margin": gm,
                    "Cost_Per_Catalog": cost_each,
                    "Expected_Revenue": revenue,
                    "Gross_Profit": gross,
                    "Campaign_Cost": cost,
                    "Net_Profit": net,
                    "ROI": roi(net, cost),
                })
    return pd.DataFrame(rows)


def breakeven_sale_amount(
    response_probability: float,
    cost_per_catalog: float = COST_PER_CATALOG,
    gross_margin: float = GROSS_MARGIN,
) -> float:
    """Sale amount at which one catalog exactly pays for itself."""
    denominator = response_probability * gross_margin
    if denominator <= 0:
        return float("inf")
    return cost_per_catalog / denominator
