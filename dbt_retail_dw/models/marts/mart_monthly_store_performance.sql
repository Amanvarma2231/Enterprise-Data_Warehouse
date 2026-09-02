{{ config(materialized='table') }}

WITH sales AS (
    SELECT * FROM {{ ref('fact_sales') }}
),
dates AS (
    SELECT * FROM {{ ref('dim_date') }}
),
stores AS (
    SELECT * FROM {{ ref('dim_store') }}
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
FROM sales f
JOIN dates d ON f.date_key = d.date_key
JOIN stores ds ON f.store_key = ds.store_key
GROUP BY d.year_month, d.year_number, d.month_number, ds.store_key, ds.store_name, ds.region, ds.channel_group
