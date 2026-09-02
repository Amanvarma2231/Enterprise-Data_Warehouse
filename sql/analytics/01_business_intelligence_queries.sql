-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Suite: 20+ Production Analytical Business Intelligence Queries
-- Target Engine: PostgreSQL / DuckDB / BigQuery / Snowflake
-- Focus: KPIs, Window Functions, CTEs, Cohorts, Rollups & RFM Analysis
-- =============================================================================

-- -----------------------------------------------------------------------------
-- QUERY 1: Executive KPI Overview (Revenue, Orders, Customers, AOV, Gross Margin)
-- -----------------------------------------------------------------------------
SELECT
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS total_active_customers,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.gross_sales_amount), 2) AS gross_revenue,
    ROUND(SUM(f.discount_amount), 2) AS total_discounts,
    ROUND(SUM(f.net_sales_amount), 2) AS net_revenue,
    ROUND(SUM(f.cost_amount), 2) AS total_cogs,
    ROUND(SUM(f.gross_profit_amount), 2) AS gross_profit,
    ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS gross_margin_pct,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value_aov
FROM warehouse.fact_sales f;


-- -----------------------------------------------------------------------------
-- QUERY 2: Monthly Revenue Trend & Month-over-Month (MoM) Growth Analysis
-- -----------------------------------------------------------------------------
WITH monthly_revenue AS (
    SELECT
        d.year_number,
        d.month_number,
        d.year_month,
        ROUND(SUM(f.net_sales_amount), 2) AS monthly_net_revenue,
        COUNT(DISTINCT f.order_id) AS monthly_orders
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    GROUP BY d.year_number, d.month_number, d.year_month
)
SELECT
    year_month,
    monthly_net_revenue,
    monthly_orders,
    LAG(monthly_net_revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
    ROUND(
        ((monthly_net_revenue - LAG(monthly_net_revenue, 1) OVER (ORDER BY year_month)) /
        NULLIF(LAG(monthly_net_revenue, 1) OVER (ORDER BY year_month), 0)) * 100.0, 2
    ) AS mom_revenue_growth_pct
FROM monthly_revenue
ORDER BY year_month;


-- -----------------------------------------------------------------------------
-- QUERY 3: Year-over-Year (YoY) Quarterly Performance Matrix
-- -----------------------------------------------------------------------------
SELECT
    d.year_number,
    d.quarter_name,
    ROUND(SUM(f.net_sales_amount), 2) AS quarterly_revenue,
    ROUND(SUM(f.gross_profit_amount), 2) AS quarterly_profit,
    LAG(SUM(f.net_sales_amount), 4) OVER (ORDER BY d.year_number, d.quarter_number) AS prev_year_same_quarter_revenue,
    ROUND(
        ((SUM(f.net_sales_amount) - LAG(SUM(f.net_sales_amount), 4) OVER (ORDER BY d.year_number, d.quarter_number)) /
        NULLIF(LAG(SUM(f.net_sales_amount), 4) OVER (ORDER BY d.year_number, d.quarter_number), 0)) * 100.0, 2
    ) AS yoy_quarterly_growth_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
GROUP BY d.year_number, d.quarter_number, d.quarter_name
ORDER BY d.year_number, d.quarter_number;


-- -----------------------------------------------------------------------------
-- QUERY 4: Top 10 Best-Selling Products by Net Revenue
-- -----------------------------------------------------------------------------
SELECT
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    p.subcategory,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.net_sales_amount), 2) AS total_revenue,
    ROUND(SUM(f.gross_profit_amount), 2) AS total_profit,
    p.profit_margin_pct AS catalog_margin_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.sku, p.product_name, p.category, p.subcategory, p.profit_margin_pct
ORDER BY total_revenue DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- QUERY 5: Product Category Contribution & Cumulative Revenue Pareto (80/20 Rule)
-- -----------------------------------------------------------------------------
WITH category_sales AS (
    SELECT
        p.category,
        ROUND(SUM(f.net_sales_amount), 2) AS category_revenue,
        SUM(f.quantity) AS category_units
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_product p ON f.product_key = p.product_key
    GROUP BY p.category
),
total_pool AS (
    SELECT SUM(category_revenue) AS grand_total FROM category_sales
)
SELECT
    cs.category,
    cs.category_revenue,
    cs.category_units,
    ROUND((cs.category_revenue / tp.grand_total) * 100.0, 2) AS revenue_share_pct,
    ROUND(
        SUM(cs.category_revenue) OVER (ORDER BY cs.category_revenue DESC) / tp.grand_total * 100.0, 2
    ) AS cumulative_revenue_share_pct
FROM category_sales cs
CROSS JOIN total_pool tp
ORDER BY cs.category_revenue DESC;


