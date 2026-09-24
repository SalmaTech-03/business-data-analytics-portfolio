"""Step 7: build excel/OG_OIP_Analysis_Workbook.xlsx (then recalculate with LibreOffice if available)."""
import _bootstrap  # noqa: F401

from og_oip import config
from og_oip.reporting.excel_workbook import build

def main():
    build(config.EXCEL_DIR / "OG_OIP_Analysis_Workbook.xlsx")


if __name__ == "__main__":
    main()
