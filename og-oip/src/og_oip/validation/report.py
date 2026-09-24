"""Build the data-quality report from ACTUAL validation results."""
from __future__ import annotations

import html
from datetime import datetime, timezone

import pandas as pd

from og_oip import config
from og_oip.utils.io import df_to_md


def build_report(raw_res: pd.DataFrame, proc_res: pd.DataFrame, clean_log: dict, defect_log: dict | None, path_md, path_html=None) -> str:
    def summ(r):
        return {"checks": len(r), "PASS": int((r.status == "PASS").sum()), "FAIL": int((r.status == "FAIL").sum()),
                "WARN": int((r.status == "WARN").sum()), "failed_rows_total": int(r.failed_rows.sum())}
    sr, sp = summ(raw_res), summ(proc_res)
    L = ["# Data Quality Report", "", f"_Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} from actual validation runs._", "",
         f"> {config.SYNTHETIC_NOTICE}", "", "## 1. Summary", "",
         "| Stage | Checks | PASS | FAIL | WARN | Failed rows (sum over checks) |", "|---|---|---|---|---|---|",
         f"| Raw | {sr['checks']} | {sr['PASS']} | {sr['FAIL']} | {sr['WARN']} | {sr['failed_rows_total']:,} |",
         f"| Processed | {sp['checks']} | {sp['PASS']} | {sp['FAIL']} | {sp['WARN']} | {sp['failed_rows_total']:,} |", ""]
    L += ["## 2. Failed checks on RAW data", "", df_to_md(raw_res[raw_res.status != "PASS"][["table", "check", "column", "failed_rows", "total_rows", "detail"]], floatfmt=".0f", max_rows=200), ""]
    L += ["## 3. Failed checks on PROCESSED data (residual issues)", ""]
    resid = proc_res[proc_res.status != "PASS"]
    L += [df_to_md(resid[["table", "check", "column", "failed_rows", "total_rows", "detail"]], floatfmt=".0f", max_rows=200) if len(resid) else "All checks passed on processed data.", ""]
    L += ["## 4. Cleaning actions (counts from the cleaning run)", ""]
    rows = []
    for t, lg in clean_log.items():
        for k, v in lg.items():
            rows.append({"table": t, "action": k, "count": v})
    L += [df_to_md(pd.DataFrame(rows), floatfmt=".0f", max_rows=400), ""]
    if defect_log:
        L += ["## 5. Injected defects (generator ground truth)", "",
              "These counts are what the synthetic generator injected into the RAW files; they document what the pipeline should detect.", "",
              df_to_md(pd.DataFrame([{"defect": k, "injected": v} for k, v in defect_log.items()]), floatfmt=".0f", max_rows=200), ""]
    L += ["## 6. Limitations", "",
          "- Rows with unparsable dates or unknown keys are quarantined (data/processed/quarantine), not repaired; they reduce row counts versus the generator truth.",
          "- Imputation is method-based (interpolation, potential-based estimate) and always flagged in `dq_flag` where the schema carries it.",
          "- Range thresholds are project assumptions, not engineering standards."]
    md = "\n".join(L)
    path_md.parent.mkdir(parents=True, exist_ok=True)
    path_md.write_text(md, encoding="utf-8")
    if path_html:
        body = "".join(f"<p>{html.escape(x)}</p>" if not x.startswith("|") else "" for x in L[:0])
        tables = "".join(f"<h3>{html.escape(n)}</h3>" + d.to_html(index=False, border=0) for n, d in
                         [("Failed checks - raw", raw_res[raw_res.status != 'PASS']), ("Failed checks - processed", resid)])
        path_html.write_text(f"<html><head><meta charset='utf-8'><title>Data Quality Report</title></head><body style='font-family:Arial'>"
                             f"<h1>Data Quality Report</h1><p>{html.escape(config.SYNTHETIC_NOTICE)}</p>"
                             f"<p>Raw: {sr}</p><p>Processed: {sp}</p>{tables}</body></html>", encoding="utf-8")
    return md
