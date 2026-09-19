"""Tests for the campaign financial model.

These are the calculations that justify budget, so they are tested against
hand-worked figures rather than against the code's own output.
"""

import math

import numpy as np
import pandas as pd
import pytest

from src import profitability as pf


class TestWorkedExample:
    """The example from the project brief, worked end to end.

    Revenue $1,000 at a 50% gross margin with $100 of campaign cost
    must give $500 gross profit and $400 net profit.
    """

    def test_gross_profit_is_five_hundred(self):
        assert pf.gross_profit(1000.0, 0.50) == 500.0

    def test_net_profit_is_four_hundred(self):
        assert pf.net_profit(pf.gross_profit(1000.0, 0.50), 100.0) == 400.0

    def test_roi_is_four_times(self):
        assert pf.roi(400.0, 100.0) == pytest.approx(4.0)


class TestExpectedRevenue:
    def test_probability_weighting(self):
        assert pf.expected_revenue(800.0, 0.25) == 200.0

    def test_certain_response_returns_full_amount(self):
        assert pf.expected_revenue(800.0, 1.0) == 800.0

    def test_zero_probability_returns_zero(self):
        assert pf.expected_revenue(800.0, 0.0) == 0.0

    def test_vectorised(self):
        result = pf.expected_revenue(np.array([100.0, 200.0]), np.array([0.5, 0.25]))
        np.testing.assert_allclose(result, [50.0, 50.0])


class TestGrossProfit:
    @pytest.mark.parametrize(
        "revenue,margin,expected",
        [(1000.0, 0.50, 500.0), (1000.0, 0.40, 400.0),
         (1000.0, 0.0, 0.0), (1000.0, 1.0, 1000.0), (0.0, 0.50, 0.0)],
    )
    def test_margin_applied(self, revenue, margin, expected):
        assert pf.gross_profit(revenue, margin) == pytest.approx(expected)

    def test_rejects_margin_above_one(self):
        with pytest.raises(ValueError):
            pf.gross_profit(1000.0, 1.5)

    def test_rejects_negative_margin(self):
        with pytest.raises(ValueError):
            pf.gross_profit(1000.0, -0.1)


class TestCampaignCost:
    def test_base_case_matches_source_project(self):
        """250 catalogs at $6.50 is the campaign cost in every report."""
        assert pf.campaign_cost(250, 6.50) == 1625.0

    def test_uses_default_unit_cost(self):
        assert pf.campaign_cost(250) == 1625.0

    def test_zero_catalogs_costs_nothing(self):
        assert pf.campaign_cost(0, 6.50) == 0.0

    def test_rejects_negative_count(self):
        with pytest.raises(ValueError):
            pf.campaign_cost(-1, 6.50)

    def test_rejects_negative_unit_cost(self):
        with pytest.raises(ValueError):
            pf.campaign_cost(250, -6.50)


class TestROI:
    def test_undefined_when_no_spend(self):
        """A zero-cost scenario is legitimate input and must not crash (BRule-12)."""
        assert math.isnan(pf.roi(500.0, 0.0))

    def test_negative_net_profit_gives_negative_roi(self):
        assert pf.roi(-50.0, 100.0) == pytest.approx(-0.5)

    def test_vectorised_handles_zero_cost_elementwise(self):
        result = pf.roi(np.array([100.0, 100.0]), np.array([50.0, 0.0]))
        assert result[0] == pytest.approx(2.0)
        assert math.isnan(result[1])


class TestAssumptionValidation:
    """BRule-11: nonsensical inputs must fail loudly, not produce plausible numbers."""

    def test_defaults_match_source_project(self):
        a = pf.CampaignAssumptions()
        assert a.cost_per_catalog == 6.50
        assert a.gross_margin == 0.50

    @pytest.mark.parametrize("kwargs", [
        {"gross_margin": 1.5},
        {"gross_margin": -0.1},
        {"cost_per_catalog": -1.0},
        {"response_multiplier": -0.5},
    ])
    def test_invalid_assumptions_rejected(self, kwargs):
        with pytest.raises(ValueError):
            pf.CampaignAssumptions(**kwargs)


@pytest.fixture
def sample_customers():
    """Three customers with hand-checkable economics."""
    return pd.DataFrame({
        "Customer_ID": [1, 2, 3],
        "Customer_Segment": ["Credit Card Only", "Loyalty Club Only", "Store Mailing List"],
        "Predicted_Sale_Amount": [1000.0, 500.0, 100.0],
        "Score_Yes": [0.50, 0.20, 0.10],
    })


