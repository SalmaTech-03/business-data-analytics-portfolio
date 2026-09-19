# Functional and Non-Functional Requirements

## Functional requirements

| ID | Requirement | Parent | Priority | Acceptance criteria |
|---|---|---|---|---|
| FR-001 | The system shall load the historical customer file and the 250-record mailing list from `data/raw/`. | BR-015 | Must | Both files load into dataframes; a missing file raises an explicit error naming the expected path. |
| FR-002 | The system shall standardise column names across both files to a single vocabulary. | BR-011 | Must | `#_Years_as_Customer` is exposed as `Years_as_Customer`; both frames share identical names for shared fields. |
| FR-003 | The system shall run data-quality checks for missing values, duplicate rows, duplicate identifiers, invalid ranges, category consistency and data types. | BR-011 | Must | A structured report is returned for each dataset and printed in the EDA notebook. |
| FR-004 | The system shall one-hot encode `Customer_Segment` using `Credit Card Only` as the reference level. | BR-005 | Must | The design matrix contains three segment indicator columns and no reference column. |
| FR-005 | The system shall exclude identifier and location fields from the model feature set. | BR-005 | Must | `Name`, `Address`, `City`, `State`, `ZIP`, `Store_Number` and `Customer_ID` do not appear in the design matrix. |
| FR-006 | The system shall fit a linear regression predicting `Avg_Sale_Amount`. | BR-005 | Must | A fitted estimator is returned with retrievable intercept and coefficients. |
| FR-007 | The system shall report R-squared, MAE and RMSE on both fitted and held-out data. | BR-012 | Must | All three metrics are produced for a train/test split and for 5-fold cross-validation. |
| FR-008 | The system shall produce residual diagnostics for the fitted model. | BR-012 | Should | Residuals versus fitted values and a residual distribution are produced and interpreted. |
| FR-009 | The system shall benchmark the baseline against at least one more flexible model. | BR-012 | Could | Test-set metrics for all candidates are reported side by side with a stated selection rationale. |
| FR-010 | The system shall score each of the 250 prospects with a predicted average sale amount. | BR-002 | Must | Every mailing-list row receives a non-null `Predicted_Sale_Amount`. |
| FR-011 | The system shall calculate expected revenue per customer as predicted sale amount multiplied by response probability. | BR-002 | Must | `Expected_Revenue` is present for all 250 rows and matches the stated formula. |
| FR-012 | The system shall calculate gross profit, catalog cost, net profit and ROI per customer. | BR-004, BR-008 | Must | All four fields are present for all 250 rows; ROI returns a null rather than an error when cost is zero. |
| FR-013 | The system shall aggregate per-customer economics to campaign-level totals. | BR-001 | Must | Campaign revenue, gross profit, cost, net profit and ROI are produced as a single summary record. |
| FR-014 | The system shall assign each customer a High, Medium or Low priority tier using a data-derived threshold. | BR-006 | Must | Tier assignment follows BRule-08; the threshold value is stored alongside the assignment. |
| FR-015 | The system shall recompute campaign economics across a grid of gross margin, catalog cost and response-multiplier scenarios. | BR-009 | Must | A scenario table with one row per combination is produced and exported. |
| FR-016 | The system shall compute the break-even response level at which net profit reaches zero. | BR-009 | Should | The break-even multiplier is reported and stated in the recommendation. |
| FR-017 | The system shall export customer-level, segment-level, priority-level, campaign-summary and sensitivity extracts as CSV. | BR-014 | Should | Five CSV files are written to `outputs/` with the schema documented in the dashboard data dictionary. |
| FR-018 | The system shall reject invalid assumption inputs. | BR-004 | Should | A gross margin outside 0-1 or a negative cost or catalog count raises a `ValueError`. |
| FR-019 | The system shall provide automated tests for the financial calculations and the cleaning logic. | BR-015 | Must | `pytest` runs green from the repository root. |
| FR-020 | The system shall run end to end from raw data to outputs with one command. | BR-015 | Must | `python run_analysis.py` completes and writes all expected files. |

## Non-functional requirements

| ID | Category | Requirement | Acceptance criteria |
|---|---|---|---|
| NFR-001 | Reproducibility | Re-running the pipeline on unchanged inputs shall produce identical outputs. | Random seeds are fixed (`random_state=42`); two consecutive runs produce byte-identical summary figures. |
| NFR-002 | Transparency | Every reported financial figure shall be traceable to a named function and a stated formula. | Each KPI in `docs/kpi_framework.md` names the function that computes it. |
| NFR-003 | Maintainability | Financial formulas shall be defined once and reused. | No formula is reimplemented inline in a notebook; all come from `src/profitability.py`. |
| NFR-004 | Performance | The full pipeline shall complete in under one minute on a standard laptop. | Measured runtime on the supplied data is a few seconds. |
| NFR-005 | Portability | The project shall run on Python 3.10+ with only the packages in `requirements.txt`. | A clean virtual environment install runs the pipeline successfully. |
| NFR-006 | Auditability | Assumptions shall be centralised and adjustable without editing analysis logic. | All three levers live in `CampaignAssumptions`. |
| NFR-007 | Privacy | Customer names and addresses shall not be used as model inputs. | Enforced by FR-005 and verified by inspecting the design matrix columns. |
| NFR-008 | Usability | Reporting outputs shall be readable by a non-technical stakeholder without running code. | Markdown reports and CSV extracts require no Python to interpret. |
