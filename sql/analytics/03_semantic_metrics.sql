-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Semantic Layer: Standardized Metric Calculation Views
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Executive Summary Semantic View
CREATE OR REPLACE VIEW analytics.v_executive_kpis AS
SELECT
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_active_customers,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.gross_sales_amount), 2) AS gross_merchandise_value,
    ROUND(SUM(f.discount_amount), 2) AS total_promotions,
    ROUND(SUM(f.net_sales_amount), 2) AS net_revenue,
    ROUND(SUM(f.cost_amount), 2) AS total_cogs,
    ROUND(SUM(f.gross_profit_amount), 2) AS gross_profit,
    ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS gross_margin_pct,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value
FROM warehouse.fact_sales f;

-- 2. Customer Performance Semantic View
CREATE OR REPLACE VIEW analytics.v_customer_performance AS
SELECT
    c.customer_id,
    c.full_name,
    c.segment,
    c.city,
    c.state,
    rfm.rfm_customer_tier,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales_amount), 2) AS lifetime_value,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS aov,
    MIN(f.order_date) AS first_order_date,
    MAX(f.order_date) AS last_order_date
FROM warehouse.dim_customer c
LEFT JOIN warehouse.fact_sales f ON c.customer_key = f.customer_key
LEFT JOIN warehouse.mart_customer_rfm rfm ON c.customer_key = rfm.customer_key
GROUP BY c.customer_id, c.full_name, c.segment, c.city, c.state, rfm.rfm_customer_tier;
