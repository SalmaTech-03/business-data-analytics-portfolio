"""Run the whole pipeline end to end: generate -> clean -> validate -> transform -> analytics -> reports -> excel."""
import _bootstrap  # noqa: F401
import time

import build_business_docs
import build_excel
import clean_data
import generate_data
import generate_reports
import run_analytics
import transform_data
import validate_data


def main():
    for name, fn in [("generate", generate_data.main), ("clean", clean_data.main), ("validate", validate_data.main), ("transform", transform_data.main),
                     ("analytics", run_analytics.main), ("reports", generate_reports.main), ("excel", build_excel.main if hasattr(build_excel, "main") else None),
                     ("business docs", build_business_docs.main)]:
        if fn is None:
            continue
        t0 = time.time(); fn(); print(f"[{name}] done in {time.time() - t0:.1f}s")
    print("Note: after building the workbook run: python /path/to/xlsx/scripts/recalc.py excel/OG_OIP_Analysis_Workbook.xlsx (LibreOffice) to cache formula values.")


if __name__ == "__main__":
    main()
