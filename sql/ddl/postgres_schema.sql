-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Engine: PostgreSQL 15+ Database DDL
-- Layer: Staging, Star Schema Warehouse, Quarantine & Analytics Schemas
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS quarantine;
CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. STAGING SCHEMAS
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
    _ingested_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id            VARCHAR(50),
    customer_id         VARCHAR(50),
    store_id            VARCHAR(50),
    order_date          VARCHAR(50),
    order_status        VARCHAR(50),
    shipping_amount     VARCHAR(50),
    discount_total      VARCHAR(50),
    payment_status      VARCHAR(50),
    _ingested_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
);

-- 2. STAR SCHEMA WAREHOUSE
CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key        BIGINT PRIMARY KEY,
    customer_id         BIGINT NOT NULL,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    full_name           VARCHAR(200) NOT NULL,
    email               VARCHAR(255) NOT NULL,
    phone               VARCHAR(50),
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    country             VARCHAR(100) NOT NULL DEFAULT 'India',
    postal_code         VARCHAR(30),
    segment             VARCHAR(50) NOT NULL,
    registration_date   DATE NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    row_effective_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    row_expiration_date DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    _loaded_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sales_key           BIGINT PRIMARY KEY,
    order_id            BIGINT NOT NULL,
    order_item_id       BIGINT NOT NULL,
    customer_key        BIGINT NOT NULL,
    product_key         BIGINT NOT NULL,
    store_key           BIGINT NOT NULL,
    date_key            INTEGER NOT NULL,
    order_date          DATE NOT NULL,
    order_status        VARCHAR(50) NOT NULL,
    quantity            INTEGER NOT NULL,
    unit_price          NUMERIC(12, 2) NOT NULL,
    unit_cost           NUMERIC(12, 2) NOT NULL,
    gross_sales_amount  NUMERIC(14, 2) NOT NULL,
    discount_amount     NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    net_sales_amount    NUMERIC(14, 2) NOT NULL,
    cost_amount         NUMERIC(14, 2) NOT NULL,
    gross_profit_amount NUMERIC(14, 2) NOT NULL,
    profit_margin_pct   NUMERIC(6, 2) NOT NULL,
    _loaded_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pg_sales_date ON warehouse.fact_sales (date_key);
CREATE INDEX IF NOT EXISTS idx_pg_sales_cust ON warehouse.fact_sales (customer_key);
CREATE INDEX IF NOT EXISTS idx_pg_sales_prod ON warehouse.fact_sales (product_key);
CREATE INDEX IF NOT EXISTS idx_pg_sales_store ON warehouse.fact_sales (store_key);
