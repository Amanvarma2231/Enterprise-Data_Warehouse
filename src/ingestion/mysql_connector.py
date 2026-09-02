"""
MySQL / MariaDB Operational Database Ingestion Connector
Extracts transactional tables from MySQL directly into Data Warehouse Staging
"""

import os
from typing import Dict, Optional
import duckdb
import pandas as pd
from sqlalchemy import create_engine

from src.config import DUCKDB_PATH
from src.utils.logger import logger


def ingest_from_mysql(
    connection_url: Optional[str] = None,
    db_path: str = str(DUCKDB_PATH)
) -> Dict[str, int]:
    """
    Ingest operational transactional tables from MySQL into DuckDB Staging.
    Default connection string uses env var MYSQL_CONNECTION_STRING or fallback localhost.
    """
    conn_str = connection_url or os.getenv(
        "MYSQL_CONNECTION_STRING",
        "mysql+pymysql://root:password@localhost:3306/retailsphere_oltp"
    )
    
    logger.info(f"Connecting to MySQL Source Database: {conn_str.split('@')[-1] if '@' in conn_str else conn_str}")
    
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
                df["_source_file"] = f"mysql://{table}"
                
                con_duck.register(f"df_{table}_mysql", df)
                con_duck.execute(f"CREATE OR REPLACE TABLE staging.stg_{table} AS SELECT * FROM df_{table}_mysql;")
                con_duck.unregister(f"df_{table}_mysql")
                
                loaded_counts[table] = len(df)
                logger.info(f"Ingested {len(df):,} rows from MySQL table: {table}")
            except Exception as te:
                logger.warning(f"Could not ingest MySQL table '{table}': {str(te)}")
                
        con_duck.close()
    except Exception as e:
        logger.error(f"MySQL connection error: {str(e)}")
        
    return loaded_counts
