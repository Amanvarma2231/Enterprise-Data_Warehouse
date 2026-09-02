{{ config(materialized='table') }}

WITH customer_stats AS (
    SELECT
        dc.customer_key,
        dc.customer_id,
        dc.full_name,
        dc.segment,
        dc.city,
        MIN(f.order_date) AS first_order_date,
        MAX(f.order_date) AS last_order_date,
        DATEDIFF('day', MAX(f.order_date), CURRENT_DATE) AS recency_days,
        COUNT(DISTINCT f.order_id) AS frequency_orders,
        SUM(f.net_sales_amount) AS monetary_spend,
        ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_basket_value
    FROM {{ ref('dim_customer') }} dc
    INNER JOIN {{ ref('fact_sales') }} f ON dc.customer_key = f.customer_key
    GROUP BY dc.customer_key, dc.customer_id, dc.full_name, dc.segment, dc.city
),
rfm_scores AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_spend ASC) AS m_score
    FROM customer_stats
)
SELECT
    customer_key,
    customer_id,
    full_name,
    segment,
    city,
    first_order_date,
    last_order_date,
    recency_days,
    frequency_orders,
    monetary_spend,
    avg_basket_value,
    r_score,
    f_score,
    m_score,
    CAST(r_score AS VARCHAR) || CAST(f_score AS VARCHAR) || CAST(m_score AS VARCHAR) AS rfm_cell,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 4 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score >= 2 AND m_score >= 2 THEN 'Potential Loyalists'
        WHEN r_score >= 4 AND f_score = 1 THEN 'Recent New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Churning'
        WHEN r_score <= 1 AND f_score <= 2 THEN 'Lost Customers'
        ELSE 'Standard Customers'
    END AS rfm_customer_tier
FROM rfm_scores
