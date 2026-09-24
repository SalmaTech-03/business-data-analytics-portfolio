"""Inventory and purchase-order simulation (SYNTHETIC)."""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

ROUTINE_MEAN_PER_DAY = {"Lubricants": 6.0, "Chemicals": 4.0, "Filters": 0.4, "Seals": 0.3, "Bearings": 0.1,
                        "Valves": 0.05, "Electrical": 0.15, "Piping": 0.1}


def assign_stock_pairs(materials: pd.DataFrame, warehouses: pd.DataFrame) -> pd.DataFrame:
    """Each material is stocked in 2 of the 4 warehouses; every warehouse stocks every category."""
    rows = []
    nw = len(warehouses)
    for c_i, (cat, g) in enumerate(materials.groupby("material_category", sort=True)):
        for k, m in enumerate(g.itertuples()):
            for off in (0, 1):
                rows.append({"material_id": m.material_id, "warehouse_id": warehouses.warehouse_id.iloc[(c_i + k + off) % nw]})
    return pd.DataFrame(rows)


def simulate_inventory(rng, materials, suppliers, warehouses, pairs, maint, maint_mat, dates):
    n_days, P = len(dates), len(pairs)
    mat = materials.set_index("material_id")
    wh_of_field = warehouses.set_index("field_id")["warehouse_id"].to_dict()
    pair_idx = {(r.material_id, r.warehouse_id): i for i, r in enumerate(pairs.itertuples())}
    day_of = {d.date(): i for i, d in enumerate(dates)}
    mm = maint_mat.merge(maint[["maintenance_id", "date"]], on="maintenance_id")
    maint_dem = np.zeros((n_days, P))
    for r in mm.itertuples():
        maint_dem[day_of[r.date], pair_idx[(r.material_id, wh_of_field[r.field_id])]] += r.quantity
    cats = np.array([mat.loc[m, "material_category"] for m in pairs.material_id])
    routine_mean = np.array([ROUTINE_MEAN_PER_DAY[c] for c in cats]) * rng.uniform(0.6, 1.4, P)
    routine = rng.poisson(routine_mean, size=(n_days, P)).astype(float)
    demand = routine + maint_dem
    mean_dem = demand.mean(axis=0)
    quoted = np.array([mat.loc[m, "lead_time_days"] for m in pairs.material_id])
    sup_id = np.array([mat.loc[m, "primary_supplier_id"] for m in pairs.material_id])
    ucost = np.array([mat.loc[m, "unit_cost"] for m in pairs.material_id])
    rop = np.ceil(mean_dem * quoted * 1.25) + 1
    qty = np.ceil(mean_dem * 35) + 1
    sup_ids = suppliers.supplier_id.tolist()
    ontime = dict(zip(sup_ids, rng.uniform(0.55, 0.95, len(sup_ids))))
    stock = rop * 2 + qty / 2
    on_order = np.zeros(P)
    arrivals = defaultdict(lambda: np.zeros(P))
    O, R, C, CL, SO = (np.zeros((n_days, P)) for _ in range(5))
    pos = []
    for d in range(n_days):
        opening = stock.copy()
        rec = arrivals.pop(d, np.zeros(P))
        avail = opening + rec
        cons = np.minimum(demand[d], avail)
        closing = avail - cons
        O[d], R[d], C[d], CL[d], SO[d] = opening, rec, cons, closing, demand[d] > avail + 1e-9
        on_order -= rec
        for p in np.nonzero((closing + on_order) <= rop)[0]:
            s = sup_id[p]
            late = rng.random() > ontime[s]
            actual = int(quoted[p] + (rng.integers(2, 15) if late else rng.integers(-2, 1)))
            actual = max(actual, 1)
            arr = d + actual
            if arr < n_days:
                arrivals[arr][p] += qty[p]
            on_order[p] += qty[p]
            pos.append(dict(order_date=dates[d].date(), material_id=pairs.material_id.iloc[p], supplier_id=s,
                            warehouse_id=pairs.warehouse_id.iloc[p], quantity=int(qty[p]),
                            quoted_lead_time_days=int(quoted[p]), promised_date=(dates[d] + pd.Timedelta(days=int(quoted[p]))).date(),
                            received_date=dates[arr].date() if arr < n_days else pd.NaT,
                            unit_cost=float(ucost[p])))
        stock = closing
    n = n_days * P
    fact = pd.DataFrame({
        "date": np.repeat(dates.date, P), "material_id": np.tile(pairs.material_id.values, n_days),
        "supplier_id": np.tile(sup_id, n_days), "warehouse_id": np.tile(pairs.warehouse_id.values, n_days),
        "opening_stock": O.ravel(), "receipts": R.ravel(), "consumption": C.ravel(), "closing_stock": CL.ravel(),
        "reorder_level": np.tile(rop, n_days), "unit_cost": np.tile(ucost, n_days),
        "stockout_flag": SO.ravel().astype(int),
    })
    po = pd.DataFrame(pos)
    po.insert(0, "po_id", [f"PO-{i + 1:06d}" for i in range(len(po))])
    po["received_date"] = pd.to_datetime(po["received_date"]).dt.date
    po["status"] = np.where(po.received_date.isna(), "Open", "Received")
    new_rop = pd.Series(rop, index=pairs.material_id.values).groupby(level=0).mean().round().astype(int)
    materials = materials.copy()
    materials["reorder_level"] = materials.material_id.map(new_rop).astype(int)
    return fact, po, materials
