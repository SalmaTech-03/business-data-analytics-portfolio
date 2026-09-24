"""Excel workbook with live formulas (SYNTHETIC core data + separate real-data sheets)."""
from __future__ import annotations

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from og_oip import config

F = "Arial"
HDR = PatternFill("solid", fgColor="1F3864")
INPUT = Font(name=F, color="0000FF")


def _write_df(ws, df, r0=1, fmt=None):
    for j, c in enumerate(df.columns, 1):
        x = ws.cell(r0, j, c); x.font = Font(name=F, bold=True, color="FFFFFF"); x.fill = HDR; x.alignment = Alignment(wrap_text=True, vertical="center")
    for i, row in enumerate(df.itertuples(index=False), r0 + 1):
        for j, v in enumerate(row, 1):
            if isinstance(v, pd.Timestamp):
                v = v.to_pydatetime()
            x = ws.cell(i, j, None if (isinstance(v, float) and pd.isna(v)) else v); x.font = Font(name=F)
            if fmt and df.columns[j - 1] in fmt:
                x.number_format = fmt[df.columns[j - 1]]
    for j in range(1, len(df.columns) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 16
    ws.freeze_panes = ws.cell(r0 + 1, 1)


def build(path):
    T = config.TABLES_DIR
    fm = pd.read_csv(config.MARTS_DIR / "mart_field_monthly.csv", parse_dates=["month"])
    es = pd.read_csv(T / "equipment_summary.csv")
    vy = pd.read_csv(T / "volve_yearly.csv"); bm = pd.read_csv(T / "bsee_monthly.csv", parse_dates=["month"])
    wb = Workbook()
    ws = wb.active; ws.title = "README"
    lines = ["OG-OIP Excel workbook", "", config.SYNTHETIC_NOTICE, "",
             "Sheets: Assumptions (inputs, blue), Field_Monthly (synthetic data from mart_field_monthly), Field_Summary (SUMIFS formulas),",
             "Equipment (synthetic; availability/MTBF/MTTR are formulas), Executive_KPIs (formulas), Volve_Real and BSEE_Real (REAL user-supplied data, separate from PetroNexa).",
             "Real-data sheets are not linked to the synthetic sheets. Blue font = editable assumption; black = formula or data.",
             "Regenerate with scripts/build_excel.py after re-running the pipeline."]
    for i, l in enumerate(lines, 1):
        ws.cell(i, 1, l).font = Font(name=F, bold=(i == 1), size=14 if i == 1 else 10)
    ws.column_dimensions["A"].width = 130
    a = wb.create_sheet("Assumptions")
    rows = [("Barrels per Sm3 (Volve conversion)", config.BBL_PER_M3, "Unit conversion constant used in the pipeline (config.py)"),
            ("Mcf per BOE", config.MCF_PER_BOE, "Industry convention 6 mcf = 1 BOE"),
            ("Exposure hours per producing well-day", config.EXPOSURE_HOURS_PER_ACTIVE_WELL_DAY, "Synthetic assumption for HSE rates"),
            ("Incident-rate base hours", config.INCIDENT_RATE_BASE_HOURS, "Per 200,000 hours convention")]
    _write_df(a, pd.DataFrame(rows, columns=["Assumption", "Value", "Source / note"]))
    for r in range(2, 6):
        a.cell(r, 2).font = INPUT
    a.column_dimensions["A"].width = 42; a.column_dimensions["C"].width = 70
    d = wb.create_sheet("Field_Monthly")
    cols = ["field_id", "month", "oil_bbl", "gas_mcf", "potential_bbl", "loss_bbl", "oil_sold_bbl", "gas_sold_mcf", "revenue_usd", "opex_total_usd", "cost_maintenance_usd", "lost_revenue_usd"]
    _write_df(d, fm[cols], fmt={"month": "yyyy-mm", "oil_bbl": "#,##0", "revenue_usd": "#,##0", "opex_total_usd": "#,##0"})
    n = len(fm) + 1
    s = wb.create_sheet("Field_Summary")
    heads = ["field_id", "oil_bbl", "potential_bbl", "loss_bbl", "loss_pct", "revenue_usd", "opex_usd", "cost_per_bbl_oil_sold", "cost_per_boe", "operating_margin_usd", "lost_revenue_usd"]
    for j, h in enumerate(heads, 1):
        c = s.cell(1, j, h); c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = HDR
    for i, fid in enumerate(sorted(fm.field_id.unique()), 2):
        s.cell(i, 1, fid)
        rng = lambda col: f"Field_Monthly!${col}$2:${col}${n}"
        sumif = lambda col: f"=SUMIFS({rng(col)},{rng('A')},$A{i})"
        s.cell(i, 2, sumif("C")); s.cell(i, 3, sumif("E")); s.cell(i, 4, sumif("F")); s.cell(i, 5, f"=D{i}/C{i}")
        s.cell(i, 6, sumif("I")); s.cell(i, 7, sumif("J")); s.cell(i, 8, f"=G{i}/SUMIFS({rng('G')},{rng('A')},$A{i})")
        s.cell(i, 9, f"=G{i}/(SUMIFS({rng('G')},{rng('A')},$A{i})+SUMIFS({rng('H')},{rng('A')},$A{i})/Assumptions!$B$3)")
        s.cell(i, 10, f"=F{i}-G{i}"); s.cell(i, 11, sumif("L"))
        for j in range(1, 12):
            s.cell(i, j).font = Font(name=F)
        for j, f in [(2, "#,##0"), (3, "#,##0"), (4, "#,##0"), (5, "0.0%"), (6, "#,##0"), (7, "#,##0"), (8, "0.00"), (9, "0.00"), (10, "#,##0"), (11, "#,##0")]:
            s.cell(i, j).number_format = f
    tr = 2 + fm.field_id.nunique()
    s.cell(tr, 1, "TOTAL").font = Font(name=F, bold=True)
    for j in (2, 3, 4, 6, 7, 10, 11):
        L = get_column_letter(j); s.cell(tr, j, f"=SUM({L}2:{L}{tr - 1})").font = Font(name=F, bold=True); s.cell(tr, j).number_format = "#,##0"
    s.cell(tr, 5, f"=D{tr}/C{tr}").number_format = "0.0%"
    for j in range(1, 12):
        s.column_dimensions[get_column_letter(j)].width = 18
    e = wb.create_sheet("Equipment")
    ec = ["equipment_id", "equipment_name", "equipment_type", "field_id", "criticality", "failures", "total_downtime_hours", "corrective_downtime_hours", "period_hours", "maintenance_cost_usd"]
    _write_df(e, es[ec])
    for c, h in zip("KLM", ["availability_pct", "mtbf_hours", "mttr_hours"]):
        x = e[f"{c}1"]; x.value = h; x.font = Font(name=F, bold=True, color="FFFFFF"); x.fill = HDR
    for r in range(2, len(es) + 2):
        e[f"K{r}"] = f"=100*(I{r}-G{r})/I{r}"; e[f"L{r}"] = f'=IF(F{r}>0,(I{r}-G{r})/F{r},"")'; e[f"M{r}"] = f'=IF(F{r}>0,H{r}/F{r},"")'
        for c, f in zip("KLM", ["0.00", "#,##0", "0.0"]):
            e[f"{c}{r}"].number_format = f; e[f"{c}{r}"].font = Font(name=F)
        e[f"J{r}"].number_format = "#,##0"
    ne = len(es) + 1
    k = wb.create_sheet("Executive_KPIs", 1)
    items = [("Total oil produced (bbl)", "=Field_Summary!B%d" % tr, "#,##0"), ("Production loss vs simulated potential (%)", "=Field_Summary!E%d" % tr, "0.0%"),
             ("Revenue (USD, synthetic)", "=Field_Summary!F%d" % tr, "#,##0"), ("Operating cost (USD, synthetic)", "=Field_Summary!G%d" % tr, "#,##0"),
             ("Operating margin (USD, synthetic)", "=Field_Summary!J%d" % tr, "#,##0"), ("Estimated lost revenue (USD)", "=Field_Summary!K%d" % tr, "#,##0"),
             ("Failures (corrective events)", f"=SUM(Equipment!F2:F{ne})", "#,##0"),
             ("Fleet MTBF (hours)", f"=(SUM(Equipment!I2:I{ne})-SUM(Equipment!G2:G{ne}))/SUM(Equipment!F2:F{ne})", "#,##0"),
             ("Fleet MTTR (hours)", f"=SUM(Equipment!H2:H{ne})/SUM(Equipment!F2:F{ne})", "0.0"),
             ("Fleet availability (%)", f"=100*(SUM(Equipment!I2:I{ne})-SUM(Equipment!G2:G{ne}))/SUM(Equipment!I2:I{ne})", "0.00"),
             ("Total maintenance cost (USD)", f"=SUM(Equipment!J2:J{ne})", "#,##0")]
    k.cell(1, 1, "Executive KPIs - SYNTHETIC PetroNexa Energy data (formulas)").font = Font(name=F, bold=True, size=13)
    for i, (lab, fml, nf) in enumerate(items, 3):
        k.cell(i, 1, lab).font = Font(name=F); c = k.cell(i, 2, fml); c.font = Font(name=F); c.number_format = nf
    k.column_dimensions["A"].width = 48; k.column_dimensions["B"].width = 22
    v = wb.create_sheet("Volve_Real")
    v.cell(1, 1, "REAL data: Volve (user-supplied). Not PetroNexa. Yearly totals converted from Sm3.").font = Font(name=F, bold=True)
    _write_df(v, vy[["year", "oil_bbl", "gas_mcf", "water_bbl"]], r0=3, fmt={"oil_bbl": "#,##0", "gas_mcf": "#,##0", "water_bbl": "#,##0"})
    v["E3"] = "water_cut_pct"; v["E3"].font = Font(name=F, bold=True, color="FFFFFF"); v["E3"].fill = HDR
    for r in range(4, 4 + len(vy)):
        v[f"E{r}"] = f"=100*D{r}/(D{r}+B{r})"; v[f"E{r}"].number_format = "0.0"; v[f"E{r}"].font = Font(name=F)
    b = wb.create_sheet("BSEE_Real")
    b.cell(1, 1, "REAL data: BSEE OGOR-A monthly totals (user-supplied; column meaning per author's understanding - verify with BSEE dictionary). Not PetroNexa.").font = Font(name=F, bold=True)
    _write_df(b, bm[["month", "oil_bbl", "gas_mcf", "water_bbl", "operators"]], r0=3, fmt={"month": "yyyy-mm", "oil_bbl": "#,##0", "gas_mcf": "#,##0", "water_bbl": "#,##0"})
    for c, h in zip("FG", ["water_to_oil_ratio", "gas_to_oil_mcf_per_bbl"]):
        b[f"{c}3"] = h; b[f"{c}3"].font = Font(name=F, bold=True, color="FFFFFF"); b[f"{c}3"].fill = HDR
    for r in range(4, 4 + len(bm)):
        b[f"F{r}"] = f"=D{r}/B{r}"; b[f"G{r}"] = f"=C{r}/B{r}"
        for c in "FG":
            b[f"{c}{r}"].number_format = "0.000"; b[f"{c}{r}"].font = Font(name=F)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
