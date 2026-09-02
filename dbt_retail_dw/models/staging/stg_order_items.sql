WITH source AS (
    SELECT * FROM staging.stg_order_items
)
SELECT
    CAST(order_item_id AS BIGINT) AS order_item_id,
    CAST(order_id AS BIGINT) AS order_id,
    CAST(product_id AS BIGINT) AS product_id,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(unit_price AS DECIMAL(12, 2)) AS unit_price,
    CAST(COALESCE(discount, '0.00') AS DECIMAL(14, 2)) AS discount_amount,
    CAST(line_total AS DECIMAL(14, 2)) AS line_total,
    _ingested_at,
    _source_file
FROM source
WHERE order_item_id IS NOT NULL 
  AND TRY_CAST(quantity AS INTEGER) > 0 
  AND TRY_CAST(unit_price AS DECIMAL(12, 2)) > 0
