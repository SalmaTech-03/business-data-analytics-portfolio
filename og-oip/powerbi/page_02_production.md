# Page 2 - Production

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

**Audience:** Operations Manager, Production Engineer

## Layout
| Visual | Fields / measures |
|---|---|
| Stacked area: monthly oil by field | dim_date[month year], dim_field[field_name], [Oil Production (bbl)] |
| Stacked column: loss split | month, [Downtime Loss (bbl)], [Other Loss (bbl)] |
| Bar: well ranking by loss (Top 15) | dim_well[well_name], [Production Loss (bbl)]; tooltip [Production Loss %] |
| Line: water cut % by field | month, [Water Cut %] |
| Line: average pressure | month, [Avg Pressure (psi)] |
| Scatter: oil rate vs water cut per well | X [Water Cut %], Y [Avg Daily Oil (bbl/d)], detail dim_well[well_name] |
| Table: data quality | [Imputed Oil Rows] |

## Filters
Field, Well type, Reservoir, Date

## Insight questions
1. Where is loss concentrated? 2. Which wells have high water cut and still high rate? 3. How much of loss is downtime vs other?
