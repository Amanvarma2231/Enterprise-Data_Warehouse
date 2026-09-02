-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Engine: SQLite 3 Embedded Database DDL
-- Layer: Staging, Star Schema Warehouse & Fast Analytical Views
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_customers (
    customer_id         TEXT,
    first_name          TEXT,
    last_name           TEXT,
    email               TEXT,
    phone               TEXT,
    city                TEXT,
    state               TEXT,
    country             TEXT,
    postal_code         TEXT,
    segment             TEXT,
    registration_date   TEXT,
    is_active           TEXT,
    _ingested_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    _source_file        TEXT
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key        INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER NOT NULL,
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    full_name           TEXT NOT NULL,
    email               TEXT NOT NULL,
    phone               TEXT,
    city                TEXT NOT NULL,
    state               TEXT NOT NULL,
    country             TEXT NOT NULL DEFAULT 'India',
    postal_code         TEXT,
    segment             TEXT NOT NULL,
    registration_date   TEXT NOT NULL,
    is_active           INTEGER NOT NULL DEFAULT 1,
    row_effective_date  TEXT NOT NULL,
    row_expiration_date TEXT DEFAULT '9999-12-31',
    is_current          INTEGER NOT NULL DEFAULT 1,
    _loaded_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key           INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id            INTEGER NOT NULL,
    order_item_id       INTEGER NOT NULL,
    customer_key        INTEGER NOT NULL,
    product_key         INTEGER NOT NULL,
    store_key           INTEGER NOT NULL,
    date_key            INTEGER NOT NULL,
    order_date          TEXT NOT NULL,
    order_status        TEXT NOT NULL,
    quantity            INTEGER NOT NULL,
    unit_price          REAL NOT NULL,
    unit_cost           REAL NOT NULL,
    gross_sales_amount  REAL NOT NULL,
    discount_amount     REAL NOT NULL DEFAULT 0.0,
    net_sales_amount    REAL NOT NULL,
    cost_amount         REAL NOT NULL,
    gross_profit_amount REAL NOT NULL,
    profit_margin_pct   REAL NOT NULL,
    _loaded_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)
);
