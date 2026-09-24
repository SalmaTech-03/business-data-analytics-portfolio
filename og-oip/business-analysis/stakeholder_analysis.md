# Stakeholder Analysis

> All operational data in this project are synthetic. PetroNexa Energy is a FICTIONAL company; stakeholders and roles are illustrative assumptions.

| Stakeholder (illustrative role) | Interest | Influence | Needs from platform | Key stories |
|---|---|---|---|---|
| Executive / VP Operations | Overall performance, margin, risk | High | One-page KPI view; loss value | US-27, US-12 |
| Operations Manager | Production delivery | High | Field/well trends, loss ranking | US-01, US-02 |
| Production Engineer | Well performance, decline, water | Medium | Decline, water cut, loss split | US-03, US-04, US-05 |
| Reliability Engineer | Failure modes, availability | Medium | MTBF/MTTR, repeat failures, risk scores | US-06, US-07, US-10, US-24 |
| Maintenance Manager | Crew and spares planning, cost | High | Priority list, Pareto, PM vs CM | US-08, US-09, US-11 |
| Finance Analyst | Opex, unit cost | Medium | Cost per bbl, margin, lost revenue | US-12 to US-15 |
| Supply Chain Analyst | Stock availability, working capital | Medium | Stockout, low stock, excess | US-16 to US-18 |
| Procurement Lead | Supplier management | Medium | On-time, lead-time gap, open POs | US-19, US-20 |
| HSE Lead | Safety performance | High | Incidents, rates, root causes | US-21, US-22 |
| Data Steward | Trust in data | Medium | Quality report, lineage | US-25, US-26 |
| Planning Analyst | Forecasts | Medium | Forecast with accuracy | US-23 |
| IT / BI Developer | Implementable specs | Low | Schema, DAX, Power Query, Tableau fields | US-27 |

## Engagement approach (assumed)
Executives and managers: monthly KPI review; engineers: working sessions on definitions (loss, priority score); data steward: owns definitions and thresholds; IT: review of the SQL schema and BI specifications.

## Communication matrix
| Audience | Content | Channel | Frequency |
|---|---|---|---|
| Executives | KPI summary, loss value, top risks | Dashboard page 1 | Monthly |
| Operations/Maintenance | Rankings, risk list | Dashboard pages 2-3, Excel | Weekly |
| Data steward | Quality report | Markdown/HTML report | Each pipeline run |
