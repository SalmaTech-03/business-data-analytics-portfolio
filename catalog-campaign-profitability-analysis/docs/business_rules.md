# Business Rules

Rules that govern the analysis and the targeting decision. Each is implemented
in code and enforced by tests where enforcement is meaningful.

| ID | Rule | Rationale | Implemented in |
|---|---|---|---|
| BRule-01 | Every mailed catalog incurs a cost of **$6.50**, whether or not the recipient responds. | Print and distribution costs are committed at mailing, not at purchase. | `src/profitability.py::campaign_cost` |
| BRule-02 | Campaign value is measured on **gross profit**, not revenue. Gross margin is **50%**. | Revenue does not fund the campaign; only the margin does. | `src/profitability.py::gross_profit` |
| BRule-03 | Expected revenue for a customer is the predicted sale amount **weighted by their probability of responding**. | A prospect with a $1,000 predicted sale but a 10% response probability is not worth $1,000 to the campaign. | `src/profitability.py::expected_revenue` |
| BRule-04 | Response probability is taken from the supplied `Score_Yes` field and is **capped at 1.0**. | Probabilities above 1 are not meaningful and would inflate revenue. | `src/profitability.py::build_customer_economics` |
| BRule-05 | Identity and location fields (`Name`, `Address`, `City`, `State`, `ZIP`, `Store_Number`, `Customer_ID`) are **excluded from the model**. | They are personally identifying or are numeric labels rather than quantities; using them risks spurious fit and creates privacy exposure. | `src/data_cleaning.py::NON_MODEL_COLUMNS`, `src/feature_engineering.py` |
| BRule-06 | A feature is used only if it is present in **both** the training file and the mailing list. | A model that depends on a field the campaign population does not have cannot be scored. This excludes `Responded_to_Last_Catalog`. | `src/feature_engineering.py` |
| BRule-07 | `Credit Card Only` is the **reference segment**. All segment coefficients are read against it. | A fixed reference level makes coefficients stable and interpretable across refreshes. | `src/feature_engineering.py::REFERENCE_SEGMENT` |
| BRule-08 | Priority tiers are assigned from the expected-net-profit distribution: **Low** if expected net profit is at or below zero; **High** if profitable and at or above the 75th percentile of profitable customers; **Medium** otherwise. | The threshold is derived from the data rather than chosen by hand, so it adapts when the model or the assumptions change. | `src/profitability.py::prioritise_customers` |
| BRule-09 | A customer whose expected net profit is not positive is **not prioritised for mailing**, regardless of segment. | A catalog that does not pay for itself destroys value even if the customer looks attractive on other measures. | `src/profitability.py::prioritise_customers` |
| BRule-10 | Model performance is reported as **explained variance (R-squared)** and is never described as an accuracy rate. | Calling R-squared "84% accuracy" misleads stakeholders into believing individual predictions are accurate to within 16%. | `src/evaluation.py::interpret_r2` |
| BRule-11 | Gross margin must lie between **0 and 1**; catalog cost and catalog count must be **non-negative**. | Prevents nonsensical scenario inputs from silently producing plausible-looking figures. | `src/profitability.py::CampaignAssumptions`, `tests/test_profitability.py` |
| BRule-12 | ROI is **undefined** when campaign cost is zero and returns a null rather than an error or an infinity. | Zero-cost scenarios are legitimate inputs in sensitivity analysis and must not crash the pipeline. | `src/profitability.py::roi` |
| BRule-13 | Any figure carried over from the source project must be **independently reproduced** from the supplied data before it is published, or labelled as unverified. | Prevents the analysis inheriting an error from its predecessor. | `notebooks/03_campaign_profitability.ipynb` |
| BRule-14 | Scenario figures must be **visually and textually distinguished** from base-case figures wherever they appear. | Stops hypothetical downside numbers being quoted as forecasts. | `notebooks/04_sensitivity_analysis.ipynb` |
