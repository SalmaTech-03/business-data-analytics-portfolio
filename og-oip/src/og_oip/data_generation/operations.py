"""Synthetic operations simulation: failures -> maintenance -> downtime -> production; sensors.

All relationships below are SIMULATED assumptions documented in docs/data_generation_methodology.md.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from og_oip import config

FAILURE_RATE_PER_YEAR = {"Pump": 3.2, "Compressor": 2.6, "Separator": 1.2, "Generator": 2.0,
                         "Valve": 1.6, "Heat Exchanger": 1.4, "Pipeline Equipment": 0.9}
FAILURE_MEDIAN_HOURS = {"Pump": 18, "Compressor": 30, "Separator": 20, "Generator": 14,
                        "Valve": 8, "Heat Exchanger": 16, "Pipeline Equipment": 24}
FAILURE_TYPES = {
    "Pump": ["Bearing Failure", "Seal Leak", "Motor Overheating", "Impeller Wear"],
    "Compressor": ["Valve Failure", "Overheating", "Excessive Vibration", "Seal Leak"],
    "Separator": ["Level Control Fault", "Fouling", "Valve Failure"],
    "Generator": ["Electrical Fault", "Overheating", "Fuel System Fault"],
    "Valve": ["Actuator Failure", "Seat Leakage", "Stuck Valve"],
    "Heat Exchanger": ["Tube Fouling", "Tube Leak", "Gasket Failure"],
    "Pipeline Equipment": ["Corrosion Leak", "Flange Leak", "Pressure Fault"],
}
EQUIP_MATERIAL_CATS = {
    "Pump": ["Seals", "Bearings", "Lubricants"], "Compressor": ["Bearings", "Valves", "Filters", "Lubricants"],
    "Separator": ["Valves", "Piping", "Chemicals"], "Generator": ["Electrical", "Filters", "Lubricants"],
    "Valve": ["Valves", "Seals"], "Heat Exchanger": ["Piping", "Seals", "Chemicals"],
    "Pipeline Equipment": ["Piping", "Seals", "Chemicals"],
}
SENSOR_BASE = {  # temp C, pressure psi, vibration mm/s, flow m3/h (synthetic), kWh per 12h
    "Pump": (65, 900, 2.2, 90, 1200), "Compressor": (85, 1200, 3.0, 400, 6000),
    "Separator": (55, 450, 0.8, 120, 300), "Generator": (95, 60, 3.5, 15, 200),
    "Valve": (45, 800, 0.6, 90, 20), "Heat Exchanger": (70, 300, 0.9, 60, 150),
    "Pipeline Equipment": (40, 700, 0.7, 110, 400),
}
CREW = {"Pump": 3, "Compressor": 5, "Separator": 3, "Generator": 3, "Valve": 2, "Heat Exchanger": 3, "Pipeline Equipment": 4}
LABOR_RATE = 85.0


def spill_hours(start_idx: int, hours: float, n_days: int):
    """Spread downtime hours from start day forward, max 24h/day (documented assumption)."""
    out, d, left = [], start_idx, hours
    while left > 1e-9 and d < n_days:
        h = min(24.0, left)
        out.append((d, h))
        left -= h
        d += 1
    return out


def simulate_maintenance(rng, equipment, mats_by_field, dates):
    """Return (maintenance_df, maint_material_df, precursors list)."""
    n_days = len(dates)
    events, mm_rows, precursors = [], [], []
    seq = 1

    def pick_material(et, fid, n_lines, low, high):
        lines = []
        for _ in range(n_lines):
            cat = str(rng.choice(EQUIP_MATERIAL_CATS[et]))
            pool = mats_by_field[fid][cat]
            m = pool.iloc[int(rng.integers(0, len(pool)))]
            lines.append((m.material_id, int(rng.integers(low, high + 1)), float(m.unit_cost)))
        return lines

    for _, e in equipment.iterrows():
        et = e.equipment_type
        age_y0 = (pd.Timestamp(config.START_DATE) - pd.Timestamp(e.installation_date)).days / 365.25
        # preventive schedule
        pm_days = []
        d = int(rng.integers(10, 100))
        while d < n_days:
            pm_days.append(d)
            d += int(rng.integers(85, 125))
        pm_set = set(pm_days)
        last_pm = -int(rng.integers(0, 90))
        busy_until = -1
        crit_f = {"Low": 0.8, "Medium": 1.0, "High": 1.2}[e.criticality]
        for di in range(n_days):
            if di in pm_set:
                last_pm = di
                events.append(dict(seq=seq, equipment_id=e.equipment_id, di=di, maintenance_type="Preventive",
                                   failure_type="None", down=float(np.clip(rng.lognormal(np.log(6 if et != "Compressor" else 10), 0.3), 2, 24)),
                                   et=et, fid=e.field_id, lines=pick_material(et, e.field_id, 1, 2, 8)))
                seq += 1
                if rng.random() < 0.35:
                    events.append(dict(seq=seq, equipment_id=e.equipment_id, di=di, maintenance_type="Inspection",
                                       failure_type="None", down=float(rng.uniform(1, 3)), et=et, fid=e.field_id,
                                       lines=pick_material(et, e.field_id, 1, 1, 2) if rng.random() < 0.5 else []))
                    seq += 1
            if di <= busy_until:
                continue
            age = age_y0 + di / 365.25
            haz = FAILURE_RATE_PER_YEAR[et] / 365.0 * (1 + 0.04 * age) * (1 + 0.6 * min((di - last_pm) / 120, 2)) * crit_f / 1.4
            if rng.random() < haz:
                down = float(np.clip(rng.lognormal(np.log(FAILURE_MEDIAN_HOURS[et]), 0.7), 2, 240))
                ftype = str(rng.choice(FAILURE_TYPES[et]))
                events.append(dict(seq=seq, equipment_id=e.equipment_id, di=di, maintenance_type="Corrective",
                                   failure_type=ftype, down=down, et=et, fid=e.field_id,
                                   lines=pick_material(et, e.field_id, int(rng.integers(1, 3)), 1, 6)))
                seq += 1
                busy_until = di + int(np.ceil(down / 24))
                detectable = rng.random() < 0.75
                precursors.append(dict(equipment_id=e.equipment_id, fail_day=di, lead=int(rng.integers(4, 15)),
                                       severity=float(rng.lognormal(0, 0.4)), detectable=detectable))
        # false alarms (sensor excursions without failure)
        for _ in range(int(rng.poisson(1.5))):
            precursors.append(dict(equipment_id=e.equipment_id, fail_day=int(rng.integers(30, n_days - 5)),
                                   lead=int(rng.integers(4, 12)), severity=float(rng.lognormal(-0.2, 0.4)),
                                   detectable=True, false_alarm=True))
    ev = pd.DataFrame(events).sort_values(["di", "equipment_id", "seq"]).reset_index(drop=True)
    recs, mm = [], []
    last_day = n_days - 1
    for i, r in ev.iterrows():
        mid = f"MNT-{i + 1:06d}"
        lab = r.down * CREW[r.et] * LABOR_RATE * rng.lognormal(0, 0.15)
        pc = {"Corrective": 0.30, "Preventive": 0.08, "Inspection": 0.03}[r.maintenance_type]
        con = float(rng.lognormal(np.log(12000 if r.maintenance_type == "Corrective" else 5000), 0.6)) if rng.random() < pc else 0.0
        mat = 0.0
        for (matid, units, ucost) in r.lines:
            mat += units * ucost
            mm.append(dict(maintenance_id=mid, material_id=matid, quantity=units, field_id=r.fid))
        crit_hi = r.down > 48
        pr = "Critical" if (r.maintenance_type == "Corrective" and crit_hi) else (
            "High" if r.maintenance_type == "Corrective" else ("Medium" if r.maintenance_type == "Preventive" else "Low"))
        status = "In Progress" if r.di >= last_day - 6 and r.maintenance_type == "Corrective" and rng.random() < 0.5 else "Completed"
        recs.append(dict(maintenance_id=mid, equipment_id=r.equipment_id, date=dates[r.di].date(),
                         maintenance_type=r.maintenance_type, failure_type=r.failure_type,
                         downtime_hours=round(r.down, 2), labor_cost=round(lab, 2), material_cost=round(mat, 2),
                         contractor_cost=round(con, 2), total_cost=round(lab + mat + con, 2),
                         priority=pr, work_order_status=status))
    maint = pd.DataFrame(recs)
    maint_mat = pd.DataFrame(mm)
    return maint, maint_mat, pd.DataFrame(precursors)


def well_downtime_matrix(rng, maint, bridge, wells, dates):
    """days x wells matrix of downtime hours (equipment-attributed + background)."""
    n_days = len(dates)
    widx = {w: i for i, w in enumerate(wells.well_id)}
    day_of = {d.date(): i for i, d in enumerate(dates)}
    eq_wells = bridge.groupby("equipment_id").apply(lambda g: list(zip(g.well_id, g.impact_factor)), include_groups=False).to_dict()
    M = np.zeros((n_days, len(wells)))
    for r in maint.itertuples():
        di = day_of[r.date]
        for d, h in spill_hours(di, r.downtime_hours, n_days):
            for w, imp in eq_wells.get(r.equipment_id, []):
                M[d, widx[w]] += h * imp
    attributed = M.copy()
    bg = (rng.random(M.shape) < 0.02) * rng.uniform(1, 8, M.shape)   # unexplained short shut-ins
    M = np.clip(M + bg, 0, 24)
    return M, attributed


def equipment_downtime_matrix(maint, equipment, dates):
    n_days = len(dates)
    eidx = {e: i for i, e in enumerate(equipment.equipment_id)}
    day_of = {d.date(): i for i, d in enumerate(dates)}
    M = np.zeros((n_days, len(equipment)))
    for r in maint.itertuples():
        for d, h in spill_hours(day_of[r.date], r.downtime_hours, n_days):
            M[d, eidx[r.equipment_id]] += h
    return np.clip(M, 0, 24)


def simulate_sensors(rng, equipment, precursors, eq_down, dates):
    n_days = len(dates)
    n = n_days * 2
    ts = pd.DatetimeIndex([d + pd.Timedelta(hours=h) for d in dates for h in (6, 18)])
    frames = []
    pre_by_eq = {k: g for k, g in precursors.groupby("equipment_id")}
    for j, e in enumerate(equipment.itertuples()):
        bt, bp, bv, bf, bk = SENSOR_BASE[e.equipment_type]
        age0 = (pd.Timestamp(config.START_DATE) - pd.Timestamp(e.installation_date)).days / 365.25
        age = age0 + np.arange(n) / 2 / 365.25
        d = np.zeros(n)          # degradation index
        if e.equipment_id in pre_by_eq:
            for p in pre_by_eq[e.equipment_id].itertuples():
                if not p.detectable:
                    continue
                s, f = max(0, (p.fail_day - p.lead) * 2), p.fail_day * 2
                if f > s:
                    ramp = ((np.arange(s, f) - s) / (f - s)) ** 1.5
                    d[s:f] = np.maximum(d[s:f], ramp * p.severity)
        def ar1(scale):
            x = np.zeros(n); eps = rng.normal(0, scale, n)
            for i in range(1, n):
                x[i] = 0.6 * x[i - 1] + eps[i]
            return x
        dfrac = np.repeat(eq_down[:, j], 2) / 24.0     # share of the day down (same for both readings)
        run = 1 - np.clip(dfrac, 0, 1)
        vib = (bv * (1 + 0.012 * age) + 1.6 * d + ar1(0.06 * bv)) * np.where(run > 0.3, 1, 0.15)
        tmp = (bt + 10 * d + ar1(0.02 * bt)) * np.where(run > 0.3, 1, 0.6) + 8 * (1 - run)
        prs = (bp * (1 + rng.normal(0, 0.015, n)) + 0.05 * bp * d * (1 if j % 2 else -1))
        flw = bf * (1 - 0.07 * d) * run * (1 + rng.normal(0, 0.03, n))
        kwh = bk * (1 + 0.05 * d) * run * (1 + rng.normal(0, 0.04, n))
        frames.append(pd.DataFrame({
            "timestamp": ts, "equipment_id": e.equipment_id,
            "temperature_c": np.round(tmp, 2), "pressure_psi": np.round(prs, 1),
            "vibration_mm_s": np.round(np.clip(vib, 0.02, None), 3), "flow_rate": np.round(np.clip(flw, 0, None), 2),
            "energy_consumption_kwh": np.round(np.clip(kwh, 0, None), 1),
            "operating_hours": np.round(12 * run, 2),
        }))
    return pd.concat(frames, ignore_index=True)


def simulate_production(rng, wells, params, downtime, dates):
    n_days = len(dates)
    rows = []
    for j, w in enumerate(wells.itertuples()):
        p = params.iloc[j]
        t = (dates - pd.Timestamp(w.commission_date)).days.values.astype(float)
        m = t >= 0
        tt = np.where(m, t, 0)
        di = p.di_annual / 365.0
        q = p.qi_bbl_d / (1 + p.b * di * tt) ** (1 / p.b)
        if p.workover_uplift > 0:
            tw = (dates - p.workover_date).days.values.astype(float)
            q = q * (1 + np.where(tw >= 0, p.workover_uplift * np.exp(-np.clip(tw, 0, None) / 200), 0))
        potential = q * (1 + rng.normal(0, 0.03, n_days))
        dt = downtime[:, j]
        op = 24 - dt
        eff = np.clip(rng.normal(0.97, 0.03, n_days), 0.85, 1.0)
        pr_eps = rng.normal(0, 0.02, n_days)
        eff = eff * (1 - np.clip(-pr_eps - 0.02, 0, None) * 0.5)
        oil = potential * (op / 24) * eff
        wc = np.clip(p.wc0 + (p.wc_max - p.wc0) * (1 - np.exp(-tt / p.wc_tau_d)) + rng.normal(0, 0.01, n_days), 0.01, 0.97)
        wat = oil * wc / (1 - wc)
        gor = p.gor0 * (1 + 0.04 * tt / 365) * rng.lognormal(0, 0.05, n_days)
        gas = oil * gor
        press = p.p0 * (1 - 0.30 * (1 - np.exp(-tt / 2500))) * (1 + pr_eps)
        temp = p.t0 + rng.normal(0, 1.2, n_days)
        df = pd.DataFrame({
            "date": dates.date, "well_id": w.well_id,
            "operating_hours": np.round(op, 2), "downtime_hours": np.round(dt, 2),
            "oil_production_bbl": np.round(oil, 1), "gas_production_mcf": np.round(gas, 1),
            "water_production_bbl": np.round(wat, 1), "pressure_psi": np.round(press, 1),
            "temperature_c": np.round(temp, 1), "potential_production_bbl": np.round(potential, 1),
        })
        df["water_cut_pct"] = np.round(100 * df.water_production_bbl / (df.oil_production_bbl + df.water_production_bbl).replace(0, np.nan), 2).fillna(0.0)
        rows.append(df[m])
    out = pd.concat(rows, ignore_index=True)
    return out[["date", "well_id", "operating_hours", "downtime_hours", "oil_production_bbl", "gas_production_mcf",
                "water_production_bbl", "pressure_psi", "temperature_c", "water_cut_pct", "potential_production_bbl"]]
