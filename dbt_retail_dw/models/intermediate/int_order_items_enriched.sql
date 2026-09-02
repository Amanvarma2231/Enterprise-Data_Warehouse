WITH items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),
products AS (
    SELECT * FROM {{ ref('stg_products') }}
),
orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
)
SELECT
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    o.store_id,
    o.order_date,
    o.order_status,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    p.unit_cost,
    (oi.quantity * oi.unit_price) AS gross_sales_amount,
    oi.discount_amount,
    (oi.quantity * oi.unit_price) - oi.discount_amount AS net_sales_amount,
    (oi.quantity * p.unit_cost) AS cost_amount,
    ((oi.quantity * oi.unit_price) - oi.discount_amount) - (oi.quantity * p.unit_cost) AS gross_profit_amount
FROM items oi
INNER JOIN orders o ON oi.order_id = o.order_id
INNER JOIN products p ON oi.product_id = p.product_id
