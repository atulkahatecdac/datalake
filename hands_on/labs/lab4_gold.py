"""Lab 4 - Gold: turn clean data into tables that answer business questions."""
import os
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt

os.chdir(Path(__file__).parents[1])
Path("lake/gold").mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
con.sql("CREATE VIEW orders AS SELECT * FROM 'lake/silver/orders.parquet'")
con.sql("CREATE VIEW customers AS SELECT * FROM 'lake/silver/customers.parquet'")

# Business rule: only completed orders count as revenue.
con.sql("""
    CREATE TABLE daily_sales AS
    SELECT order_date, count(*) AS num_orders, sum(amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY order_date
    ORDER BY order_date
""")

# TODO 1: Create table customer_summary, with one row per customer that has a completed order:
#   customer_id, name, city, num_orders, total_spent
# Hint: JOIN orders and customers USING (customer_id), then GROUP BY customer_id, name, city
raise SystemExit("TODO 1: replace this line with your code")

for table in ["daily_sales", "customer_summary"]:
    con.sql(f"COPY {table} TO 'lake/gold/{table}.parquet' (FORMAT parquet)")

# Check: Gold must agree with Silver.
print("Revenue check (the two numbers must match):")
con.sql("""
    SELECT (SELECT sum(revenue) FROM daily_sales) AS gold_revenue,
           (SELECT sum(amount) FROM orders WHERE status = 'completed') AS silver_revenue
""").show()

# TODO 2: Answer from the Gold tables: which are the 5 cities with the highest revenue?
# Hint: SELECT city, sum(total_spent) AS revenue FROM customer_summary GROUP BY ...
raise SystemExit("TODO 2: replace this line with your code")

# TODO 3: Answer: who are the top 5 customers by total_spent?
raise SystemExit("TODO 3: replace this line with your code")

# Monthly revenue chart for the business team.
monthly = con.sql("""
    SELECT strftime(order_date, '%b') AS month, sum(revenue) / 1000000 AS revenue_millions
    FROM daily_sales GROUP BY month, month(order_date) ORDER BY month(order_date)
""").df()
plt.bar(monthly["month"], monthly["revenue_millions"], color="#2563eb")
plt.title("Monthly revenue, completed orders")
plt.ylabel("Revenue (₹ millions)")
plt.savefig("lake/gold/monthly_revenue.png", dpi=120)
print("Chart saved: lake/gold/monthly_revenue.png")
