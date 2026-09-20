# Portfolio Quality Checklist

- [x] Dataset documented -- `docs/data_dictionary.md`, `docs/data_quality.md`
- [x] Data quality validated -- 8/9 automated checks pass; the 1 failure is
      a documented, pinned, non-blocking known quirk (`docs/data_quality.md`)
- [x] Python pipeline works -- `python run_analysis.py` runs end-to-end
      without error, 10,194 rows in / 10,194 rows out, no PII in outputs
- [x] SQL queries created -- 8 files, logic-validated against real data
      (see `docs/analytical_methodology.md` for the validation method and
      its one disclosed limitation: SQLite validation, not live PostgreSQL)
- [x] KPIs validated -- 15 KPIs, each with formula + actual calculated
      value, cross-checked between Python and SQL implementations
- [x] Power BI model documented -- `dashboard/dashboard_data_dictionary.md`
      (star schema: FactSales + 4 dimensions)
- [x] DAX documented -- `dashboard/dax_measures.md`, 12 measures, each
      matching its `docs/kpi_framework.md` definition exactly
- [x] Dashboard specification complete -- `dashboard/dashboard_requirements.md`
      (5 pages), `dashboard/power_bi_build_guide.md` (step-by-step)
- [x] Tests pass -- 36/36 (see `reports/project_report.md` section 13 for
      the honest note on how they were executed in this sandbox)
- [x] README complete -- all 18 required sections present
- [x] No PII -- enforced by `PII_COLUMNS` in `run_analysis.py` and by an
      automated test (`tests/test_business_rules.py::test_no_pii_columns_in_de_identified_output`)
- [x] No fabricated findings -- every number in `docs/findings.md`,
      `docs/recommendations.md`, `reports/`, and `README.md` traces to a
      specific SQL query, notebook cell, or `outputs/tables/*.csv` file
- [x] GitHub-safe -- `.gitignore` excludes `data/raw/`, all Excel/CSV
      source files, and Python/Jupyter artifacts
- [x] Resume entry complete -- `docs/resume_project_entry.md`
- [x] Interview questions complete -- `docs/interview_questions.md`, 25
      questions with project-specific answers

## Final status report

**Files created:** 45 files across `src/`, `sql/`, `notebooks/`, `docs/`,
`dashboard/`, `reports/`, `tests/`, plus root-level config and README files.

**Files requiring manual action from you:**
- The raw dataset itself (`data/raw/sample_-_superstore.xlsx`) is not
  committed to Git per the privacy requirement -- you'll need to keep your
  own local copy to re-run the pipeline, and NOT push it to GitHub.
- The actual `.pbix` Power BI file does not exist yet -- follow
  `dashboard/power_bi_build_guide.md` to build it in Power BI Desktop.
- Consider adding 1-2 dashboard page screenshots to `outputs/figures/` (or
  a new `dashboard/screenshots/` folder) once you've built the `.pbix`, to
  make the README more visually compelling for recruiters.

**Python execution status:** `run_analysis.py` runs successfully end-to-end
(verified in this build).

**Test status:** 36/36 passing (verified in this build; see
`reports/project_report.md` section 13 for the environment note).

**SQL status:** All 8 files' logic verified against the real dataset via a
local SQLite mirror (see `docs/analytical_methodology.md`); re-confirm
Postgres-specific syntax against your actual warehouse before production use.

**Power BI manual steps:** Full build required -- follow
`dashboard/power_bi_build_guide.md` steps 1-7.

**Privacy status:** No customer PII in any committed file; enforced by
`.gitignore` and an automated test.

**GitHub readiness:** Ready to push as-is, after you confirm
`data/raw/` is genuinely excluded (check `git status` before your first
commit) and add your own repo URL to `README.md`'s "How to Run" section.

**Resume-ready project title:** Sales Performance & Profitability Analytics

**Resume-ready bullets:** see `docs/resume_project_entry.md`.
