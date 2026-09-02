-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Layer: Staging / Ingestion Layer (Raw Landing)
-- Target Engines: PostgreSQL / DuckDB / SQLite / BigQuery
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS staging;

-- 1. Raw Customers Landing Table
CREATE TABLE IF NOT EXISTS staging.stg_customers (
    customer_id         VARCHAR(50),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    email               VARCHAR(255),
    phone               VARCHAR(50),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100),
    postal_code         VARCHAR(30),
    segment             VARCHAR(50),
    registration_date   VARCHAR(50),
    is_active           VARCHAR(20),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);

-- 2. Raw Products Landing Table
CREATE TABLE IF NOT EXISTS staging.stg_products (
    product_id          VARCHAR(50),
    sku                 VARCHAR(100),
    product_name        VARCHAR(255),
    category            VARCHAR(100),
    subcategory         VARCHAR(100),
    unit_cost           VARCHAR(50),
    unit_price          VARCHAR(50),
    reorder_level       VARCHAR(50),
    is_discontinued     VARCHAR(20),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);

-- 3. Raw Stores Landing Table
CREATE TABLE IF NOT EXISTS staging.stg_stores (
    store_id            VARCHAR(50),
    store_name          VARCHAR(255),
    store_type          VARCHAR(100),
    region              VARCHAR(100),
    city                VARCHAR(100),
    state               VARCHAR(100),
    square_feet         VARCHAR(50),
    opened_date         VARCHAR(50),
    manager_name        VARCHAR(150),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);

-- 4. Raw Orders Landing Table
CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id            VARCHAR(50),
    customer_id         VARCHAR(50),
    store_id            VARCHAR(50),
    order_date          VARCHAR(50),
    order_status        VARCHAR(50),
    shipping_amount     VARCHAR(50),
    discount_total      VARCHAR(50),
    payment_status      VARCHAR(50),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);

-- 5. Raw Order Items Landing Table
CREATE TABLE IF NOT EXISTS staging.stg_order_items (
    order_item_id       VARCHAR(50),
    order_id            VARCHAR(50),
    product_id          VARCHAR(50),
    quantity            VARCHAR(50),
    unit_price          VARCHAR(50),
    discount            VARCHAR(50),
    line_total          VARCHAR(50),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);

-- 6. Raw Payments Landing Table
CREATE TABLE IF NOT EXISTS staging.stg_payments (
    payment_id          VARCHAR(50),
    order_id            VARCHAR(50),
    payment_method      VARCHAR(50),
    payment_status      VARCHAR(50),
    payment_amount      VARCHAR(50),
    payment_date        VARCHAR(50),
    transaction_ref     VARCHAR(100),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);
