"""Wrap-up: the quiz, then the map from today's labs to AWS.  Run: python wrapup_quiz.py"""

QUIZ = [
    ("A Data Lake has millions of undocumented, unorganized files. What is this called?",
     ["Data Warehouse", "Data Swamp", "Data Mart"], 2),
    ("You have 5 TB of CSV files and queries are slow. What is a useful optimization?",
     ["Convert to Parquet and partition appropriately", "Store more duplicate files",
      "Remove the data catalog"], 1),
    ("Your source system adds a new column. Which concept helps your pipeline handle it?",
     ["Data masking", "Schema evolution", "Data compression"], 2),
    ("Which practice helps protect confidential customer data?",
     ["Public bucket access", "Encryption and access control", "Disabling audit logs"], 2),
]

AWS_MAP = [
    ("source_data/ files", "RDS, MySQL, APIs"),
    ("Copying files (Lab 1)", "AWS DMS, Kinesis"),
    ("lake/ folder", "Amazon S3"),
    ("DuckDB transforms (Labs 2, 4)", "AWS Glue, PySpark on EMR"),
    ("DuckDB queries (Labs 3, 4)", "Amazon Athena, Redshift"),
    ("matplotlib chart (Lab 4)", "Power BI, QuickSight"),
    ("Delta table (Lab 5)", "Delta Lake or Iceberg on S3"),
    ("Logging and retries (Lab 6)", "Airflow, CloudWatch"),
]

score = 0
for number, (question, options, answer) in enumerate(QUIZ, 1):
    print(f"\n{number}. {question}")
    for i, option in enumerate(options, 1):
        print(f"   {i}) {option}")
    if input("Your answer: ").strip() == str(answer):
        score += 1
        print("Correct")
    else:
        print(f"Answer: {options[answer - 1]}")
print(f"\nScore: {score}/{len(QUIZ)}")

print(f"\n{'What you built today':<34}In AWS")
for local, aws in AWS_MAP:
    print(f"{local:<34}{aws}")
