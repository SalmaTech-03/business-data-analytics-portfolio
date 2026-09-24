"""Step 6: write narrative reports (business findings, real-data case studies)."""
import _bootstrap  # noqa: F401

from og_oip import config
from og_oip.reporting import markdown_reports as mr


def main():
    (config.REPORTS_DIR / "business_findings.md").write_text(mr.build_findings(), encoding="utf-8")
    (config.REPORTS_DIR / "real_data_case_studies.md").write_text(mr.build_real_report(), encoding="utf-8")


if __name__ == "__main__":
    main()
