"""
Initialize and Reset Database Schemas
Supports DuckDB, PostgreSQL, MySQL, and SQLite Target Environments
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import duckdb
from src.config import DUCKDB_PATH, SQL_DIR


def init_duckdb():
    print(f"[*] Initializing DuckDB Enterprise Data Warehouse at: {DUCKDB_PATH}")
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_PATH))

    # Create Schemas
    con.execute("CREATE SCHEMA IF NOT EXISTS staging;")
    con.execute("CREATE SCHEMA IF NOT EXISTS quarantine;")
    con.execute("CREATE SCHEMA IF NOT EXISTS warehouse;")

    print("[+] Schemas created: staging, quarantine, warehouse")
    con.close()
    print("[SUCCESS] DuckDB initialization complete!")


def main():
    parser = argparse.ArgumentParser(description="Initialize RetailSphere Warehouse Schemas")
    parser.add_argument("--engine", choices=["duckdb", "postgres", "mysql", "sqlite"], default="duckdb")
    args = parser.parse_args()

    if args.engine == "duckdb":
        init_duckdb()
    else:
        print(f"[*] Engine {args.engine} selected. See sql/ddl/{args.engine}_schema.sql for manual/container deployment.")


if __name__ == "__main__":
    main()
