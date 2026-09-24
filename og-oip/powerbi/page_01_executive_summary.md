# Page 1 - Executive Summary

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

**Audience:** Executives

## Layout
| Zone | Visual | Fields / measures |
|---|---|---|
| Top row (6 cards) | KPI cards | [Oil Production (bbl)], [Production Loss %], [Revenue (USD)], [Cost per bbl Oil Sold], [Availability %], [Incident Rate per 200k h] |
| Middle left | Line + column: monthly oil and loss % | Axis dim_date[month year]; columns [Oil Production (bbl)]; line [Production Loss %] |
| Middle right | Clustered bar: estimated lost revenue by field | dim_field[field_name], [Estimated Lost Revenue (USD)] |
| Bottom left | Table: top 5 priority equipment | dim_equipment[equipment_name], [Failures], [Equipment Downtime Hours], [Priority Score] (Top N=5) |
| Bottom right | Table: items at or below reorder + open POs | [Items At or Below Reorder], [Open POs] |

## Filters
Date range, Field

## Insight questions
1. Is production loss trending up or down? 2. Which field carries the most lost revenue? 3. Which equipment should be reviewed first?
