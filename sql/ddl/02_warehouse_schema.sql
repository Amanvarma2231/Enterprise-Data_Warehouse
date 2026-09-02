-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Layer: Dimensional Data Warehouse (Star Schema & Marts)
-- Target Engines: PostgreSQL / DuckDB / SQLite / BigQuery
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

-- =============================================================================
-- 1. DIMENSION TABLES
-- =============================================================================

-- Date Dimension (Conformed Dimension)
CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key            INTEGER PRIMARY KEY,            -- e.g., 20260902
    full_date           DATE NOT NULL UNIQUE,
    day_of_month        INTEGER NOT NULL,
    month_number        INTEGER NOT NULL,
    month_name          VARCHAR(20) NOT NULL,
    month_short_name    VARCHAR(3) NOT NULL,
    quarter_number      INTEGER NOT NULL,
    quarter_name        VARCHAR(10) NOT NULL,
    year_number         INTEGER NOT NULL,
    year_month          VARCHAR(7) NOT NULL,            -- e.g., '2026-09'
    day_of_week         INTEGER NOT NULL,               -- 1 = Monday, 7 = Sunday
    day_name            VARCHAR(20) NOT NULL,
    week_of_year        INTEGER NOT NULL,
    is_weekend          BOOLEAN NOT NULL,
    is_holiday          BOOLEAN DEFAULT FALSE,
    fiscal_year         INTEGER NOT NULL,
    fiscal_quarter      VARCHAR(10) NOT NULL
);

-- Customer Dimension (SCD Type 1 with Type 2 audit columns)
CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key        BIGINT PRIMARY KEY,             -- Surrogate Key
    customer_id         BIGINT NOT NULL,                -- Natural / Business Key
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    full_name           VARCHAR(200) NOT NULL,
    email               VARCHAR(255) NOT NULL,
    phone               VARCHAR(50),
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    country             VARCHAR(100) NOT NULL DEFAULT 'India',
    postal_code         VARCHAR(30),
    segment             VARCHAR(50) NOT NULL,           -- Regular, Premium, VIP, Corporate
    registration_date   DATE NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    row_effective_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    row_expiration_date DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Dimension (Conformed Dimension)
CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    product_key         BIGINT PRIMARY KEY,             -- Surrogate Key
    product_id          BIGINT NOT NULL,                -- Natural / Business Key
    sku                 VARCHAR(100) NOT NULL UNIQUE,
    product_name        VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL,
    subcategory         VARCHAR(100) NOT NULL,
    unit_cost           DECIMAL(12, 2) NOT NULL,
    unit_price          DECIMAL(12, 2) NOT NULL,
    profit_margin_pct   DECIMAL(6, 2) NOT NULL,
    price_tier          VARCHAR(50) NOT NULL,           -- Budget, Mid-Range, Premium, Luxury
    reorder_level       INTEGER NOT NULL,
    is_discontinued     BOOLEAN NOT NULL DEFAULT FALSE,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Store Dimension (Conformed Dimension)
