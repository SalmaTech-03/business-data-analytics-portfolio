# Assumptions and Constraints

> All operational data in this project are synthetic. PetroNexa Energy is a FICTIONAL company; stakeholders and roles are illustrative assumptions.

## Assumptions (synthetic model)
1. Well potential follows an Arps hyperbolic decline with parameters drawn per well (see data/reference/well_generation_parameters.csv); some wells receive a workover uplift.
2. Actual oil = potential x (operating hours/24) x an efficiency factor (mean 0.97, clipped 0.85-1.0). Loss is therefore driven by downtime and an efficiency shortfall.
3. Equipment failures follow a hazard that grows with equipment age, time since preventive maintenance and criticality; downtime is lognormal by equipment type.
4. Downtime is spread from the maintenance date at up to 24 h/day; well impact = hours x impact_factor from the bridge table; a small background of unexplained shut-ins is added.
5. 75% of failures are preceded by a simulated sensor ramp (4-14 days); false-alarm excursions also occur. Therefore ML metrics are only meaningful for synthetic data.
6. Prices follow a mean-reverting random walk (oil around 72 USD/bbl, gas around 3.2 USD/mcf) with field differentials.
7. Operating cost components are formula-based on wells, volumes, energy use, maintenance events and noise.
8. HSE incident frequency depends on field size and recent corrective activity; the effect is modest and was not detected in the monthly association test.
9. Exposure hours = 30 h per producing well-day (assumption for incident rates).
10. Inventory demand = routine Poisson demand + maintenance material use; reorder points derive from mean demand x quoted lead time x 1.25 + 1. Unmet demand is assumed covered by emergency purchases outside the ledger.
11. Supplier on-time behaviour is drawn per supplier (55%-95% hidden parameter).

## Constraints
- Build environment had no internet: pytest, statsmodels, streamlit, nbformat, PostgreSQL were unavailable. Consequences: ARIMA not included; tests run with a bundled runner that also supports pytest; Streamlit app and SQL were not executed here.
- Real-data column semantics for BSEE OGOR-A rely on the author's understanding of the layout and magnitude checks.
- No real user acceptance testing was performed.

## Exclusions
No capex, tax, royalties, hedging, reservoir engineering, real-time data, or company data. No claims about real companies or fields other than the analysis of the supplied public-style datasets.
