{{ config(materialized='table') }}

WITH base_stores AS (
    SELECT * FROM {{ ref('stg_stores') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY store_id) AS store_key,
    store_id,
    store_name,
    store_type,
    channel_group,
    region,
    city,
    state,
    square_feet,
    opened_date,
    store_age_years,
    manager_name,
    CURRENT_TIMESTAMP AS _loaded_at
FROM base_stores
