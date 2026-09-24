# Page 6 - HSE

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

**Audience:** HSE Lead

## Layout
| Visual | Fields / measures |
|---|---|
| Cards | [Incidents], [Lost Time Incidents], [Days Lost], [Incident Rate per 200k h], [LTI Rate per 200k h] |
| Column: incidents by month | month, [Incidents] with [Lost Time Incidents] |
| Stacked bar: severity by field | dim_field[field_name], fact_hse[severity], [Incidents] |
| Bar: root cause | fact_hse[root_cause], [Incidents] |
| Matrix: incident type x department | [Incidents] |
| Info box | Exposure hours are an assumption (30 h per producing well-day; what-if parameter) |

## Filters
Field, Severity, Incident type, Date

## Insight questions
1. Which fields have the highest normalised rate? 2. Which root causes dominate? 3. Is severity shifting?
