"""Build and EXECUTE the 7 EDA notebooks without Jupyter (nbformat/ipykernel were unavailable).
Cells are executed sequentially in one namespace; stdout, last-expression values and matplotlib figures are stored as notebook outputs.
The resulting .ipynb files are standard nbformat v4 JSON and can be re-run in Jupyter."""
import _bootstrap  # noqa: F401
import ast
import base64
import contextlib
import io
import json
import os
import traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from og_oip import config

NB = config.ROOT / "notebooks"
SETUP = '''import sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
ROOT = Path.cwd().parent
sys.path.insert(0, str(ROOT / "src"))
import numpy as np, pandas as pd, matplotlib.pyplot as plt
pd.set_option("display.width", 160); pd.set_option("display.max_columns", 30); pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
from og_oip import config
NOTICE = config.SYNTHETIC_NOTICE
print(NOTICE)'''
MARTS = '''M = {p.stem: pd.read_csv(p, parse_dates=[c for c in ("date","month") if c in pd.read_csv(p, nrows=0).columns]) for p in config.MARTS_DIR.glob("mart_*.csv")}
wd, fm, es = M["mart_well_daily"], M["mart_field_monthly"], M["mart_equipment_summary"]'''


def md(t): return ("md", t)
def code(t): return ("code", t)


