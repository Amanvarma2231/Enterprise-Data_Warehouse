-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Engine: Snowflake Cloud Data Platform DDL
-- Layer: Virtual Warehouses, Transient Staging & Clustered Star Schema
-- =============================================================================

CREATE DATABASE IF NOT EXISTS RETAILSPHERE_DW;
USE DATABASE RETAILSPHERE_DW;

CREATE SCHEMA IF NOT EXISTS STAGING;
CREATE SCHEMA IF NOT EXISTS WAREHOUSE;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;

-- 1. TRANSIENT STAGING TABLES (Optimized for Cost & High-Velocity ELT)
CREATE OR REPLACE TRANSIENT TABLE STAGING.STG_ORDERS (
    order_id            VARCHAR(50),
    customer_id         VARCHAR(50),
    store_id            VARCHAR(50),
    order_date          VARCHAR(50),
    order_status        VARCHAR(50),
    shipping_amount     VARCHAR(50),
    discount_total      VARCHAR(50),
    payment_status      VARCHAR(50),
    _ingested_at        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file        VARCHAR(255)
);

-- 2. STAR SCHEMA DIMENSIONS & FACTS (Clustered for Fast Analytics)
CREATE OR REPLACE TABLE WAREHOUSE.DIM_CUSTOMER (
    customer_key        NUMBER(38,0) NOT NULL PRIMARY KEY,
    customer_id         NUMBER(38,0) NOT NULL,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    full_name           VARCHAR(200) NOT NULL,
    email               VARCHAR(255) NOT NULL,
    phone               VARCHAR(50),
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    country             VARCHAR(100) DEFAULT 'India',
    postal_code         VARCHAR(30),
    segment             VARCHAR(50) NOT NULL,
    registration_date   DATE NOT NULL,
    is_active           BOOLEAN DEFAULT TRUE,
    row_effective_date  DATE DEFAULT CURRENT_DATE(),
    row_expiration_date DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN DEFAULT TRUE,
    _loaded_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY (customer_id, segment);

CREATE OR REPLACE TABLE WAREHOUSE.FACT_SALES (
    sales_key           NUMBER(38,0) NOT NULL PRIMARY KEY,
    order_id            NUMBER(38,0) NOT NULL,
    order_item_id       NUMBER(38,0) NOT NULL,
    customer_key        NUMBER(38,0) NOT NULL REFERENCES WAREHOUSE.DIM_CUSTOMER(customer_key),
    product_key         NUMBER(38,0) NOT NULL,
    store_key           NUMBER(38,0) NOT NULL,
    date_key            NUMBER(8,0) NOT NULL,
    order_date          DATE NOT NULL,
    order_status        VARCHAR(50) NOT NULL,
    quantity            NUMBER(10,0) NOT NULL,
    unit_price          NUMBER(12,2) NOT NULL,
    unit_cost           NUMBER(12,2) NOT NULL,
    gross_sales_amount  NUMBER(14,2) NOT NULL,
    discount_amount     NUMBER(14,2) DEFAULT 0.00,
    net_sales_amount    NUMBER(14,2) NOT NULL,
    cost_amount         NUMBER(14,2) NOT NULL,
    gross_profit_amount NUMBER(14,2) NOT NULL,
    profit_margin_pct   NUMBER(6,2) NOT NULL,
    _loaded_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY (order_date, customer_key, product_key);
