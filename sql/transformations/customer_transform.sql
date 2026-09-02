-- =============================================================================
-- SQL Transformation: Staging Customers -> Conformed dim_customer
-- Deduplicates, standardizes contact details, and assigns surrogate keys
-- =============================================================================

INSERT INTO warehouse.dim_customer (
    customer_key,
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
    row_effective_date,
    row_expiration_date,
    is_current,
    _loaded_at
)
SELECT
    ROW_NUMBER() OVER (ORDER BY CAST(customer_id AS BIGINT)) AS customer_key,
    CAST(customer_id AS BIGINT) AS customer_id,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    TRIM(first_name) || ' ' || TRIM(last_name) AS full_name,
    LOWER(TRIM(email)) AS email,
    TRIM(phone) AS phone,
    TRIM(city) AS city,
    TRIM(state) AS state,
    COALESCE(TRIM(country), 'India') AS country,
    TRIM(postal_code) AS postal_code,
    COALESCE(TRIM(segment), 'Regular') AS segment,
    CAST(registration_date AS DATE) AS registration_date,
    CASE WHEN LOWER(TRIM(is_active)) IN ('true', '1', 't') THEN TRUE ELSE FALSE END AS is_active,
    CURRENT_DATE AS row_effective_date,
    CAST('9999-12-31' AS DATE) AS row_expiration_date,
    TRUE AS is_current,
    CURRENT_TIMESTAMP AS _loaded_at
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY registration_date DESC) as rn
    FROM staging.stg_customers
    WHERE customer_id IS NOT NULL 
      AND TRIM(customer_id) != ''
      AND email LIKE '%@%.%'
) deduped
WHERE rn = 1;