NOTEBOOKS = {
"01_data_generation_and_quality": [
 md("# 01 - Synthetic data generation and data quality\nFictional company **PetroNexa Energy**. Compares RAW (defective) files with PROCESSED files and reads the actual validation results.\n\n" + config.SYNTHETIC_NOTICE),
 code(SETUP),
 code('''import json
man = json.load(open(config.REFERENCE_DIR / "generation_manifest.json"))
pd.DataFrame({k: {"rows": v["rows"]} for k, v in man["tables"].items() if not k.startswith("_")}).T'''),
 code('''print("Total fact rows in clean generator truth:", f"{man['total_fact_rows']:,}")
raw_p = pd.read_csv(config.RAW_DIR / "fact_production.csv", low_memory=False); proc_p = pd.read_csv(config.PROCESSED_DIR / "fact_production.csv")
print("production rows raw / processed:", len(raw_p), len(proc_p))
raw_p.head()'''),
 md("## Injected defects (generator ground truth)"),
 code('''dl = json.load(open(config.REFERENCE_DIR / "defect_injection_log.json"))
pd.Series(dl, name="injected").to_frame()'''),
 md("## Validation results: raw vs processed"),
 code('''r = pd.read_csv(config.TABLES_DIR / "dq_results_raw.csv"); p = pd.read_csv(config.TABLES_DIR / "dq_results_processed.csv")
print(f"RAW: {len(r)} checks, {(r.status!='PASS').sum()} failed, {r.failed_rows.sum():,} failed rows (summed over checks)")
print(f"PROCESSED: {len(p)} checks, {(p.status!='PASS').sum()} failed")
r[r.status != "PASS"].sort_values("failed_rows", ascending=False).head(15)[["table", "check", "column", "failed_rows"]]'''),
 code('''log = json.load(open(config.PROCESSED_DIR / "cleaning_log.json"))
pd.DataFrame({t: {k: v for k, v in l.items() if k in ("rows_in", "rows_out", "rows_quarantined")} for t, l in log.items()}).T'''),
 md("Quarantined rows (unparsable dates, missing/unknown keys) are kept in `data/processed/quarantine/`; they are not repaired or silently dropped."),
],
"02_production_eda": [
 md("# 02 - Production EDA (SYNTHETIC)\nQuestions: where is production lost, and which wells decline or water out fastest?"), code(SETUP), code(MARTS),
 code('''from og_oip.analytics import production
k = production.portfolio_kpis(wd)
print(f"Oil {k['total_oil_bbl']/1e6:.2f} MMbbl | loss {k['production_loss_pct']:.1f}% of simulated potential | downtime share of loss {k['downtime_share_of_loss_pct']:.0f}%")
print(f"Downtime hours associated with maintenance events: {k['maintenance_associated_downtime_share_pct']:.0f}%")'''),
 code('''from og_oip.reporting import charts
fig, ax = plt.subplots(figsize=(9,4)); p = fm.pivot_table(index="month", columns="field_id", values="oil_bbl", aggfunc="sum")/1e3
ax.stackplot(p.index, p.T.values, labels=p.columns); ax.legend(); ax.set_title("Monthly oil by field (k bbl) - synthetic"); plt.show()'''),
 code('''fields = pd.read_csv(config.PROCESSED_DIR / "dim_field.csv")
production.by_field(wd, fields)[["field_id","field_name","oil_bbl","loss_bbl","loss_pct","water_cut_pct"]]'''),
 md("### Well ranking\nRanking metrics are explicit: `rank_by_loss_bbl` (total barrels lost) and `rank_by_loss_pct` (loss / potential)."),
 code('production.by_well(wd).head(10)[["well_name","field_id","loss_bbl","loss_pct","avg_oil_rate_bbl_d","rank_by_loss_bbl","rank_by_loss_pct"]]'),
 code('''dec = production.decline_analysis(wd)
print("wells with a decline fit:", len(dec), "| median nominal annual decline %:", round(dec.nominal_annual_decline_pct.median(),1))
dec.head(8)'''),
 md("Decline fits are indicative: workovers and downtime create step changes that a single exponential does not capture."),
 code('''la = production.loss_associations(wd); la'''),
 md("Spearman correlations are **associations only**. The strong correlation with downtime hours is by construction (loss is computed from downtime)."),
],
"03_maintenance_reliability_eda": [
 md("# 03 - Maintenance and reliability EDA (SYNTHETIC)"), code(SETUP), code(MARTS),
 code('''from og_oip.analytics import maintenance
maint = pd.read_csv(config.PROCESSED_DIR / "fact_maintenance.csv", parse_dates=["date"])
k = maintenance.kpis(es, maint); k'''),
 code('bt = maintenance.by_type(es); bt'),
 code('''fig, ax = plt.subplots(1,2, figsize=(10,3.5)); bt.plot.barh(x="equipment_type", y="mtbf_hours", ax=ax[0], legend=False, title="MTBF (h)"); bt.plot.barh(x="equipment_type", y="mttr_hours", ax=ax[1], legend=False, title="MTTR (h)"); plt.show()'''),
 code('maintenance.critical_equipment(es)'),
 md("Priority score = criticality weight (High 3, Medium 2, Low 1) x total downtime hours."),
 code('''eq = pd.read_csv(config.PROCESSED_DIR / "dim_equipment.csv"); maintenance.by_failure_type(maint, eq).head(10)'''),
 code('''pareto = maintenance.cost_pareto(es); print("share of cost from top 10 units (%):", round(pareto.cum_share_pct.iloc[9],1)); maintenance.age_association(es)'''),
 md("Age-failure correlations are computed within equipment type; with 4-16 units per type the statistical power is low."),
],
"04_finance_inventory_hse_eda": [
 md("# 04 - Finance, inventory/suppliers and HSE EDA (SYNTHETIC)"), code(SETUP), code(MARTS),
 md("## Finance"),
 code('''from og_oip.analytics import financial, inventory, hse
fields = pd.read_csv(config.PROCESSED_DIR / "dim_field.csv")
print(financial.kpis(fm)); financial.by_year(fm)'''),
 code('financial.cost_breakdown(fm)'),
 md("## Inventory and suppliers"),
 code('''mi, sp = M["mart_inventory"], M["mart_supplier_performance"]
inv = pd.read_csv(config.PROCESSED_DIR / "fact_inventory.csv", parse_dates=["date"]); dm = pd.read_csv(config.PROCESSED_DIR / "dim_material.csv")
print(inventory.kpis(inv, mi, dm)); inventory.by_category(mi)'''),
 code('sp[["supplier_id","supplier_name","pos_received","on_time_pct","avg_quoted_lead_days","avg_actual_lead_days"]]'),
 code('inventory.supplier_association(sp)'),
 md("n = 8 suppliers: correlation is indicative only."),
 md("## HSE"),
 code('''hm, em = M["mart_hse_monthly"], M["mart_equipment_monthly"]; h = pd.read_csv(config.PROCESSED_DIR / "fact_hse.csv", parse_dates=["date"])
print(hse.kpis(h, hm)); print(hse.maintenance_association(hm, em)); hse.by_field_rate(hm)'''),
 code('hse.distributions(h)["root_cause"]'),
],
"05_forecasting_and_predictive_maintenance": [
 md("# 05 - Forecasting and predictive maintenance (SYNTHETIC)\nARIMA is not included (statsmodels unavailable); an OLS autoregression is used as a labelled alternative."), code(SETUP),
 code('''from og_oip.forecasting import models as fmod
t_prod = pd.read_csv(config.PROCESSED_DIR / "fact_production.csv", parse_dates=["date"])
ser = t_prod.groupby("date")["oil_production_bbl"].sum().asfreq("D")
det, summ = fmod.backtest(ser); summ'''),
 code('''best = summ.iloc[0].model; fc = fmod.final_forecast(ser, best, 30)
fig, ax = plt.subplots(figsize=(9,3.5)); ax.plot(ser.index[-120:], ser.values[-120:]); ax.plot(fc.date, fc.forecast_oil_bbl, "r--"); ax.set_title(f"30-day forecast: {best} (synthetic)"); plt.show()'''),
 md("Backtests are rolling-origin (6 origins, 30-day horizon). New wells create level shifts no baseline can anticipate."),
 md("## Predictive maintenance: 7-day failure risk"),
 code('''from og_oip.ml import predictive_maintenance as pm
sd = pd.read_csv(config.MARTS_DIR / "mart_sensor_daily.csv", parse_dates=["date"]); maint = pd.read_csv(config.PROCESSED_DIR / "fact_maintenance.csv", parse_dates=["date"])
eq = pd.read_csv(config.PROCESSED_DIR / "dim_equipment.csv", parse_dates=["installation_date"])
d = pm.build_dataset(sd, maint, eq); print(d.shape, "positive rate %:", round(100*d.label.mean(),2))
res, info, fitted, (tr, va, te), scores = pm.run_experiment(d); info'''),
 code('res.round(3)'),
 code('''best_row = res.iloc[:3].sort_values("pr_auc", ascending=False).iloc[0]
print("test prevalence (random-model PR-AUC):", round(te.label.mean(),3)); print(pm.event_level_recall(te, scores[best_row.model], best_row.threshold))
pm.feature_importance(fitted).head(10)'''),
 md("The sensor-failure link is **simulated** (75% of failures have a ramp), so these metrics show the pipeline works, not real-fleet performance. The threshold is chosen on validation data only."),
],
"06_volve_case_study": [
 md("# 06 - REAL DATA case study: Volve production\nSeparate from PetroNexa. Units converted from Sm3 with documented factors."), code(SETUP),
 code('''from og_oip.real_data import volve
daily, monthly = volve.load(); v = volve.analyse(daily, monthly); v["data_quality"]'''),
 code('v["well_summary"][["wellbore","first_date","last_date","cum_oil_bbl","water_cut_pct","uptime_pct_of_calendar_span","oil_share_pct"]]'),
 code('''fmn = v["field_monthly"]; fig, ax = plt.subplots(figsize=(9,3.5)); ax.plot(fmn.month, fmn.avg_daily_oil_bbl/1e3); ax2 = ax.twinx(); ax2.plot(fmn.month, fmn.water_cut_pct, "b--")
ax.set_title("Volve (REAL): oil rate (k bbl/d) and water cut (%)"); plt.show()'''),
 code('v["field_decline"], v["yearly"]'),
 code('volve.forecast_backtest(fmn)[1]'),
 md("Limits: no maintenance, cost or price data in the file, so no reliability or financial KPIs are derived."),
],
"07_bsee_ogora_case_study": [
 md("# 07 - REAL DATA case study: BSEE OGOR-A\nSeparate from PetroNexa. Column names follow the author's understanding of the OGOR-A layout (files have no header); verify against the BSEE data dictionary. OGOR-B/C not used."), code(SETUP),
 code('''from og_oip.real_data import bsee
d = bsee.load(); a = bsee.analyse(d); a["data_quality"]'''),
 code('a["monthly"][["month","oil_bbl","gas_mcf","water_bbl","completions","operators","water_to_oil_ratio"]]'),
 code('a["operators"].head(10)[["operator_name","oil_bbl","oil_share_pct","water_to_oil_ratio"]], a["concentration"]'),
 code('a["areas"].head(8)'),
 code('''m = a["monthly"]; fig, ax = plt.subplots(figsize=(9,3.5)); ax.plot(m.month, m.oil_bbl/1e6, marker="o"); ax.set_title("BSEE OGOR-A (REAL): monthly reported oil (million bbl)"); plt.show()'''),
 md("18 months are too few for decline or seasonality conclusions. A falling completion count may reflect reporting changes as well as operations."),
],
}


