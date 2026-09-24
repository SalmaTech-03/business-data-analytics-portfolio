"""Dimension tables (all SYNTHETIC / fictional)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from og_oip import config

WELLS_PER_FIELD = [18, 16, 14, 12]
FIELD_NAMES = ["Synthetic Field Alpha", "Synthetic Field Bravo", "Synthetic Field Charlie", "Synthetic Field Delta"]
FIELD_QI_FACTOR = [1.3, 1.0, 0.8, 1.1]

EQUIP_TYPES = ["Pump"] * 4 + ["Compressor"] * 2 + ["Separator"] * 2 + ["Generator", "Valve", "Heat Exchanger", "Pipeline Equipment"]

MATERIAL_CATEGORIES = {   # category: (base unit cost USD, unit, supplier category)
    "Seals": (150, "EA", "Mechanical Parts"),
    "Bearings": (900, "EA", "Mechanical Parts"),
    "Lubricants": (60, "L", "Lubricants & Chemicals"),
    "Valves": (2500, "EA", "Valves & Fittings"),
    "Filters": (120, "EA", "Filtration"),
    "Electrical": (700, "EA", "Electrical"),
    "Piping": (1200, "EA", "Piping"),
    "Chemicals": (90, "KG", "Lubricants & Chemicals"),
}
SUPPLIER_SPECS = [  # name, category
    ("Aurelia Industrial Supply", "Mechanical Parts"),
    ("Borealis Machine Parts", "Mechanical Parts"),
    ("Cobalt Valve & Fitting Co", "Valves & Fittings"),
    ("Delmar Lubricants & Chemicals", "Lubricants & Chemicals"),
    ("Everglen Filtration Systems", "Filtration"),
    ("Fulcrum Electrical Works", "Electrical"),
    ("Granite Pipe & Flange Ltd", "Piping"),
    ("Helix Chemical Trading", "Lubricants & Chemicals"),
]
SUPPLIER_LEAD = {"Mechanical Parts": 14, "Valves & Fittings": 21, "Lubricants & Chemicals": 7,
                 "Filtration": 10, "Electrical": 18, "Piping": 24}
MANUFACTURERS = ["Norvane Systems", "Kestrel Dynamics", "Tarsis Machinery", "Omnigrid Industrial", "Vantor Process"]


def build_dim_date() -> pd.DataFrame:
    d = pd.date_range(config.START_DATE, config.END_DATE, freq="D")
    return pd.DataFrame({
        "date_key": d.strftime("%Y%m%d").astype(int),
        "date": d.date,
        "year": d.year, "quarter": d.quarter, "month": d.month,
        "month_name": d.strftime("%B"),
        "week": d.isocalendar().week.astype(int).values,
        "day": d.day, "day_of_week": d.dayofweek + 1,
        "is_weekend": (d.dayofweek >= 5),
    })


def build_dim_field(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i, name in enumerate(FIELD_NAMES, 1):
        rows.append({
            "field_id": f"FIELD-{i:03d}", "field_name": name,
            "region": f"Synthetic Region {'NSEW'[i - 1]}", "basin": f"Synthetic Basin {1 + (i - 1) // 2}",
            "field_type": "Onshore" if i % 2 else "Offshore", "operator": config.COMPANY,
            "commission_date": pd.Timestamp("2008-01-01") + pd.Timedelta(days=int(rng.integers(0, 1500))),
            "status": "Producing",
        })
    df = pd.DataFrame(rows)
    df["commission_date"] = df["commission_date"].dt.date
    return df


def build_dim_equipment(rng: np.random.Generator, fields: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = 1
    for fid in fields["field_id"]:
        for k, et in enumerate(EQUIP_TYPES, 1):
            crit = {"Pump": "Medium", "Compressor": "High", "Separator": "High", "Generator": "High",
                    "Valve": "Low", "Heat Exchanger": "Medium", "Pipeline Equipment": "Medium"}[et]
            if rng.random() < 0.2:  # some variation
                crit = str(rng.choice(["Low", "Medium", "High"]))
            rows.append({
                "equipment_id": f"EQ-{n:04d}", "equipment_name": f"{et} {fid[-3:]}-{k:02d}",
                "equipment_type": et, "field_id": fid, "manufacturer": str(rng.choice(MANUFACTURERS)),
                "installation_date": (pd.Timestamp("2008-06-01") + pd.Timedelta(days=int(rng.integers(0, 4700)))).date(),
                "criticality": crit, "status": "In Service",
            })
            n += 1
    return pd.DataFrame(rows)


def build_dim_supplier(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i, (name, cat) in enumerate(SUPPLIER_SPECS, 1):
        rows.append({
            "supplier_id": f"SUP-{i:03d}", "supplier_name": name, "supplier_category": cat,
            "region": f"Synthetic Region {'NSEW'[int(rng.integers(0, 4))]}",
            "lead_time_days": int(SUPPLIER_LEAD[cat] + rng.integers(-2, 4)),
            "supplier_rating": round(float(rng.uniform(2.8, 4.8)), 1),
        })
    return pd.DataFrame(rows)


def build_dim_material(rng: np.random.Generator, suppliers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = 1
    for cat, (base, unit, scat) in MATERIAL_CATEGORIES.items():
        cands = suppliers[suppliers["supplier_category"] == scat]
        for k in range(1, 6):
            sup = cands.iloc[int(rng.integers(0, len(cands)))]
            cost = round(float(base * rng.lognormal(0, 0.35)), 2)
            rows.append({
                "material_id": f"MAT-{n:03d}", "material_name": f"{cat} Item {k:02d}",
                "material_category": cat, "unit": unit, "unit_cost": cost,
                "reorder_level": int(max(3, round(rng.uniform(4, 14) * (300 / max(cost, 30)) ** 0.35))),
                "lead_time_days": int(sup["lead_time_days"] + rng.integers(-1, 3)),
                "primary_supplier_id": sup["supplier_id"],
            })
            n += 1
    return pd.DataFrame(rows)


def build_dim_warehouse(fields: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "warehouse_id": [f"WH-{i:03d}" for i in range(1, len(fields) + 1)],
        "warehouse_name": [f"Synthetic Warehouse {i}" for i in range(1, len(fields) + 1)],
        "field_id": fields["field_id"].values,
    })


def build_dim_well(rng: np.random.Generator, fields: pd.DataFrame, equipment: pd.DataFrame):
    """Returns (dim_well, well_params). well_params are generator ground-truth parameters."""
    wells, params = [], []
    n = 1
    for f_idx, fid in enumerate(fields["field_id"]):
        pumps = equipment[(equipment.field_id == fid) & (equipment.equipment_type == "Pump")]["equipment_id"].tolist()
        for k in range(WELLS_PER_FIELD[f_idx]):
            new_well = rng.random() < 0.25
            if new_well:
                cd = pd.Timestamp(config.START_DATE) + pd.Timedelta(days=int(rng.integers(30, 900)))
            else:
                cd = pd.Timestamp("2011-01-01") + pd.Timedelta(days=int(rng.integers(0, 3600)))
            wid = f"WELL-{n:04d}"
            wells.append({
                "well_id": wid, "well_name": f"PNX-{fid[-1]}{k + 1:02d}", "field_id": fid,
                "well_type": str(rng.choice(["Vertical", "Directional", "Horizontal"], p=[0.3, 0.4, 0.3])),
                "reservoir": f"Synthetic Reservoir R{int(rng.integers(1, 4))}",
                "depth_m": int(rng.integers(1500, 4500)),
                # Synthetic local grid coordinates (NOT geographic positions)
                "latitude": round(float(f_idx + rng.uniform(0, 0.9)), 4),
                "longitude": round(float(f_idx * 1.5 + rng.uniform(0, 0.9)), 4),
                "commission_date": cd.date(), "status": "Producing",
                "primary_equipment_id": pumps[k % len(pumps)],
            })
            wo = rng.random() < 0.2
            params.append({
                "well_id": wid, "qi_bbl_d": float(700 * rng.lognormal(0, 0.45) * FIELD_QI_FACTOR[f_idx]),
                "di_annual": float(rng.uniform(0.25, 0.7)), "b": float(rng.uniform(0.3, 1.0)),
                "wc0": float(rng.uniform(0.05, 0.3)), "wc_max": float(rng.uniform(0.6, 0.92)),
                "wc_tau_d": float(rng.uniform(1200, 3500)), "gor0": float(rng.uniform(0.4, 1.6)),
                "p0": float(rng.uniform(2200, 4200)), "t0": float(rng.uniform(60, 95)),
                "workover_date": (pd.Timestamp(config.START_DATE) + pd.Timedelta(days=int(rng.integers(100, 1000)))) if wo else pd.NaT,
                "workover_uplift": float(rng.uniform(0.2, 0.4)) if wo else 0.0,
            })
            n += 1
    return pd.DataFrame(wells), pd.DataFrame(params)


def build_bridge_equipment_well(rng: np.random.Generator, wells: pd.DataFrame, equipment: pd.DataFrame) -> pd.DataFrame:
    """Which wells are affected when an equipment item is down, and by how much (impact_factor)."""
    factor = {"Compressor": 0.6, "Separator": 0.6, "Generator": 0.8, "Pipeline Equipment": 0.5}
    rows = []
    for _, e in equipment.iterrows():
        fw = wells[wells.field_id == e.field_id]["well_id"].tolist()
        et = e.equipment_type
        if et == "Pump":
            ws = wells[(wells.primary_equipment_id == e.equipment_id)]["well_id"].tolist(); imp = 1.0
        elif et in factor:
            ws = fw; imp = factor[et]
        else:  # Valve, Heat Exchanger: a fixed group of wells
            ws = list(rng.choice(fw, size=min(4, len(fw)), replace=False)); imp = 0.7
        rows += [{"equipment_id": e.equipment_id, "well_id": w, "impact_factor": imp} for w in ws]
    return pd.DataFrame(rows)
