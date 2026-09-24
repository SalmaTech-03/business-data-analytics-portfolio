# Business Requirements Document (BRD)

> All operational, production, financial, maintenance, inventory, sensor and HSE data in this project are synthetic/simulated and created for portfolio demonstration purposes. They do not represent actual operations of a real company.
> PetroNexa Energy is a FICTIONAL company. Stakeholders, roles and targets described here are illustrative assumptions.

## 1. Purpose
PetroNexa Energy (fictional) wants one analytics platform that links production, maintenance, finance, inventory, HSE and sensor data so managers can find where production and money are lost and where risk is concentrated.

## 2. Business context and problem statement
Operational data live in separate systems (production allocation, maintenance work orders, ERP costs, warehouse stock, HSE logs, sensor historian). Reports are assembled manually, definitions differ between teams, and data quality issues (duplicates, unit mix-ups, missing values, naming variants) erode trust. As a result leaders cannot answer basic questions consistently, such as how much production is lost to downtime and what it costs.

## 3. Objectives
1. Provide governed KPI definitions and a single relational model (BR-01 to BR-08).
2. Make data quality visible and repeatable (BR-09).
3. Provide baseline forecasting and failure-risk scoring with honest accuracy reporting (BR-10, BR-11).
4. Provide self-service outputs: SQL, dashboard specifications, Excel, Streamlit (BR-12).
5. Demonstrate the same analytical methods on separate real datasets without mixing them into the fictional company (BR-13).

## 4. Business requirements
| ID | Requirement | Success statement |
|---|---|---|
| BR-01 | Monitor production performance by field and well | Operations Manager sees oil, gas, water and water cut trends at field/well level. |
| BR-02 | Quantify production loss versus potential and separate downtime from other loss | Production Engineer can size and rank losses. |
| BR-03 | Track equipment reliability (MTBF, MTTR, availability, failure modes) | Reliability Engineer can compare equipment types and units. |
| BR-04 | Prioritise maintenance effort by downtime, cost and criticality | Maintenance Manager gets a ranked, explainable priority list. |
| BR-05 | Understand operating cost, unit cost per barrel and margin | Finance Analyst can track opex and unit economics by field. |
| BR-06 | Monitor inventory, stockouts and reorder exposure | Supply Chain Analyst can see stockout and excess stock. |
| BR-07 | Evaluate supplier delivery performance and lead times | Procurement can compare suppliers on-time and lead-time gaps. |
| BR-08 | Monitor HSE incidents, severity and rates | HSE Lead can track incidents, lost time and root causes. |
| BR-09 | Ensure trusted data via validation, cleaning and lineage | Data Steward can see defects found, fixed and quarantined. |
| BR-10 | Provide short-term production forecasts with honest accuracy measures | Planning can use baseline forecasts with backtest errors. |
| BR-11 | Provide early-warning failure risk scoring | Reliability Engineer gets ranked equipment risk with documented limits. |
| BR-12 | Deliver self-service analytics (SQL, dashboards specs, Streamlit, Excel) | Executives and analysts can explore KPIs without code. |
| BR-13 | Demonstrate methods on separate real datasets (Volve, BSEE OGOR-A) without mixing them into the synthetic company | Portfolio reviewers see real-data rigour and clear separation. |

## 5. Scope
**In scope:** synthetic PetroNexa dataset (4 fields, 60 wells, 48 equipment units, 3 years daily), data quality pipeline, KPIs, analytics, forecasting baseline, failure-risk model, PostgreSQL model and queries, BI specifications, Excel, Streamlit app, real-data case studies (Volve, BSEE OGOR-A).

**Out of scope:** real-time streaming, reservoir simulation, economic evaluation with capex/tax/royalty, integration with production systems, real company data, use of OGOR-B/C files.

## 6. Success criteria (measurable in this project)
- Processed data passes 100% of the implemented validation checks (see data quality report).
- Every KPI in the KPI dictionary is reproducible in Python and SQL.
- Tests pass and every claimed metric is produced by code (no manually typed results).

## 7. Constraints, assumptions, risks
See assumptions_and_constraints.md and risk_register.md.

## 8. Approval
This is a portfolio document; there is no real sign-off. Stakeholders are illustrative (see stakeholder_analysis.md).
