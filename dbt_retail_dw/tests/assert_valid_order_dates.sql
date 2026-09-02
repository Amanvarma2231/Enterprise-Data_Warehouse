-- Custom Singular Test: Ensure no future order dates exist in the warehouse
SELECT
    order_id,
    order_date
FROM {{ ref('stg_orders') }}
WHERE order_date > CURRENT_DATE
