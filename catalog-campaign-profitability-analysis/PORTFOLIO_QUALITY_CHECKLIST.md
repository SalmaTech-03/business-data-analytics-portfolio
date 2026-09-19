# Portfolio Quality Checklist

Final verification pass for **Catalog Campaign Profitability & Customer Targeting Analysis**.

Both datasets were supplied, so **nothing in this project is blocked on missing data**. Every
financial figure quoted anywhere in the repository was recomputed from
`data/raw/p1-customers.xlsx` and `data/raw/p1-mailinglist.xlsx` by `run_analysis.py`, and the
canonical values are written to `outputs/analysis_facts.json`.

---

## 1. Source results — independently reproduced

The three headline figures reported in the 2017 source project were reproduced **exactly**
from the raw data, not inherited on trust:

| Figure | Source project | This analysis | Status |
|---|---|---|---|
| Predicted average sales (total) | $138,292.13 | $138,292.13 | Reproduced |
| Predicted revenue | $47,224.87 | $47,224.87 | Reproduced |
| Predicted profit | $21,987.44 | $21,987.44 | Reproduced |
| R² | ≈ 0.84 | 0.8369 in-sample | Reproduced |

Because these were reproduced, the README and reports present them as verified results
rather than as "results reported in the source project."

## 2. Completeness against the specification

| Deliverable | File(s) | Status |
|---|---|---|
| Repository scaffolding | `README.md`, `LICENSE`, `.gitignore`, `requirements.txt`, `pytest.ini` | Complete |
| End-to-end pipeline | `run_analysis.py` | Complete, runs clean |
| Source modules | `src/data_cleaning.py`, `feature_engineering.py`, `modeling.py`, `profitability.py`, `evaluation.py` | Complete |
| EDA notebook | `notebooks/01_exploratory_data_analysis.ipynb` | Complete |
| Predictive model notebook | `notebooks/02_predictive_model.ipynb` | Complete |
| Profitability notebook | `notebooks/03_campaign_profitability.ipynb` | Complete |
| Sensitivity notebook | `notebooks/04_sensitivity_analysis.ipynb` | Complete |
| Business analysis docs | 15 files in `docs/` | Complete |
| Dashboard specification | `dashboard/dashboard_requirements.md`, `dashboard_data_dictionary.md` | Complete |
| Reports | `reports/executive_summary.md`, `reports/project_report.md` | Complete |
| Power BI-ready outputs | 5 CSVs + JSON in `outputs/` | Generated |
| Tests | `tests/test_profitability.py`, `tests/test_data_cleaning.py` | **77 passing** |
| Interview preparation | `docs/interview_questions.md`, `docs/resume_project_entry.md` | Complete |

## 3. Pre-finalisation checks

| # | Check | Result |
|---|---|---|
| 1 | Filenames match README references | Every path linked in `README.md` resolves |
| 2 | Formulas consistent across files | Revenue, gross profit, cost, net profit and ROI defined identically in `src/profitability.py`, `docs/kpi_framework.md`, the notebooks and both reports |
| 3 | Financial arithmetic correct | $47,224.87 × 0.50 = $23,612.44; − $1,625.00 = $21,987.44; ÷ $1,625.00 = 13.53x. Verified in code and by unit test |
| 4 | No fake claims | No company names, no employment claims, no production-deployment claims, no invented impact figures |
| 5 | Legible to a BA recruiter | `docs/` opens with the business case, stakeholders and requirements before any code appears |
| 6 | Legible to a Data Analyst recruiter | Notebooks, `src/` modules and the validation section carry the technical narrative |
| 7 | Coherent story | Business problem → data quality → EDA → model → economics → prioritisation → sensitivity → decision |
| 8 | GitHub-ready | Clean structure, MIT licence, `.gitignore`, pinned `requirements.txt`, no secrets, no large binaries |

## 4. Honesty register

Things this project deliberately states rather than hides:

- **R² is never described as "accuracy."** It is presented as ~84% of variance explained,
  always paired with MAE of $93.07 so per-customer error is visible.
- **The linear model is not the most accurate tested.** A decision tree and random forest both
  reach test R² ≈ 0.879 against 0.832. The linear model was retained for explainability, and
  the trade-off is documented rather than omitted.
- **Population shift is flagged.** The mailing list skews to higher-value segments than the
  training data (Store Mailing List 46.7% → 8.0%; Loyalty Club Only 24.4% → 48.8%). The
  forecast is presented as directionally sound, not precise.
- **Response probabilities were supplied, not modelled.** The `Score_Yes` field was used as-is;
  no probability methodology was invented, and the assumption that these are calibrated is
  registered as a risk.
- **A counter-intuitive finding is reported, not suppressed.** Prior responders average $156.40
  versus $418.66 for non-responders — a segment confound, explained rather than buried.
- **The one illustrative number is labelled.** The 3.0x ROI hurdle in
  `docs/decision_framework.md` is explicitly marked an example assumption, because no
  organisational threshold was available.
- **Priority tiers are data-derived.** High/Medium/Low come from the expected-profit
  distribution (the 75th percentile and the campaign break-even point), not from invented
  round numbers. This yields 63 High, 187 Medium, 0 Low — and the zero is reported as-is
  rather than forced into a three-way split.

## 5. Items requiring input the data cannot supply

These are limitations of the dataset, not gaps in the build. Each is documented in
`docs/assumptions_and_constraints.md` with the code path ready should the data arrive.

| Item | Why unresolved | What would resolve it |
|---|---|---|
| Product-level gross margin | Only a flat 50% assumption was given | COGS or category margin data |
| Response-score provenance | Calibration is undocumented | Historical campaign outcomes |
| Incremental lift | Measures gross response, not lift over no contact | A holdout control group, designed before launch |
| Recency / frequency signal | Not present; "years as customer" carries none (r = 0.030) | Transaction-level history |
| Actual campaign outcomes | Campaign not executed | Post-launch tracking per `docs/kpi_framework.md` |

## 6. Verification commands

```bash
pip install -r requirements.txt
python run_analysis.py      # regenerates every figure and all outputs/
pytest -q                   # 77 tests
```

Any figure in this repository can be traced to `outputs/analysis_facts.json`, which
`run_analysis.py` rewrites from the raw data on every run.
