"""
Automated PyTest Suite: End-to-End Pipeline Execution Tests
"""

from pathlib import Path
import duckdb
import pytest
from src.config import DUCKDB_PATH, METADATA_DIR, DOCS_DIR
from src.transformation.date_dimension_generator import generate_date_dimension_df


def test_date_dimension_generation():
    """Verify that date dimension generator produces all calendar and fiscal attributes."""
    df_date = generate_date_dimension_df(start_year=2024, end_year=2025)
    assert len(df_date) == 731 # 366 (leap 2024) + 365 (2025)
    assert "date_key" in df_date.columns
    assert "fiscal_quarter" in df_date.columns
    assert "is_weekend" in df_date.columns
    assert df_date["date_key"].is_monotonic_increasing


def test_metadata_artifacts_exist():
    """Verify that metadata catalog and governance documents are generated."""
    assert (METADATA_DIR / "metadata.csv").exists()
    assert (DOCS_DIR / "data_dictionary.md").exists()
    assert (DOCS_DIR / "data_dictionary.xlsx").exists()
    assert (DOCS_DIR / "data-lineage.md").exists()
    assert (DOCS_DIR / "governance.md").exists()


def test_warehouse_tables_populated(db_conn):
    """Verify that all core star schema and mart tables have positive row counts."""
    expected_tables = [
        "dim_customer",
        "dim_product",
        "dim_store",
        "dim_date",
        "fact_sales",
        "fact_payments",
        "mart_monthly_store_performance",
        "mart_customer_rfm",
    ]
    
    for tbl in expected_tables:
        count = db_conn.execute(f"SELECT COUNT(*) FROM warehouse.{tbl}").fetchone()[0]
        assert count > 0, f"Table warehouse.{tbl} is unexpectedly empty!"
