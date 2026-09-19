# Business Requirements

Requirements are traced to the business case and to the artefact that satisfies
them. Priority uses MoSCoW: **Must**, **Should**, **Could**.

## Business requirements

| ID | Requirement | Business rationale | Priority | Acceptance criteria | Satisfied by |
|---|---|---|---|---|---|
| BR-001 | Determine whether the 250-customer campaign is expected to generate positive net profit. | Catalog cost is committed before any revenue arrives; management will not release budget without a quantified expected outcome. | Must | A single net-profit figure is produced for the full 250-customer campaign, with every input formula shown and reproducible from the supplied data. | `notebooks/03_campaign_profitability.ipynb`, `outputs/campaign_summary.csv` |
| BR-002 | Estimate expected campaign revenue. | Revenue is the top of the profit calculation and the number Finance will challenge first. | Must | Expected revenue is calculated per customer as predicted sale amount weighted by response probability, and summed to a campaign total. | `src/profitability.py::expected_revenue`, `outputs/campaign_summary.csv` |
| BR-003 | Calculate campaign distribution and printing cost. | Cost is the only certain figure in the model and sets the hurdle the campaign must clear. | Must | Campaign cost equals number of catalogs multiplied by the unit cost of $6.50, and is recomputed automatically if either input changes. | `src/profitability.py::campaign_cost`, `tests/test_profitability.py` |
| BR-004 | Estimate gross profit using the stated gross-margin assumption. | Revenue overstates value; only the margin contributes to profit. | Must | Gross profit equals expected revenue multiplied by the 50% gross-margin assumption, with the assumption explicitly registered and adjustable. | `src/profitability.py::gross_profit`, `docs/assumptions_and_constraints.md` |
| BR-005 | Identify customer characteristics associated with higher average sales. | Targeting and future list-building depend on knowing what drives spend, not just who scores well. | Must | The relationship between average sale amount and each candidate characteristic is quantified and interpreted in business terms, including direction and dollar magnitude. | `notebooks/01_exploratory_data_analysis.ipynb`, `notebooks/02_predictive_model.ipynb` |
| BR-006 | Prioritise customers according to predicted economic value. | If the budget is cut, marketing must know which names to drop first. | Must | Every one of the 250 customers carries an expected net profit, a rank and a documented priority tier derived from the data rather than chosen by hand. | `src/profitability.py::prioritise_customers`, `outputs/customer_scores.csv` |
| BR-007 | Provide management with a clear decision-support summary. | The decision is made by non-technical stakeholders under time pressure. | Must | A one-page summary states the recommendation, the expected financial outcome, the assumptions it depends on and the conditions that would reverse it. | `reports/executive_summary.md` |
| BR-008 | Quantify the expected return on campaign spend. | Marketing budget competes with other uses of the same money; ROI is the comparison currency. | Must | ROI is reported as net profit divided by campaign cost, at campaign level and per customer. | `src/profitability.py::roi`, `outputs/campaign_summary.csv` |
| BR-009 | Show how the decision changes if the core assumptions change. | Margin, unit cost and response rate are estimates; the decision must be robust to being wrong about them. | Must | Net profit and ROI are recomputed across a documented grid of gross margin, catalog cost and response-rate scenarios, and the break-even point is stated. | `notebooks/04_sensitivity_analysis.ipynb`, `outputs/sensitivity_analysis.csv` |
| BR-010 | Quantify expected value by customer segment. | Segment is the unit marketing actually plans and buys against. | Should | Expected revenue, profit and ROI are reported for each of the four customer segments. | `outputs/segment_summary.csv` |
| BR-011 | Document data-quality condition of the inputs. | A financial recommendation built on unverified data is not defensible. | Should | Missing values, duplicates, invalid ranges, outliers, type issues and category consistency are checked in code and the findings are reported. | `docs/data_quality.md`, `src/data_cleaning.py::check_data_quality` |
| BR-012 | State the model's limitations in language a non-technical manager can act on. | Overstated confidence leads to overspending on subsequent campaigns. | Should | Model performance is reported as explained variance with a plain-language interpretation, plus an average error in dollars, and is never described as an accuracy rate. | `src/evaluation.py::interpret_r2`, `reports/project_report.md` |
| BR-013 | Define the KPIs to be measured after the campaign runs. | The forecast is only useful if it is tested against reality. | Should | A KPI set with formulas, owners and data sources is defined before launch. | `docs/kpi_framework.md` |
| BR-014 | Provide reporting outputs consumable by a BI tool. | Management consumes decisions through dashboards, not notebooks. | Could | Flat CSV extracts with a documented schema are produced for direct import. | `dashboard/dashboard_data_dictionary.md`, `outputs/*.csv` |
| BR-015 | Make the analysis reproducible end to end. | A one-off spreadsheet cannot be re-run for the next campaign or audited later. | Should | The full pipeline runs from raw files to outputs with a single documented command. | `run_analysis.py`, `README.md` |

## Traceability: business question to requirement

| Business question | Requirement |
|---|---|
| Is the campaign financially attractive? | BR-001, BR-002, BR-003, BR-004, BR-008 |
| Which customers should be prioritised? | BR-005, BR-006, BR-010 |
| What could change the decision? | BR-009, BR-011, BR-012 |
| How will we know it worked? | BR-013, BR-014 |
