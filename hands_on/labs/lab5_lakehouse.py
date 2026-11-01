"""Lab 5 - Lakehouse: Parquet files plus transactions, schema evolution and time travel."""
import os
import shutil
from pathlib import Path

import duckdb
import pandas as pd
from deltalake import DeltaTable, write_deltalake

os.chdir(Path(__file__).parents[1])
TABLE = "lake/delta/customers"
shutil.rmtree(TABLE, ignore_errors=True)

# Version 0: the Silver customers become a Delta table.
customers = duckdb.sql("SELECT * FROM 'lake/silver/customers.parquet'").df()
write_deltalake(TABLE, customers)
print("Rows in version 0:", DeltaTable(TABLE).to_pandas().shape[0])

# ---------- Part A: schema evolution ----------
# The source application has started sending a new email column.
new_customers = pd.read_json("source_data/incoming/customers_with_email.json", lines=True)
print("\nNew batch:\n", new_customers)

try:
    write_deltalake(TABLE, new_customers, mode="append")
except Exception as error:
    print("\nDelta protected the table. It refused the unknown column:\n ", str(error)[:120])

# TODO 1: Append new_customers again, this time allowing the new column.
# Hint: add schema_mode="merge" to the write_deltalake call
raise SystemExit("TODO 1: replace this line with your code")

table = DeltaTable(TABLE)
print("\nColumns now:", [field.name for field in table.schema().fields])
print(table.to_pandas().query("customer_id in [101, 6001]"))  # old rows have an empty email

# ---------- Part B: update a row in place (plain Parquet cannot do this) ----------
# TODO 2: Customer 101 has moved. Set the city to Hyderabad.
# Hint: table.update(predicate="customer_id = 101", updates={"city": "'Hyderabad'"})
raise SystemExit("TODO 2: replace this line with your code")
print("\nAfter the update:\n", table.to_pandas().query("customer_id == 101"))

# ---------- Part C: undo a mistake with time travel ----------
# Someone runs a bad job that replaces the whole table with 2 rows.
write_deltalake(TABLE, new_customers, mode="overwrite", schema_mode="overwrite")
print("\nAfter the bad job, rows:", DeltaTable(TABLE).to_pandas().shape[0])

print("\nTable history:")
for entry in DeltaTable(TABLE).history():
    print(f"  version {entry['version']}: {entry['operation']}")

# TODO 3: Look at version 0 without changing anything, then restore the version before the bad job.
# Hint: DeltaTable(TABLE, version=0).to_pandas()
#       DeltaTable(TABLE).restore(2)  - version 2 is the update from Part B
raise SystemExit("TODO 3: replace this line with your code")

print("Rows after restore:", DeltaTable(TABLE).to_pandas().shape[0])
print("\nQuestion: open lake/delta/customers. What is inside _delta_log, and why were no files lost?")
