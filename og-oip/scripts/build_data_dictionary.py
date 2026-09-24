"""Generate docs/data_dictionary.md from the ACTUAL processed CSV headers/dtypes plus a description map."""
import _bootstrap  # noqa: F401
import pandas as pd

from og_oip import config
from og_oip.data_generation.generator import DIM_TABLES, FACT_TABLES

D = {
 "date_key": "yyyymmdd integer key", "date": "Calendar date", "year": "Calendar year", "quarter": "Quarter 1-4", "month": "Month number", "month_name": "Month name", "week": "ISO week", "day": "Day of month", "day_of_week": "1=Mon..7=Sun", "is_weekend": "Weekend flag",
 "field_id": "Field key (FIELD-nnn)", "field_name": "Fictional field name", "region": "Synthetic region label", "basin": "Synthetic basin label", "field_type": "Onshore/Offshore", "operator": "Operating company (fictional PetroNexa Energy)", "commission_date": "Date put on production", "status": "Operational status",
 "well_id": "Well key (WELL-nnnn)", "well_name": "Well name", "well_type": "Vertical/Directional/Horizontal", "reservoir": "Synthetic reservoir label", "depth_m": "Depth in metres", "latitude": "Synthetic local grid Y (NOT geographic)", "longitude": "Synthetic local grid X (NOT geographic)", "primary_equipment_id": "Primary lift pump serving the well",
 "equipment_id": "Equipment key (EQ-nnnn)", "equipment_name": "Equipment name", "equipment_type": "Pump/Compressor/Separator/Generator/Valve/Heat Exchanger/Pipeline Equipment", "manufacturer": "Fictional manufacturer", "installation_date": "Installation date", "criticality": "Low/Medium/High",
 "supplier_id": "Supplier key", "supplier_name": "Fictional supplier name", "supplier_category": "Supplier category", "lead_time_days": "Quoted lead time (days)", "supplier_rating": "Static rating 1-5 (attribute, not measured performance)",
 "material_id": "Material key", "material_name": "Material name", "material_category": "Material category", "unit": "Unit of measure", "unit_cost": "Unit cost USD", "reorder_level": "Reorder point (units)", "primary_supplier_id": "Default supplier",
 "warehouse_id": "Warehouse key", "warehouse_name": "Warehouse name", "impact_factor": "Share of equipment downtime attributed to the well",
 "operating_hours": "Hours operating in the period", "downtime_hours": "Hours down", "oil_production_bbl": "Oil (bbl)", "gas_production_mcf": "Gas (mcf)", "water_production_bbl": "Water (bbl)", "pressure_psi": "Pressure (psi)", "temperature_c": "Temperature (C)", "water_cut_pct": "100 x water/(oil+water)", "potential_production_bbl": "SIMULATED unconstrained oil potential (bbl)", "dq_flag": "Pipe-separated cleaning flags (imputed/recomputed values)",
 "timestamp": "Reading time (2 readings/day at 06:00 and 18:00)", "vibration_mm_s": "Vibration (mm/s)", "flow_rate": "Flow (synthetic m3/h)", "energy_consumption_kwh": "Energy over the 12h reading window (kWh)",
 "maintenance_id": "Work order key", "maintenance_type": "Corrective/Preventive/Inspection", "failure_type": "Failure mode ('None' if not a failure)", "labor_cost": "Labour cost USD", "material_cost": "Material cost USD (= sum quantity x unit_cost)", "contractor_cost": "Contractor cost USD", "total_cost": "labor + material + contractor", "priority": "Critical/High/Medium/Low", "work_order_status": "Completed/In Progress", "quantity": "Units",
 "oil_volume_bbl": "Oil sold (bbl)", "gas_volume_mcf": "Gas sold (mcf)", "oil_price_usd": "Realised oil price USD/bbl", "gas_price_usd": "Gas price USD/mcf", "revenue_usd": "oil x price + gas x price",
 "cost_category": "Production/Energy/Labor/Maintenance/Transportation/Utilities/Other", "cost_amount_usd": "Operating cost USD",
 "opening_stock": "Opening stock (units)", "receipts": "Units received", "consumption": "Units consumed", "closing_stock": "opening + receipts - consumption", "stockout_flag": "1 if demand exceeded available stock",
 "po_id": "Purchase order key", "order_date": "Order date", "quoted_lead_time_days": "Quoted lead time", "promised_date": "order_date + quoted lead time", "received_date": "Receipt date (blank if open)",
 "incident_id": "Incident key", "incident_type": "Incident type", "severity": "Low/Medium/High/Critical", "lost_time_flag": "1 if lost-time incident", "days_lost": "Days lost", "root_cause": "Root cause category", "department": "Department",
}


def main():
    L = ["# Data Dictionary (processed tables)", "", f"> {config.SYNTHETIC_NOTICE}", "", "Generated from the actual CSV headers in data/processed.", ""]
    for t in DIM_TABLES + FACT_TABLES:
        df = pd.read_csv(config.PROCESSED_DIR / f"{t}.csv", nrows=2000)
        L += [f"## {t}", "", f"Rows in processed file: {sum(1 for _ in open(config.PROCESSED_DIR / f'{t}.csv', encoding='utf-8')) - 1:,}", "", "| Column | Type (inferred) | Description |", "|---|---|---|"]
        for c in df.columns:
            L.append(f"| {c} | {df[c].dtype} | {D.get(c, '')} |")
        L.append("")
    (config.ROOT / "docs" / "data_dictionary.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
