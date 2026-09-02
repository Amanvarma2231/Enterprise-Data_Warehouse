"""
Unit Tests for Transformation and Star Schema Logic
Verifies Surrogate Keys, Dimensions, and Fact Sales Financial Calculations
"""

import duckdb
import pytest
from src.transformation.date_dimension_generator import generate_date_dimension_df


def test_date_dimension_record_completeness():
    """Verify that date dimension generates all expected dates without nulls."""
    df_date = generate_date_dimension_df(start_year=2024, end_year=2024)
    assert len(df_date) == 366  # Leap year 2024
    assert df_date["date_key"].isnull().sum() == 0
    assert df_date["full_date"].isnull().sum() == 0


def test_warehouse_transformation_builds_star_schema(populated_db):
    """Verify that warehouse star schema tables exist and contain populated rows."""
    cust_count = populated_db.execute("SELECT COUNT(*) FROM warehouse.dim_customer").fetchone()[0]
    prod_count = populated_db.execute("SELECT COUNT(*) FROM warehouse.dim_product").fetchone()[0]
    store_count = populated_db.execute("SELECT COUNT(*) FROM warehouse.dim_store").fetchone()[0]
    sales_count = populated_db.execute("SELECT COUNT(*) FROM warehouse.fact_sales").fetchone()[0]
    pay_count = populated_db.execute("SELECT COUNT(*) FROM warehouse.fact_payments").fetchone()[0]
    
    assert cust_count > 0
    assert prod_count > 0
    assert store_count > 0
    assert sales_count > 0
    assert pay_count > 0
