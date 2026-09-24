"""Step 4: build analytical marts (data/marts/*.csv) from processed data."""
import _bootstrap  # noqa: F401

from og_oip import config
from og_oip.ingestion.loaders import load_processed
from og_oip.transformation.marts import build_all_marts
from og_oip.utils.io import write_csv
from og_oip.utils.logging_utils import get_logger

log = get_logger("transform_data")


def main():
    config.ensure_dirs()
    marts = build_all_marts(load_processed())
    for name, df in marts.items():
        write_csv(df, config.MARTS_DIR / f"{name}.csv")
        log.info("%s rows=%d", name, len(df))


if __name__ == "__main__":
    main()
