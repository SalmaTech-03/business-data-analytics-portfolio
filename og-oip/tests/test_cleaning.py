from _common import *  # noqa
import numpy as np
import pandas as pd
from og_oip.validation.checks import run_all_checks


def test_processed_passes_all_checks_and_raw_fails_many():
    raw, _ = raw_and_log(); proc, _, _ = cleaned()
    assert (run_all_checks(raw, "raw").status != "PASS").sum() >= 40
    res = run_all_checks(proc, "processed")
    assert res[res.status != "PASS"].empty, res[res.status != "PASS"][["table", "check", "column", "failed_rows"]].to_string()


def test_no_silent_row_loss():
    raw, _ = raw_and_log(); proc, quar, log = cleaned()
    for t in ["fact_production", "fact_sensor", "fact_maintenance", "fact_inventory", "fact_sales", "fact_operating_cost", "fact_hse"]:
        l = log[t]
        removed = sum(v for k, v in l.items() if k.startswith("duplicate") or k.startswith("business_dup"))
        assert l["rows_in"] == l["rows_out"] + l["rows_quarantined"] + removed, (t, l)
        assert len(quar[t]) == l["rows_quarantined"]


def test_cleaned_values_match_truth_or_are_flagged():
    t = truth(); proc, _, _ = cleaned()
    c = proc["fact_production"].copy(); c["date"] = pd.to_datetime(c["date"])
    g = t["fact_production"].copy(); g["date"] = pd.to_datetime(g["date"])
    j = c.merge(g, on=["date", "well_id"], suffixes=("_c", "_t"))
    diff = (j.oil_production_bbl_c - j.oil_production_bbl_t).abs() > 0.15
    unflagged = diff & ~j.dq_flag.fillna("").str.contains("oil_imputed")
    _, log = raw_and_log()
    # residual unflagged errors can only come from injected x10 outliers that stayed below the detection threshold
    assert unflagged.sum() <= log["production_oil_outliers_x10"], (int(unflagged.sum()), log["production_oil_outliers_x10"])
    assert unflagged.sum() / len(j) < 0.001


def test_unit_conversions_and_duplicates_removed():
    raw, log = raw_and_log(); _, _, cl = cleaned()
    assert cl["fact_production"]["oil_m3_to_bbl_converted"] >= log["production_oil_reported_in_m3"] - 5
    assert cl["fact_production"]["duplicates_removed"] >= log["production_exact_duplicates"] - 5
    assert cl["dim_supplier"]["rows_out"] == 8


def test_raw_not_modified_by_cleaning():
    raw, _ = raw_and_log(); n = {k: len(v) for k, v in raw.items()}
    cleaned()
    assert n == {k: len(v) for k, v in raw.items()}


def test_quarantine_has_reason():
    _, quar, _ = cleaned()
    for k, q in quar.items():
        if len(q):
            assert q.quarantine_reason.notna().all(), k
