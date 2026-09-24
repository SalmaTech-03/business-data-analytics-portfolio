# Functional Requirements Document (FRD)

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.
> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.

| ID | Functional requirement | Supports | Implementation |
|---|---|---|---|
| FR-01 | Generate a relationally consistent synthetic dataset (8 dimension/bridge tables, 9 fact tables) reproducible from a seed | BR-09,BR-12 | src/og_oip/data_generation/*, scripts/generate_data.py |
| FR-02 | Produce a raw dataset with documented injected defects and a defect log | BR-09 | src/og_oip/data_generation/defects.py, data/reference/defect_injection_log.json |
| FR-03 | Clean raw data into processed tables; quarantine unrepairable rows; log every action | BR-09 | src/og_oip/cleaning/cleaners.py, scripts/clean_data.py |
| FR-04 | Run validation checks (keys, nulls, ranges, dates, referential, domains, units, logic) and publish a data quality report from actual results | BR-09 | src/og_oip/validation/*, reports/data_quality_report.md |
| FR-05 | Build analytical marts (well-day, field-month, equipment, sensor-day, inventory, supplier, HSE) | BR-01..BR-08 | src/og_oip/transformation/marts.py |
| FR-06 | Report production, loss (downtime vs other), decline and pressure/water-cut trends | BR-01,BR-02 | src/og_oip/analytics/production.py |
| FR-07 | Rank wells by defined metrics (loss bbl, loss %, avg rate) with explicit definitions | BR-02 | analytics/production.py::by_well |
| FR-08 | Associate downtime with maintenance events through the equipment-well bridge | BR-02,BR-04 | transformation/marts.py::attributed_downtime |
| FR-09 | Compute MTBF, MTTR, availability, failure counts by equipment and type | BR-03 | analytics/maintenance.py, marts.build_mart_equipment_summary |
| FR-10 | Produce a criticality-weighted maintenance priority ranking with an explicit formula | BR-04 | analytics/maintenance.py::critical_equipment |
| FR-11 | Compute cost per bbl, cost per BOE, margin and cost breakdown by field/year | BR-05 | analytics/financial.py |
| FR-12 | Estimate revenue impact of production loss using realised daily oil price | BR-02,BR-05 | marts.build_mart_well_daily |
| FR-13 | Compute inventory KPIs: stockout rate, turnover, days of inventory, low stock, excess stock | BR-06 | analytics/inventory.py |
| FR-14 | Compute supplier on-time %, quoted vs actual lead time from purchase orders | BR-07 | marts.build_mart_supplier_performance |
| FR-15 | Compute HSE incident counts, lost-time counts, rates per 200,000 assumed exposure hours, root-cause distribution | BR-08 | analytics/hse.py |
| FR-16 | Quantify associations (Spearman) between operational factors and outcomes, labelled as association not causation | BR-02,BR-08 | analytics/* |
| FR-17 | Backtest naive, moving-average, exponential-smoothing and AR models with rolling origins; report MAE/RMSE/MAPE/bias | BR-10 | src/og_oip/forecasting/models.py |
| FR-18 | Train and evaluate failure-risk models with time-based splits and real (not fabricated) metrics | BR-11 | src/og_oip/ml/predictive_maintenance.py |
| FR-19 | Provide 40+ PostgreSQL analytical queries, views and a load script | BR-12 | sql/* |
| FR-20 | Provide Power BI and Tableau build specifications (no fabricated binary files) | BR-12 | powerbi/*, tableau/* |
| FR-21 | Provide an Excel workbook with live formulas | BR-12 | excel/OG_OIP_Analysis_Workbook.xlsx |
| FR-22 | Provide a Streamlit exploration app | BR-12 | app/streamlit_app.py |
| FR-23 | Analyse Volve production data separately (conversions, reconciliation, decline, water cut, forecast backtest) | BR-13 | src/og_oip/real_data/volve.py |
| FR-24 | Analyse BSEE OGOR-A data separately (monthly totals, operator concentration, areas, quality checks) | BR-13 | src/og_oip/real_data/bsee.py |
| FR-25 | Provide automated tests for generation, cleaning, validation, KPIs, forecasting, ML, SQL schema, real-data loaders | BR-09 | tests/* |
| FR-26 | Provide reproducible pipeline entry points and documentation of assumptions and limitations | BR-09,BR-12 | scripts/*, README.md, docs/* |

## Non-functional requirements
| ID | Requirement |
|---|---|
| NFR-01 | Reproducibility: fixed seed 42; regenerating gives identical content hashes (data/reference/generation_manifest.json) |
| NFR-02 | No credentials in code; database settings via environment variables |
| NFR-03 | Full pipeline runs on a single CPU in minutes with pandas/numpy/scikit-learn/scipy/matplotlib |
| NFR-04 | Every synthetic output carries a synthetic-data notice; every real-data output carries a real-data label |
| NFR-05 | Raw data are never overwritten by cleaning |
