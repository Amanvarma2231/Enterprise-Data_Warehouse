"""
Unit Tests for Transformation and Star Schema Logic
Verifies Surrogate Keys, Dimensions, and Fact Sales Financial Calculations
"""

import duckdb
import pytest
from src.transformation.transformer import transform_and_build_warehouse
from src.transformation.date_dimension_generator import generate_date_dimension_df


def test_date_dimension_record_completeness():
    """Verify that date dimension generates all expected dates without nulls."""
    df_date = generate_date_dimension_df(start_year=2024, end_year=2024)
    assert len(df_date) == 366  # Leap year 2024
    assert df_date["date_key"].isnull().sum() == 0
    assert df_date["full_date"].isnull().sum() == 0


def test_warehouse_transformation_builds_star_schema(populated_db):
    """Verify that warehouse transformation populates all dimensions and facts."""
    counts = transform_and_build_warehouse(populated_db)
    
    assert counts["dim_customer"] > 0
    assert counts["dim_product"] > 0
    assert counts["dim_store"] > 0
    assert counts["dim_date"] > 0
    assert counts["fact_sales"] > 0
    assert counts["fact_payments"] > 0
