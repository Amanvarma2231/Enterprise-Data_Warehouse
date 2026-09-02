"""
RetailSphere Enterprise Ingestion Script (Python + SQLAlchemy + Pandas)
Generates/Reads Raw Operational Feeds and Ingests into PostgreSQL/DuckDB Staging Tables
Staff Data Architect & Lead Data Engineer Implementation
Author: Aman Varma (https://github.com/Amanvarma2231)
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

# Ensure project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import RAW_DATA_DIR, SAMPLE_DATA_DIR, DUCKDB_PATH
from src.data_generator import generate_all_data


def get_db_engine():
    """Returns a SQLAlchemy engine configured from environment or fallback to SQLite/DuckDB."""
    pg_conn_str = os.getenv("POSTGRES_CONNECTION_STRING")
    if pg_conn_str:
        return create_engine(pg_conn_str)
    # Default to local SQLite/DuckDB compatible engine
    sqlite_path = root_dir / "data" / "warehouse" / "retailsphere_staging.db"
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{sqlite_path}")


def ingest_raw_data_to_staging(source_dir: Path = RAW_DATA_DIR, engine=None):
    """
    Reads raw CSV feeds (Customers, Products, Stores, Orders, Order Items, Payments)
    and loads them into normalized staging tables using pandas to_sql and SQLAlchemy.
    """
    if engine is None:
        engine = get_db_engine()

    print(f"[*] Starting raw data ingestion from {source_dir}...")

    # Verify or generate source CSVs
    if not (source_dir / "orders.csv").exists():
        print("[!] Raw CSV files not found. Generating fresh synthetic dataset...")
        generate_all_data(n_customers=2000, n_products=300, n_stores=20, n_orders=10000, target_dir=source_dir)

    staging_map = {
        "customers.csv": "stg_customers",
        "products.csv": "stg_products",
        "stores.csv": "stg_stores",
        "orders.csv": "stg_orders",
        "order_items.csv": "stg_order_items",
        "payments.csv": "stg_payments",
    }

    ingested_counts = {}
    with engine.begin() as conn:
        for csv_file, table_name in staging_map.items():
            file_path = source_dir / csv_file
            if file_path.exists():
                df = pd.read_csv(file_path, dtype=str)
                df["_source_system"] = "CSV_OLTP_STREAM"
                df["_ingested_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                # Ingest to staging table
                df.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists="replace",
                    index=False,
                    chunksize=5000,
                )
                ingested_counts[table_name] = len(df)
                print(f"  [+] Successfully loaded {len(df):,} rows -> {table_name}")

    print("[SUCCESS] All raw operational feeds successfully ingested into staging layer!")
    return ingested_counts


if __name__ == "__main__":
    ingest_raw_data_to_staging()
