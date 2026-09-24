# Dashboard Specification

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

## Purpose and audience
Executive and functional managers of the fictional PetroNexa Energy; see business-analysis/stakeholder_analysis.md.

## Pages
| # | Page | Primary audience | Key questions |
|---|---|---|---|
| 1 | Executive Summary | Executives | How much did we produce, lose, earn, spend? What is at risk? |
| 2 | Production | Ops / Production Eng | Where and why is production lost? Which wells decline/water out? |
| 3 | Maintenance & Reliability | Reliability / Maintenance | Which equipment and failure modes drive downtime and cost? |
| 4 | Financial | Finance | Unit cost, margin, value of loss |
| 5 | Inventory & Suppliers | Supply chain / Procurement | Stockouts, excess, supplier reliability |
| 6 | HSE | HSE | Incident volume, severity, rates, root causes |
| 7 | Predictive & Forecast | Reliability / Planning | Ranked failure risk; forecast with backtest error |

## Design system
- Canvas 16:9 (1280x720), light theme, neutral grey background, one accent colour per domain (production blue, maintenance orange, finance green, inventory purple, HSE red).
- Fonts: Segoe UI; titles 16 pt, KPI cards 28 pt, axes 10 pt.
- Every page shows a footer text box: "Synthetic data - fictional PetroNexa Energy. Not real operations."
- KPI cards top row; trend visual left-middle; breakdown right-middle; detail table bottom.
- Conditional formatting: red for worse-than-threshold. Thresholds are display choices, not standards; store them as parameters.

## Global filters (synced slicers)
Date range (dim_date[date]), Field (dim_field[field_name]). Page-specific slicers listed in page files.

## Navigation and interactions
Left navigation buttons (page navigator). Cross-filtering ON between visuals except KPI cards. Drill-through pages: Well detail (from Production), Equipment detail (from Maintenance). Tooltips: report-page tooltip showing month trend.

## Performance
Import mode; avoid row-level SUMX on fact_sensor in visuals (use aggregated tables if needed); limit table visuals to Top N. Use the precomputed data/marts tables if DAX loss measures are slow.

## Validation
Reconcile headline numbers to reports/tables/kpi_summary.json (see README).

## Accessibility
Colour-blind-safe palette, data labels on key bars, alt text on each visual.
