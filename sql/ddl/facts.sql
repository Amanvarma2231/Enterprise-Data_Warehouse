-- =============================================================================
-- RetailSphere Enterprise Data Warehouse - Fact Tables DDL
-- Atomic Fact Sales (Line-Item Grain) and Order-Level Fact Payments
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sales_key           BIGINT PRIMARY KEY,
    order_id            BIGINT NOT NULL,
    order_item_id       BIGINT NOT NULL,
    customer_key        BIGINT NOT NULL REFERENCES warehouse.dim_customer(customer_key),
    product_key         BIGINT NOT NULL REFERENCES warehouse.dim_product(product_key),
    store_key           BIGINT NOT NULL REFERENCES warehouse.dim_store(store_key),
    date_key            INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
    order_date          DATE NOT NULL,
    order_status        VARCHAR(50) NOT NULL,
    quantity            INTEGER NOT NULL,
    unit_price          DECIMAL(12, 2) NOT NULL,
    unit_cost           DECIMAL(12, 2) NOT NULL,
    discount_amount     DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    gross_sales_amount  DECIMAL(12, 2) NOT NULL,
    net_sales_amount    DECIMAL(12, 2) NOT NULL,
    cost_amount         DECIMAL(12, 2) NOT NULL,
    gross_profit_amount DECIMAL(12, 2) NOT NULL,
    profit_margin_pct   DECIMAL(5, 2),
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.fact_payments (
    payment_key         BIGINT PRIMARY KEY,
    payment_id          BIGINT NOT NULL,
    order_id            BIGINT NOT NULL,
    customer_key        BIGINT NOT NULL REFERENCES warehouse.dim_customer(customer_key),
    store_key           BIGINT NOT NULL REFERENCES warehouse.dim_store(store_key),
    date_key            INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
    payment_date        DATE NOT NULL,
    payment_method      VARCHAR(50) NOT NULL,
    payment_status      VARCHAR(50) NOT NULL,
    payment_amount      DECIMAL(12, 2) NOT NULL,
    _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
