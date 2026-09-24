"""Load data/processed/*.csv into PostgreSQL (schema og_oip). Requires psycopg2 and a database created via sql/01-04.
Connection settings come ONLY from environment variables: PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.
NOTE: not executed in the build environment (no PostgreSQL / psycopg2 available). Alternative: psql -f sql/08_load_data.psql"""
import _bootstrap  # noqa: F401

from og_oip import config
from og_oip.data_generation.generator import DIM_TABLES, FACT_TABLES

ORDER = ["dim_date", "dim_field", "dim_supplier", "dim_warehouse", "dim_equipment", "dim_well", "dim_material", "bridge_equipment_well",
         "fact_production", "fact_sensor", "fact_maintenance", "fact_maintenance_material", "fact_sales", "fact_operating_cost",
         "fact_inventory", "fact_purchase_order", "fact_hse"]
assert set(ORDER) == set(DIM_TABLES + FACT_TABLES)


def main():
    try:
        import psycopg2
    except ImportError:
        raise SystemExit("psycopg2 is not installed. Install psycopg2-binary or use: psql -d og_oip -f sql/08_load_data.psql")
    db = config.DBConfig()
    conn = psycopg2.connect(host=db.host, port=db.port, dbname=db.database, user=db.user, password=db.password)
    with conn, conn.cursor() as cur:
        cur.execute("SET search_path TO og_oip")
        for t in ORDER:
            with open(config.PROCESSED_DIR / f"{t}.csv", encoding="utf-8") as fh:
                cols = fh.readline().strip()
                cur.copy_expert(f"COPY {t} ({cols}) FROM STDIN WITH (FORMAT csv)", fh)
            print("loaded", t)
    conn.close()


if __name__ == "__main__":
    main()
