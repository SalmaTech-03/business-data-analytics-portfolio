# Risk Register

Impact and likelihood are rated Low / Medium / High. Owners are generic roles.

| Risk ID | Risk | Impact | Likelihood | Mitigation | Owner |
|---|---|---|---|---|---|
| R-01 | **Model prediction error.** Predicted sale amounts differ materially from actuals. Held-out mean absolute error is $93.40 per customer against a mean predicted sale of $553. | Medium | High | Report error in dollars alongside R-squared rather than a single headline figure. Size the worst case explicitly (about $11,675 of gross profit across 250 customers). Compare predicted against actual order values after launch (M-08) and refresh the model before the next campaign. | Data / Analytics |
| R-02 | **Response probabilities are wrong.** `Score_Yes` comes from a model that is not supplied and cannot be validated in this project. | High | Medium | Stress-test across 60%-120% of supplied values. Publish the break-even response level (6.9% of modelled) so decision makers can see the headroom. Measure actual response by priority tier after launch (M-01, M-09). Request the response model's documentation before the next campaign. | Data / Analytics, Marketing Manager |
| R-03 | **Gross-margin assumption changes.** The blended 50% margin does not hold for the catalog product mix. | High | Medium | Obtain written confirmation from Finance before mailing. Sensitivity table covers 40%-60%, where net profit ranges from $17,265 to $26,710. Reconcile realised margin after the campaign (M-05). | Finance Manager |
| R-04 | **Catalog cost increases.** Print or postage exceeds $6.50 per unit. | Low | Medium | Confirm the unit cost against a current supplier quote before committing. Sensitivity shows cost would have to reach about $94 per catalog to eliminate the profit, so tolerance is very wide. | Marketing Operations |
| R-05 | **Customer behaviour changes.** Historical purchase patterns no longer predict current behaviour. | Medium | Medium | Treat the forecast as a decision input, not a guarantee. Track actual against forecast weekly during the response window. Re-estimate the model on fresh data before reusing it. | Marketing Manager, Data / Analytics |
| R-06 | **Data-quality degradation on refresh.** Future extracts introduce missing values, new segment labels or changed field definitions. | Medium | Medium | Automated quality checks run as part of the pipeline (`check_data_quality`) and fail loudly on unexpected segment levels or out-of-range probabilities. Data dictionary defines every field's expected type and domain. | Data / Analytics, IT |
| R-07 | **Model drift.** The relationship between products purchased, segment and spend weakens over time. No timestamp exists in the source data, so the age of the training set is unknown. | Medium | High | Re-estimate before each campaign and compare coefficients against the previous run. Monitor held-out R-squared and MAE at each refresh. Request dated snapshots for all future extracts. | Data / Analytics |
| R-08 | **Over-targeting and contact fatigue.** High-value customers are repeatedly selected across campaigns because the model ranks them highest every time, leading to opt-outs and relationship damage. | Medium | Medium | Apply a contact-frequency cap outside the model. Monitor opt-out and complaint rates by priority tier (M-11). Give Sales / Customer Management a veto over individual names on the mail file. | Sales / Customer Management |
| R-09 | **Insufficient campaign tracking.** Orders cannot be attributed to the catalog, so none of the monitoring KPIs can be measured. | High | Medium | Agree the attribution mechanism (campaign code, unique offer code or matched-back customer ID) and the response window **before** the catalogs are mailed. Treat this as a go/no-go item in Phase 3 of the implementation plan. | Marketing Operations |
| R-10 | **Non-incremental revenue.** Orders attributed to the catalog would have occurred anyway, so measured profit overstates true value. | High | Medium | Acknowledged as assumption A-08 and flagged as the limitation most capable of reversing the conclusion. Build a randomised holdout group into the next campaign so incrementality can be measured directly. | Marketing Manager, Data / Analytics |
| R-11 | **Population mismatch.** The mailing list has a materially different segment mix from the training population (Store Mailing List is 47% of training but 8% of the list). | Medium | High | Documented as constraint C-04. Report segment-level performance separately after launch (M-10) so any segment where the model misses is identified rather than averaged away. | Data / Analytics |
| R-12 | **Decision over-confidence.** Stakeholders read R-squared as an accuracy rate and treat the forecast as precise. | Medium | Medium | BRule-10 prohibits accuracy language anywhere in the repository. Every performance statement pairs explained variance with an error in dollars. Executive summary states the forecast as conditional on named assumptions. | Data / Analytics, Marketing Manager |

## Risks explicitly out of scope

- Print production and logistics failures (owned by Marketing Operations, outside the analysis)
- Regulatory and data-protection compliance of the mailing itself
- Competitive response to the campaign
- Brand and creative effectiveness of the catalog contents

## Top three risks by exposure

1. **R-02 — response probabilities.** High impact, unverifiable provenance, and the single largest driver of expected revenue.
2. **R-10 — non-incrementality.** High impact and untestable with the current campaign design. The only risk capable of reversing the recommendation entirely.
3. **R-09 — tracking.** High impact and entirely preventable. If tracking is not agreed before mailing, the organisation learns nothing from the campaign regardless of how it performs.
