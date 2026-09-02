WITH source AS (
    SELECT * FROM staging.stg_products
)
SELECT
    CAST(product_id AS BIGINT) AS product_id,
    TRIM(sku) AS sku,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    TRIM(subcategory) AS subcategory,
    CAST(unit_cost AS DECIMAL(12, 2)) AS unit_cost,
    CAST(unit_price AS DECIMAL(12, 2)) AS unit_price,
    ROUND(((CAST(unit_price AS DECIMAL(12, 2)) - CAST(unit_cost AS DECIMAL(12, 2))) / CAST(unit_price AS DECIMAL(12, 2))) * 100.0, 2) AS profit_margin_pct,
    CASE 
        WHEN CAST(unit_price AS DECIMAL(12, 2)) < 500 THEN 'Budget'
        WHEN CAST(unit_price AS DECIMAL(12, 2)) BETWEEN 500 AND 3000 THEN 'Mid-Range'
        WHEN CAST(unit_price AS DECIMAL(12, 2)) BETWEEN 3001 AND 15000 THEN 'Premium'
        ELSE 'Luxury'
    END AS price_tier,
    CAST(COALESCE(reorder_level, '10') AS INTEGER) AS reorder_level,
    CASE WHEN LOWER(TRIM(is_discontinued)) IN ('true', '1', 't') THEN TRUE ELSE FALSE END AS is_discontinued,
    _ingested_at,
    _source_file
FROM source
WHERE product_id IS NOT NULL 
  AND TRY_CAST(unit_price AS DECIMAL(12, 2)) > 0
