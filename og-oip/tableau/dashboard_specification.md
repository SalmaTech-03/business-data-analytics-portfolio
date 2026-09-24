# Dashboard Specification (Tableau)

> Synthetic data (fictional PetroNexa Energy). Specification only; no .twb/.twbx file is provided because none can be produced or verified in the build environment.

| Dashboard | Worksheets | Filters | Actions |
|---|---|---|---|
| 1 Executive Overview | KPI tiles (Oil, Loss %, Revenue, Cost per bbl, Availability, Incident rate); monthly oil + loss % dual axis; lost revenue by field; top-5 priority equipment | Date (month range), Field | Field filter action to other dashboards |
| 2 Production | Oil by field (area); loss decomposition (stacked bar downtime vs other); well ranking by loss (Top N parameter); water cut trend; pressure trend | Field, Well type, Reservoir | Highlight well from ranking to trends |
| 3 Reliability | Downtime Pareto; MTBF/MTTR by type; failures by type; monthly failures; priority table | Equipment type, Criticality, Field | Click equipment -> Equipment Monthly |
| 4 Financial | Cost per bbl vs price; opex by category; margin by field; lost revenue | Field, Cost category | - |
| 5 Inventory & Suppliers | Stockout by category; excess flag table; supplier on-time; lead time gap | Warehouse, Category, Supplier | - |
| 6 HSE | Incidents by month; severity by field; incident rate by field; root cause | Field, Severity | - |
| 7 Predictive & Forecast | Risk bar (Top 15); metrics table; forecast line; backtest table | Equipment type | - |

Standards: 1280x720 fixed size; notice text "Synthetic data - fictional PetroNexa Energy" on every dashboard; colour palette consistent across dashboards; tooltips state metric definitions from business-analysis/kpi_dictionary.md; validate headline numbers against reports/tables/kpi_summary.json.