class TestCustomerEconomics:
    def test_expected_revenue_per_customer(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        np.testing.assert_allclose(econ["Expected_Revenue"], [500.0, 100.0, 10.0])

    def test_gross_profit_per_customer(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        np.testing.assert_allclose(econ["Gross_Profit"], [250.0, 50.0, 5.0])

    def test_net_profit_subtracts_catalog_cost(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        np.testing.assert_allclose(econ["Expected_Net_Profit"], [243.50, 43.50, -1.50])

    def test_unprofitable_customer_is_identified(self, sample_customers):
        """The third customer cannot cover a $6.50 catalog and must show a loss."""
        econ = pf.build_customer_economics(sample_customers)
        assert econ.loc[2, "Expected_Net_Profit"] < 0

    def test_probability_capped_at_one(self):
        """BRule-04: a multiplier must never push probability above 1.0."""
        df = pd.DataFrame({"Predicted_Sale_Amount": [100.0], "Score_Yes": [0.9]})
        econ = pf.build_customer_economics(
            df, pf.CampaignAssumptions(response_multiplier=2.0)
        )
        assert econ["Response_Probability"].iloc[0] == 1.0

    def test_missing_response_column_falls_back_and_flags_it(self):
        """Without a probability, the fallback must be documented in the output."""
        df = pd.DataFrame({"Predicted_Sale_Amount": [100.0]})
        econ = pf.build_customer_economics(df, response_col=None)
        assert econ["Response_Probability"].iloc[0] == 1.0
        assert "Not available" in econ["Response_Basis"].iloc[0]


class TestCampaignSummary:
    def test_totals_reconcile(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        s = pf.campaign_summary(econ)
        assert s["expected_revenue"] == pytest.approx(610.0)
        assert s["gross_profit"] == pytest.approx(305.0)
        assert s["campaign_cost"] == pytest.approx(19.50)
        assert s["net_profit"] == pytest.approx(285.50)

    def test_net_profit_identity_holds(self, sample_customers):
        """Net profit must always equal gross profit minus campaign cost."""
        econ = pf.build_customer_economics(sample_customers)
        s = pf.campaign_summary(econ)
        assert s["net_profit"] == pytest.approx(s["gross_profit"] - s["campaign_cost"])

    def test_roi_identity_holds(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        s = pf.campaign_summary(econ)
        assert s["roi"] == pytest.approx(s["net_profit"] / s["campaign_cost"])


class TestPrioritisation:
    def test_unprofitable_customers_are_low_priority(self, sample_customers):
        """BRule-09: a catalog that does not pay for itself is never prioritised."""
        econ = pf.prioritise_customers(pf.build_customer_economics(sample_customers))
        assert econ.loc[2, "Priority"] == "Low"

    def test_highest_value_customer_is_high_priority(self, sample_customers):
        econ = pf.prioritise_customers(pf.build_customer_economics(sample_customers))
        assert econ.loc[0, "Priority"] == "High"

    def test_ranking_is_descending_by_profit(self, sample_customers):
        econ = pf.prioritise_customers(pf.build_customer_economics(sample_customers))
        assert econ.loc[0, "Profit_Rank"] == 1
        assert econ.loc[2, "Profit_Rank"] == 3

    def test_every_customer_receives_a_tier(self, sample_customers):
        econ = pf.prioritise_customers(pf.build_customer_economics(sample_customers))
        assert econ["Priority"].isin(["High", "Medium", "Low"]).all()


class TestSensitivityGrid:
    def test_grid_covers_every_combination(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        grid = pf.sensitivity_grid(econ, [0.4, 0.5], [5.0, 6.5], [0.8, 1.0])
        assert len(grid) == 8

    def test_base_case_cell_matches_the_summary(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        base = pf.campaign_summary(econ)
        grid = pf.sensitivity_grid(econ, [0.50], [6.50], [1.0])
        assert grid["Net_Profit"].iloc[0] == pytest.approx(base["net_profit"])

    def test_higher_cost_reduces_net_profit(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        grid = pf.sensitivity_grid(econ, [0.50], [5.0, 10.0], [1.0])
        assert grid["Net_Profit"].iloc[0] > grid["Net_Profit"].iloc[1]

    def test_higher_margin_increases_net_profit(self, sample_customers):
        econ = pf.build_customer_economics(sample_customers)
        grid = pf.sensitivity_grid(econ, [0.40, 0.60], [6.50], [1.0])
        assert grid["Net_Profit"].iloc[1] > grid["Net_Profit"].iloc[0]


class TestBreakeven:
    def test_breakeven_sale_amount(self):
        """At 50% response and 50% margin, $6.50 of cost needs a $26 sale."""
        assert pf.breakeven_sale_amount(0.50, 6.50, 0.50) == pytest.approx(26.0)

    def test_zero_probability_is_never_breakeven(self):
        assert pf.breakeven_sale_amount(0.0) == float("inf")

    def test_breakeven_customer_has_zero_net_profit(self):
        """A customer at exactly the break-even sale amount must net zero."""
        be = pf.breakeven_sale_amount(0.40, 6.50, 0.50)
        df = pd.DataFrame({"Predicted_Sale_Amount": [be], "Score_Yes": [0.40]})
        econ = pf.build_customer_economics(df)
        assert econ["Expected_Net_Profit"].iloc[0] == pytest.approx(0.0, abs=1e-9)


class TestEdgeCases:
    def test_empty_campaign_does_not_crash(self):
        df = pd.DataFrame({"Predicted_Sale_Amount": [], "Score_Yes": []})
        econ = pf.build_customer_economics(df)
        s = pf.campaign_summary(econ)
        assert s["customers"] == 0
        assert s["expected_revenue"] == 0.0

    def test_zero_margin_makes_every_catalog_a_loss(self, sample_customers):
        econ = pf.build_customer_economics(
            sample_customers, pf.CampaignAssumptions(gross_margin=0.0)
        )
        assert (econ["Expected_Net_Profit"] < 0).all()

    def test_free_catalogs_make_every_positive_customer_profitable(self, sample_customers):
        econ = pf.build_customer_economics(
            sample_customers, pf.CampaignAssumptions(cost_per_catalog=0.0)
        )
        assert (econ["Expected_Net_Profit"] >= 0).all()
