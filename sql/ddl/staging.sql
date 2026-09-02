-- =============================================================================
-- RetailSphere Enterprise Data Warehouse - Staging Layer DDL
-- Operational landing tables for raw ingested feeds
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.stg_customers (
    customer_id         VARCHAR(50),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    email               VARCHAR(150),
    phone               VARCHAR(50),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100),
    postal_code         VARCHAR(20),
    segment             VARCHAR(50),
    registration_date   VARCHAR(50),
    is_active           VARCHAR(20),
    _source_system      VARCHAR(50) DEFAULT 'CSV_FEED',
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_products (
    product_id          VARCHAR(50),
    sku                 VARCHAR(50),
    product_name        VARCHAR(150),
    category            VARCHAR(100),
    subcategory         VARCHAR(100),
    unit_cost           VARCHAR(50),
    unit_price          VARCHAR(50),
    reorder_level       VARCHAR(20),
    is_discontinued     VARCHAR(20),
    _source_system      VARCHAR(50) DEFAULT 'CSV_FEED',
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_stores (
    store_id            VARCHAR(50),
    store_name          VARCHAR(150),
    store_type          VARCHAR(50),
    region              VARCHAR(50),
    city                VARCHAR(100),
    state               VARCHAR(100),
    square_feet         VARCHAR(50),
    opening_date        VARCHAR(50),
    is_active           VARCHAR(20),
    _source_system      VARCHAR(50) DEFAULT 'CSV_FEED',
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id            VARCHAR(50),
    customer_id         VARCHAR(50),
    store_id            VARCHAR(50),
    order_date          VARCHAR(50),
    order_status        VARCHAR(50),
    channel             VARCHAR(50),
    _source_system      VARCHAR(50) DEFAULT 'CSV_FEED',
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_order_items (
    order_item_id       VARCHAR(50),
    order_id            VARCHAR(50),
    product_id          VARCHAR(50),
    quantity            VARCHAR(50),
    unit_price          VARCHAR(50),
    discount_amount     VARCHAR(50),
    line_total          VARCHAR(50),
    _source_system      VARCHAR(50) DEFAULT 'CSV_FEED',
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_payments (
    payment_id          VARCHAR(50),
    order_id            VARCHAR(50),
    payment_date        VARCHAR(50),
    payment_method      VARCHAR(50),
    payment_status      VARCHAR(50),
    payment_amount      VARCHAR(50),
    _source_system      VARCHAR(50) DEFAULT 'CSV_FEED',
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
