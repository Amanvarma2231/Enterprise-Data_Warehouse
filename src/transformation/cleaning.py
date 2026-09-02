"""
Data Cleansing & Standardization Module
Handles Trimming, Lowercasing, Type Casting, and Default Imputations
"""

import duckdb
from src.utils.logger import logger


def clean_staging_data(con: duckdb.DuckDBPyConnection):
    """Execute cleansing routines on staging tables."""
    logger.info("Standardizing and cleansing staging data...")
    # Clean string fields and standardize values
    con.execute("""
        UPDATE staging.stg_customers
        SET first_name = TRIM(first_name),
            last_name = TRIM(last_name),
            email = LOWER(TRIM(email))
        WHERE email IS NOT NULL;
    """)
    logger.info("Staging data cleansing completed.")
