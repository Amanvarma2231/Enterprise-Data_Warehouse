import duckdb
import pytest
from src.config import DUCKDB_PATH


def test_fact_sales_financial_math(db_conn):
    """Verify that gross_sales, discount, net_sales, cost and profit reconcile mathematically."""
    mismatches = db_conn.execute("""
        SELECT COUNT(*)
        FROM warehouse.fact_sales
        WHERE ABS(gross_sales_amount - (quantity * unit_price)) > 0.05
           OR ABS(net_sales_amount - (gross_sales_amount - discount_amount)) > 0.05
           OR ABS(gross_profit_amount - (net_sales_amount - cost_amount)) > 0.05
    """).fetchone()[0]
    
    assert mismatches == 0, f"Detected {mismatches} financial calculation discrepancies in fact_sales"


def test_customer_rfm_scores_bounded(db_conn):
    """Verify that RFM scores are strictly within the 1-5 discrete range."""
    invalid_scores = db_conn.execute("""
        SELECT COUNT(*)
        FROM warehouse.mart_customer_rfm
        WHERE r_score NOT BETWEEN 1 AND 5
           OR f_score NOT BETWEEN 1 AND 5
           OR m_score NOT BETWEEN 1 AND 5
    """).fetchone()[0]
    
    assert invalid_scores == 0, f"Found {invalid_scores} RFM scores outside the [1, 5] bounds"


def test_monthly_store_mart_aggregation_reconciliation(db_conn):
    """Verify that monthly store mart revenue matches sum of fact_sales."""
    fact_rev = db_conn.execute("SELECT ROUND(SUM(net_sales_amount), 2) FROM warehouse.fact_sales").fetchone()[0]
    mart_rev = db_conn.execute("SELECT ROUND(SUM(net_revenue), 2) FROM warehouse.mart_monthly_store_performance").fetchone()[0]
    
    assert abs(fact_rev - mart_rev) < 1.0, f"Reconciliation error: fact={fact_rev} vs mart={mart_rev}"
