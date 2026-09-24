from _common import *  # noqa
import pandas as pd
from og_oip.validation import checks as c
from og_oip.validation.report import build_report
from pathlib import Path
import tempfile


def test_null_pk_range_domain_referential_detected():
    df = pd.DataFrame({"id": [1, 1, 2], "v": [1.0, None, 200.0], "k": ["A", "B", "Z"]})
    assert c.null_check(df, "t", ["v"])[0]["failed_rows"] == 1
    assert c.pk_check(df, "t", ["id"])[0]["failed_rows"] == 1
    assert c.range_check(df, "t", "v", 0, 100)[0]["failed_rows"] == 1
    assert c.domain_check(df, "t", "k", {"A", "B"})[0]["failed_rows"] == 1
    parent = pd.DataFrame({"k": ["A", "B"]})
    assert c.referential_check(df, "t", "k", parent, "k")[0]["failed_rows"] == 1


def test_date_checks():
    df = pd.DataFrame({"d": ["2023-01-05", "05-Jan-2023", "2023-13-45"]})
    assert c.date_validity(df, "t", "d")[0]["failed_rows"] == 1
    assert c.date_format_consistency(df, "t", "d")[0]["failed_rows"] == 1


def test_logic_checks_flag_broken_identities():
    raw, _ = raw_and_log()
    res = c.run_all_checks(raw, "raw")
    r = res[res.check == "total_cost_eq_components"].iloc[0]
    assert r.failed_rows > 0
    proc, _, _ = cleaned()
    res = c.run_all_checks(proc, "processed")
    assert res[res.check == "total_cost_eq_components"].iloc[0].failed_rows == 0


def test_report_is_generated_from_results():
    raw, log = raw_and_log(); proc, _, cl = cleaned()
    rr, pr = c.run_all_checks(raw, "raw"), c.run_all_checks(proc, "processed")
    with tempfile.TemporaryDirectory() as d:
        md = build_report(rr, pr, cl, log, Path(d) / "r.md", Path(d) / "r.html")
        assert f"| Raw | {len(rr)} |" in md and f"| Processed | {len(pr)} |" in md
        assert (Path(d) / "r.html").exists()
