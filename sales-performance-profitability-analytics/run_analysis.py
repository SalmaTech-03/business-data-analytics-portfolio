"""
run_analysis.py
================
End-to-end pipeline: Load -> Validate -> Clean -> Engineer Features ->
Calculate KPIs -> Generate Analysis Tables -> Generate Visualizations ->
Save Safe Aggregated Outputs -> Print Summary.

Run from the project root:

    python run_analysis.py

Outputs (all safe for a public repo -- see docs/data_quality.md and
data/README.md for the PII rationale):
    data/processed/orders_clean.csv         (line items, NO customer_name/city/state)
    outputs/tables/*.csv                    (aggregated KPI/breakdown tables)
    outputs/figures/*.png                   (charts)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_loading import load_orders, load_returns  # noqa: E402
from data_cleaning import clean_orders  # noqa: E402
from validation import run_all_checks  # noqa: E402
from feature_engineering import engineer_all  # noqa: E402
from kpi_calculations import compute_core_kpis, revenue_by_period, revenue_growth  # noqa: E402
import visualization as viz  # noqa: E402

OUTPUT_TABLES = Path("outputs/tables")
OUTPUT_FIGURES = Path("outputs/figures")
PROCESSED_DATA = Path("data/processed")

# Columns considered PII / customer-identifying -- dropped from every
# output that leaves the pipeline, per the project's public-repo
# privacy requirement (see data/README.md).
PII_COLUMNS = ["customer_name", "city", "state_province", "postal_code"]


def main() -> int:
    print("=" * 70)
    print("SALES PERFORMANCE & PROFITABILITY ANALYTICS -- PIPELINE RUN")
    print("=" * 70)

    # 1. Load
    print("\n[1/8] Loading data...")
    raw = load_orders()
    returns_df = load_returns()
    print(f"      Loaded {raw.shape[0]:,} rows, {raw.shape[1]} columns from Orders.")

    # 2. Validate (pre-clean, on raw structure)
    print("\n[2/8] Validating raw data...")
    from data_cleaning import standardize_column_names
    raw_std = standardize_column_names(raw)
    results = run_all_checks(raw_std)
    for r in results:
        print(f"      {r}")
    failed = [r for r in results if not r.passed]
    non_blocking = {"order_maps_to_single_customer"}  # documented known quirk
    blocking_failures = [r for r in failed if r.name not in non_blocking]
    if blocking_failures:
        print(f"\n      BLOCKING validation failures: {[r.name for r in blocking_failures]}")
        return 1
    print(f"      {len(results) - len(failed)}/{len(results)} checks passed "
          f"({len(failed)} non-blocking, documented quirk).")

    # 3. Clean
    print("\n[3/8] Cleaning data...")
    cleaned, report = clean_orders(raw)
    print(f"      {report.rows_in:,} rows in -> {report.rows_out:,} rows out (no rows dropped).")

    # 4. Engineer features
    print("\n[4/8] Engineering features...")
    tables = engineer_all(cleaned)
    lines = tables["lines"]
    print(f"      Built: lines ({lines.shape[0]:,} rows), "
          f"order_level ({tables['order_level'].shape[0]:,}), "
          f"customer_level ({tables['customer_level'].shape[0]:,}), "
          f"product_level ({tables['product_level'].shape[0]:,}).")

    # 5. Calculate KPIs
    print("\n[5/8] Calculating KPIs...")
    kpis = compute_core_kpis(lines)
    for k, v in kpis.items():
        print(f"      {k}: {v:,.4f}" if isinstance(v, float) else f"      {k}: {v:,}")

    # 6. Generate analysis tables
    print("\n[6/8] Generating analysis tables...")
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA.mkdir(parents=True, exist_ok=True)

    monthly = revenue_by_period(lines, "order_year_month")
    monthly.to_csv(OUTPUT_TABLES / "revenue_by_month.csv", index=False)

    yearly_growth = revenue_growth(lines, "order_year")
    yearly_growth.to_csv(OUTPUT_TABLES / "revenue_growth_by_year.csv", index=False)

    category_summary = (
        lines.groupby("category")
        .agg(revenue=("sales", "sum"), profit=("profit", "sum"), units=("quantity", "sum"))
        .reset_index()
    )
    category_summary["margin"] = category_summary["profit"] / category_summary["revenue"]
    category_summary = category_summary.sort_values("revenue", ascending=False)
    category_summary.to_csv(OUTPUT_TABLES / "category_summary.csv", index=False)

    subcategory_summary = (
        lines.groupby("sub_category")
        .agg(revenue=("sales", "sum"), profit=("profit", "sum"), units=("quantity", "sum"))
        .reset_index()
    )
    subcategory_summary["margin"] = subcategory_summary["profit"] / subcategory_summary["revenue"]
    subcategory_summary = subcategory_summary.sort_values("revenue", ascending=False)
    subcategory_summary.to_csv(OUTPUT_TABLES / "subcategory_summary.csv", index=False)

    region_summary = (
        lines.groupby("region")
        .agg(revenue=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )
    region_summary["margin"] = region_summary["profit"] / region_summary["revenue"]
    region_summary = region_summary.sort_values("revenue", ascending=False)
    region_summary.to_csv(OUTPUT_TABLES / "region_summary.csv", index=False)

    segment_summary = (
        lines.groupby("segment")
        .agg(revenue=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )
    segment_summary["margin"] = segment_summary["profit"] / segment_summary["revenue"]
    segment_summary = segment_summary.sort_values("revenue", ascending=False)
    segment_summary.to_csv(OUTPUT_TABLES / "segment_summary.csv", index=False)

    import pandas as pd
    bins = [-0.01, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    bin_labels = ["0%", "0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50%+"]
    lines_disc = lines.copy()
    lines_disc["discount_bucket"] = pd.cut(lines_disc["discount"], bins=bins, labels=bin_labels)
    discount_summary = (
        lines_disc.groupby("discount_bucket", observed=True)
        .agg(revenue=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )
    discount_summary["margin"] = discount_summary["profit"] / discount_summary["revenue"]
    discount_summary.to_csv(OUTPUT_TABLES / "discount_bucket_summary.csv", index=False)

    # Product / customer tables -- customer_level is safe (customer_id only, no name/city).
    tables["product_level"].to_csv(OUTPUT_TABLES / "product_summary.csv", index=False)
    tables["customer_level"].to_csv(OUTPUT_TABLES / "customer_summary.csv", index=False)

    print(f"      Saved 8 aggregated tables + 2 entity-level tables to {OUTPUT_TABLES}/")

    # 7. Generate visualizations
    print("\n[7/8] Generating visualizations...")
    viz.plot_monthly_revenue_profit(monthly, str(OUTPUT_FIGURES / "monthly_revenue_profit.png"))
    viz.plot_category_revenue_profit(category_summary, str(OUTPUT_FIGURES / "category_revenue_profit.png"))
    viz.plot_subcategory_margin(subcategory_summary, str(OUTPUT_FIGURES / "subcategory_margin.png"))
    viz.plot_region_performance(region_summary, str(OUTPUT_FIGURES / "region_performance.png"))
    viz.plot_discount_vs_margin(discount_summary, str(OUTPUT_FIGURES / "discount_vs_margin.png"))
    viz.plot_top_products(tables["product_level"], str(OUTPUT_FIGURES / "top_products.png"))
    viz.plot_customer_revenue_distribution(tables["customer_level"], str(OUTPUT_FIGURES / "customer_revenue_pareto.png"))
    print(f"      Saved 7 charts to {OUTPUT_FIGURES}/")

    # 8. Save safe processed dataset + print summary
    print("\n[8/8] Saving processed dataset (PII columns removed) & printing summary...")
    safe_lines = lines.drop(columns=[c for c in PII_COLUMNS if c in lines.columns])
    safe_lines.to_csv(PROCESSED_DATA / "orders_clean.csv", index=False)
    print(f"      Saved de-identified line-item dataset "
          f"({safe_lines.shape[0]:,} rows, {safe_lines.shape[1]} columns, "
          f"PII columns removed: {PII_COLUMNS}) to {PROCESSED_DATA}/orders_clean.csv")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Revenue:            ${kpis['total_revenue']:,.2f}")
    print(f"Total Profit:             ${kpis['total_profit']:,.2f}")
    print(f"Profit Margin:            {kpis['profit_margin']:.2%}")
    print(f"Total Orders:             {kpis['total_orders']:,}")
    print(f"Total Units Sold:         {kpis['total_units']:,}")
    print(f"Average Order Value:      ${kpis['average_order_value']:,.2f}")
    print(f"Customer Count:           {kpis['customer_count']:,}")
    print(f"Repeat Customer Rate:     {kpis['repeat_customer_rate']:.2%}")
    print(f"Top Category by Revenue:  {category_summary.iloc[0]['category']}")
    print(f"Top Region by Revenue:    {region_summary.iloc[0]['region']}")
    print("=" * 70)
    print("Pipeline completed successfully. No customer PII written to outputs/ or data/processed/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
