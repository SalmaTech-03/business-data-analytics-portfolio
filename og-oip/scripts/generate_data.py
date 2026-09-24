"""Step 1: generate the SYNTHETIC PetroNexa dataset -> data/raw (with injected defects)."""
import _bootstrap  # noqa: F401
import argparse

from og_oip import config
from og_oip.data_generation import defects, generator
from og_oip.utils.io import write_csv, write_json
from og_oip.utils.logging_utils import get_logger

log = get_logger("generate_data")


def main(seed: int = config.RANDOM_SEED):
    config.ensure_dirs()
    tables = generator.generate_all(seed)
    raw, defect_log = defects.build_raw(tables, seed)
    for name, df in raw.items():
        write_csv(df, config.RAW_DIR / f"{name}.csv")
        log.info("raw/%s.csv rows=%d", name, len(df))
    write_json(defect_log, config.REFERENCE_DIR / "defect_injection_log.json")
    write_json(generator.manifest(tables, seed), config.REFERENCE_DIR / "generation_manifest.json")
    write_csv(tables["_well_params"], config.REFERENCE_DIR / "well_generation_parameters.csv")
    (config.RAW_DIR / "README.md").write_text(
        "# data/raw\n\n" + config.SYNTHETIC_NOTICE + "\n\nFiles here intentionally contain data-quality defects "
        "(see data/reference/defect_injection_log.json). Do not edit; run `scripts/clean_data.py` to create data/processed.\n")
    log.info("total fact rows (clean truth): %d", generator.manifest(tables, seed)["total_fact_rows"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=config.RANDOM_SEED)
    main(ap.parse_args().seed)
