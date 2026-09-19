# Data

## Files

| File | Location | Rows | Description |
|---|---|---|---|
| `p1-customers.xlsx` | `raw/` | 2,375 | Historical customers with a known `Avg_Sale_Amount`. Used to train the model. |
| `p1-mailinglist.xlsx` | `raw/` | 250 | Campaign prospects. Scored by the model. Carries the supplied `Score_Yes` response probability but no sale amount. |

Both files are included in this repository, so the pipeline runs immediately
after installing the dependencies.

## Directory layout

```
data/
├── raw/          Source files. Never modified by any code in this repository.
└── processed/    Cleaned and scored intermediates written by run_analysis.py.
```

`processed/` is regenerated on every run and is git-ignored. `raw/` is the single
source of truth.

## Provenance

These datasets originate from the source project *Predicting Catalog Demand*.
They represent a retail company's customer base in a single US metropolitan area.

**The data carries no timestamp.** Its age and extraction date are unknown, which
is registered as constraint C-09 and risk R-07. Any future refresh should include
a snapshot date.

## Schema

Full field-level documentation — business meaning, type, role in the model, and
data-quality considerations for every column — is in
[`../docs/data_dictionary.md`](../docs/data_dictionary.md).

## Data quality

All quality checks are implemented in `src/data_cleaning.py::check_data_quality`
and run as part of the pipeline. Findings are documented in
[`../docs/data_quality.md`](../docs/data_quality.md).

Summary: no missing values, no duplicates, no invalid ranges and no unexpected
category labels in either file. The issues that exist are definitional (integer
ZIP codes, an inconsistently typed tenure field, a field present in one file but
not the other) and are handled explicitly in cleaning or excluded from modelling.

## Refreshing the data

To run this analysis on a new customer file or mailing list:

1. Place the new files in `data/raw/` using the same filenames, or pass explicit
   paths to `load_customers()` and `load_mailing_list()`.
2. Confirm the schema matches the data dictionary. New segment levels will be
   flagged by the quality check but will change the model's encoding.
3. Run `python run_analysis.py`.
4. Review the quality report in `outputs/analysis_facts.json` before trusting any
   figure.

Coefficients should be compared against the previous run at each refresh. A large
shift indicates either a data problem or genuine model drift, and either warrants
investigation before the outputs are used for a spending decision.
