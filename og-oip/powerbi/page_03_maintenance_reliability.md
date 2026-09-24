# Page 3 - Maintenance & Reliability

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

**Audience:** Reliability Engineer, Maintenance Manager

## Layout
| Visual | Fields / measures |
|---|---|
| Cards | [Failures], [MTBF (h)], [MTTR (h)], [Availability %], [Corrective Cost Share %] |
| Pareto column: downtime by equipment | dim_equipment[equipment_name], [Equipment Downtime Hours] sorted desc |
| Bar: MTBF and MTTR by equipment type | dim_equipment[equipment_type], [MTBF (h)], [MTTR (h)] |
| Bar: failures by failure_type | fact_maintenance[failure_type], [Failures] (filter maintenance_type = Corrective) |
| Column: monthly failures | month, [Failures] |
| Table: priority list | equipment, criticality, [Priority Score]; note: score = weight (High 3, Medium 2, Low 1) x downtime hours |

## Filters
Equipment type, Criticality, Field, Maintenance type, Date

## Insight questions
1. Which equipment types drive downtime? 2. Is corrective work dominating cost? 3. Which failure modes repeat?
