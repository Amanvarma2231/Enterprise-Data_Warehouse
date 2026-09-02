{{ config(materialized='table') }}

WITH stg_pay AS (
    SELECT * FROM {{ ref('stg_payments') }}
),
stg_ord AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY p.payment_id) AS payment_key,
    p.payment_id,
    p.order_id,
    COALESCE(dc.customer_key, 0) AS customer_key,
    CAST(strftime(CAST(p.payment_timestamp AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
    p.payment_method,
    p.payment_status,
    p.payment_amount,
    p.payment_timestamp,
    p.transaction_ref,
    p.is_successful,
    CURRENT_TIMESTAMP AS _loaded_at
FROM stg_pay p
LEFT JOIN stg_ord o ON p.order_id = o.order_id
LEFT JOIN customers dc ON o.customer_id = dc.customer_id
