"""Sales, operating cost and HSE simulation (SYNTHETIC assumptions documented in docs/)."""
from __future__ import annotations

import numpy as np
import pandas as pd

OIL_SALES_RATIO = 0.985
GAS_SALES_RATIO = 0.92          # fuel/flare/shrink
ENERGY_TARIFF_USD_KWH = 0.09
COST_CATEGORIES = ["Production", "Energy", "Labor", "Maintenance", "Transportation", "Utilities", "Other"]


def price_series(rng, dates):
    months = pd.period_range(dates[0], dates[-1], freq="M")
    lo, lg = np.log(75.0), np.log(3.2)
    oil, gas = [], []
    for _ in months:
        lo = lo + 0.25 * (np.log(72.0) - lo) + rng.normal(0, 0.06)
        lg = lg + 0.25 * (np.log(3.2) - lg) + rng.normal(0, 0.10)
        oil.append(float(np.clip(np.exp(lo), 45, 110))); gas.append(float(np.clip(np.exp(lg), 1.8, 5.5)))
    return pd.DataFrame({"month": months, "oil": oil, "gas": gas})


def simulate_sales(rng, production, wells, fields, dates):
    p = production.merge(wells[["well_id", "field_id"]], on="well_id")
    d = p.groupby(["date", "field_id"], as_index=False)[["oil_production_bbl", "gas_production_mcf"]].sum()
    px = price_series(rng, dates)
    d["month"] = pd.PeriodIndex(pd.to_datetime(d["date"]), freq="M")
    d = d.merge(px, on="month")
    diff = {f: -rng.uniform(1.0, 5.0) for f in fields.field_id}
    d["oil_volume_bbl"] = (d.oil_production_bbl * OIL_SALES_RATIO * (1 + rng.normal(0, 0.005, len(d)))).round(1)
    d["gas_volume_mcf"] = (d.gas_production_mcf * GAS_SALES_RATIO * (1 + rng.normal(0, 0.005, len(d)))).round(1)
    d["oil_price_usd"] = (d.oil * (1 + rng.normal(0, 0.008, len(d))) + d.field_id.map(diff)).round(2)
    d["gas_price_usd"] = (d.gas * (1 + rng.normal(0, 0.01, len(d)))).round(3)
    d["revenue_usd"] = (d.oil_volume_bbl * d.oil_price_usd + d.gas_volume_mcf * d.gas_price_usd).round(2)
    return d[["date", "field_id", "oil_volume_bbl", "gas_volume_mcf", "oil_price_usd", "gas_price_usd", "revenue_usd"]].sort_values(["date", "field_id"]).reset_index(drop=True)


def simulate_operating_cost(rng, production, sales, sensor, maint, equipment, wells, dates):
    fld = equipment.set_index("equipment_id")["field_id"]
    s = sensor.copy()
    s["date"] = s.timestamp.dt.date
    s["field_id"] = s.equipment_id.map(fld)
    kwh = s.groupby(["date", "field_id"])["energy_consumption_kwh"].sum().rename("kwh")
    m = maint.copy(); m["field_id"] = m.equipment_id.map(fld)
    mcost = m.groupby(["date", "field_id"])["total_cost"].sum().rename("mcost")
    ncorr = m[m.maintenance_type == "Corrective"].groupby(["date", "field_id"]).size().rename("ncorr")
    pw = production.merge(wells[["well_id", "field_id"]], on="well_id")
    nw = pw[pw.oil_production_bbl > 0].groupby(["date", "field_id"]).size().rename("nwells")
    base = sales.set_index(["date", "field_id"])[["oil_volume_bbl"]].join([kwh, mcost, ncorr, nw]).fillna(0).reset_index()
    n = len(base)
    tariff_m = 1 + 0.10 * np.sin(2 * np.pi * pd.to_datetime(base["date"]).dt.month / 12)
    cats = {
        "Production": base.nwells * 1000 * (1 + rng.normal(0, 0.03, n)) + base.oil_volume_bbl * 5.0,
        "Energy": base.kwh * ENERGY_TARIFF_USD_KWH * tariff_m,
        "Labor": base.nwells * 1350 * (1 + rng.normal(0, 0.03, n)) + base.ncorr * 800,
        "Maintenance": base.mcost,
        "Transportation": base.oil_volume_bbl * 3.0 * (1 + rng.normal(0, 0.05, n)),
        "Utilities": 6000 * (1 + rng.normal(0, 0.08, n)),
        "Other": rng.lognormal(np.log(4500), 0.4, n),
    }
    rows = []
    for c, v in cats.items():
        rows.append(pd.DataFrame({"date": base["date"], "field_id": base.field_id, "cost_category": c,
                                  "cost_amount_usd": np.round(np.clip(v, 0, None), 2)}))
    return pd.concat(rows).sort_values(["date", "field_id", "cost_category"]).reset_index(drop=True)


