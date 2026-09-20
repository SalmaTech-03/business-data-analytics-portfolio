"""
run_analysis.py

End-to-end pipeline entry point:
1. Load data
2. Validate data
3. Clean data
4. Engineer features
5. Calculate KPIs
6. Generate analysis (group-by) tables -> outputs/tables/
7. Generate selected visualizations -> outputs/figures/
8. Save safe, aggregated outputs only (no row-level / PII-adjacent data)
9. Print a concise analysis summary

Run from the project root:
    python run_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from data_loading import load_dataset          # noqa: E402
from data_cleaning import clean_dataset          # noqa: E402
from feature_engineering import engineer_features  # noqa: E402
from validation import run_all_validations       # noqa: E402
import kpi_calculations as kpi                    # noqa: E402
import visualization as viz                        # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def main() -> None:
    print("=" * 60)
    print("BUDGET PERFORMANCE & VARIANCE ANALYTICS - PIPELINE RUN")
    print("=" * 60)

    # 1. Load
    print("\n[1/9] Loading data...")
    raw = load_dataset()
    print(f"   Loaded {len(raw):,} rows, {len(raw.columns)} columns.")

    # 2. Validate (pre-clean, on standardized copy for validation module)
    print("\n[2/9] Validating raw data...")
    from data_cleaning import standardize_columns, convert_types
    pre = convert_types(standardize_columns(raw))
    result = run_all_validations(pre)
    print("   " + result.report().replace("\n", "\n   "))
    if not result.passed:
        print("\n   VALIDATION FAILED - stopping pipeline.")
        sys.exit(1)

    # 3. Clean
    print("\n[3/9] Cleaning data...")
    cleaned, clean_report = clean_dataset(raw)
    print("   " + clean_report.summary().replace("\n", "\n   "))

    # 4. Feature engineering
    print("\n[4/9] Engineering features...")
    df = engineer_features(cleaned)
    print(f"   Added columns: utilization_rate, budget_variance_pct, "
          f"revenue_variance_pct, revenue_realization_rate, "
          f"monthly_expense_to_budget, is_overspent, is_underspent, "
          f"efficiency_tier")

    # 5. KPIs
    print("\n[5/9] Calculating KPIs...")
    summary = kpi.kpi_summary(df)
    by_dept = kpi.kpis_by_department(df)
    by_category = kpi.kpis_by_expense_category(df)
    by_quarter = kpi.kpis_by_quarter(df)
    top_combos = kpi.top_overspent_department_category(df, 10)

    # 6. Save analysis tables (aggregated only - see data/README.md)
    print("\n[6/9] Saving analysis tables to outputs/tables/...")
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    with open(TABLES_DIR / "kpi_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    by_dept.to_csv(TABLES_DIR / "kpis_by_department.csv")
    by_category.to_csv(TABLES_DIR / "kpis_by_expense_category.csv")
    by_quarter.to_csv(TABLES_DIR / "kpis_by_quarter.csv")
    top_combos.to_csv(TABLES_DIR / "top_utilization_combinations.csv", index=False)
    print(f"   Saved 5 aggregated tables.")

    # 7. Visualizations
    print("\n[7/9] Generating visualizations to outputs/figures/...")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    viz.plot_budget_vs_utilized_by_department(by_dept, FIGURES_DIR / "budget_vs_utilized_by_department.png")
    viz.plot_utilization_rate_by_department(by_dept, FIGURES_DIR / "utilization_rate_by_department.png")
    viz.plot_allocation_efficiency_distribution(df, FIGURES_DIR / "allocation_efficiency_distribution.png")
    viz.plot_budget_status_by_department(df, FIGURES_DIR / "budget_status_by_department.png")
    viz.plot_revenue_forecast_vs_actual(by_dept, df, FIGURES_DIR / "revenue_forecast_vs_actual.png")
    viz.plot_spending_volatility_vs_status(df, FIGURES_DIR / "spending_volatility_vs_status.png")
    print("   Saved 6 figures.")

    # 8. Privacy check note
    print("\n[8/9] Privacy check: outputs contain only aggregated group-by "
          "tables and summary statistics - no row-level records.")

    # 9. Summary
    print("\n[9/9] ANALYSIS SUMMARY")
    print("-" * 60)
    print(f"Records analyzed:          {summary['record_count']:,}")
    print(f"Departments:               {summary['department_count']}")
    print(f"Total Budget Allocated:    ${summary['total_budget_allocated']:,.2f}")
    print(f"Total Budget Utilized:     ${summary['total_budget_utilized']:,.2f}")
    print(f"Overall Utilization Rate:  {summary['overall_utilization_rate']:.2%}")
    print(f"Total Revenue Forecast:    ${summary['total_revenue_forecast']:,.2f}")
    print(f"Total Actual Revenue:      ${summary['total_actual_revenue']:,.2f}")
    print(f"Revenue Realization Rate:  {summary['revenue_realization_rate']:.2%}")
    print(f"Avg Allocation Efficiency: {summary['average_allocation_efficiency']:.2f} / 100")
    print("Budget Status Mix:         " + ", ".join(
        f"{k}: {v:.1%}" for k, v in summary['budget_status_distribution'].items()
    ))
    print("-" * 60)
    print("Pipeline complete. See outputs/tables/ and outputs/figures/.")


if __name__ == "__main__":
    main()
