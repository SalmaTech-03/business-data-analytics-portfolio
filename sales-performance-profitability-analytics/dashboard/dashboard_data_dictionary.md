# Power BI Data Model & Dashboard Data Dictionary

## Recommended model: star schema

The source data (`data/processed/orders_clean.csv`) is a single flat
table. Power BI works best with a star schema, so the build process
splits it into one fact table and dimension tables using Power Query
(see `power_bi_build_guide.md` for the exact steps).

```
                    DimDate
                       |
   DimProduct ---- FactSales ---- DimGeography
                       |
                  DimCustomer
```

## FactSales

Grain: one row per original line item (`row_id`).

| Column | Type | Source |
|---|---|---|
| row_id | Whole Number | orders_clean.csv |
| order_id | Text | orders_clean.csv |
| order_date | Date | orders_clean.csv (relates to DimDate) |
| ship_date | Date | orders_clean.csv |
| ship_mode | Text | orders_clean.csv |
| customer_id | Text | orders_clean.csv (relates to DimCustomer) |
| product_id | Text | orders_clean.csv (relates to DimProduct) |
| region | Text | orders_clean.csv (relates to DimGeography, or kept here directly -- see note below) |
| sales | Decimal Number | orders_clean.csv |
| quantity | Whole Number | orders_clean.csv |
| discount | Decimal Number | orders_clean.csv |
| profit | Decimal Number | orders_clean.csv |

**Note on Region:** since `region`/`country_region` are the only
geography fields retained after PII removal (city/state/postal code are
excluded), `DimGeography` is a small dimension (country_region, region --
4 regions, 2 countries). It's included as a separate dimension for
star-schema correctness and extensibility, but a simplified build could
also just keep `region`/`country_region` directly on FactSales given how
low-cardinality they are.

## DimDate

Grain: one row per calendar date spanning the fact table's date range
(2023-01-01 to 2026-12-31 recommended, to cover both order_date and
ship_date fully).

| Column | Type | Formula (Power Query / DAX) |
|---|---|---|
| Date | Date | Calendar column |
| Year | Whole Number | `YEAR([Date])` |
| Quarter | Whole Number | `QUARTER([Date])` |
| Month | Whole Number | `MONTH([Date])` |
| MonthName | Text | `FORMAT([Date], "MMMM")` |
| YearMonth | Text | `FORMAT([Date], "YYYY-MM")` |
| YearQuarter | Text | `YEAR([Date]) & "-Q" & QUARTER([Date])` |
| DayOfWeek | Text | `FORMAT([Date], "dddd")` |

Mark this table as the official **Date Table** in Power BI (Table Tools ->
Mark as Date Table) so time-intelligence DAX functions
(`SAMEPERIODLASTYEAR`, `DATEADD`, etc.) work correctly.

## DimProduct

Grain: one row per `(product_id, product_name, category, sub_category)`
combination -- note that 32 `product_id`s legitimately produce 2 rows
here due to the recorded-name-variant quirk documented in
`docs/data_quality.md`; this is intentional, not a modeling error.

| Column | Type |
|---|---|
| product_id | Text |
| product_name | Text |
| category | Text |
| sub_category | Text |

## DimCustomer

Grain: one row per `customer_id`. **Contains no PII** -- `customer_name`
is deliberately excluded.

| Column | Type |
|---|---|
| customer_id | Text |
| segment | Text |

## DimGeography

Grain: one row per `(country_region, region)` combination (8 rows max: 2
countries x 4 regions, though not every combination may be populated).

| Column | Type |
|---|---|
| country_region | Text |
| region | Text |

## Relationships

| From | To | Cardinality | Filter Direction |
|---|---|---|---|
| DimDate[Date] | FactSales[order_date] | 1:many | Single (DimDate filters FactSales) |
| DimProduct[product_id] | FactSales[product_id] | 1:many | Single |
| DimCustomer[customer_id] | FactSales[customer_id] | 1:many | Single |
| DimGeography[region] | FactSales[region] | 1:many | Single |

All relationships use **single-direction** filtering (dimension -> fact),
which is the standard star-schema pattern and avoids ambiguous
many-to-many filter paths. Do not enable bidirectional filtering unless a
specific visual requires it (none of the pages in
`dashboard_requirements.md` do).
