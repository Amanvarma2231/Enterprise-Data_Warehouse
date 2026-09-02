{{ config(materialized='table') }}

WITH base_products AS (
    SELECT * FROM {{ ref('stg_products') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY product_id) AS product_key,
    product_id,
    sku,
    product_name,
    category,
    subcategory,
    unit_cost,
    unit_price,
    profit_margin_pct,
    price_tier,
    reorder_level,
    is_discontinued,
    CURRENT_TIMESTAMP AS _loaded_at
FROM base_products
