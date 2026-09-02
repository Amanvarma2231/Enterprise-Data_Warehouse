WITH order_lines AS (
    SELECT * FROM {{ ref('int_order_items_enriched') }}
)
SELECT
    order_id,
    customer_id,
    store_id,
    order_date,
    order_status,
    COUNT(order_item_id) AS total_items,
    SUM(quantity) AS total_units_ordered,
    SUM(gross_sales_amount) AS order_gross_total,
    SUM(discount_amount) AS order_discount_total,
    SUM(net_sales_amount) AS order_net_total,
    SUM(cost_amount) AS order_total_cost,
    SUM(gross_profit_amount) AS order_gross_profit
FROM order_lines
GROUP BY order_id, customer_id, store_id, order_date, order_status
