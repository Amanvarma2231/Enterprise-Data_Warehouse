WITH source AS (
    SELECT * FROM staging.stg_customers
),
cleansed AS (
    SELECT
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
        _ingested_at,
        _source_file,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY registration_date DESC) as row_num
    FROM source
    WHERE customer_id IS NOT NULL 
      AND email LIKE '%@%.%'
)
SELECT
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
    _ingested_at,
    _source_file
FROM cleansed
WHERE row_num = 1
