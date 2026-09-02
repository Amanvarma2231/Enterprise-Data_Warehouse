"""
Data Quality Check: Business Logic, Date, Range & Syntax Validations
"""

import duckdb


def check_positive_quantities(con: duckdb.DuckDBPyConnection) -> dict:
    """Validate that order item quantity is strictly positive (> 0)."""
    total = con.execute("SELECT COUNT(*) FROM staging.stg_order_items").fetchone()[0]
    bad = con.execute("""
        SELECT COUNT(*) 
        FROM staging.stg_order_items 
        WHERE TRY_CAST(quantity AS INTEGER) <= 0 OR TRY_CAST(quantity AS INTEGER) IS NULL
    """).fetchone()[0]
    
    return {
        "check_category": "Range Validation",
        "table_name": "staging.stg_order_items",
        "column_name": "quantity",
        "total_rows": total,
        "failed_rows": bad,
        "failure_rate_pct": round((bad / max(1, total)) * 100.0, 3),
        "status": "PASSED" if bad == 0 else "FAILED",
        "severity": "HIGH",
        "rule_description": "Quantity must be strictly positive (> 0)",
    }


def check_future_order_dates(con: duckdb.DuckDBPyConnection) -> dict:
    """Validate that order date is not in the future."""
    total = con.execute("SELECT COUNT(*) FROM staging.stg_orders").fetchone()[0]
    bad = con.execute("""
        SELECT COUNT(*) 
        FROM staging.stg_orders 
        WHERE TRY_CAST(order_date AS DATE) > CURRENT_DATE
    """).fetchone()[0]
    
    return {
        "check_category": "Date Validation",
        "table_name": "staging.stg_orders",
        "column_name": "order_date",
        "total_rows": total,
        "failed_rows": bad,
        "failure_rate_pct": round((bad / max(1, total)) * 100.0, 3),
        "status": "PASSED" if bad == 0 else "FAILED",
        "severity": "HIGH",
        "rule_description": "Order date must not be greater than current date (no future orders)",
    }


def check_email_syntax_validity(con: duckdb.DuckDBPyConnection) -> dict:
    """Validate email formatting in staging customers."""
    total = con.execute("SELECT COUNT(*) FROM staging.stg_customers").fetchone()[0]
    bad = con.execute("""
        SELECT COUNT(*) 
        FROM staging.stg_customers 
        WHERE email NOT LIKE '%@%.%' OR email IS NULL
    """).fetchone()[0]
    
    return {
        "check_category": "Format / Syntax Validation",
        "table_name": "staging.stg_customers",
        "column_name": "email",
        "total_rows": total,
        "failed_rows": bad,
        "failure_rate_pct": round((bad / max(1, total)) * 100.0, 3),
        "status": "PASSED" if bad == 0 else "FAILED",
        "severity": "MEDIUM",
        "rule_description": "Customer email must adhere to valid format pattern (contain @ and domain)",
    }


def check_line_total_calculation(con: duckdb.DuckDBPyConnection) -> dict:
    """Validate that line_total equals (quantity * unit_price) - discount within tolerance."""
    total = con.execute("SELECT COUNT(*) FROM staging.stg_order_items").fetchone()[0]
    bad = con.execute("""
        SELECT COUNT(*) 
        FROM staging.stg_order_items 
        WHERE TRY_CAST(quantity AS INTEGER) > 0 
          AND ABS(
            TRY_CAST(line_total AS DECIMAL(12,2)) - 
            ((TRY_CAST(quantity AS DECIMAL(12,2)) * TRY_CAST(unit_price AS DECIMAL(12,2))) - TRY_CAST(discount AS DECIMAL(12,2)))
          ) > 0.05
    """).fetchone()[0]
    
    return {
        "check_category": "Business Logic",
        "table_name": "staging.stg_order_items",
        "column_name": "line_total",
        "total_rows": total,
        "failed_rows": bad,
        "failure_rate_pct": round((bad / max(1, total)) * 100.0, 3),
        "status": "PASSED" if bad == 0 else "FAILED",
        "severity": "HIGH",
        "rule_description": "Line total must reconcile with (quantity * unit_price) - discount",
    }
