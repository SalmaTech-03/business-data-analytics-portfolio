# Portfolio Quality Checklist

Verified against the actual repository contents and actual execution
results — not aspirational.

| | Item | Status |
|---|---|---|
| [x] | **Dataset documented** | 6,780 rows × 20 columns fully profiled in `docs/data_dictionary.md`; scope adaptation from the original retail brief disclosed in `docs/assumptions_and_constraints.md` |
| [x] | **Data quality validated** | `docs/data_quality.md` — 0 nulls, 0 duplicates, 0 domain violations; 2 issues flagged and disclosed (258 utilization outliers, unreconciled variance columns) |
| [x] | **Python pipeline works** | `python run_analysis.py` executed successfully end-to-end; produced 5 tables and 6 figures |
| [x] | **SQL queries created** | 8 PostgreSQL-compatible scripts in `sql/`, each with business purpose, comments, and output explanation |
| [x] | **KPIs validated** | 11 headline KPIs, each with explicit formula, docstring, and unit tests verifying against hand-computed values |
| [x] | **Power BI model documented** | Star schema with fact + 2 dimensions, relationships and filter direction specified in `dashboard/power_bi_build_guide.md` |
| [x] | **DAX documented** | 12 measures in `dashboard/dax_measures.md`, each mapped to its Python counterpart; omitted time-intelligence measures explained |
| [x] | **Dashboard specification complete** | 5 pages fully specified with KPI cards, charts, and interactivity requirements |
| [x] | **Tests pass** | 34/34 pytest tests passing |
| [x] | **Notebooks execute** | All 5 notebooks run top-to-bottom without error, with outputs embedded |
| [x] | **No PII** | Dataset contains no personal data; `data/raw/` git-ignored on principle; only aggregated outputs committed |
| [x] | **No fabricated findings** | Every figure in README, findings, recommendations, and reports comes from actual pipeline execution |
| [x] | **GitHub-safe** | `.gitignore` excludes raw data and all CSV/Excel except aggregated outputs; no credentials, no absolute paths |
| [x] | **Resume entry complete** | `docs/resume_project_entry.md` — 5 bullets, no fabricated metrics |
| [x] | **Interview questions complete** | `docs/interview_questions.md` — 25 questions with project-specific answers |

## Honesty audit

Explicit checks that this project does **not** overclaim:

- [x] Dataset identified as public/sample representing a fictional
      organization; no real-company claim anywhere.
- [x] No `.pbix` file is claimed to exist — the dashboard is
      documented as a specification.
- [x] No production deployment is claimed.
- [x] No business impact (revenue saved, cost reduced) is claimed for
      a fictional company.
- [x] No causal claims — all findings framed as cross-sectional
      associations.
- [x] No growth rates or trends computed, because the data has no
      fiscal year to support them.
- [x] Retail-style questions the dataset cannot answer (top products,
      regional sales, discount vs. profit, repeat customer rate) are
      omitted rather than answered with substitutes.
- [x] The scope change from the original retail brief is disclosed in
      the README, not buried.
- [x] Data-quality problems are disclosed in the README rather than
      only in a deep-linked doc.
- [x] Limitations appear in README, executive summary, project report,
      and per-recommendation.

## Review log

| Date | Challenge raised | Outcome |
|---|---|---|
| Pre-release | Do department record counts drop 39/63 rows vs. the raw 6,780? | **No discrepancy.** Counts sum to exactly 6,780 (904+886+841+843+843+833+816+814). Verified against the delivered CSV and now locked by two regression tests (`test_department_record_counts_sum_to_total_rows`, `test_expense_category_record_counts_sum_to_total_rows`). |
| Pre-release | Is `total_variance` a different measure from the utilization calculations? | **Yes, correctly identified.** The column was `SUM(Budget_Variance)` (supplied) while all rates used Allocated/Utilized. Renamed to `supplied_budget_variance` and added `computed_budget_gap` alongside it; three regression tests added; `data_dictionary.md`, `data_quality.md`, `kpi_framework.md`, and README updated with exact figures. |
| Pre-release | — | **Error found and fixed:** `data_dictionary.md` listed Budget_Variance's range as "-~221,801 to +~19,998". The lower bound was mistakenly carried over from the reconciliation-difference distribution. Corrected to the actual -19,995.81 to +19,998.28. |

## Known manual steps

| Step | Why |
|---|---|
| Build the Power BI `.pbix` | Power BI Desktop is not available in the build environment; full build guide provided |
| Load CSV into PostgreSQL | SQL scripts are written but not executed against a live database in this repo |
| Add GitHub Actions CI | Listed as a future improvement, not implemented |
