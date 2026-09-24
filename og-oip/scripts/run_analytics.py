"""Step 5: run analytics (synthetic core + separate real-data case studies)."""
import _bootstrap  # noqa: F401
import argparse

from og_oip import config
from og_oip.analytics import runner


def main(skip_real: bool = False):
    config.ensure_dirs()
    runner.run_synthetic()
    if not skip_real:
        runner.run_real()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--skip-real", action="store_true")
    main(ap.parse_args().skip_real)
