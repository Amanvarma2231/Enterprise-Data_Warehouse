"""
SQLite Operational Database Ingestion Connector
Extracts tables from SQLite databases into Data Warehouse Staging
"""

import sqlite3
from pathlib import Path
from typing import Dict, Optional
import duckdb
import pandas as pd

from src.config import DUCKDB_PATH
from src.utils.logger import logger


def ingest_from_sqlite(
    sqlite_db_path: Optional[str] = None,
    db_path: str = str(DUCKDB_PATH)
) -> Dict[str, int]:
    """Ingest operational tables from SQLite into DuckDB Staging."""
    sqlite_file = sqlite_db_path or "data/oltp/retailsphere_oltp.db"
    logger.info(f"Connecting to SQLite Source Database: {sqlite_file}")
    
    tables = ["customers", "products", "stores", "orders", "order_items", "payments"]
    loaded_counts = {}
    
    if not Path(sqlite_file).exists():
        logger.warning(f"SQLite file not found at {sqlite_file}")
        return loaded_counts
        
    try:
        con_sqlite = sqlite3.connect(sqlite_file)
        con_duck = duckdb.connect(db_path)
        con_duck.execute("CREATE SCHEMA IF NOT EXISTS staging;")
        
        for table in tables:
            try:
                df = pd.read_sql(f"SELECT * FROM {table}", con=con_sqlite)
                df["_ingested_at"] = pd.Timestamp.now()
                df["_source_file"] = f"sqlite://{sqlite_file}/{table}"
                
                con_duck.register(f"df_{table}_sqlite", df)
                con_duck.execute(f"CREATE OR REPLACE TABLE staging.stg_{table} AS SELECT * FROM df_{table}_sqlite;")
                con_duck.unregister(f"df_{table}_sqlite")
                
                loaded_counts[table] = len(df)
                logger.info(f"Ingested {len(df):,} rows from SQLite table: {table}")
            except Exception as te:
                logger.warning(f"Could not ingest SQLite table '{table}': {str(te)}")
                
        con_sqlite.close()
        con_duck.close()
    except Exception as e:
        logger.error(f"SQLite connection error: {str(e)}")
        
    return loaded_counts