CREATE TABLE IF NOT EXISTS warehouse.dim_store (
    store_key           BIGINT PRIMARY KEY,             -- Surrogate Key
    store_id            BIGINT NOT NULL,                -- Natural / Business Key
    store_name          VARCHAR(255) NOT NULL,
    store_type          VARCHAR(100) NOT NULL,          -- Flagship, Standard, Outlet, Online
    channel_group       VARCHAR(50) NOT NULL,           -- Physical vs Digital
    region              VARCHAR(100) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    square_feet         INTEGER NOT NULL,
    opened_date         DATE NOT NULL,
    store_age_years     INTEGER NOT NULL,
    manager_name        VARCHAR(150),
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 2. FACT TABLES
-- =============================================================================

-- Sales Fact Table (Transactional Grain: One row per order line item)
CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sales_key           BIGINT PRIMARY KEY,             -- Surrogate Key
    order_id            BIGINT NOT NULL,                -- Degenerate Dimension
    order_item_id       BIGINT NOT NULL,                -- Degenerate Dimension
    customer_key        BIGINT NOT NULL,                -- FK -> dim_customer
    product_key         BIGINT NOT NULL,                -- FK -> dim_product
    store_key           BIGINT NOT NULL,                -- FK -> dim_store
    date_key            INTEGER NOT NULL,               -- FK -> dim_date
    order_date          DATE NOT NULL,
    order_status        VARCHAR(50) NOT NULL,
    quantity            INTEGER NOT NULL,
    unit_price          DECIMAL(12, 2) NOT NULL,
    unit_cost           DECIMAL(12, 2) NOT NULL,
    gross_sales_amount  DECIMAL(14, 2) NOT NULL,        -- quantity * unit_price
    discount_amount     DECIMAL(14, 2) NOT NULL DEFAULT 0.00,
    net_sales_amount    DECIMAL(14, 2) NOT NULL,        -- gross_sales - discount
    cost_amount         DECIMAL(14, 2) NOT NULL,        -- quantity * unit_cost
    gross_profit_amount DECIMAL(14, 2) NOT NULL,        -- net_sales - cost_amount
    profit_margin_pct   DECIMAL(6, 2) NOT NULL,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments Fact Table (Transactional Grain: One row per payment transaction)
CREATE TABLE IF NOT EXISTS warehouse.fact_payments (
    payment_key         BIGINT PRIMARY KEY,             -- Surrogate Key
    payment_id          BIGINT NOT NULL,                -- Natural Key
    order_id            BIGINT NOT NULL,                -- Degenerate Dimension
    customer_key        BIGINT NOT NULL,                -- FK -> dim_customer
    date_key            INTEGER NOT NULL,               -- FK -> dim_date
    payment_method      VARCHAR(50) NOT NULL,
    payment_status      VARCHAR(50) NOT NULL,
    payment_amount      DECIMAL(14, 2) NOT NULL,
    payment_timestamp   TIMESTAMP NOT NULL,
    transaction_ref     VARCHAR(100) NOT NULL,
    is_successful       BOOLEAN NOT NULL,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 3. AGGREGATED ANALYTICAL MARTS (Periodic Snapshot / Rollup)
-- =============================================================================

-- Monthly Store Performance Mart
CREATE TABLE IF NOT EXISTS warehouse.mart_monthly_store_performance (
    mart_key            BIGINT PRIMARY KEY,
    year_month          VARCHAR(7) NOT NULL,
    year_number         INTEGER NOT NULL,
    month_number        INTEGER NOT NULL,
    store_key           BIGINT NOT NULL,
    store_name          VARCHAR(255) NOT NULL,
    region              VARCHAR(100) NOT NULL,
    channel_group       VARCHAR(50) NOT NULL,
    total_orders        BIGINT NOT NULL,
    total_units_sold    BIGINT NOT NULL,
    gross_revenue       DECIMAL(16, 2) NOT NULL,
    total_discounts     DECIMAL(16, 2) NOT NULL,
    net_revenue         DECIMAL(16, 2) NOT NULL,
    total_profit        DECIMAL(16, 2) NOT NULL,
    avg_order_value     DECIMAL(12, 2) NOT NULL,
    overall_margin_pct  DECIMAL(6, 2) NOT NULL
);

-- Customer RFM Segmentation Mart
CREATE TABLE IF NOT EXISTS warehouse.mart_customer_rfm (
    customer_key        BIGINT PRIMARY KEY,
    customer_id         BIGINT NOT NULL,
    full_name           VARCHAR(200) NOT NULL,
    segment             VARCHAR(50) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    first_order_date    DATE,
    last_order_date     DATE,
    recency_days        INTEGER,
    frequency_orders    INTEGER NOT NULL,
    monetary_spend      DECIMAL(14, 2) NOT NULL,
    avg_basket_value    DECIMAL(12, 2) NOT NULL,
    r_score             INTEGER NOT NULL,
    f_score             INTEGER NOT NULL,
    m_score             INTEGER NOT NULL,
    rfm_cell            VARCHAR(10) NOT NULL,
    rfm_customer_tier   VARCHAR(50) NOT NULL           -- Champions, Loyal, At Risk, Lost, New
);
