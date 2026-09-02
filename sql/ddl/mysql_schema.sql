-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Engine: MySQL 8.0+ / MariaDB Database DDL
-- Layer: Staging, Star Schema Warehouse & Referential Integrity Constraints
-- =============================================================================

CREATE DATABASE IF NOT EXISTS retailsphere_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE retailsphere_dw;

-- =============================================================================
-- 1. STAGING LAYER (Operational Landing Tables)
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_customers (
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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stg_products (
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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stg_stores (
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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stg_orders (
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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stg_order_items (
    order_item_id       VARCHAR(50),
    order_id            VARCHAR(50),
    product_id          VARCHAR(50),
    quantity            VARCHAR(50),
    unit_price          VARCHAR(50),
    discount            VARCHAR(50),
    line_total          VARCHAR(50),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stg_payments (
    payment_id          VARCHAR(50),
    order_id            VARCHAR(50),
    payment_method      VARCHAR(50),
    payment_status      VARCHAR(50),
    payment_amount      VARCHAR(50),
    payment_date        VARCHAR(50),
    transaction_ref     VARCHAR(100),
    _ingested_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _source_file        VARCHAR(255)
) ENGINE=InnoDB;

-- =============================================================================
-- 2. DIMENSION TABLES (Kimball Star Schema)
-- =============================================================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_key            INT PRIMARY KEY,
    full_date           DATE NOT NULL UNIQUE,
    day_of_month        INT NOT NULL,
    month_number        INT NOT NULL,
    month_name          VARCHAR(20) NOT NULL,
    month_short_name    VARCHAR(3) NOT NULL,
    quarter_number      INT NOT NULL,
    quarter_name        VARCHAR(10) NOT NULL,
    year_number         INT NOT NULL,
    year_month          VARCHAR(7) NOT NULL,
    day_of_week         INT NOT NULL,
    day_name            VARCHAR(20) NOT NULL,
    week_of_year        INT NOT NULL,
    is_weekend          BOOLEAN NOT NULL,
    is_holiday          BOOLEAN DEFAULT FALSE,
    fiscal_year         INT NOT NULL,
    fiscal_quarter      VARCHAR(10) NOT NULL,
    INDEX idx_date_ym (year_number, month_number)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_customer (
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
    row_effective_date  DATE NOT NULL,
    row_expiration_date DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cust_nat (customer_id),
    INDEX idx_cust_segment (segment)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_product (
    product_key         BIGINT PRIMARY KEY,
    product_id          BIGINT NOT NULL,
    sku                 VARCHAR(100) NOT NULL UNIQUE,
    product_name        VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL,
    subcategory         VARCHAR(100) NOT NULL,
    unit_cost           DECIMAL(12, 2) NOT NULL,
    unit_price          DECIMAL(12, 2) NOT NULL,
    profit_margin_pct   DECIMAL(6, 2) NOT NULL,
    price_tier          VARCHAR(50) NOT NULL,
    reorder_level       INT NOT NULL,
    is_discontinued     BOOLEAN NOT NULL DEFAULT FALSE,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_prod_nat (product_id),
    INDEX idx_prod_cat (category, subcategory)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_store (
    store_key           BIGINT PRIMARY KEY,
    store_id            BIGINT NOT NULL,
    store_name          VARCHAR(255) NOT NULL,
    store_type          VARCHAR(100) NOT NULL,
    channel_group       VARCHAR(50) NOT NULL,
    region              VARCHAR(100) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    square_feet         INT NOT NULL,
    opened_date         DATE NOT NULL,
    store_age_years     INT NOT NULL,
    manager_name        VARCHAR(150),
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_store_nat (store_id),
    INDEX idx_store_region (region)
) ENGINE=InnoDB;

-- =============================================================================
-- 3. FACT TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key           BIGINT PRIMARY KEY,
    order_id            BIGINT NOT NULL,
    order_item_id       BIGINT NOT NULL,
    customer_key        BIGINT NOT NULL,
    product_key         BIGINT NOT NULL,
    store_key           BIGINT NOT NULL,
    date_key            INT NOT NULL,
    order_date          DATE NOT NULL,
    order_status        VARCHAR(50) NOT NULL,
    quantity            INT NOT NULL,
    unit_price          DECIMAL(12, 2) NOT NULL,
    unit_cost           DECIMAL(12, 2) NOT NULL,
    gross_sales_amount  DECIMAL(14, 2) NOT NULL,
    discount_amount     DECIMAL(14, 2) NOT NULL DEFAULT 0.00,
    net_sales_amount    DECIMAL(14, 2) NOT NULL,
    cost_amount         DECIMAL(14, 2) NOT NULL,
    gross_profit_amount DECIMAL(14, 2) NOT NULL,
    profit_margin_pct   DECIMAL(6, 2) NOT NULL,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mysql_sales_cust FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_mysql_sales_prod FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    CONSTRAINT fk_mysql_sales_store FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
    CONSTRAINT fk_mysql_sales_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    INDEX idx_sales_order (order_id),
    INDEX idx_sales_date (date_key)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fact_payments (
    payment_key         BIGINT PRIMARY KEY,
    payment_id          BIGINT NOT NULL,
    order_id            BIGINT NOT NULL,
    customer_key        BIGINT NOT NULL,
    date_key            INT NOT NULL,
    payment_method      VARCHAR(50) NOT NULL,
    payment_status      VARCHAR(50) NOT NULL,
    payment_amount      DECIMAL(14, 2) NOT NULL,
    payment_timestamp   DATETIME NOT NULL,
    transaction_ref     VARCHAR(100) NOT NULL,
    is_successful       BOOLEAN NOT NULL,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pay_order (order_id),
    INDEX idx_pay_status (payment_status)
) ENGINE=InnoDB;
