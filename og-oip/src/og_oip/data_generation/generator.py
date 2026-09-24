"""Orchestrates the synthetic PetroNexa Energy data generation (deterministic for a given seed)."""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from og_oip import config
from og_oip.data_generation import commercial, dimensions as dim, operations as ops, supply_chain as sc

FACT_TABLES = ["fact_production", "fact_sensor", "fact_maintenance", "fact_maintenance_material", "fact_sales",
               "fact_operating_cost", "fact_inventory", "fact_purchase_order", "fact_hse"]
DIM_TABLES = ["dim_date", "dim_field", "dim_well", "dim_equipment", "dim_supplier", "dim_material",
              "dim_warehouse", "bridge_equipment_well"]


def generate_all(seed: int = config.RANDOM_SEED) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(config.START_DATE, config.END_DATE, freq="D")
    dim_date = dim.build_dim_date()
    fields = dim.build_dim_field(rng)
    equipment = dim.build_dim_equipment(rng, fields)
    suppliers = dim.build_dim_supplier(rng)
    materials = dim.build_dim_material(rng, suppliers)
    warehouses = dim.build_dim_warehouse(fields)
    wells, params = dim.build_dim_well(rng, fields, equipment)
    bridge = dim.build_bridge_equipment_well(rng, wells, equipment)
    pairs = sc.assign_stock_pairs(materials, warehouses)

    wh_of_field = warehouses.set_index("field_id")["warehouse_id"].to_dict()
    mats_by_field = {}
    for f, wh in wh_of_field.items():
        ids = pairs[pairs.warehouse_id == wh]["material_id"]
        sub = materials[materials.material_id.isin(ids)]
        mats_by_field[f] = {c: g for c, g in sub.groupby("material_category")}

    maint, maint_mat, precursors = ops.simulate_maintenance(rng, equipment, mats_by_field, dates)
    well_dt, attributed = ops.well_downtime_matrix(rng, maint, bridge, wells, dates)
    eq_dt = ops.equipment_downtime_matrix(maint, equipment, dates)
    sensor = ops.simulate_sensors(rng, equipment, precursors, eq_dt, dates)
    production = ops.simulate_production(rng, wells, params, well_dt, dates)
    sales = commercial.simulate_sales(rng, production, wells, fields, dates)
    opcost = commercial.simulate_operating_cost(rng, production, sales, sensor, maint, equipment, wells, dates)
    hse = commercial.simulate_hse(rng, maint, equipment, wells, fields, dates)
    inventory, po, materials = sc.simulate_inventory(rng, materials, suppliers, warehouses, pairs, maint, maint_mat, dates)

    maint_mat = maint_mat.groupby(["maintenance_id", "material_id"], as_index=False).agg(quantity=("quantity", "sum")).copy()
    maint_mat["warehouse_id"] = maint.set_index("maintenance_id").loc[maint_mat.maintenance_id, "equipment_id"].map(
        equipment.set_index("equipment_id")["field_id"]).map(wh_of_field).values
    tables = {
        "dim_date": dim_date, "dim_field": fields, "dim_well": wells, "dim_equipment": equipment,
        "dim_supplier": suppliers, "dim_material": materials, "dim_warehouse": warehouses,
        "bridge_equipment_well": bridge,
        "fact_production": production, "fact_sensor": sensor, "fact_maintenance": maint,
        "fact_maintenance_material": maint_mat, "fact_sales": sales, "fact_operating_cost": opcost,
        "fact_inventory": inventory, "fact_purchase_order": po, "fact_hse": hse,
    }
    tables["_well_params"] = params          # generator ground truth (documented), not loaded to DB
    tables["_sensor_precursors"] = precursors
    return tables


def manifest(tables: dict[str, pd.DataFrame], seed: int) -> dict:
    out = {"seed": seed, "company": config.COMPANY + " (FICTIONAL)", "notice": config.SYNTHETIC_NOTICE, "tables": {}}
    for k, v in tables.items():
        h = hashlib.sha256(pd.util.hash_pandas_object(v, index=False).values.tobytes()).hexdigest()[:16]
        out["tables"][k] = {"rows": int(len(v)), "columns": list(map(str, v.columns)), "content_hash": h}
    out["total_fact_rows"] = int(sum(len(tables[t]) for t in FACT_TABLES))
    return out
