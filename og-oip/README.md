# OG-OIP: Oil & Gas Operations Intelligence & Production Optimization Platform

A portfolio-grade analytics project for the **fictional** company **PetroNexa Energy**, built on a **hybrid data architecture**:

| Dataset | Nature | Role |
|---|---|---|
| PetroNexa Energy (Production, Maintenance, Finance, Inventory/Suppliers, HSE, Sensors) | **SYNTHETIC**, relationally linked | Integrated core: KPIs, SQL model, dashboards, forecasting, predictive maintenance |
| Volve production data (`Volve_production_data.xlsx`) | **REAL** | Separate case study A |
| BSEE OGOR-A monthly production (`ogora2025delimit.txt`, `ogoradelimit.txt`) | **REAL** | Separate case study B |

Real records are **never merged** into PetroNexa tables and no relationships between the datasets are claimed. OGOR-B/C files were supplied but are not used.

> All PetroNexa data are synthetic/simulated for portfolio demonstration. They do not represent a real company. Every relationship that was built into the generator is listed in `docs/data_generation_methodology.md`.

## Quick start
```bash
pip install -r requirements.txt          # pandas, numpy, scipy, scikit-learn, matplotlib, openpyxl
python scripts/run_all.py                # generate -> clean -> validate -> marts -> analytics -> reports -> Excel -> BA docs
python tests/run_tests.py                # 44 tests (or: pytest tests/)
python scripts/build_data_dictionary.py && python scripts/build_notebooks.py
streamlit run app/streamlit_app.py       # optional, needs streamlit
```
Step by step: `generate_data.py` -> `clean_data.py` -> `validate_data.py` -> `transform_data.py` -> `run_analytics.py` -> `generate_reports.py` -> `build_excel.py`. To cache Excel formula values, recalculate the workbook once in Excel/LibreOffice.

## Project map
| Path | Content |
|---|---|
| `src/og_oip/` | data_generation, ingestion, cleaning, validation, transformation (marts), analytics, forecasting, ml, real_data, reporting |
| `data/raw` | messy CSVs with injected defects; `data/processed` cleaned tables (+ `quarantine/`, `cleaning_log.json`); `data/marts` analytical marts; `data/real` user-supplied real files; `data/reference` manifest, defect log, generator parameters |
| `sql/` | PostgreSQL schema (01-04), views (05), 46 analysis queries (06), 12 business questions (07), loader (08) |
| `powerbi/`, `tableau/` | build **specifications** (measures, Power Query, pages, calculated fields). No .pbix/.twb is included because none can be produced or verified here |
| `excel/OG_OIP_Analysis_Workbook.xlsx` | workbook with live formulas (synthetic sheets + separate real-data sheets) |
| `notebooks/` | 7 executed EDA notebooks |
| `app/streamlit_app.py` | exploration app |
| `business-analysis/` | BRD, FRD, stakeholders, as-is/to-be, 28 user stories, acceptance criteria, RTM, KPI dictionary, data requirements, assumptions, risks, UAT cases |
| `reports/` | data quality report, business findings, real-data case studies, tables, figures |
| `docs/` | methodology, data dictionary |

## Headline results (from `reports/tables/kpi_summary.json`, synthetic)
- 291,319 fact rows; raw data fails 60 of 179 validation checks (36,743 failed rows summed over checks); processed data passes 178 of 178 (quarantined rows are documented).
- Production loss versus simulated potential ~9.4%, of which ~67% is downtime-related; 412 failures across 48 units; cost per bbl of oil sold ~24 USD (synthetic cost model).
- Failure-risk model (time-based split, synthetic sensors): best test PR-AUC ~0.50 (Random Forest) versus a 5.8% random baseline; 72% of failure windows raised at least one alert with ~4 false-alert days per equipment-year. These describe simulated data only.
- Forecast baseline: 30-day moving average had the lowest backtest MAE among tested methods.

## Honest limitations
- ARIMA is not included (statsmodels was not installable offline); an OLS autoregression is provided instead.
- `pytest`, `streamlit`, PostgreSQL and Jupyter were unavailable in the build environment. Tests run with the bundled `tests/run_tests.py` (also pytest-compatible); the Streamlit app was compile-checked and smoke-tested against a stub; SQL was checked by tests for schema/CSV consistency but **not executed on a live PostgreSQL server**; notebooks were executed by `scripts/build_notebooks.py`, not Jupyter.
- BSEE column names follow the author's understanding of the OGOR-A layout; volume columns were identified by magnitude checks. Verify against the official BSEE data dictionary before publishing conclusions.
- Check the original publishers' terms before redistributing the real data files.
- No real user acceptance testing was performed; UAT cases are prepared scripts.

## Author
Salma S. Portfolio project; see `business-analysis/` for the requirements set.
