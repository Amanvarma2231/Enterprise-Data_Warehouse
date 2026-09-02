WITH customer_orders AS (
    SELECT * FROM {{ ref('int_orders_aggregated') }}
)
SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS lifetime_orders,
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS most_recent_order_date,
    SUM(order_net_total) AS lifetime_net_spend,
    SUM(order_gross_profit) AS lifetime_gross_profit,
    ROUND(SUM(order_net_total) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_order_value
FROM customer_orders
GROUP BY customer_id
