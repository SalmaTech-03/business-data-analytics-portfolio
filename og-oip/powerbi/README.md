# Power BI Specification - OG-OIP

> Synthetic data (fictional PetroNexa Energy). This folder contains SPECIFICATIONS to build the report; no .pbix file is included because none can be produced or verified in the build environment.

## What is here
| File | Purpose |
|---|---|
| data_model.md | Tables, keys, relationships, storage mode, calculated columns |
| power_query_m_code.txt | Power Query (M) to load the CSV outputs (parameterised folder path) |
| dax_measures.dax | All measures, grouped by page, matching business-analysis/kpi_dictionary.md |
| dashboard_specification.md | Design system, navigation, filters, interactions, performance notes |
| page_01 ... page_07 | Page-by-page visuals, fields, measures, filters |

## How to build (about half a day for an experienced developer)
1. Run the pipeline: `python scripts/run_all.py` (creates data/processed, data/marts, reports/tables).
2. Open Power BI Desktop, create parameter `DataFolder` = absolute path of the project root.
3. Paste queries from power_query_m_code.txt (Advanced Editor), one per table. Disable load for staging queries only.
4. Create relationships per data_model.md; mark dim_date as date table.
5. Create a "_Measures" table and paste dax_measures.dax measure by measure.
6. Build pages following page_*.md. Add the synthetic-data notice text box on every page.
7. Optionally switch the source to PostgreSQL (schema og_oip, see sql/) using the same table names.

## Validation checklist after building
- Total oil equals the value in reports/tables/kpi_summary.json (production.total_oil_bbl).
- Failures equals maintenance.failure_count; fleet availability equals maintenance.fleet_availability_pct.
- Revenue and opex equal financial.revenue_usd_synthetic and financial.operating_cost_usd.
Differences indicate a relationship or filter error.
