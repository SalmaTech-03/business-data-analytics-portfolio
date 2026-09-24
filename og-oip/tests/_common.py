"""Shared cached fixtures (plain functions so tests run with pytest OR tests/run_tests.py)."""
import io
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from og_oip import config
from og_oip.cleaning.cleaners import clean_all
from og_oip.data_generation import defects, generator


@lru_cache(maxsize=1)
def truth():
    return generator.generate_all(config.RANDOM_SEED)


@lru_cache(maxsize=1)
def raw_and_log():
    t = truth()
    before = generator.manifest(t, config.RANDOM_SEED)
    raw, log = defects.build_raw(t)
    after = generator.manifest(t, config.RANDOM_SEED)
    assert before == after, "build_raw modified the clean truth tables"
    raw_csv = {k: pd.read_csv(io.StringIO(v.to_csv(index=False)), low_memory=False) for k, v in raw.items()}
    return raw_csv, log


@lru_cache(maxsize=1)
def cleaned():
    raw, _ = raw_and_log()
    return clean_all(raw)


def processed_typed():
    """Processed tables with dates parsed, for marts (in memory)."""
    proc, _, _ = cleaned()
    t = {}
    for k, df in proc.items():
        d = df.copy()
        for c in ["date", "commission_date", "installation_date", "order_date", "promised_date", "received_date"]:
            if c in d.columns:
                d[c] = pd.to_datetime(d[c], errors="coerce")
        if "timestamp" in d.columns:
            d["timestamp"] = pd.to_datetime(d["timestamp"])
        t[k] = d
    return t


@lru_cache(maxsize=1)
def marts():
    from og_oip.transformation.marts import build_all_marts
    return build_all_marts(processed_typed())
