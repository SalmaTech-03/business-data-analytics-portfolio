# Tableau Specification - OG-OIP

> Synthetic data (fictional PetroNexa Energy). Specification only; no .twb/.twbx file is provided because none can be produced or verified in the build environment.

## Files
data_source_schema.md (tables, joins, types), calculated_fields.md (all calculations), dashboard_specification.md (dashboards, worksheets, actions).

## Build steps
1. Run `python scripts/run_all.py`.
2. Connect to Text File (CSV) for data/marts/*.csv (recommended: pre-joined marts) or to PostgreSQL schema og_oip.
3. Follow data_source_schema.md to create the data sources and relationships (Tableau relationships/logical layer, not physical joins, for multi-fact models).
4. Create calculated fields from calculated_fields.md.
5. Build worksheets and dashboards from dashboard_specification.md; add the synthetic-data notice to every dashboard.
6. Validate against reports/tables/kpi_summary.json.
