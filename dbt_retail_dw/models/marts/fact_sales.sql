{{ config(materialized='table') }}

WITH enriched_items AS (
    SELECT * FROM {{ ref('int_order_items_enriched') }}
),
customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),
products AS (
    SELECT * FROM {{ ref('dim_product') }}
),
stores AS (
    SELECT * FROM {{ ref('dim_store') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY oi.order_id, oi.order_item_id) AS sales_key,
    oi.order_id,
    oi.order_item_id,
    dc.customer_key,
    dp.product_key,
    ds.store_key,
    CAST(strftime(CAST(oi.order_date AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
    oi.order_date,
    oi.order_status,
    oi.quantity,
    oi.unit_price,
    oi.unit_cost,
    oi.gross_sales_amount,
    oi.discount_amount,
    oi.net_sales_amount,
    oi.cost_amount,
    oi.gross_profit_amount,
    ROUND(
        CASE 
            WHEN oi.net_sales_amount > 0 THEN (oi.gross_profit_amount / oi.net_sales_amount) * 100.0
            ELSE 0.0
        END, 2
    ) AS profit_margin_pct,
    CURRENT_TIMESTAMP AS _loaded_at
FROM enriched_items oi
INNER JOIN customers dc ON oi.customer_id = dc.customer_id
INNER JOIN products dp ON oi.product_id = dp.product_id
INNER JOIN stores ds ON oi.store_id = ds.store_id
