from _common import *  # noqa
import re
from pathlib import Path
import pandas as pd
from og_oip import config

SQL = config.ROOT / "sql"


def _schema():
    txt = (SQL / "02_create_dimensions.sql").read_text() + (SQL / "03_create_facts.sql").read_text()
    out = {}
    for m in re.finditer(r"CREATE TABLE (\w+) \((.*?)\n\);", txt, re.S):
        cols = []
        for line in m.group(2).split("\n"):
            line = line.strip()
            if not line or line.startswith(("PRIMARY KEY", "--", "CHECK", "FOREIGN")):
                continue
            cols.append(line.split()[0])
        out[m.group(1)] = cols
    return out


def test_sql_columns_match_processed_csv_headers():
    proc, _, _ = cleaned()
    sch = _schema()
    for name, df in proc.items():
        assert name in sch, f"{name} missing from SQL schema"
        assert sch[name] == list(df.columns), (name, sch[name], list(df.columns))


def test_query_count_and_views_and_loader():
    q = (SQL / "06_analysis_queries.sql").read_text() + (SQL / "07_business_questions.sql").read_text()
    assert len(re.findall(r"^-- (Q|BQ)\d+", q, re.M)) >= 40
    views = (SQL / "05_views.sql").read_text()
    assert len(re.findall(r"CREATE OR REPLACE VIEW", views)) >= 6
    load = (SQL / "08_load_data.psql").read_text()
    for t in _schema():
        assert f"\\copy {t} " in load, t


def test_referenced_tables_exist():
    sch = set(_schema()); views = set(re.findall(r"CREATE OR REPLACE VIEW (\w+)", (SQL / "05_views.sql").read_text()))
    txt = (SQL / "06_analysis_queries.sql").read_text() + (SQL / "07_business_questions.sql").read_text() + views_text()
    used = set(re.findall(r"\b(?:FROM|JOIN)\s+((?:fact_|dim_|bridge_|v_)\w+)", txt))
    unknown = used - sch - views
    assert not unknown, unknown


def views_text():
    return (SQL / "05_views.sql").read_text()


def test_no_hardcoded_credentials_in_python():
    for f in list(config.ROOT.glob("src/**/*.py")) + list(config.ROOT.glob("scripts/*.py")) + list(config.ROOT.glob("app/*.py")):
        for line in f.read_text().splitlines():
            assert not re.search(r"password\s*=\s*[\"'][^\"']+[\"']", line, re.I), (f, line)


def test_dax_columns_exist_in_schema():
    sch = _schema(); dax = (config.ROOT / "powerbi" / "dax_measures.dax").read_text()
    skip = {"ml_latest_equipment_risk", "forecast_next_30d", "Exposure Hours per Well-Day"}
    for tbl, col in re.findall(r"\b(\w+)\[(\w+)\]", dax):
        if tbl in sch:
            assert col in sch[tbl] + ["on_time", "actual_lead_days", "date"], (tbl, col)
