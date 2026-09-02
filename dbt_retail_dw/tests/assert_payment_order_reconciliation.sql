-- Custom Singular Test: Ensure payment amounts are non-negative
SELECT
    payment_id,
    payment_amount
FROM {{ ref('fact_payments') }}
WHERE payment_amount < 0
