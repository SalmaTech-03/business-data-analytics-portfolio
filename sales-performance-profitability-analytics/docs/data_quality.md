# Data Quality Report

Generated from actual profiling of `sample_-_superstore.xls`, run via
`notebooks/01_data_quality.ipynb` and `src/validation.py`. Every number
below was calculated, not estimated.

## Summary

| Check | Result |
|---|---|
| Total rows (Orders) | 10,194 |
| Missing values (any column) | 0 |
| Fully duplicated rows | 0 |
| Duplicate `row_id` values | 0 |
| Rows with `sales` <= 0 | 0 |
| Rows with `quantity` <= 0 | 0 |
| Rows with `discount` outside [0, 1] | 0 |
| Rows where `ship_date` < `order_date` | 0 |
| Order Date range | 2023-01-03 to 2026-12-30 |
| Ship Date range | 2023-01-07 to 2027-01-05 |
| Distinct orders | 5,111 |
| Distinct customers | 804 |
| Distinct products (`product_id`) | 1,862 |
| Distinct categories | 3 |
| Distinct sub-categories | 17 |
| Distinct regions | 4 |
| Distinct countries | 2 (United States, Canada) |
| Returns rows referencing an unknown Order ID | 0 of 296 |

**Verdict: this dataset is clean at the row level.** No rows were dropped
anywhere in this pipeline (`src/data_cleaning.py` documents every check it
performs and confirms none required deletion).

## Known quirks (documented, not silently corrected)

### 1. Two `order_id`s span multiple `customer_id`s

`CA-2025-121465` and `CA-2026-130494` each have 4 line items, and each line
item is attributed to a *different* `customer_id` (`HO-15231` through
`HO-15234`), all belonging to the same `customer_name`, **"Harry Olson"**.
This is a source-system data-entry artifact -- the same person appears to
have been issued 4 separate Customer IDs.

- **Why it wasn't corrected:** there's no reliable way to know which of the
  4 IDs is "canonical" without external information not present in the
  dataset. Merging them would be a guess, not a data-quality fix.
- **How it's handled:** flagged by `src/validation.py`
  (`check_order_customer_consistency`), explicitly excluded from the
  blocking-failure list in `run_analysis.py` (documented, not silently
  ignored), and pinned by a regression test
  (`tests/test_data_quality.py::test_known_multi_customer_order_quirk_is_exactly_two`)
  so a future dataset refresh that changes this count is caught immediately.
- **Impact on KPIs:** negligible. It affects 2 of 5,111 orders (0.04%) and
  does not change any headline number materially.

### 2. 32 `product_id`s map to more than one `product_name`

`product_name` has 1,849 distinct values against 1,862 distinct
`product_id` values -- meaning some product IDs were recorded under
slightly different name text at different times (e.g. spelling/formatting
variants). `category` and `sub_category` are consistent per `product_id`
in all cases (0 conflicts), so this only affects the display name, not
categorization or any financial calculation.

- **Handling:** `src/feature_engineering.py`'s `build_product_level_table`
  groups by `(product_id, product_name, category, sub_category)` together,
  which means these 32 product IDs appear as 2 rows each in
  `product_summary.csv` (one per name variant) rather than being silently
  merged into one. This is a deliberate choice to avoid guessing which name
  is correct; a reviewer can identify and merge them manually if a single
  canonical name is needed.

### 3. Dataset includes dates after the pipeline's "current date" reference

The dataset's Order Date extends to 2026-12-30, which is a synthetic/demo
date range built into this sample dataset (not evidence of a data error).
All 4 calendar years present (2023-2026) have a full 12 months of data, so
year-over-year comparisons in this project are between complete years.

### 4. Dataset spans 2 countries, not 1

This version of the Sample Superstore dataset includes 200 rows from
Canada (vs. 9,994 from the United States) -- more than the single-country
version some readers may be more familiar with. `country_region` is
retained as a real dimension throughout this project rather than assumed
away.

## Validation suite results

Running `src/validation.py::run_all_checks()` against the cleaned dataset
produces:

```
[PASS] required_columns
[PASS] no_missing_values
[PASS] no_full_duplicate_rows
[PASS] row_id_is_unique
[PASS] dates_valid
[PASS] positive_quantity
[PASS] positive_sales
[PASS] discount_in_valid_range
[FAIL] order_maps_to_single_customer   (documented quirk #1 above)

8/9 checks passed.
```

This single, well-understood, low-impact failure is the only validation
issue in the entire dataset.
