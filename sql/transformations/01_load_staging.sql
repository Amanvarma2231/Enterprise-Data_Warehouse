-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Transformation: Ingestion / Staging Table Population
-- =============================================================================

-- Staging truncate and load patterns (Idempotent execution)
TRUNCATE TABLE staging.stg_customers;
TRUNCATE TABLE staging.stg_products;
TRUNCATE TABLE staging.stg_stores;
TRUNCATE TABLE staging.stg_orders;
TRUNCATE TABLE staging.stg_order_items;
TRUNCATE TABLE staging.stg_payments;

-- In DuckDB / PostgreSQL / BigQuery, files are loaded via high-speed loaders or copy commands:
-- DuckDB:
-- INSERT INTO staging.stg_customers SELECT *, CURRENT_TIMESTAMP, 'customers.csv' FROM read_csv_auto('data/raw/customers.csv');
