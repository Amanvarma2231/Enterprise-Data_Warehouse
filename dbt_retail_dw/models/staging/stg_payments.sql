WITH source AS (
    SELECT * FROM staging.stg_payments
)
SELECT
    CAST(payment_id AS BIGINT) AS payment_id,
    CAST(order_id AS BIGINT) AS order_id,
    TRIM(payment_method) AS payment_method,
    TRIM(payment_status) AS payment_status,
    CAST(payment_amount AS DECIMAL(14, 2)) AS payment_amount,
    TRY_CAST(payment_date AS TIMESTAMP) AS payment_timestamp,
    TRIM(transaction_ref) AS transaction_ref,
    CASE WHEN TRIM(payment_status) = 'Success' THEN TRUE ELSE FALSE END AS is_successful,
    _ingested_at,
    _source_file
FROM source
WHERE payment_id IS NOT NULL
