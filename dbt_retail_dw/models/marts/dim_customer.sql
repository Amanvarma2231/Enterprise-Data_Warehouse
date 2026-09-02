{{ config(materialized='table') }}

WITH base_customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    first_name,
    last_name,
    full_name,
    email,
    phone,
    city,
    state,
    country,
    postal_code,
    segment,
    registration_date,
    is_active,
    CURRENT_DATE AS row_effective_date,
    CAST('9999-12-31' AS DATE) AS row_expiration_date,
    TRUE AS is_current,
    CURRENT_TIMESTAMP AS _loaded_at
FROM base_customers
