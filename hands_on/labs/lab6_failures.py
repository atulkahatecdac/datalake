"""Lab 6 - Break the pipeline: reruns, corrupt files and flaky connections.

Part A shows the problem. Parts B and C fix it.
"""
import logging
import os
import random
import shutil
import time
from pathlib import Path

import duckdb

os.chdir(Path(__file__).parents[1])
logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
log = logging.getLogger("pipeline")
random.seed(1)

INCOMING = sorted(Path("source_data/incoming").glob("orders_*.csv"))
QUARANTINE = Path("lake/quarantine")
shutil.rmtree(QUARANTINE, ignore_errors=True)
QUARANTINE.mkdir(parents=True)

con = duckdb.connect()
con.sql("""
    CREATE TABLE fact_orders (order_id INTEGER, customer_id INTEGER, order_date DATE,
                              amount DOUBLE, status VARCHAR, source_file VARCHAR)
""")


def read_query(path):
    """Strict types, so that a bad value raises an error instead of loading."""
    return f"""
        SELECT order_id, customer_id, order_date, CAST(amount AS DOUBLE), status, '{path.name}'
        FROM read_csv('{path.as_posix()}', all_varchar=true)
    """


def revenue():
    return con.sql("SELECT sum(amount) FROM fact_orders").fetchall()[0][0]


# ---------- Part A: the naive load, run twice ----------
good_file = INCOMING[0]
for run in [1, 2]:  # the scheduler retried, or someone clicked Run again
    con.execute(f"INSERT INTO fact_orders {read_query(good_file)}")
    print(f"Naive load, run {run}: revenue = {revenue():,.0f}")
print("The second run doubled the revenue, and nothing reported an error!\n")
con.sql("DELETE FROM fact_orders")


# ---------- Part B: an idempotent load ----------
def load_file(path):
    """Running this once or ten times must give the same result."""
    # In one transaction, delete the rows from this file, then insert them again.
    con.begin()
    try:
        con.execute("DELETE FROM fact_orders WHERE source_file = ?", [path.name])
        con.execute(f"INSERT INTO fact_orders {read_query(path)}")
        con.commit()
    except Exception:
        con.rollback()
        raise


for run in [1, 2]:
    load_file(good_file)
    print(f"Idempotent load, run {run}: revenue = {revenue():,.0f}")
print()


# ---------- Part C: retries, and one bad file must not stop the rest ----------
def fetch_file(path):
    """Pretends to download a file. The network fails half the time."""
    if random.random() < 0.5:
        raise ConnectionError("network timeout")
    return path


def with_retries(path, attempts=4):
    # Try fetch_file(path). On ConnectionError, log a warning, wait longer each time, and try again.
    # After the last attempt, raise the error.
    for attempt in range(1, attempts + 1):
        try:
            return fetch_file(path)
        except ConnectionError as error:
            log.warning("%s: attempt %d failed (%s)", path.name, attempt, error)
            if attempt == attempts:
                raise
            time.sleep(0.2 * attempt)


for path in INCOMING:
    # Load each file with with_retries() and load_file(), and log success.
    # If the load fails, log an error and copy the file to QUARANTINE, then continue.
    try:
        load_file(with_retries(path))
        log.info("%s: loaded", path.name)
    except Exception as error:
        log.error("%s: quarantined (%s)", path.name, str(error).splitlines()[0])
        shutil.copy(path, QUARANTINE)

print("\nFinal table:")
con.sql("SELECT source_file, count(*) AS rows, sum(amount) AS revenue FROM fact_orders GROUP BY 1 ORDER BY 1").show()
print("Quarantined files:", [p.name for p in QUARANTINE.iterdir()])
print("Question: orders_2026-07-02.csv has one good row. Should that row have been loaded?")
