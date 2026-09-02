WITH source AS (
    SELECT * FROM staging.stg_stores
)
SELECT
    CAST(store_id AS BIGINT) AS store_id,
    TRIM(store_name) AS store_name,
    TRIM(store_type) AS store_type,
    CASE WHEN TRIM(store_type) = 'Online Store' THEN 'Digital Channel' ELSE 'Physical Retail' END AS channel_group,
    TRIM(region) AS region,
    TRIM(city) AS city,
    TRIM(state) AS state,
    CAST(COALESCE(square_feet, '0') AS INTEGER) AS square_feet,
    CAST(opened_date AS DATE) AS opened_date,
    EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM CAST(opened_date AS DATE)) AS store_age_years,
    TRIM(manager_name) AS manager_name,
    _ingested_at,
    _source_file
FROM source
WHERE store_id IS NOT NULL
