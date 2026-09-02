-- =============================================================================
-- RetailSphere Enterprise Data Warehouse - Conformed Dimensions DDL
-- Star schema dimensional layer with surrogate keys and SCD support
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key            INTEGER PRIMARY KEY,
    full_date           DATE NOT NULL,
    day_of_month        INTEGER NOT NULL,
    day_name            VARCHAR(20) NOT NULL,
    day_of_week         INTEGER NOT NULL,
    month_number        INTEGER NOT NULL,
    month_name          VARCHAR(20) NOT NULL,
    year_month          VARCHAR(7) NOT NULL,
    calendar_quarter    INTEGER NOT NULL,
    calendar_year       INTEGER NOT NULL,
    fiscal_quarter      VARCHAR(10) NOT NULL,
    fiscal_year         INTEGER NOT NULL,
    week_of_year        INTEGER NOT NULL,
    is_weekend          BOOLEAN NOT NULL,
    is_holiday          BOOLEAN NOT NULL,
    holiday_name        VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key        BIGINT PRIMARY KEY,
    customer_id         BIGINT NOT NULL,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    full_name           VARCHAR(200) NOT NULL,
    email               VARCHAR(150),
    phone               VARCHAR(50),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100),
    postal_code         VARCHAR(20),
    segment             VARCHAR(50),
    registration_date   DATE,
    is_active           BOOLEAN DEFAULT TRUE,
    row_effective_date  DATE DEFAULT CURRENT_DATE,
    row_expiration_date DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN DEFAULT TRUE,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    product_key         BIGINT PRIMARY KEY,
    product_id          BIGINT NOT NULL,
    sku                 VARCHAR(50) NOT NULL,
    product_name        VARCHAR(150) NOT NULL,
    category            VARCHAR(100) NOT NULL,
    subcategory         VARCHAR(100),
    unit_cost           DECIMAL(12, 2) NOT NULL,
    unit_price          DECIMAL(12, 2) NOT NULL,
    profit_margin_pct   DECIMAL(5, 2),
    price_tier          VARCHAR(50),
    reorder_level       INTEGER,
    is_discontinued     BOOLEAN DEFAULT FALSE,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.dim_store (
    store_key           BIGINT PRIMARY KEY,
    store_id            BIGINT NOT NULL,
    store_name          VARCHAR(150) NOT NULL,
    store_type          VARCHAR(50),
    channel_group       VARCHAR(50) NOT NULL,
    region              VARCHAR(50) NOT NULL,
    city                VARCHAR(100),
    state               VARCHAR(100),
    square_feet         INTEGER,
    opening_date        DATE,
    store_age_years     DECIMAL(4, 1),
    is_active           BOOLEAN DEFAULT TRUE,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