def run_cells(cells):
    ns = {"__name__": "__nb__"}; out_cells = []; n = 0
    for kind, src in cells:
        if kind == "md":
            out_cells.append({"cell_type": "markdown", "metadata": {}, "source": src.splitlines(True)}); continue
        n += 1; outputs = []; buf = io.StringIO()
        tree = ast.parse(src); last = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = ast.Expression(tree.body.pop().value)
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(tree, "<cell>", "exec"), ns)
                val = eval(compile(last, "<cell>", "eval"), ns) if last is not None else None
            if buf.getvalue():
                outputs.append({"output_type": "stream", "name": "stdout", "text": buf.getvalue().splitlines(True)})
            if val is not None:
                txt = val.to_string(max_rows=25) if isinstance(val, (pd.DataFrame, pd.Series)) else repr(val)
                outputs.append({"output_type": "execute_result", "execution_count": n, "metadata": {}, "data": {"text/plain": txt.splitlines(True)}})
        except Exception:
            outputs.append({"output_type": "error", "ename": "Error", "evalue": "cell failed", "traceback": traceback.format_exc().splitlines()})
            raise
        for num in plt.get_fignums():
            b = io.BytesIO(); plt.figure(num).savefig(b, format="png", dpi=90, bbox_inches="tight")
            outputs.append({"output_type": "display_data", "metadata": {}, "data": {"image/png": base64.b64encode(b.getvalue()).decode(), "text/plain": ["<Figure>"]}})
        plt.close("all")
        out_cells.append({"cell_type": "code", "metadata": {}, "execution_count": n, "source": src.splitlines(True), "outputs": outputs})
    return out_cells


def main():
    NB.mkdir(exist_ok=True); cwd = os.getcwd(); os.chdir(NB)
    try:
        for name, cells in NOTEBOOKS.items():
            nb = {"cells": run_cells(cells), "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"},
                                                           "og_oip_note": "Executed by scripts/build_notebooks.py (no Jupyter available in build environment)."}, "nbformat": 4, "nbformat_minor": 5}
            (NB / f"{name}.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8"); print("built", name)
    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    main()
