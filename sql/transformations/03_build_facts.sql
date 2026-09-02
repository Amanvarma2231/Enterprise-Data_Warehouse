-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Transformation: Populate Fact Tables & Aggregated Marts
-- =============================================================================

-- 1. Fact Sales Transformation (Star Schema Key Lookup & Financial Calculation)
INSERT INTO warehouse.fact_sales (
    sales_key,
    order_id,
    order_item_id,
    customer_key,
    product_key,
    store_key,
    date_key,
    order_date,
    order_status,
    quantity,
    unit_price,
    unit_cost,
    gross_sales_amount,
    discount_amount,
    net_sales_amount,
    cost_amount,
    gross_profit_amount,
    profit_margin_pct,
    _loaded_at
)
SELECT
    ROW_NUMBER() OVER (ORDER BY o.order_id, oi.order_item_id) AS sales_key,
    CAST(o.order_id AS BIGINT) AS order_id,
    CAST(oi.order_item_id AS BIGINT) AS order_item_id,
    dc.customer_key,
    dp.product_key,
    ds.store_key,
    CAST(strftime(CAST(o.order_date AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
    CAST(o.order_date AS DATE) AS order_date,
    TRIM(o.order_status) AS order_status,
    CAST(oi.quantity AS INTEGER) AS quantity,
    CAST(oi.unit_price AS DECIMAL(12, 2)) AS unit_price,
    dp.unit_cost,
    CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2)) AS gross_sales_amount,
    CAST(oi.discount AS DECIMAL(14, 2)) AS discount_amount,
    (CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2)) AS net_sales_amount,
    CAST(oi.quantity AS INTEGER) * dp.unit_cost AS cost_amount,
    ((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2))) - (CAST(oi.quantity AS INTEGER) * dp.unit_cost) AS gross_profit_amount,
    ROUND(
        CASE 
            WHEN ((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2))) > 0
            THEN (
                (((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2))) - (CAST(oi.quantity AS INTEGER) * dp.unit_cost)) /
                ((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2)))
            ) * 100.0
            ELSE 0.0
        END, 2
    ) AS profit_margin_pct,
    CURRENT_TIMESTAMP AS _loaded_at
FROM staging.stg_order_items oi
INNER JOIN staging.stg_orders o 
    ON oi.order_id = o.order_id
INNER JOIN warehouse.dim_customer dc 
    ON CAST(o.customer_id AS BIGINT) = dc.customer_id
INNER JOIN warehouse.dim_product dp 
    ON CAST(oi.product_id AS BIGINT) = dp.product_id
INNER JOIN warehouse.dim_store ds 
    ON CAST(o.store_id AS BIGINT) = ds.store_id
WHERE CAST(oi.quantity AS INTEGER) > 0
  AND CAST(oi.unit_price AS DECIMAL(12, 2)) > 0
  AND CAST(o.order_date AS DATE) <= CURRENT_DATE;


-- 2. Fact Payments Transformation
INSERT INTO warehouse.fact_payments (
    payment_key,
    payment_id,
    order_id,
    customer_key,
    date_key,
    payment_method,
    payment_status,
    payment_amount,
    payment_timestamp,
    transaction_ref,
    is_successful,
    _loaded_at
)
SELECT
    ROW_NUMBER() OVER (ORDER BY CAST(p.payment_id AS BIGINT)) AS payment_key,
    CAST(p.payment_id AS BIGINT) AS payment_id,
    CAST(p.order_id AS BIGINT) AS order_id,
    COALESCE(dc.customer_key, -1) AS customer_key,
    CAST(strftime(CAST(p.payment_date AS TIMESTAMP), '%Y%m%d') AS INTEGER) AS date_key,
    TRIM(p.payment_method) AS payment_method,
    TRIM(p.payment_status) AS payment_status,
    CAST(p.payment_amount AS DECIMAL(14, 2)) AS payment_amount,
    CAST(p.payment_date AS TIMESTAMP) AS payment_timestamp,
    TRIM(p.transaction_ref) AS transaction_ref,
    CASE WHEN TRIM(p.payment_status) = 'Success' THEN TRUE ELSE FALSE END AS is_successful,
    CURRENT_TIMESTAMP AS _loaded_at
FROM staging.stg_payments p
LEFT JOIN staging.stg_orders o 
    ON p.order_id = o.order_id
LEFT JOIN warehouse.dim_customer dc 
    ON CAST(o.customer_id AS BIGINT) = dc.customer_id
WHERE p.payment_id IS NOT NULL;


-- 3. Monthly Store Performance Mart Population
INSERT INTO warehouse.mart_monthly_store_performance (
    mart_key,
    year_month,
    year_number,
    month_number,
    store_key,
    store_name,
    region,
    channel_group,
    total_orders,
    total_units_sold,
    gross_revenue,
    total_discounts,
    net_revenue,
    total_profit,
    avg_order_value,
    overall_margin_pct
)
SELECT
    ROW_NUMBER() OVER (ORDER BY d.year_month, ds.store_key) AS mart_key,
    d.year_month,
    d.year_number,
    d.month_number,
    ds.store_key,
    ds.store_name,
    ds.region,
    ds.channel_group,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    SUM(f.gross_sales_amount) AS gross_revenue,
    SUM(f.discount_amount) AS total_discounts,
    SUM(f.net_sales_amount) AS net_revenue,
    SUM(f.gross_profit_amount) AS total_profit,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value,
    ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS overall_margin_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_store ds ON f.store_key = ds.store_key
GROUP BY d.year_month, d.year_number, d.month_number, ds.store_key, ds.store_name, ds.region, ds.channel_group;
