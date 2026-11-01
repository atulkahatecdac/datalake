"""Instructor demo: the Lab 2 order cleaning, written in PySpark.

Run after Lab 1. Needs Java:  pip install pyspark  then  python demo_spark.py
The point: the steps are the same as in DuckDB. Spark spreads them over many machines.
"""
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = SparkSession.builder.master("local[*]").appName("silver").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# An exact path, because wildcards need Hadoop's winutils.exe on Windows.
raw = spark.read.csv("lake/bronze/orders/load_date=2026-07-01/orders.csv", header=True)

clean = (
    raw.dropDuplicates()
    .withColumn("amount", F.expr("try_cast(amount AS DOUBLE)"))
    .withColumn("order_date", F.coalesce(
        F.expr("try_to_date(order_date, 'yyyy-MM-dd')"),
        F.expr("try_to_date(order_date, 'dd/MM/yyyy')"),
    ))
    .filter("amount > 0 AND order_date IS NOT NULL")
)

print("Raw rows:  ", raw.count())
print("Clean rows:", clean.count())
clean.groupBy("status").agg(F.sum("amount").alias("revenue")).show()
spark.stop()
