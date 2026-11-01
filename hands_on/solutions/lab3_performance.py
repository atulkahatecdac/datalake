"""Lab 3 - Make it fast: same data, same question, three storage layouts."""
import os
import shutil
import time
from pathlib import Path

import duckdb

os.chdir(Path(__file__).parents[1])
PERF = Path("lake/perf")
shutil.rmtree(PERF, ignore_errors=True)
PERF.mkdir(parents=True)
con = duckdb.connect()

# Copy the Silver orders 100 times to get about 20 million rows.
# Ids and amounts vary, because exact copies would compress unrealistically well.
con.sql("""
    CREATE TABLE big_orders AS
    SELECT o.order_id + 1000000 * r.range AS order_id, o.customer_id, o.order_date,
           round(o.amount * (0.9 + random() * 0.2)) AS amount, o.status,
           year(o.order_date) AS year, month(o.order_date) AS month
    FROM 'lake/silver/orders.parquet' o, range(100) r
""")
print("Rows:", con.sql("SELECT count(*) FROM big_orders").fetchall()[0][0])

con.sql("COPY big_orders TO 'lake/perf/orders.csv' (HEADER)")

# TODO 1: Write big_orders as one Parquet file: lake/perf/orders.parquet
# Hint: COPY table TO 'path' (FORMAT parquet)
con.sql("COPY big_orders TO 'lake/perf/orders.parquet' (FORMAT parquet)")
# END TODO

# TODO 2: Write big_orders as Parquet, partitioned by year and month, to lake/perf/partitioned
# Hint: add PARTITION_BY (year, month) inside the brackets
con.sql("COPY big_orders TO 'lake/perf/partitioned' (FORMAT parquet, PARTITION_BY (year, month))")
# END TODO


def size_mb(path):
    path = Path(path)
    files = path.rglob("*") if path.is_dir() else [path]
    return sum(f.stat().st_size for f in files if f.is_file()) / 1_000_000


# January 2026 revenue, asked three times.
tests = {
    "CSV": ("lake/perf/orders.csv", """
        SELECT sum(amount) FROM read_csv('lake/perf/orders.csv')
        WHERE year = 2026 AND month = 1"""),
    "Parquet": ("lake/perf/orders.parquet", """
        SELECT sum(amount) FROM 'lake/perf/orders.parquet'
        WHERE year = 2026 AND month = 1"""),
}

# TODO 3: Add the third test, named "Parquet + partitions", in the same format as above.
# Hint: FROM read_parquet('lake/perf/partitioned/*/*/*.parquet', hive_partitioning=true)
tests["Parquet + partitions"] = ("lake/perf/partitioned", """
    SELECT sum(amount)
    FROM read_parquet('lake/perf/partitioned/*/*/*.parquet', hive_partitioning=true)
    WHERE year = 2026 AND month = 1""")
# END TODO

print(f"\n{'Layout':<22}{'Size MB':>10}{'Seconds':>10}{'Revenue':>18}")
for name, (path, query) in tests.items():
    start = time.perf_counter()
    revenue = duckdb.sql(query).fetchall()[0][0]  # a new query, nothing kept in memory
    seconds = time.perf_counter() - start
    print(f"{name:<22}{size_mb(path):>10,.0f}{seconds:>10.3f}{revenue:>18,.0f}")

print("\nThe revenue must be identical in all three rows. If it is not, stop and find out why.")
print("Question: which folders did the partitioned query not need to open?")
shutil.rmtree(PERF)  # free the disk space
