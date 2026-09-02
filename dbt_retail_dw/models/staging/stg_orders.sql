WITH source AS (
    SELECT * FROM staging.stg_orders
),
cleansed AS (
    SELECT
        CAST(order_id AS BIGINT) AS order_id,
        CAST(customer_id AS BIGINT) AS customer_id,
        CAST(store_id AS BIGINT) AS store_id,
        TRY_CAST(order_date AS DATE) AS order_date,
        TRIM(order_status) AS order_status,
        CAST(COALESCE(shipping_amount, '0.00') AS DECIMAL(10, 2)) AS shipping_amount,
        CAST(COALESCE(discount_total, '0.00') AS DECIMAL(10, 2)) AS discount_total,
        TRIM(payment_status) AS payment_status,
        _ingested_at,
        _source_file,
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY _ingested_at DESC) as row_num
    FROM source
    WHERE order_id IS NOT NULL 
      AND customer_id IS NOT NULL
      AND TRIM(customer_id) != ''
      AND TRY_CAST(order_date AS DATE) <= CURRENT_DATE
)
SELECT
    order_id,
    customer_id,
    store_id,
    order_date,
    order_status,
    shipping_amount,
    discount_total,
    payment_status,
    _ingested_at,
    _source_file
FROM cleansed
WHERE row_num = 1
