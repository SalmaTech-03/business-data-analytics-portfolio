# Data Dictionary

Two source files are supplied in `data/raw/`.

| File | Rows | Columns | Purpose |
|---|---|---|---|
| `p1-customers.xlsx` | 2,375 | 12 | Historical customers with a known average sale amount. Used to train the model. |
| `p1-mailinglist.xlsx` | 250 | 12 | The prospects targeted by the campaign. Scored by the model; has no sale amount. |

---

## `p1-customers.xlsx` — historical customers (training set)

| Column name | Business meaning | Data type | Example | Role | Data-quality considerations |
|---|---|---|---|---|---|
| `Name` | Customer's full name. | String | `Pamela Wright` | Excluded — personally identifying, no predictive content | Not used in modelling. Free text; would need masking before wider sharing. |
| `Customer_Segment` | Relationship classification: `Credit Card Only`, `Loyalty Club Only`, `Loyalty Club and Credit Card`, `Store Mailing List`. | String (categorical) | `Store Mailing List` | **Predictor** (categorical, one-hot encoded) | Exactly four levels present, no nulls, no casing or spacing variants. Verified in `docs/data_quality.md`. |
| `Customer_ID` | Unique customer identifier. | Integer | `2` | Identifier — excluded from modelling | Unique across all 2,375 rows. Numeric but ordinal only; must never be treated as a quantity. |
| `Address` | Street address. | String | `376 S Jasmine St` | Excluded — personally identifying | Not used. |
| `City` | City of residence. | String | `Denver` | Excluded — high-cardinality location proxy | Not used as a predictor. Available for dashboard filtering. |
| `State` | State of residence. | String | `CO` | Excluded — single dominant value | Effectively constant in this dataset; carries no information. |
| `ZIP` | Postal code. | Integer in source; cast to zero-padded string | `80224` | Excluded from modelling | Stored as an integer, which silently strips leading zeros. Cast to a 5-character string during cleaning. Not a quantity. |
| `Avg_Sale_Amount` | Average dollar value of the customer's historical purchases. | Float | `227.90` | **Target variable** | Right-skewed; 58 values sit beyond the 1.5x IQR fence. All values are positive. No nulls. |
| `Store_Number` | Store the customer is associated with. | Integer | `100` | Excluded from modelling | Numeric label, not a quantity. Retained for dashboard filtering. |
| `Responded_to_Last_Catalog` | Whether the customer responded to the previous catalog. | String (`Yes` / `No`) | `No` | Excluded from modelling — not available for the mailing list | Present only in the training file. Using it would make the model unscoreable on the campaign population. See leakage note below. |
| `Avg_Num_Products_Purchased` | Average number of products bought per purchase occasion. | Integer | `1` | **Predictor** (numeric) | Strongest single driver of sale amount (r = 0.86). No nulls, no negative values. |
| `#_Years_as_Customer` | Tenure in years. Renamed to `Years_as_Customer` during cleaning. | Integer | `6` | Candidate predictor — excluded after testing | Near-zero correlation with the target (r = 0.03). The leading `#` breaks SQL and BI field naming. |

---

## `p1-mailinglist.xlsx` — campaign prospects (scoring set)

| Column name | Business meaning | Data type | Example | Role | Data-quality considerations |
|---|---|---|---|---|---|
| `Name` | Prospect's full name. | String | `A Giametti` | Excluded — personally identifying | Required for mail-file production, not for modelling. |
| `Customer_Segment` | Relationship classification, same four levels as the training file. | String (categorical) | `Loyalty Club Only` | **Predictor** | All four levels present; distribution differs from the training set (see below). |
| `Customer_ID` | Unique prospect identifier. | Integer | `2213` | Identifier / join key | Unique across all 250 rows. Used to join scores back to the mail file. |
| `Address` | Street address. | String | `5326 S Lisbon Way` | Excluded — personally identifying | Required by Marketing Operations for distribution. |
| `City` | City of residence. | String | `Centennial` | Excluded from modelling | Available as a dashboard filter. |
| `State` | State of residence. | String | `CO` | Excluded from modelling | Effectively constant. |
| `ZIP` | Postal code. | Integer in source; cast to string | `80015` | Excluded from modelling | Same leading-zero issue as the training file. |
| `Store_Number` | Associated store. | Integer | `105` | Excluded from modelling | Numeric label, not a quantity. |
| `Avg_Num_Products_Purchased` | Average number of products purchased. | Integer | `3` | **Predictor** | Same definition as the training file. |
| `#_Years_as_Customer` | Tenure in years. | Float | `0.2` | Excluded from modelling | Stored as a float here but as an integer in the training file, and on a visibly different scale. A further reason not to use it as a predictor. |
| `Score_No` | Modelled probability that the prospect does **not** respond to the catalog. | Float (0-1) | `0.694964` | Supporting input | Supplied with the source data; the underlying response model is not included. Complements `Score_Yes`. |
| `Score_Yes` | Modelled probability that the prospect **does** respond to the catalog. | Float (0-1) | `0.305036` | **Response probability** used to weight expected revenue | Ranges 0.186 to 1.000, mean 0.341. `Score_Yes + Score_No = 1` for every row. Provenance is external to this project — treated as a supplied input and registered as assumption A-05. |

---

## Variable roles at a glance

| Role | Variables |
|---|---|
| Target variable | `Avg_Sale_Amount` |
| Numeric predictor | `Avg_Num_Products_Purchased` |
| Categorical predictor | `Customer_Segment` (one-hot encoded, reference level `Credit Card Only`) |
| Response probability input | `Score_Yes` (mailing list only) |
| Identifiers | `Customer_ID`, `Store_Number`, `ZIP` |
| Personally identifying, excluded | `Name`, `Address`, `City`, `State` |
| Tested and excluded | `Years_as_Customer` (negligible correlation, inconsistent typing across files) |
| Excluded to avoid an unscoreable model | `Responded_to_Last_Catalog` (absent from the mailing list) |

## Encoding scheme

`Customer_Segment` is one-hot encoded with **`Credit Card Only` as the reference
level**. Each segment coefficient is therefore read as the dollar difference in
average sale amount versus an otherwise identical Credit-Card-Only customer.

## Note on `Responded_to_Last_Catalog`

This field exists in the training file but not in the mailing list. Including it
would produce a model that cannot be scored on the campaign population — the
classic train/serve skew failure. It is excluded from the feature set and used
in EDA only, where it surfaces a counter-intuitive finding documented in
`notebooks/01_exploratory_data_analysis.ipynb`.

## Note on `Score_Yes`

`Score_Yes` arrives with the mailing list. The model that generated it is not
supplied with this project, so its methodology cannot be validated here. It is
used as given, registered as assumption **A-05**, and stress-tested in the
sensitivity analysis by scaling it between 60% and 120% of its supplied value.
