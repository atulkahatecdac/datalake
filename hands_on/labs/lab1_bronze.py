"""Lab 1 - Bronze: bring the raw files into the lake, unchanged.

Rule of Bronze: never edit the data. If a later step has a bug, you can always
go back to the original.
"""
import os
import shutil
from pathlib import Path

import duckdb

os.chdir(Path(__file__).parents[1])  # run from the hands_on folder

LOAD_DATE = "2026-07-01"  # fixed for class; a real pipeline uses today's date
SOURCES = {
    "orders": "source_data/orders.csv",
    "customers": "source_data/customers.json",
    "clicks": "source_data/clicks.log",
}

for table, source_file in SOURCES.items():
    target_dir = Path(f"lake/bronze/{table}/load_date={LOAD_DATE}")

    # TODO 1: Create target_dir (with parents) and copy source_file into it.
    # Hint: target_dir.mkdir(parents=True, exist_ok=True) and shutil.copy(from, to)
    raise SystemExit("TODO 1: replace this line with your code")

    print(f"Loaded {source_file} -> {target_dir}")

# Query raw files directly, without loading them into a database first.
print("\nFirst rows of raw orders:")
duckdb.sql("SELECT * FROM read_csv('lake/bronze/orders/*/*.csv', all_varchar=true) LIMIT 5").show()

# TODO 2: Count the rows in the raw orders and in the raw customers.
# Hint: customers are JSON lines, so use read_json('lake/bronze/customers/*/*.json')
raise SystemExit("TODO 2: replace this line with your code")

print("Question: why does Bronze have more orders (over 200,000) than were ever placed?")
