"""Lab 2 - Silver: find the bad data, clean it, keep the rejects, mask private data."""
import os
from pathlib import Path

import duckdb

os.chdir(Path(__file__).parents[1])
Path("lake/silver").mkdir(parents=True, exist_ok=True)
con = duckdb.connect()

# Read everything as text first, so that bad values cannot crash the load.
con.sql("""
    CREATE TABLE raw_orders AS
    SELECT * FROM read_csv('lake/bronze/orders/*/*.csv', all_varchar=true)
""")
con.sql("CREATE TABLE raw_customers AS SELECT * FROM read_json('lake/bronze/customers/*/*.json')")

# ---------- Part A: profile the data before changing it ----------
print("Rows that are exact duplicates, and rows with a missing amount:")
con.sql("""
    SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT * FROM raw_orders)) AS duplicate_rows,
           count(*) FILTER (WHERE amount IS NULL) AS missing_amount
    FROM raw_orders
""").show()

# Count orders whose amount is negative, and orders with a date containing '/'.
con.sql("""
    SELECT count(*) FILTER (WHERE TRY_CAST(amount AS DOUBLE) < 0) AS negative_amount,
           count(*) FILTER (WHERE order_date LIKE '%/%') AS slash_dates
    FROM raw_orders
""").show()

# ---------- Part B: clean the customers ----------
# Create table customers from raw_customers:
#   - keep only distinct rows
#   - age outside 0-120 becomes NULL
#   - phone is masked so that only the last 2 digits show, e.g. XXXXXXXX10
con.sql("""
    CREATE TABLE customers AS
    SELECT DISTINCT customer_id, name,
           CASE WHEN age BETWEEN 0 AND 120 THEN age END AS age,
           city,
           'XXXXXXXX' || right(phone, 2) AS phone
    FROM raw_customers
""")

# ---------- Part C: clean the orders ----------
# Fix the types once. Values that cannot be converted become NULL.
con.sql("""
    CREATE TABLE typed_orders AS
    SELECT DISTINCT
        TRY_CAST(order_id AS INTEGER) AS order_id,
        TRY_CAST(customer_id AS INTEGER) AS customer_id,
        COALESCE(TRY_STRPTIME(order_date, '%Y-%m-%d'),
                 TRY_STRPTIME(order_date, '%d/%m/%Y'))::DATE AS order_date,
        TRY_CAST(amount AS DOUBLE) AS amount,
        status
    FROM raw_orders
""")

# Split typed_orders into two tables, so that no row is silently lost:
#   orders         - amount > 0 AND order_date IS NOT NULL AND the customer exists
#   rejected_orders - all the other rows
# A NULL amount makes "amount > 0" NULL, so COALESCE turns it into false.
is_valid = """
    COALESCE(amount > 0, false)
    AND order_date IS NOT NULL
    AND customer_id IN (SELECT customer_id FROM customers)
"""
con.sql(f"CREATE TABLE orders AS SELECT * FROM typed_orders WHERE {is_valid}")
con.sql(f"CREATE TABLE rejected_orders AS SELECT * FROM typed_orders WHERE NOT ({is_valid})")

# ---------- Part D: parse the text log with regular expressions ----------
con.sql(r"""
    CREATE TABLE clicks AS
    SELECT regexp_extract(line, '^(\S+)', 1)::TIMESTAMP AS click_time,
           regexp_extract(line, 'customer=(\d+)', 1)::INTEGER AS customer_id,
           regexp_extract(line, 'page=(\S+)', 1) AS page,
           regexp_extract(line, 'action=(\S+)', 1) AS action
    FROM read_csv('lake/bronze/clicks/*/*.log', columns={'line': 'VARCHAR'}, header=false, delim='\t')
""")

# ---------- Save everything as Parquet ----------
for table in ["customers", "orders", "rejected_orders", "clicks"]:
    con.sql(f"COPY {table} TO 'lake/silver/{table}.parquet' (FORMAT parquet)")

# ---------- Check: every distinct row must be either kept or rejected ----------
print("Reconciliation:")
con.sql("""
    SELECT (SELECT count(*) FROM raw_orders) AS bronze,
           (SELECT count(*) FROM typed_orders) AS after_dedup,
           (SELECT count(*) FROM orders) AS silver,
           (SELECT count(*) FROM rejected_orders) AS rejected
""").show()
print("Customers 101, 102, 103 after cleaning:")
con.sql("SELECT * FROM customers WHERE customer_id <= 103 ORDER BY customer_id").show()
