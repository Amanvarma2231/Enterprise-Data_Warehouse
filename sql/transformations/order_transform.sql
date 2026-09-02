-- =============================================================================
-- SQL Transformation: Staging Payments -> Fact Payments
-- Order-level transaction reconciliation and payment status classification
-- =============================================================================

INSERT INTO warehouse.fact_payments (
    payment_key,
    payment_id,
    order_id,
    customer_key,
    store_key,
    date_key,
    payment_date,
    payment_method,
    payment_status,
    payment_amount,
    _loaded_at
)
SELECT
    ROW_NUMBER() OVER (ORDER BY CAST(p.payment_id AS BIGINT)) AS payment_key,
    CAST(p.payment_id AS BIGINT) AS payment_id,
    CAST(p.order_id AS BIGINT) AS order_id,
    dc.customer_key,
    ds.store_key,
    dd.date_key,
    CAST(p.payment_date AS DATE) AS payment_date,
    TRIM(p.payment_method) AS payment_method,
    TRIM(p.payment_status) AS payment_status,
    CAST(p.payment_amount AS DECIMAL(12, 2)) AS payment_amount,
    CURRENT_TIMESTAMP AS _loaded_at
FROM staging.stg_payments p
JOIN staging.stg_orders o ON p.order_id = o.order_id
JOIN warehouse.dim_customer dc ON CAST(o.customer_id AS BIGINT) = dc.customer_id
JOIN warehouse.dim_store ds ON CAST(o.store_id AS BIGINT) = ds.store_id
JOIN warehouse.dim_date dd ON CAST(p.payment_date AS DATE) = dd.full_date
WHERE TRY_CAST(p.payment_amount AS DECIMAL(12, 2)) >= 0;
