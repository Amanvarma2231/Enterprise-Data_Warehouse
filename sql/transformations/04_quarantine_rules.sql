-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Transformation: Data Quarantine & Anomaly Isolation Rules
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS quarantine;

-- 1. Quarantine Orders with NULL customer_id or Future Order Dates
CREATE TABLE IF NOT EXISTS quarantine.quarantine_orders AS
SELECT 
    o.*,
    CASE 
        WHEN o.customer_id IS NULL OR TRIM(o.customer_id) = '' THEN 'ERR_NULL_CUSTOMER_KEY'
        WHEN CAST(o.order_date AS DATE) > CURRENT_DATE THEN 'ERR_FUTURE_ORDER_DATE'
        ELSE 'ERR_UNSPECIFIED'
    END AS rejection_reason_code,
    CURRENT_TIMESTAMP AS quarantined_at
FROM staging.stg_orders o
WHERE o.customer_id IS NULL 
   OR TRIM(o.customer_id) = ''
   OR CAST(o.order_date AS DATE) > CURRENT_DATE;

-- 2. Quarantine Order Items with Non-Positive Quantity or Orphaned Product Keys
CREATE TABLE IF NOT EXISTS quarantine.quarantine_order_items AS
SELECT 
    oi.*,
    CASE 
        WHEN CAST(oi.quantity AS INTEGER) <= 0 THEN 'ERR_INVALID_QUANTITY_NON_POSITIVE'
        WHEN dp.product_id IS NULL THEN 'ERR_ORPHAN_PRODUCT_KEY'
        WHEN CAST(oi.unit_price AS DECIMAL(12, 2)) <= 0 THEN 'ERR_INVALID_UNIT_PRICE'
        ELSE 'ERR_UNSPECIFIED'
    END AS rejection_reason_code,
    CURRENT_TIMESTAMP AS quarantined_at
FROM staging.stg_order_items oi
LEFT JOIN staging.stg_products dp 
    ON oi.product_id = dp.product_id
WHERE CAST(oi.quantity AS INTEGER) <= 0
   OR dp.product_id IS NULL
   OR CAST(oi.unit_price AS DECIMAL(12, 2)) <= 0;

-- 3. Quarantine Customers with Invalid Email Formatting
CREATE TABLE IF NOT EXISTS quarantine.quarantine_customers AS
SELECT 
    c.*,
    'ERR_MALFORMED_EMAIL_SYNTAX' AS rejection_reason_code,
    CURRENT_TIMESTAMP AS quarantined_at
FROM staging.stg_customers c
WHERE c.email NOT LIKE '%@%.%' 
   OR c.email IS NULL;
