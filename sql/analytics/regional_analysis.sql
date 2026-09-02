-- =============================================================================
-- Analytics Query 5: Regional Market Penetration & Geographic Contribution
-- Order density, average transaction value, and market share by region
-- =============================================================================

SELECT
    s.region,
    COUNT(DISTINCT s.store_key) AS store_count,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_customers,
    ROUND(SUM(f.net_sales_amount), 2) AS regional_revenue_inr,
    ROUND(SUM(f.gross_profit_amount), 2) AS regional_profit_inr,
    ROUND((SUM(f.net_sales_amount) / SUM(SUM(f.net_sales_amount)) OVER ()) * 100.0, 2) AS national_revenue_share_pct,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value_inr
FROM warehouse.fact_sales f
JOIN warehouse.dim_store s ON f.store_key = s.store_key
GROUP BY s.region
ORDER BY regional_revenue_inr DESC;