INCIDENT_TYPES = ["Near Miss", "First Aid", "Equipment Damage", "Environmental Release", "Process Safety Event", "Injury", "Vehicle Incident"]
INCIDENT_P = [0.35, 0.18, 0.14, 0.09, 0.06, 0.12, 0.06]
SEV_P = {"Near Miss": [0.6, 0.35, 0.05, 0.0], "First Aid": [0.7, 0.3, 0.0, 0.0], "Equipment Damage": [0.3, 0.45, 0.2, 0.05],
         "Environmental Release": [0.35, 0.4, 0.2, 0.05], "Process Safety Event": [0.2, 0.4, 0.3, 0.1],
         "Injury": [0.1, 0.5, 0.3, 0.1], "Vehicle Incident": [0.4, 0.4, 0.15, 0.05]}
SEVERITIES = ["Low", "Medium", "High", "Critical"]
DEPT = {"Near Miss": ["Operations", "Maintenance", "Facilities"], "First Aid": ["Operations", "Maintenance"],
        "Equipment Damage": ["Maintenance", "Operations"], "Environmental Release": ["Operations", "Facilities"],
        "Process Safety Event": ["Operations", "Facilities"], "Injury": ["Maintenance", "Operations", "Logistics"],
        "Vehicle Incident": ["Logistics"]}
ROOT_CAUSES = ["Equipment Failure", "Human Error", "Procedure Not Followed", "Inadequate Maintenance",
               "Environmental Conditions", "Contractor Activity", "Unknown"]


def simulate_hse(rng, maint, equipment, wells, fields, dates):
    fld = equipment.set_index("equipment_id")["field_id"]
    m = maint[maint.maintenance_type == "Corrective"].copy(); m["field_id"] = m.equipment_id.map(fld)
    nwell = wells.groupby("field_id").size()
    corr = {f: np.zeros(len(dates)) for f in fields.field_id}
    day_of = {d.date(): i for i, d in enumerate(dates)}
    for r in m.itertuples():
        corr[r.field_id][day_of[r.date]] += 1
    rows = []
    for f in fields.field_id:
        c7 = pd.Series(corr[f]).rolling(7, min_periods=1).sum().values
        c3 = pd.Series(corr[f]).rolling(3, min_periods=1).sum().values
        lam = 0.09 * (nwell[f] / 16) * (1 + 0.15 * c7)
        k = rng.poisson(lam)
        for di in np.nonzero(k)[0]:
            for _ in range(k[di]):
                t = str(rng.choice(INCIDENT_TYPES, p=INCIDENT_P))
                sev = str(rng.choice(SEVERITIES, p=SEV_P[t]))
                lt = int(t == "Injury" and rng.random() < {"Low": 0.05, "Medium": 0.35, "High": 0.7, "Critical": 1.0}[sev])
                p = np.array([0.15, 0.22, 0.14, 0.12, 0.08, 0.08, 0.21])
                if c3[di] > 0:
                    p[0] += 0.25; p[3] += 0.10
                p = p / p.sum()
                rows.append(dict(date=dates[di].date(), field_id=f, incident_type=t, severity=sev, lost_time_flag=lt,
                                 days_lost=int(1 + rng.geometric(0.2)) if lt else 0,
                                 root_cause=str(rng.choice(ROOT_CAUSES, p=p)), department=str(rng.choice(DEPT[t]))))
    df = pd.DataFrame(rows).sort_values(["date", "field_id"]).reset_index(drop=True)
    df.insert(0, "incident_id", [f"HSE-{i + 1:06d}" for i in range(len(df))])
    return df
