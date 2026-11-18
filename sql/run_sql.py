"""Run the SQL files with DuckDB and print each result.

Usage (from the repository root):
    pip install duckdb
    python sql/run_sql.py
"""
from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).resolve().parent
con = duckdb.connect()

for path in sorted(SQL_DIR.glob("*.sql")):
    print(f"\n=== {path.name} ===")
    df = con.execute(path.read_text()).fetchdf()
    print(df.head(12).to_string(index=False))
    if len(df) > 12:
        print(f"... {len(df):,} rows")
