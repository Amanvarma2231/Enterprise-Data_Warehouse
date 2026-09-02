"""
PostgreSQL Operational Database Ingestion Connector
Extracts relational tables from PostgreSQL into Data Warehouse Staging
"""

import os
from typing import Dict, Optional
import duckdb
import pandas as pd
from sqlalchemy import create_engine

from src.config import DUCKDB_PATH
from src.utils.logger import logger


def ingest_from_postgres(
    connection_url: Optional[str] = None,
    db_path: str = str(DUCKDB_PATH)
) -> Dict[str, int]:
    """Ingest operational tables from PostgreSQL into DuckDB Staging."""
    conn_str = connection_url or os.getenv(
        "POSTGRES_CONNECTION_STRING",
        "postgresql://postgres:postgres@localhost:5432/retailsphere_oltp"
    )
    
    logger.info(f"Connecting to PostgreSQL Source Database: {conn_str.split('@')[-1] if '@' in conn_str else conn_str}")
    tables = ["customers", "products", "stores", "orders", "order_items", "payments"]
    loaded_counts = {}
    
    try:
        engine = create_engine(conn_str)
        con_duck = duckdb.connect(db_path)
        con_duck.execute("CREATE SCHEMA IF NOT EXISTS staging;")
        
        for table in tables:
            try:
                query = f"SELECT * FROM {table}"
                df = pd.read_sql(query, con=engine)
                df["_ingested_at"] = pd.Timestamp.now()
                df["_source_file"] = f"postgres://{table}"
                
                con_duck.register(f"df_{table}_pg", df)
                con_duck.execute(f"CREATE OR REPLACE TABLE staging.stg_{table} AS SELECT * FROM df_{table}_pg;")
                con_duck.unregister(f"df_{table}_pg")
                
                loaded_counts[table] = len(df)
                logger.info(f"Ingested {len(df):,} rows from PostgreSQL table: {table}")
            except Exception as te:
                logger.warning(f"Could not ingest PostgreSQL table '{table}': {str(te)}")
                
        con_duck.close()
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {str(e)}")
        
    return loaded_counts
