"""Step 3: validate RAW and PROCESSED data and write reports/data_quality_report.{md,html}."""
import _bootstrap  # noqa: F401

from og_oip import config
from og_oip.ingestion.loaders import load_all
from og_oip.utils.io import read_json, write_csv
from og_oip.utils.logging_utils import get_logger
from og_oip.validation.checks import run_all_checks
from og_oip.validation.report import build_report

log = get_logger("validate_data")


def main():
    config.ensure_dirs()
    raw_res = run_all_checks(load_all(config.RAW_DIR), "raw")
    proc = load_all(config.PROCESSED_DIR)
    proc_res = run_all_checks(proc, "processed")
    write_csv(raw_res, config.TABLES_DIR / "dq_results_raw.csv")
    write_csv(proc_res, config.TABLES_DIR / "dq_results_processed.csv")
    defect_path = config.REFERENCE_DIR / "defect_injection_log.json"
    build_report(raw_res, proc_res, read_json(config.PROCESSED_DIR / "cleaning_log.json"),
                 read_json(defect_path) if defect_path.exists() else None,
                 config.REPORTS_DIR / "data_quality_report.md", config.REPORTS_DIR / "data_quality_report.html")
    log.info("raw failed checks=%d processed failed checks=%d", (raw_res.status != "PASS").sum(), (proc_res.status != "PASS").sum())
    return proc_res


if __name__ == "__main__":
    main()
