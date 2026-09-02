-- =============================================================================
-- SQL Transformation: Staging Order Items -> Atomic fact_sales
-- Calculates financial metrics: Gross Sales, Net Sales, COGS, Profit & Margin %
-- =============================================================================

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
    discount_amount,
    gross_sales_amount,
    net_sales_amount,
    cost_amount,
    gross_profit_amount,
    profit_margin_pct,
    _loaded_at
)
SELECT
    ROW_NUMBER() OVER (ORDER BY CAST(o.order_id AS BIGINT), CAST(oi.order_item_id AS BIGINT)) AS sales_key,
    CAST(o.order_id AS BIGINT) AS order_id,
    CAST(oi.order_item_id AS BIGINT) AS order_item_id,
    dc.customer_key,
    dp.product_key,
    ds.store_key,
    dd.date_key,
    CAST(o.order_date AS DATE) AS order_date,
    TRIM(o.order_status) AS order_status,
    CAST(oi.quantity AS INTEGER) AS quantity,
    CAST(oi.unit_price AS DECIMAL(12, 2)) AS unit_price,
    dp.unit_cost,
    CAST(COALESCE(oi.discount_amount, '0.00') AS DECIMAL(12, 2)) AS discount_amount,
    CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2)) AS gross_sales_amount,
    (CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(COALESCE(oi.discount_amount, '0.00') AS DECIMAL(12, 2)) AS net_sales_amount,
    CAST(oi.quantity AS INTEGER) * dp.unit_cost AS cost_amount,
    ((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(COALESCE(oi.discount_amount, '0.00') AS DECIMAL(12, 2))) - (CAST(oi.quantity AS INTEGER) * dp.unit_cost) AS gross_profit_amount,
    ROUND(((((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(COALESCE(oi.discount_amount, '0.00') AS DECIMAL(12, 2))) - (CAST(oi.quantity AS INTEGER) * dp.unit_cost)) / NULLIF(((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(COALESCE(oi.discount_amount, '0.00') AS DECIMAL(12, 2))), 0)) * 100.0, 2) AS profit_margin_pct,
    CURRENT_TIMESTAMP AS _loaded_at
FROM staging.stg_order_items oi
JOIN staging.stg_orders o ON oi.order_id = o.order_id
JOIN warehouse.dim_customer dc ON CAST(o.customer_id AS BIGINT) = dc.customer_id
JOIN warehouse.dim_product dp ON CAST(oi.product_id AS BIGINT) = dp.product_id
JOIN warehouse.dim_store ds ON CAST(o.store_id AS BIGINT) = ds.store_id
JOIN warehouse.dim_date dd ON CAST(o.order_date AS DATE) = dd.full_date
WHERE TRY_CAST(oi.quantity AS INTEGER) > 0;
