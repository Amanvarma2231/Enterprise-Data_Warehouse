-- =============================================================================
-- Analytics Query 3: Product Merchandising & Pareto 80/20 Contribution
-- Category velocity, SKU ranking, and cumulative revenue percentage
-- =============================================================================

WITH product_revenue AS (
    SELECT
        p.product_id,
        p.sku,
        p.product_name,
        p.category,
        p.subcategory,
        p.price_tier,
        SUM(f.quantity) AS total_units_sold,
        ROUND(SUM(f.net_sales_amount), 2) AS total_revenue_inr,
        ROUND(SUM(f.gross_profit_amount), 2) AS total_profit_inr,
        ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS realized_margin_pct
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_product p ON f.product_key = p.product_key
    GROUP BY p.product_id, p.sku, p.product_name, p.category, p.subcategory, p.price_tier
)
SELECT
    *,
    ROUND(SUM(total_revenue_inr) OVER (ORDER BY total_revenue_inr DESC) / 
          SUM(total_revenue_inr) OVER () * 100.0, 2) AS cumulative_revenue_pct
FROM product_revenue
ORDER BY total_revenue_inr DESC
LIMIT 25;
