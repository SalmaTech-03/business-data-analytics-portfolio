"""OG-OIP exploration app (Streamlit). Run:  streamlit run app/streamlit_app.py
Reads data/marts, reports/tables (create them first with scripts/run_all.py).
All PetroNexa Energy data are SYNTHETIC. Real-data tabs (Volve, BSEE OGOR-A) are separate and clearly labelled."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import streamlit as st

from og_oip import config

st.set_page_config(page_title="OG-OIP", layout="wide")
NOTICE = "SYNTHETIC data - fictional PetroNexa Energy. Not real operations."


@st.cache_data
def marts(name: str) -> pd.DataFrame:
    df = pd.read_csv(config.MARTS_DIR / f"{name}.csv")
    for c in ("date", "month"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c])
    return df


@st.cache_data
def table(name: str) -> pd.DataFrame:
    return pd.read_csv(config.TABLES_DIR / f"{name}.csv")


@st.cache_data
def kpis() -> dict:
    return json.loads((config.TABLES_DIR / "kpi_summary.json").read_text())


def need_pipeline() -> bool:
    if not (config.TABLES_DIR / "kpi_summary.json").exists():
        st.error("Outputs not found. Run `python scripts/run_all.py` first.")
        return True
    return False


st.title("Oil & Gas Operations Intelligence Platform (OG-OIP)")
st.caption(NOTICE)
if need_pipeline():
    st.stop()

K = kpis()
fm, es = marts("mart_field_monthly"), marts("mart_equipment_summary")
fields = sorted(fm.field_id.unique())
sel = st.sidebar.multiselect("Field", fields, default=fields)
fmf = fm[fm.field_id.isin(sel)]
tabs = st.tabs(["Executive", "Production", "Maintenance", "Finance", "Inventory & Suppliers", "HSE", "Forecast & Risk", "Real data: Volve", "Real data: BSEE OGOR-A", "Data quality"])

with tabs[0]:
    c = st.columns(6)
    oil, loss, pot = fmf.oil_bbl.sum(), fmf.loss_bbl.sum(), fmf.potential_bbl.sum()
    c[0].metric("Oil (bbl)", f"{oil:,.0f}")
    c[1].metric("Loss vs potential", f"{100 * loss / pot:.1f}%")
    c[2].metric("Revenue (USD)", f"{fmf.revenue_usd.sum():,.0f}")
    c[3].metric("Cost / bbl", f"{fmf.opex_total_usd.sum() / fmf.oil_sold_bbl.sum():.2f}")
    c[4].metric("Fleet availability", f"{K['maintenance']['fleet_availability_pct']:.2f}%")
    c[5].metric("Incident rate /200k h", f"{K['hse']['portfolio_incident_rate_per_200k_h']:.1f}")
    st.line_chart(fmf.pivot_table(index="month", columns="field_id", values="oil_bbl", aggfunc="sum"))
    st.caption("Availability and incident rate are portfolio-level (not filtered by field).")

with tabs[1]:
    st.subheader("Production loss by field")
    st.dataframe(table("production_by_field"), use_container_width=True)
    st.bar_chart(fmf.groupby("month")[["downtime_loss_bbl", "loss_bbl"]].sum())
    st.subheader("Well ranking (rank_by_loss_bbl / rank_by_loss_pct)")
    bw = table("production_by_well_ranking")
    st.dataframe(bw[bw.field_id.isin(sel)].head(20), use_container_width=True)
    st.subheader("Decline analysis (indicative)")
    st.dataframe(table("well_decline_analysis").head(20), use_container_width=True)

with tabs[2]:
    esf = es[es.field_id.isin(sel)]
    st.dataframe(table("maintenance_by_equipment_type"), use_container_width=True)
    st.subheader("Priority equipment (score = criticality weight x downtime hours)")
    esf = esf.assign(weight=esf.criticality.map({"High": 3, "Medium": 2, "Low": 1}))
    esf["priority_score"] = esf.weight * esf.total_downtime_hours
    st.dataframe(esf.sort_values("priority_score", ascending=False).head(10)[["equipment_id", "equipment_name", "criticality", "failures", "total_downtime_hours", "priority_score"]], use_container_width=True)
    st.subheader("Failure modes")
    st.dataframe(table("maintenance_by_failure_type").head(15), use_container_width=True)

with tabs[3]:
    st.dataframe(table("financial_by_field"), use_container_width=True)
    st.line_chart(fmf.groupby("month")[["opex_total_usd", "revenue_usd"]].sum())
    st.dataframe(table("cost_breakdown"), use_container_width=True)

with tabs[4]:
    st.dataframe(table("inventory_by_category"), use_container_width=True)
    st.subheader("Supplier performance")
    st.dataframe(table("supplier_performance")[["supplier_id", "supplier_name", "pos_received", "on_time_pct", "avg_quoted_lead_days", "avg_actual_lead_days"]], use_container_width=True)
    st.subheader("Items at or below reorder level (last day)")
    st.dataframe(table("low_stock_items"), use_container_width=True)

with tabs[5]:
    hm = marts("mart_hse_monthly"); hmf = hm[hm.field_id.isin(sel)]
    st.bar_chart(hmf.groupby("month")[["incidents", "lost_time_incidents"]].sum())
    st.dataframe(table("hse_rate_by_field"), use_container_width=True)
    st.dataframe(table("hse_by_root_cause"), use_container_width=True)
    st.caption("Exposure hours are an assumption (30 h per producing well-day).")

with tabs[6]:
    st.subheader("30-day production forecast (portfolio, baseline)")
    st.dataframe(table("forecast_backtest_summary"), use_container_width=True)
    st.line_chart(table("forecast_next_30d").set_index("date")["forecast_oil_bbl"])
    st.caption("ARIMA not included (statsmodels unavailable in the build environment).")
    st.subheader("Failure-risk model (synthetic sensors)")
    st.dataframe(table("ml_model_metrics_test"), use_container_width=True)
    st.dataframe(table("ml_latest_equipment_risk").head(15), use_container_width=True)
    st.warning("Sensor-failure relationships are simulated; metrics apply to synthetic data only.")

with tabs[7]:
    st.info("REAL data (user-supplied Volve workbook). Separate from PetroNexa.")
    if (config.TABLES_DIR / "volve_field_monthly.csv").exists():
        vm = table("volve_field_monthly"); vm["month"] = pd.to_datetime(vm["month"])
        st.line_chart(vm.set_index("month")["avg_daily_oil_bbl"])
        st.dataframe(table("volve_well_summary"), use_container_width=True)
        st.dataframe(table("volve_data_quality"), use_container_width=True)

with tabs[8]:
    st.info("REAL data (user-supplied BSEE OGOR-A files). Column meaning per the author's understanding; verify with the BSEE dictionary. Separate from PetroNexa.")
    if (config.TABLES_DIR / "bsee_monthly.csv").exists():
        bm = table("bsee_monthly"); bm["month"] = pd.to_datetime(bm["month"])
        st.line_chart(bm.set_index("month")["oil_bbl"])
        st.dataframe(table("bsee_operators").head(15), use_container_width=True)
        st.dataframe(table("bsee_data_quality"), use_container_width=True)

with tabs[9]:
    r, p = table("dq_results_raw"), table("dq_results_processed")
    c = st.columns(2)
    c[0].metric("Raw: failed checks", int((r.status != "PASS").sum()), f"of {len(r)}")
    c[1].metric("Processed: failed checks", int((p.status != "PASS").sum()), f"of {len(p)}")
    st.dataframe(r[r.status != "PASS"][["table", "check", "column", "failed_rows"]], use_container_width=True)