-- -----------------------------------------------------------------------------
-- QUERY 6: Regional Performance & Store Ranking (Dense Rank within Region)
-- -----------------------------------------------------------------------------
WITH store_performance AS (
    SELECT
        s.region,
        s.store_name,
        s.store_type,
        s.channel_group,
        COUNT(DISTINCT f.order_id) AS total_orders,
        ROUND(SUM(f.net_sales_amount), 2) AS store_revenue,
        ROUND(SUM(f.gross_profit_amount), 2) AS store_profit
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_store s ON f.store_key = s.store_key
    GROUP BY s.region, s.store_name, s.store_type, s.channel_group
)
SELECT
    region,
    store_name,
    store_type,
    channel_group,
    total_orders,
    store_revenue,
    store_profit,
    DENSE_RANK() OVER (PARTITION BY region ORDER BY store_revenue DESC) AS rank_in_region
FROM store_performance
ORDER BY region, rank_in_region;


-- -----------------------------------------------------------------------------
-- QUERY 7: Omnichannel Comparison (Physical Retail vs Digital Channel)
-- -----------------------------------------------------------------------------
SELECT
    s.channel_group,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_shoppers,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.net_sales_amount), 2) AS net_revenue,
    ROUND(SUM(f.gross_profit_amount), 2) AS gross_profit,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS average_order_value,
    ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS profit_margin_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_store s ON f.store_key = s.store_key
GROUP BY s.channel_group;


-- -----------------------------------------------------------------------------
-- QUERY 8: Top 10 High-Value Customers (Customer Lifetime Value - CLV)
-- -----------------------------------------------------------------------------
SELECT
    c.customer_id,
    c.full_name,
    c.segment,
    c.city,
    c.state,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_items_bought,
    ROUND(SUM(f.net_sales_amount), 2) AS customer_lifetime_value,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_spend_per_order
FROM warehouse.fact_sales f
JOIN warehouse.dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.full_name, c.segment, c.city, c.state
ORDER BY customer_lifetime_value DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- QUERY 9: Customer Segment Contribution & Behavioral Profile
-- -----------------------------------------------------------------------------
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_key) AS total_customers_in_segment,
    COUNT(DISTINCT f.order_id) AS total_orders_placed,
    ROUND(SUM(f.net_sales_amount), 2) AS total_segment_revenue,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT c.customer_key), 0), 2) AS revenue_per_customer,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS segment_aov
FROM warehouse.dim_customer c
LEFT JOIN warehouse.fact_sales f ON c.customer_key = f.customer_key
GROUP BY c.segment
ORDER BY total_segment_revenue DESC;


-- -----------------------------------------------------------------------------
-- QUERY 10: RFM Customer Distribution Analysis (Recency, Frequency, Monetary)
-- -----------------------------------------------------------------------------
SELECT
    rfm_customer_tier,
    COUNT(*) AS customer_count,
    ROUND(SUM(monetary_spend), 2) AS total_tier_spend,
    ROUND(AVG(monetary_spend), 2) AS avg_tier_spend,
    ROUND(AVG(frequency_orders), 1) AS avg_tier_order_frequency,
    ROUND(AVG(recency_days), 1) AS avg_tier_recency_days
FROM warehouse.mart_customer_rfm
GROUP BY rfm_customer_tier
ORDER BY total_tier_spend DESC;


-- -----------------------------------------------------------------------------
-- QUERY 11: Weekend vs Weekday Shopping Patterns
-- -----------------------------------------------------------------------------
SELECT
    CASE WHEN d.is_weekend THEN 'Weekend (Sat-Sun)' ELSE 'Weekday (Mon-Fri)' END AS day_type,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.net_sales_amount), 2) AS total_revenue,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS aov
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
GROUP BY d.is_weekend;


-- -----------------------------------------------------------------------------
-- QUERY 12: Day of Week Performance Breakdown
-- -----------------------------------------------------------------------------
SELECT
    d.day_of_week,
    d.day_name,
    COUNT(DISTINCT f.order_id) AS order_volume,
    ROUND(SUM(f.net_sales_amount), 2) AS total_revenue,
    ROUND(AVG(f.net_sales_amount), 2) AS avg_item_sale_val
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
GROUP BY d.day_of_week, d.day_name
ORDER BY d.day_of_week;


-- -----------------------------------------------------------------------------
-- QUERY 13: Payment Method Volume & Gateway Failure / Success Rates
-- -----------------------------------------------------------------------------
SELECT
    payment_method,
    COUNT(*) AS total_transactions,
    COUNT(CASE WHEN is_successful THEN 1 END) AS successful_transactions,
    COUNT(CASE WHEN payment_status = 'Failed' THEN 1 END) AS failed_transactions,
    COUNT(CASE WHEN payment_status = 'Refunded' THEN 1 END) AS refunded_transactions,
    ROUND(SUM(payment_amount), 2) AS total_payment_volume,
    ROUND((COUNT(CASE WHEN is_successful THEN 1 END) * 100.0) / COUNT(*), 2) AS success_rate_pct
FROM warehouse.fact_payments
GROUP BY payment_method
ORDER BY total_payment_volume DESC;


