"""Step 2: clean data/raw -> data/processed (+ quarantine + cleaning log)."""
import _bootstrap  # noqa: F401

from og_oip import config
from og_oip.cleaning.cleaners import clean_all
from og_oip.ingestion.loaders import load_all
from og_oip.utils.io import write_csv, write_json
from og_oip.utils.logging_utils import get_logger

log = get_logger("clean_data")


def main():
    config.ensure_dirs()
    processed, quarantine, logs = clean_all(load_all(config.RAW_DIR))
    for name, df in processed.items():
        write_csv(df, config.PROCESSED_DIR / f"{name}.csv")
    for name, q in quarantine.items():
        if len(q):
            write_csv(q, config.QUARANTINE_DIR / f"{name}_quarantine.csv")
    write_json(logs, config.PROCESSED_DIR / "cleaning_log.json")
    for k, v in logs.items():
        log.info("%s: in=%s out=%s quarantined=%s", k, v.get("rows_in"), v.get("rows_out"), v.get("rows_quarantined"))


if __name__ == "__main__":
    main()
