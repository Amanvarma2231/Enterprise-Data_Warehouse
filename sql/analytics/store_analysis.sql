-- =============================================================================
-- Analytics Query 4: Store Productivity & Channel Performance
-- Square-foot efficiency, revenue density, and channel margin comparison
-- =============================================================================

SELECT
    s.store_id,
    s.store_name,
    s.store_type,
    s.channel_group,
    s.region,
    s.city,
    s.square_feet,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales_amount), 2) AS total_revenue_inr,
    ROUND(SUM(f.gross_profit_amount), 2) AS total_profit_inr,
    ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS realized_margin_pct,
    ROUND(SUM(f.net_sales_amount) / NULLIF(s.square_feet, 0), 2) AS revenue_per_sqft_inr
FROM warehouse.fact_sales f
JOIN warehouse.dim_store s ON f.store_key = s.store_key
GROUP BY s.store_id, s.store_name, s.store_type, s.channel_group, s.region, s.city, s.square_feet
ORDER BY total_revenue_inr DESC;
