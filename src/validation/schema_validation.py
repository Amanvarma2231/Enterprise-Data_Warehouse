"""
Schema & Data Contract Validation Engine
Verifies Staging and Warehouse Schemas Against Data Contracts
"""

import duckdb
from src.utils.logger import logger


EXPECTED_STAGING_SCHEMAS = {
    "staging.stg_customers": ["customer_id", "first_name", "last_name", "email", "phone", "city", "state"],
    "staging.stg_products": ["product_id", "sku", "product_name", "category", "unit_cost", "unit_price"],
    "staging.stg_stores": ["store_id", "store_name", "store_type", "region", "city"],
    "staging.stg_orders": ["order_id", "customer_id", "store_id", "order_date", "order_status"],
    "staging.stg_order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount"],
    "staging.stg_payments": ["payment_id", "order_id", "payment_method", "payment_status", "payment_amount"]
}


def validate_staging_schemas(con: duckdb.DuckDBPyConnection) -> dict[str, bool]:
    """Validate that all required staging tables and columns exist."""
    results = {}
    for table, expected_cols in EXPECTED_STAGING_SCHEMAS.items():
        try:
            df = con.execute(f"SELECT * FROM {table} LIMIT 0").df()
            cols = list(df.columns)
            missing = [c for c in expected_cols if c not in cols]
            if missing:
                logger.error(f"Schema validation FAILED for {table}. Missing columns: {missing}")
                results[table] = False
            else:
                logger.info(f"Schema validation PASSED for {table}.")
                results[table] = True
        except Exception as e:
            logger.error(f"Schema check error on {table}: {e}")
            results[table] = False

    return results
