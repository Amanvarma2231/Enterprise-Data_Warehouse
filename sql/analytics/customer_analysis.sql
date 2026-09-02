-- =============================================================================
-- Analytics Query 2: Customer LTV & RFM Behavioral Segmentation
-- Top customer lifetime spend, order frequency, and recency analysis
-- =============================================================================

SELECT
    c.customer_id,
    c.full_name,
    c.city,
    c.segment,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_items_purchased,
    ROUND(SUM(f.net_sales_amount), 2) AS lifetime_spend_inr,
    ROUND(AVG(f.net_sales_amount), 2) AS avg_item_spend_inr,
    MAX(f.order_date) AS last_order_date,
    CURRENT_DATE - MAX(f.order_date) AS days_since_last_order,
    DENSE_RANK() OVER (ORDER BY SUM(f.net_sales_amount) DESC) AS customer_revenue_rank
FROM warehouse.fact_sales f
JOIN warehouse.dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.full_name, c.city, c.segment
ORDER BY lifetime_spend_inr DESC
LIMIT 20;
