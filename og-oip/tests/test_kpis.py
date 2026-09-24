from _common import *  # noqa
import numpy as np
import pandas as pd
from og_oip.analytics import financial, maintenance, production


def test_loss_decomposition_adds_up_and_nonnegative():
    wd = marts()["mart_well_daily"]
    assert (wd.production_loss_bbl >= 0).all() and (wd.downtime_loss_bbl >= 0).all() and (wd.other_loss_bbl >= -1e-9).all()
    assert np.allclose(wd.downtime_loss_bbl + wd.other_loss_bbl, wd.production_loss_bbl, atol=1e-6)


def test_field_monthly_reconciles_to_well_daily_and_sales():
    M = marts(); t = processed_typed()
    assert np.isclose(M["mart_field_monthly"].oil_bbl.sum(), M["mart_well_daily"].oil_production_bbl.sum())
    assert np.isclose(M["mart_field_monthly"].revenue_usd.sum(), t["fact_sales"].revenue_usd.sum())
    assert np.isclose(M["mart_field_monthly"].opex_total_usd.sum(), t["fact_operating_cost"].cost_amount_usd.sum())


def test_cost_per_bbl_definition():
    fm = marts()["mart_field_monthly"]
    k = financial.kpis(fm)
    assert np.isclose(k["cost_per_bbl_oil_sold"], fm.opex_total_usd.sum() / fm.oil_sold_bbl.sum())
    assert np.isclose(k["operating_margin_usd"], fm.revenue_usd.sum() - fm.opex_total_usd.sum())


def test_mtbf_mttr_availability_definitions():
    es = marts()["mart_equipment_summary"]
    r = es[es.failures > 0].iloc[0]
    assert np.isclose(r.mtbf_hours, (r.period_hours - r.total_downtime_hours) / r.failures)
    assert np.isclose(r.mttr_hours, r.corrective_downtime_hours / r.failures)
    assert (es.availability_pct.between(0, 100)).all()
    z = es[es.failures == 0]
    assert z.mtbf_hours.isna().all()


def test_priority_score_formula():
    es = marts()["mart_equipment_summary"]
    ce = maintenance.critical_equipment(es, top=5)
    r = ce.iloc[0]
    w = {"High": 3, "Medium": 2, "Low": 1}[r.criticality]
    assert np.isclose(r.priority_score, w * r.total_downtime_hours)
    assert ce.priority_score.is_monotonic_decreasing


def test_well_ranking_definitions_and_decline_output():
    wd = marts()["mart_well_daily"]
    bw = production.by_well(wd)
    assert bw.rank_by_loss_bbl.min() == 1 and bw.iloc[0].loss_bbl == bw.loss_bbl.max()
    dec = production.decline_analysis(wd)
    assert {"months_used", "r_squared", "slope_p_value"} <= set(dec.columns) and (dec.months_used >= 18).all()


def test_water_cut_weighted_not_averaged():
    wd = marts()["mart_well_daily"]
    k = production.portfolio_kpis(wd)
    exp = 100 * wd.water_production_bbl.sum() / (wd.water_production_bbl.sum() + wd.oil_production_bbl.sum())
    assert np.isclose(k["overall_water_cut_pct"], exp)


def test_mart_row_counts_consistent():
    M = marts(); t = processed_typed()
    assert len(M["mart_well_daily"]) == len(t["fact_production"])
    assert M["mart_inventory"].stockout_days.sum() == t["fact_inventory"].stockout_flag.sum()
