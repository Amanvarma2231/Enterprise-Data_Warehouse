-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Layer: Indexes, Foreign Keys & Query Optimization
-- Target Engines: PostgreSQL / DuckDB / SQLite / BigQuery
-- =============================================================================

-- =============================================================================
-- 1. FOREIGN KEY CONSTRAINTS (Referential Integrity)
-- =============================================================================

-- fact_sales Foreign Keys
ALTER TABLE warehouse.fact_sales
    ADD CONSTRAINT fk_sales_customer FOREIGN KEY (customer_key)
    REFERENCES warehouse.dim_customer(customer_key);

ALTER TABLE warehouse.fact_sales
    ADD CONSTRAINT fk_sales_product FOREIGN KEY (product_key)
    REFERENCES warehouse.dim_product(product_key);

ALTER TABLE warehouse.fact_sales
    ADD CONSTRAINT fk_sales_store FOREIGN KEY (store_key)
    REFERENCES warehouse.dim_store(store_key);

ALTER TABLE warehouse.fact_sales
    ADD CONSTRAINT fk_sales_date FOREIGN KEY (date_key)
    REFERENCES warehouse.dim_date(date_key);

-- fact_payments Foreign Keys
ALTER TABLE warehouse.fact_payments
    ADD CONSTRAINT fk_payment_customer FOREIGN KEY (customer_key)
    REFERENCES warehouse.dim_customer(customer_key);

ALTER TABLE warehouse.fact_payments
    ADD CONSTRAINT fk_payment_date FOREIGN KEY (date_key)
    REFERENCES warehouse.dim_date(date_key);

-- =============================================================================
-- 2. PERFORMANCE INDEXES (Star Schema Join Acceleration)
-- =============================================================================

-- Dimensions Natural Key Indexes
CREATE INDEX IF NOT EXISTS idx_dim_cust_nat_id ON warehouse.dim_customer (customer_id);
CREATE INDEX IF NOT EXISTS idx_dim_prod_nat_id ON warehouse.dim_product (product_id);
CREATE INDEX IF NOT EXISTS idx_dim_prod_sku ON warehouse.dim_product (sku);
CREATE INDEX IF NOT EXISTS idx_dim_store_nat_id ON warehouse.dim_store (store_id);
CREATE INDEX IF NOT EXISTS idx_dim_date_full ON warehouse.dim_date (full_date);
CREATE INDEX IF NOT EXISTS idx_dim_date_ym ON warehouse.dim_date (year_number, month_number);

-- fact_sales Foreign Key & Slicing Indexes
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON warehouse.fact_sales (date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_cust ON warehouse.fact_sales (customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_prod ON warehouse.fact_sales (product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_store ON warehouse.fact_sales (store_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_order ON warehouse.fact_sales (order_id);

-- Composite / Covering Index for High-Frequency Aggregations (Date + Store + Product)
CREATE INDEX IF NOT EXISTS idx_fact_sales_rollup ON warehouse.fact_sales (
    date_key,
    store_key,
    product_key,
    net_sales_amount,
    quantity
);

-- fact_payments Indexes
CREATE INDEX IF NOT EXISTS idx_fact_pay_order ON warehouse.fact_payments (order_id);
CREATE INDEX IF NOT EXISTS idx_fact_pay_status ON warehouse.fact_payments (payment_status);
CREATE INDEX IF NOT EXISTS idx_fact_pay_date ON warehouse.fact_payments (date_key);
