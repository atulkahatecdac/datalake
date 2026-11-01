"""Creates the messy e-commerce source files used in all labs.

Run once before Lab 1:  python generate_data.py
The flaws are planted on purpose. Same seed = same data for everyone.
"""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
SOURCE = Path(__file__).parent / "source_data"
(SOURCE / "incoming").mkdir(parents=True, exist_ok=True)

NUM_CUSTOMERS = 5_000
NUM_ORDERS = 200_000
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata", "Pune"]
NAMES = ["Rahul", "Amit", "Priya", "Sneha", "Vikram", "Anita", "Karan", "Neha"]
STATUSES = ["completed"] * 8 + ["cancelled", "returned"]


def random_day():
    return date(2026, 1, 1) + timedelta(days=random.randrange(181))  # Jan-Jun


# ---------- customers.json: duplicate rows, NULL age, impossible age ----------
customers = [
    {"customer_id": 101, "name": "Rahul", "age": 25, "city": "Mumbai", "phone": "9876543210"},
    {"customer_id": 101, "name": "Rahul", "age": 25, "city": "Mumbai", "phone": "9876543210"},
    {"customer_id": 102, "name": "Amit", "age": None, "city": "Delhi", "phone": "9876500000"},
    {"customer_id": 103, "name": "Priya", "age": -10, "city": "Pune", "phone": "9812345678"},
]
for cid in range(104, 101 + NUM_CUSTOMERS):
    customers.append({
        "customer_id": cid,
        "name": random.choice(NAMES),
        "age": random.randint(18, 70),
        "city": random.choice(CITIES),
        "phone": str(random.randint(9000000000, 9999999999)),
    })
with open(SOURCE / "customers.json", "w") as f:
    for c in customers:
        f.write(json.dumps(c) + "\n")


# ---------- orders.csv: duplicates, missing/negative amounts, mixed dates ----------
def make_order(order_id):
    day = random_day()
    r = random.random()
    order_date = day.strftime("%d/%m/%Y") if r < 0.05 else day.isoformat()  # 5% DD/MM/YYYY

    r = random.random()
    amount = "" if r < 0.005 else -100 if r < 0.007 else random.randint(100, 5000)

    # 0.2% of orders point to a customer who does not exist
    customer_id = 999999 if random.random() < 0.002 else random.randint(101, 100 + NUM_CUSTOMERS)
    return [order_id, customer_id, order_date, amount, random.choice(STATUSES)]


HEADER = ["order_id", "customer_id", "order_date", "amount", "status"]
with open(SOURCE / "orders.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)
    for order_id in range(1, NUM_ORDERS + 1):
        row = make_order(order_id)
        writer.writerow(row)
        if random.random() < 0.01:  # 1% exact duplicates
            writer.writerow(row)

# ---------- clicks.log: plain text website activity ----------
with open(SOURCE / "clicks.log", "w") as f:
    for _ in range(50_000):
        f.write(
            f"{random_day()}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00 "
            f"customer={random.randint(101, 100 + NUM_CUSTOMERS)} "
            f"page=/product/{random.randint(1, 50)} "
            f"action={random.choice(['view', 'view', 'view', 'cart', 'buy'])}\n"
        )

# ---------- Lab 5: the source application has added an email column ----------
with open(SOURCE / "incoming" / "customers_with_email.json", "w") as f:
    for cid, name in [(6001, "Meera"), (6002, "Arjun")]:
        f.write(json.dumps({
            "customer_id": cid, "name": name, "age": 30, "city": "Pune",
            "phone": "98XXXXXX10", "email": f"{name.lower()}@example.com",
        }) + "\n")

# ---------- Lab 6: two good daily files and one corrupt file ----------
for name, rows in {
    "orders_2026-07-01.csv": [[300001, 101, "2026-07-01", 2000, "completed"],
                              [300002, 102, "2026-07-01", 3500, "completed"]],
    "orders_2026-07-02.csv": [[300003, 103, "2026-07-02", "abc", "completed"],
                              [300004, 104, "2026-07-02", 1000, "completed"]],
    "orders_2026-07-03.csv": [[300005, 105, "2026-07-03", 1500, "completed"]],
}.items():
    with open(SOURCE / "incoming" / name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

print("Source files created:")
for path in sorted(SOURCE.rglob("*.*")):
    print(f"  {path.relative_to(SOURCE)}  ({path.stat().st_size / 1_000_000:.2f} MB)")
