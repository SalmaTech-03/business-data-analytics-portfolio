# Data Quality Assessment

Every finding below was produced by running `src/data_cleaning.check_data_quality`
against the two supplied files. Nothing in this document is asserted without the
check that produced it. Reproduce with:

```bash
python run_analysis.py      # writes outputs/analysis_facts.json
```

or interactively in `notebooks/01_exploratory_data_analysis.ipynb`.

## Summary

| Check | `p1-customers.xlsx` (2,375 rows) | `p1-mailinglist.xlsx` (250 rows) | Verdict |
|---|---|---|---|
| Missing values | 0 across all 12 columns | 0 across all 12 columns | Clean |
| Duplicate rows | 0 | 0 | Clean |
| Duplicate `Customer_ID` | 0 | 0 | Clean |
| Invalid target values | 0 non-positive `Avg_Sale_Amount` (min $1.22) | n/a — no target present | Clean |
| Negative product counts | 0 | 0 | Clean |
| Probability range violations | n/a | 0 values outside [0, 1] | Clean |
| `Score_Yes + Score_No = 1` | n/a | Maximum deviation from 1.0 is below 1e-9 | Consistent |
| Unexpected segment levels | 0 — exactly the four expected levels | 0 — same four levels | Consistent |
| Data-type issues | 2 found (see below) | 2 found (see below) | Addressed in cleaning |
| Outliers in target | 58 rows beyond the 1.5x IQR fence (2.4%) | n/a | Retained, see below |

## Findings

### DQ-01 — `ZIP` is stored as an integer (both files)

**Observation.** `ZIP` has dtype `int64`. Any postal code with a leading zero
would be silently corrupted (`01234` becomes `1234`), and arithmetic on a postal
code is meaningless.

**Materiality.** No practical impact here: every ZIP in both files is a Colorado
code in the 80xxx range, so no leading zeros are actually lost.

**Action taken.** Cast to a zero-padded 5-character string during cleaning. The
field is excluded from modelling regardless.

### DQ-02 — `#_Years_as_Customer` has an awkward and inconsistent name and type

**Observation.** The leading `#` is invalid or awkward in SQL, in BI tools and in
Python attribute access. The field is `int64` in the customer file but `float64`
in the mailing list.

**Materiality.** Medium. The type difference is a symptom of a deeper problem —
the mailing-list values (mean well below 1, e.g. 0.2, 0.6, 0.9) are on a
visibly different scale from the training values (integers such as 3 and 6).
The two files do not appear to measure the same thing under the same name.

**Action taken.** Renamed to `Years_as_Customer` during cleaning and **excluded
from modelling** (constraint C-05). Its correlation with the target is 0.03 in
any case, so nothing predictive is lost.

### DQ-03 — `Responded_to_Last_Catalog` is missing from the mailing list

**Observation.** The field exists in the training file only.

**Materiality.** High if overlooked. A model trained on this feature could not be
scored on the campaign population at all — train/serve skew that would only
surface at scoring time.

**Action taken.** Excluded from the feature set under BRule-06. Used in EDA only.

### DQ-04 — Outliers in `Avg_Sale_Amount`

**Observation.** 58 of 2,375 records (2.4%) sit beyond the 1.5x IQR fence.
The distribution is right-skewed: mean $399.77 against a median $281.32, with a
maximum of $2,963.49 versus a minimum of $1.22.

**Materiality.** Medium. Ordinary least squares is sensitive to large residuals,
and high-value customers exert leverage on the fitted line.

**Action taken.** **Retained.** These are not data errors — they are genuine
high-value customers, concentrated in the `Loyalty Club and Credit Card`
segment, which is exactly the population the campaign most wants to reach.
Removing them would bias the model against the most profitable prospects.
The consequence is documented in the residual analysis: the model
under-predicts at the top of the range.

### DQ-05 — `Customer_ID` and `Store_Number` are numeric but not quantities

**Observation.** Both are stored as integers and would be accepted without
complaint by any regression routine.

**Materiality.** High if used naively — the model would treat "store 105" as
five units more of something than "store 100".

**Action taken.** Both are registered as identifiers in the data dictionary and
excluded from the design matrix (BRule-05).

### DQ-06 — Segment distribution differs between the two files

**Observation.**

| Segment | Training share | Mailing-list share |
|---|---|---|
| Store Mailing List | 46.7% | 8.0% |
| Loyalty Club Only | 24.4% | 48.8% |
| Credit Card Only | 20.8% | 32.8% |
| Loyalty Club and Credit Card | 8.2% | 10.4% |

**Materiality.** Medium. This is not an error — it is a population difference.
The mailing list skews towards higher-value segments, which is plausible for a
curated prospect list, but it means the campaign forecast leans on parts of the
model estimated from a smaller share of the training data.

**Action taken.** Documented as constraint C-04 and as a limitation in the
project report. The `Loyalty Club and Credit Card` coefficient is estimated from
194 training records, the smallest supporting sample of any segment.

### DQ-07 — Potential leakage check

**Observation.** No field in the feature set is a transformation of the target or
a post-outcome measurement. `Avg_Num_Products_Purchased` and `Customer_Segment`
are both known before any catalog is sent.

**Caveat.** `Avg_Num_Products_Purchased` and `Avg_Sale_Amount` are both averages
over the same historical purchase history, and correlate at r = 0.86. This is
not leakage of the campaign outcome, but it does mean the model is partly
restating an accounting relationship — customers who buy more items have larger
baskets — rather than discovering an independent behavioural driver. Noted as a
model limitation.

**Action taken.** Documented. No feature removed.

### DQ-08 — No timestamps anywhere in either file

**Observation.** Neither file carries a date of extraction, a purchase date or a
snapshot label.

**Materiality.** Medium. The recency of the training data cannot be established,
so model drift cannot be assessed against elapsed time.

**Action taken.** Registered as constraint C-09 and risk R-07. A dated snapshot
should be requested for any future refresh.

## Data-quality verdict

Both files are **fit for the intended analysis**. There are no missing values, no
duplicates and no invalid ranges. The issues found are typing and definitional
rather than corruption, and all are either corrected in the cleaning step or
explicitly excluded from modelling. The two matters that genuinely constrain the
conclusions are the differing segment mix (DQ-06) and the unverifiable
provenance of `Score_Yes` (constraint C-03), both of which are carried through
to the limitations section rather than resolved.
