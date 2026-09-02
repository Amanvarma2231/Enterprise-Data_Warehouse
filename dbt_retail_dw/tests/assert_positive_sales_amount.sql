-- Custom Singular Test: Ensure no negative or zero net sales amounts in fact table
SELECT
    sales_key,
    net_sales_amount
FROM {{ ref('fact_sales') }}
WHERE net_sales_amount <= 0
