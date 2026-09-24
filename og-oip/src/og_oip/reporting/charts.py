"""Matplotlib charts (saved to reports/figures). All values come from computed tables."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from og_oip import config

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.25, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9})
NOTE = "SYNTHETIC data - PetroNexa Energy (fictional)"


def _save(fig, name, note=NOTE):
    if note:
        fig.text(0.99, 0.005, note, ha="right", va="bottom", fontsize=7, color="gray")
    p = config.FIGURES_DIR / f"{name}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0, 0.02, 1, 1)); fig.savefig(p); plt.close(fig)
    return p


def production_trend(fm):
    p = fm.pivot_table(index="month", columns="field_id", values="oil_bbl", aggfunc="sum") / 1e3
    fig, ax = plt.subplots(figsize=(8, 4)); p.plot.area(ax=ax, alpha=0.8); ax.set_ylabel("Oil (thousand bbl / month)"); ax.set_title("Monthly oil production by field")
    return _save(fig, "production_trend_by_field")


def loss_by_field(bf):
    fig, ax = plt.subplots(figsize=(7, 4)); d = bf.sort_values("field_id")
    ax.bar(d.field_id, d.loss_bbl / 1e3, color="#c0504d"); ax.set_ylabel("Production loss (thousand bbl)"); ax.set_title("Production loss vs simulated potential, by field")
    for i, (l, p) in enumerate(zip(d.loss_bbl / 1e3, d.loss_pct)): ax.text(i, l, f"{p:.1f}%", ha="center", va="bottom")
    return _save(fig, "production_loss_by_field")


def loss_decomposition(wd):
    m = wd.groupby("month")[["downtime_loss_bbl", "other_loss_bbl"]].sum() / 1e3
    x = np.arange(len(m)); fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x, m.downtime_loss_bbl.values, color="#c0504d", label="Downtime-related loss")
    ax.bar(x, m.other_loss_bbl.values, bottom=m.downtime_loss_bbl.values, color="#f79646", label="Other (efficiency) loss")
    ax.set_ylabel("thousand bbl"); ax.set_xticks(x[::3]); ax.set_xticklabels([d.strftime("%Y-%m") for d in m.index[::3]], rotation=45)
    ax.legend(); ax.set_title("Production loss decomposition (downtime vs other)")
    return _save(fig, "loss_decomposition_monthly")


def downtime_pareto(es, top=15):
    d = es.sort_values("total_downtime_hours", ascending=False).head(top)
    fig, ax = plt.subplots(figsize=(9, 4)); ax.bar(d.equipment_id, d.total_downtime_hours, color="#4f81bd"); ax.tick_params(axis="x", rotation=60)
    ax2 = ax.twinx(); ax2.plot(d.equipment_id, 100 * d.total_downtime_hours.cumsum() / es.total_downtime_hours.sum(), color="k", marker="o", ms=3); ax2.set_ylabel("cumulative % of fleet downtime"); ax2.grid(False)
    ax.set_ylabel("Downtime hours"); ax.set_title(f"Top {top} equipment by downtime hours (Pareto)")
    return _save(fig, "equipment_downtime_pareto")


def mtbf_mttr(bt):
    fig, axs = plt.subplots(1, 2, figsize=(9, 4)); d = bt.sort_values("mtbf_hours")
    axs[0].barh(d.equipment_type, d.mtbf_hours, color="#9bbb59"); axs[0].set_title("MTBF (hours)"); axs[1].barh(d.equipment_type, d.mttr_hours, color="#8064a2"); axs[1].set_title("MTTR (hours)")
    return _save(fig, "mtbf_mttr_by_type")


def cost_per_bbl(fm):
    d = fm.groupby("month").agg(o=("opex_total_usd", "sum"), b=("oil_sold_bbl", "sum"), r=("revenue_usd", "sum")).reset_index()
    fig, ax = plt.subplots(figsize=(8, 4)); ax.plot(d.month, d.o / d.b, label="Opex per bbl oil sold"); ax.plot(d.month, d.r / d.b, label="Revenue per bbl oil sold (incl. gas revenue)")
    ax.legend(); ax.set_ylabel("USD / bbl (synthetic)"); ax.set_title("Unit economics (synthetic)")
    return _save(fig, "unit_economics_monthly")


def stockout_by_category(bc):
    fig, ax = plt.subplots(figsize=(7, 4)); d = bc.sort_values("stockout_rate_pct")
    ax.barh(d.material_category, d.stockout_rate_pct, color="#f79646"); ax.set_xlabel("Stockout rate (% of item-warehouse-days)"); ax.set_title("Stockout rate by material category")
    return _save(fig, "stockout_by_category")


def hse_monthly(hm):
    m = hm.groupby("month")[["incidents", "lost_time_incidents"]].sum()
    fig, ax = plt.subplots(figsize=(8, 4)); ax.bar(m.index, m.incidents, width=20, label="All incidents"); ax.bar(m.index, m.lost_time_incidents, width=20, label="Lost-time", color="#c0504d")
    ax.legend(); ax.set_title("HSE incidents per month (synthetic)")
    return _save(fig, "hse_incidents_monthly")


def forecast_plot(series, fc, name="forecast_portfolio_oil", title="Portfolio daily oil - 30 day forecast"):
    fig, ax = plt.subplots(figsize=(8, 4)); s = series.iloc[-120:]; ax.plot(s.index, s.values, label="Actual (last 120 days)")
    ax.plot(fc.date, fc.forecast_oil_bbl, "r--", label=f"Forecast: {fc.model.iloc[0]}"); ax.legend(); ax.set_ylabel("bbl/day"); ax.set_title(title)
    return _save(fig, name)


def ml_curves(res, scores, y):
    from sklearn.metrics import precision_recall_curve, roc_curve
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    for n, p in scores.items():
        f, t, _ = roc_curve(y, p); axs[0].plot(f, t, label=n)
        pr, rc, _ = precision_recall_curve(y, p); axs[1].plot(rc, pr, label=n)
    axs[0].plot([0, 1], [0, 1], "k:"); axs[0].set_title("ROC (test set)"); axs[0].set_xlabel("FPR"); axs[0].set_ylabel("TPR")
    axs[1].axhline(y.mean(), color="k", ls=":", label="prevalence"); axs[1].set_title("Precision-Recall (test set)"); axs[1].set_xlabel("Recall"); axs[1].legend(fontsize=7)
    return _save(fig, "ml_roc_pr_test")


def ml_importance(fi):
    d = fi.head(12).iloc[::-1]; fig, ax = plt.subplots(figsize=(7, 4)); ax.barh(d.feature, d.rf_importance); ax.set_title("Random Forest feature importance (synthetic sensor data)")
    return _save(fig, "ml_feature_importance")


def volve_field(fm):
    fig, ax = plt.subplots(figsize=(8, 4)); ax.plot(fm.month, fm.avg_daily_oil_bbl / 1e3, label="Oil (k bbl/d)"); ax2 = ax.twinx(); ax2.plot(fm.month, fm.water_cut_pct, color="tab:blue", ls="--", label="Water cut %"); ax2.grid(False)
    ax.set_ylabel("k bbl/day"); ax2.set_ylabel("water cut %"); ax.set_title("Volve (REAL data): field oil rate and water cut")
    return _save(fig, "volve_field_rate_watercut", note="REAL data: Volve (user-supplied). Not PetroNexa.")


def volve_wells(ws):
    d = ws.sort_values("cum_oil_bbl"); fig, ax = plt.subplots(figsize=(7, 4)); ax.barh(d.wellbore, d.cum_oil_bbl / 1e6); ax.set_xlabel("Cumulative oil (million bbl)"); ax.set_title("Volve (REAL data): cumulative oil by wellbore")
    return _save(fig, "volve_cum_oil_by_well", note="REAL data: Volve (user-supplied). Not PetroNexa.")


def bsee_monthly(m):
    fig, ax = plt.subplots(figsize=(8, 4)); ax.plot(m.month, m.oil_bbl / 1e6, marker="o", label="Oil (million bbl / month)"); ax.set_ylabel("million bbl"); ax2 = ax.twinx()
    ax2.plot(m.month, m.water_to_oil_ratio, color="tab:green", marker="s", ls="--", label="Water/oil ratio"); ax2.grid(False); ax.set_title("BSEE OGOR-A (REAL data): monthly totals, 2025-01 to 2026-06")
    return _save(fig, "bsee_monthly_totals", note="REAL data: BSEE OGOR-A (user-supplied). Not PetroNexa.")


def bsee_operators(op, top=10):
    d = op.head(top).iloc[::-1]; fig, ax = plt.subplots(figsize=(8, 4.5)); ax.barh(d.operator_name.str.slice(0, 32), d.oil_bbl / 1e6); ax.set_xlabel("Oil (million bbl, 18 months)")
    ax.set_title(f"BSEE OGOR-A (REAL data): top {top} operators by reported oil")
    return _save(fig, "bsee_top_operators", note="REAL data: BSEE OGOR-A (user-supplied). Not PetroNexa.")
