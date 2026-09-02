"""
Enterprise Data Warehouse - Configuration Module
RetailSphere Data Platform
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
QUARANTINE_DATA_DIR = DATA_DIR / "quarantine"
WAREHOUSE_DATA_DIR = DATA_DIR / "warehouse"
METADATA_DIR = BASE_DIR / "metadata"
DOCS_DIR = BASE_DIR / "docs"
SQL_DIR = BASE_DIR / "sql"

# Ensure required directories exist
for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    SAMPLE_DATA_DIR,
    QUARANTINE_DATA_DIR,
    WAREHOUSE_DATA_DIR,
    METADATA_DIR,
    DOCS_DIR,
    SQL_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Configurations
DUCKDB_PATH = WAREHOUSE_DATA_DIR / "retailsphere_dw.duckdb"
DUCKDB_URI = f"duckdb:///{DUCKDB_PATH.as_posix()}"

# Optional PostgreSQL configuration via environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "retailsphere_dw")
POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Data Quality Thresholds
DQ_THRESHOLDS = {
    "max_null_rate_critical_keys": 0.0,
    "max_null_rate_descriptive": 0.05,
    "max_duplicate_rate_pks": 0.0,
    "min_quantity": 1,
    "max_discount_percentage": 0.50,
    "min_price": 0.01,
}

# Date Dimension Generation Parameters
DATE_DIM_START_YEAR = 2022
DATE_DIM_END_YEAR = 2030

# File names
RAW_FILES = {
    "customers": "customers.csv",
    "products": "products.csv",
    "stores": "stores.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
    "payments": "payments.csv",
}
