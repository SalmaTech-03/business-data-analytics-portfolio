# Business Process - To Be

> All operational data in this project are synthetic. PetroNexa Energy is a FICTIONAL company; stakeholders and roles are illustrative assumptions.

```mermaid
flowchart LR
  subgraph Sources
    A[Production] --- B[Maintenance] --- C[Finance] --- D[Inventory/POs] --- E[HSE] --- F[Sensors]
  end
  Sources --> I[Ingest raw files]
  I --> V1[Validate raw]
  V1 --> CL[Clean + quarantine + log]
  CL --> V2[Validate processed]
  V2 --> MT[Marts + PostgreSQL model]
  MT --> AN[KPIs, analytics, forecast, risk model]
  AN --> OUT[Dashboards, Excel, Streamlit, reports]
  OUT --> DEC[Weekly review and actions]
  V1 -.defect report.-> DS[Data steward]
```

![To-be diagram](diagrams/to_be.png)

## Changes versus as-is
| Area | To-be |
|---|---|
| Data model | One relational model with keys and a bridge table linking equipment to affected wells |
| Data quality | Automated checks before and after cleaning; quarantine instead of silent drops |
| KPIs | Single dictionary implemented identically in Python, SQL and BI measures |
| Loss valuation | Production loss valued with realised prices; downtime associated with maintenance events |
| Foresight | Backtested baseline forecast and a failure-risk ranking (moderate accuracy, stated) |
| Governance | Assumptions and limitations recorded in assumptions_and_constraints.md |

## RACI (assumed)
| Activity | Data Steward | Analyst | Ops/Maint Mgr | IT |
|---|---|---|---|---|
| KPI definitions | A | R | C | I |
| Pipeline operation | C | R | I | A |
| Dashboard review | I | R | A | C |
| Action follow-up | I | C | A/R | I |
