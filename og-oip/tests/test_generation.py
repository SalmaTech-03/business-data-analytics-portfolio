from _common import *  # noqa
import numpy as np
import pandas as pd
from og_oip import config
from og_oip.data_generation import generator
from og_oip.validation.checks import run_all_checks


def test_reproducible_for_same_seed():
    a = generator.manifest(generator.generate_all(7), 7)
    b = generator.manifest(generator.generate_all(7), 7)
    assert a["tables"] == b["tables"]


def test_different_seed_differs():
    a = generator.manifest(generator.generate_all(7), 7)["tables"]["fact_production"]["content_hash"]
    assert a != generator.manifest(truth(), 42)["tables"]["fact_production"]["content_hash"]


def test_scale_and_table_counts():
    t = truth()
    assert len(t["dim_field"]) == 4 and len(t["dim_well"]) == 60 and len(t["dim_equipment"]) == 48
    total = sum(len(t[k]) for k in generator.FACT_TABLES)
    assert total > 250_000, total
    for k in generator.DIM_TABLES + generator.FACT_TABLES:
        assert len(t[k]) > 0, k


def test_clean_truth_passes_all_validation_checks():
    res = run_all_checks({k: v for k, v in truth().items() if not k.startswith("_")}, "truth")
    bad = res[res.status != "PASS"]
    assert bad.empty, bad[["table", "check", "column", "failed_rows"]].to_string()


def test_business_relationships_hold():
    t = truth()
    m, mm, mat = t["fact_maintenance"], t["fact_maintenance_material"], t["dim_material"].set_index("material_id")
    cost = (mm.quantity * mm.material_id.map(mat.unit_cost)).groupby(mm.maintenance_id).sum()
    j = m.set_index("maintenance_id").material_cost
    assert np.allclose(j.reindex(cost.index).values, cost.values, atol=0.05)
    p = t["fact_production"]
    assert (p.oil_production_bbl <= p.potential_production_bbl * 1.0001 + 0.1).mean() > 0.999
    assert ((p.operating_hours + p.downtime_hours - 24).abs() < 0.02).all()
    oc = t["fact_operating_cost"]; eq = t["dim_equipment"].set_index("equipment_id").field_id
    mcost = m.assign(field_id=m.equipment_id.map(eq)).groupby(["date", "field_id"]).total_cost.sum()
    occ = oc[oc.cost_category == "Maintenance"].set_index(["date", "field_id"]).cost_amount_usd
    assert np.allclose(mcost.reindex(occ.index).fillna(0).values, occ.values, atol=0.05)


def test_all_dimension_keys_used_and_no_real_names():
    t = truth()
    assert set(t["fact_production"].well_id) <= set(t["dim_well"].well_id)
    assert all(n.startswith("Synthetic Field") for n in t["dim_field"].field_name)
    assert set(t["dim_field"].operator) == {config.COMPANY}