-- -----------------------------------------------------------------------------
-- QUERY 14: Discount Sensitivity Analysis (Price Realization by Discount Level)
-- -----------------------------------------------------------------------------
SELECT
    CASE 
        WHEN discount_amount = 0 THEN '0% Full Price'
        WHEN (discount_amount / gross_sales_amount) <= 0.05 THEN '1% - 5% Discount'
        WHEN (discount_amount / gross_sales_amount) <= 0.10 THEN '6% - 10% Discount'
        WHEN (discount_amount / gross_sales_amount) <= 0.15 THEN '11% - 15% Discount'
        ELSE '16%+ High Promo'
    END AS discount_bracket,
    COUNT(*) AS transaction_lines,
    SUM(quantity) AS units_sold,
    ROUND(SUM(gross_sales_amount), 2) AS gross_sales,
    ROUND(SUM(discount_amount), 2) AS discounts_given,
    ROUND(SUM(net_sales_amount), 2) AS net_sales,
    ROUND((SUM(gross_profit_amount) / NULLIF(SUM(net_sales_amount), 0)) * 100.0, 2) AS realized_margin_pct
FROM warehouse.fact_sales
GROUP BY 1
ORDER BY net_sales DESC;


-- -----------------------------------------------------------------------------
-- QUERY 15: Moving 3-Month Rolling Average Revenue
-- -----------------------------------------------------------------------------
WITH monthly_data AS (
    SELECT
        d.year_month,
        ROUND(SUM(f.net_sales_amount), 2) AS monthly_revenue
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    GROUP BY d.year_month
)
SELECT
    year_month,
    monthly_revenue,
    ROUND(
        AVG(monthly_revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    ) AS rolling_3_month_avg_revenue
FROM monthly_data
ORDER BY year_month;


-- -----------------------------------------------------------------------------
-- QUERY 16: Customer Cohort Retention (Registration Year vs Purchasing Activity)
-- -----------------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM c.registration_date) AS cohort_year,
    d.year_number AS purchase_year,
    COUNT(DISTINCT c.customer_key) AS active_cohort_customers,
    ROUND(SUM(f.net_sales_amount), 2) AS cohort_revenue,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT c.customer_key), 0), 2) AS revenue_per_active_user
FROM warehouse.fact_sales f
JOIN warehouse.dim_customer c ON f.customer_key = c.customer_key
JOIN warehouse.dim_date d ON f.date_key = d.date_key
GROUP BY cohort_year, purchase_year
ORDER BY cohort_year, purchase_year;


-- -----------------------------------------------------------------------------
-- QUERY 17: Product Price Tier Revenue & Unit Volume Breakdown
-- -----------------------------------------------------------------------------
SELECT
    p.price_tier,
    COUNT(DISTINCT p.product_key) AS catalog_product_count,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.net_sales_amount), 2) AS total_revenue,
    ROUND(SUM(f.gross_profit_amount), 2) AS gross_profit,
    ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS avg_margin_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_product p ON f.product_key = p.product_key
GROUP BY p.price_tier
ORDER BY total_revenue DESC;


-- -----------------------------------------------------------------------------
-- QUERY 18: Store Revenue Density per Square Foot
-- -----------------------------------------------------------------------------
SELECT
    s.store_name,
    s.region,
    s.store_type,
    s.square_feet,
    ROUND(SUM(f.net_sales_amount), 2) AS total_revenue,
    ROUND(SUM(f.net_sales_amount) / NULLIF(s.square_feet, 0), 2) AS revenue_per_sqft
FROM warehouse.fact_sales f
JOIN warehouse.dim_store s ON f.store_key = s.store_key
WHERE s.channel_group = 'Physical Retail' AND s.square_feet > 0
GROUP BY s.store_name, s.region, s.store_type, s.square_feet
ORDER BY revenue_per_sqft DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- QUERY 19: High-Volume Basket Cross-Sell (Units per Transaction Distribution)
-- -----------------------------------------------------------------------------
WITH order_item_counts AS (
    SELECT
        order_id,
        COUNT(order_item_id) AS items_in_basket,
        SUM(quantity) AS units_in_basket,
        SUM(net_sales_amount) AS total_order_amount
    FROM warehouse.fact_sales
    GROUP BY order_id
)
SELECT
    items_in_basket,
    COUNT(*) AS total_orders,
    ROUND(AVG(total_order_amount), 2) AS avg_basket_spend
FROM order_item_counts
GROUP BY items_in_basket
ORDER BY items_in_basket;


-- -----------------------------------------------------------------------------
-- QUERY 20: Reorder Alert & Inventory Safety Monitoring
-- -----------------------------------------------------------------------------
SELECT
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    p.reorder_level,
    COALESCE(SUM(f.quantity), 0) AS total_units_sold_all_time,
    ROUND(AVG(f.quantity), 2) AS avg_units_per_order
FROM warehouse.dim_product p
LEFT JOIN warehouse.fact_sales f ON p.product_key = f.product_key
WHERE p.is_discontinued = FALSE
GROUP BY p.product_id, p.sku, p.product_name, p.category, p.reorder_level
ORDER BY total_units_sold_all_time DESC
LIMIT 15;
