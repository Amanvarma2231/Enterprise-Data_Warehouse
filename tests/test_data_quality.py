"""
Automated PyTest Suite: Data Quality Engine & Quarantine Isolation
"""

import duckdb
import pytest
from src.config import DUCKDB_PATH, QUARANTINE_DATA_DIR
from src.validation.business_rules import (
    check_email_syntax_validity,
    check_future_order_dates,
    check_line_total_calculation,
    check_positive_quantities,
)
from src.validation.duplicate_checks import check_primary_key_uniqueness
from src.validation.integrity_checks import check_foreign_key_integrity
from src.validation.null_checks import check_null_counts


def test_warehouse_customer_pk_unique_and_not_null(db_conn):
    """Ensure dim_customer has 0 null PKs and 0 duplicates."""
    null_res = check_null_counts(db_conn, "warehouse.dim_customer", ["customer_key", "customer_id"])
    for r in null_res:
        assert r["failed_rows"] == 0, f"Found NULLs in {r['table_name']}.{r['column_name']}"

    dup_res = check_primary_key_uniqueness(db_conn, "warehouse.dim_customer", ["customer_key"])
    assert dup_res["failed_rows"] == 0, f"Duplicate customer keys detected: {dup_res['failed_rows']}"


def test_warehouse_product_pk_unique_and_not_null(db_conn):
    """Ensure dim_product has 0 null PKs and 0 duplicates."""
    null_res = check_null_counts(db_conn, "warehouse.dim_product", ["product_key", "product_id"])
    for r in null_res:
        assert r["failed_rows"] == 0

    dup_res = check_primary_key_uniqueness(db_conn, "warehouse.dim_product", ["product_key"])
    assert dup_res["failed_rows"] == 0


def test_fact_sales_referential_integrity(db_conn):
    """Ensure all foreign keys in fact_sales resolve to valid dimension keys."""
    fk_cust = check_foreign_key_integrity(db_conn, "warehouse.fact_sales", "customer_key", "warehouse.dim_customer", "customer_key")
    assert fk_cust["failed_rows"] == 0, "Orphaned customer_key in fact_sales"

    fk_prod = check_foreign_key_integrity(db_conn, "warehouse.fact_sales", "product_key", "warehouse.dim_product", "product_key")
    assert fk_prod["failed_rows"] == 0, "Orphaned product_key in fact_sales"

    fk_store = check_foreign_key_integrity(db_conn, "warehouse.fact_sales", "store_key", "warehouse.dim_store", "store_key")
    assert fk_store["failed_rows"] == 0, "Orphaned store_key in fact_sales"

    fk_date = check_foreign_key_integrity(db_conn, "warehouse.fact_sales", "date_key", "warehouse.dim_date", "date_key")
    assert fk_date["failed_rows"] == 0, "Orphaned date_key in fact_sales"


def test_fact_sales_positive_metrics(db_conn):
    """Ensure no negative sales amounts or non-positive quantities exist in warehouse facts."""
    bad_rows = db_conn.execute("""
        SELECT COUNT(*) 
        FROM warehouse.fact_sales 
        WHERE quantity <= 0 OR unit_price <= 0 OR net_sales_amount <= 0
    """).fetchone()[0]
    assert bad_rows == 0, f"Found {bad_rows} non-positive sales metrics in fact_sales"


def test_quarantine_isolation_efficacy(db_conn):
    """Ensure quarantined anomalous records are properly isolated and tracked."""
    q_orders_count = db_conn.execute("SELECT COUNT(*) FROM quarantine.quarantine_orders").fetchone()[0]
    q_items_count = db_conn.execute("SELECT COUNT(*) FROM quarantine.quarantine_order_items").fetchone()[0]
    q_cust_count = db_conn.execute("SELECT COUNT(*) FROM quarantine.quarantine_customers").fetchone()[0]

    assert q_orders_count > 0, "Expected quarantine_orders to capture injected anomalies"
    assert q_items_count > 0, "Expected quarantine_order_items to capture injected anomalies"
    assert q_cust_count > 0, "Expected quarantine_customers to capture injected anomalies"
