# Build a mini data lake: 4-hour hands-on session

You will take messy e-commerce files through Bronze, Silver and Gold, then make the pipeline fast and reliable.

## Setup (do this before the session)

You need Python 3.11 or newer and about 2 GB of free disk space. Lab 3 uses this space for a short time.

Run these from this folder. They create a virtual environment called `.venv`, so the packages stay separate from the rest of your computer.

Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_data.py
```

Mac or Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python generate_data.py
```

If PowerShell refuses to run the activate script, run `Set-ExecutionPolicy -Scope Process RemoteSigned` and try again.

Create your own `.venv` on each computer. A copied one won't work, so don't include it if you share this folder.

## How the labs work

Activate the environment each time you open a new terminal: `.venv\Scripts\activate` on Windows, or `source .venv/bin/activate` on Mac or Linux. Your prompt then starts with `(.venv)`.

Run the labs from this folder, for example `python labs/lab1_bronze.py`.

Each file in `labs/` stops at the first gap with a message like `TODO 1: replace this line with your code`. Read the TODO and hint above that line, replace the line with your code, and run the file again.

**Stuck or behind?** Run the solution, for example `python solutions/lab2_silver.py`. It creates everything the next lab needs, so you can carry on from there. To start again, delete the `lake` folder.

## Schedule

| Time | Activity | File |
|---|---|---|
| 0:00-0:15 | Lake, warehouse and lakehouse | |
| 0:15-0:50 | Lab 1: Bronze, load the raw files | `lab1_bronze.py` |
| 0:50-1:35 | Lab 2: Silver, clean, reject and mask | `lab2_silver.py` |
| 1:35-1:45 | Break | |
| 1:45-2:15 | Lab 3: CSV vs Parquet vs partitions | `lab3_performance.py` |
| 2:15-2:45 | Lab 4: Gold, business tables and a chart | `lab4_gold.py` |
| 2:45-2:55 | Break | |
| 2:55-3:25 | Lab 5: Lakehouse, schema evolution and time travel | `lab5_lakehouse.py` |
| 3:25-3:45 | Lab 6: Break the pipeline, then fix it | `lab6_failures.py` |
| 3:45-4:00 | Quiz and AWS mapping | `wrapup_quiz.py` |

Labs 1 to 5 build on each other, so run them in order. Lab 6 only needs `generate_data.py`.

## For the instructor

- **Spark demo:** `demo_spark.py` repeats the Lab 2 order cleaning in PySpark. It needs Java and `pip install pyspark` (with `.venv` active), and only you need to run it.
- **Changing a lab:** edit the file in `solutions/`, then run `python make_labs.py`. This overwrites `labs/`, so don't edit those files directly.
