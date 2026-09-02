"""
Unit Tests for Data Ingestion Module
Verifies CSV Loader and Staging Schema Population
"""

import duckdb
import pytest
from src.config import SAMPLE_DATA_DIR
from src.ingestion.load_csv import load_raw_csvs_to_staging


def test_csv_ingestion_populates_staging_tables(temp_db):
    """Test that CSV ingestion successfully loads rows into all staging tables."""
    counts = load_raw_csvs_to_staging(source_dir=SAMPLE_DATA_DIR, db_path=temp_db)
    
    assert counts["customers"] > 0
    assert counts["products"] > 0
    assert counts["stores"] > 0
    assert counts["orders"] > 0
    assert counts["order_items"] > 0
    assert counts["payments"] > 0

    con = duckdb.connect(str(temp_db))
    stg_cust_count = con.execute("SELECT COUNT(*) FROM staging.stg_customers").fetchone()[0]
    assert stg_cust_count == counts["customers"]
    con.close()
