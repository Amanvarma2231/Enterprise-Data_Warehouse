-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Transformation: Populate Dimension Tables with Surrogate Keys & Enrichment
-- =============================================================================

-- 1. Dim Customer Transformation (SCD Type 1 with deduping & cleansing)
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
      AND email LIKE '%@%.%'
) deduped_customers
WHERE rn = 1;


-- 2. Dim Product Transformation (Pricing Tiers & Profit Margin Enrichment)
INSERT INTO warehouse.dim_product (
    product_key,
    product_id,
    sku,
    product_name,
    category,
    subcategory,
    unit_cost,
    unit_price,
    profit_margin_pct,
    price_tier,
    reorder_level,
    is_discontinued,
    _loaded_at
)
SELECT
    ROW_NUMBER() OVER (ORDER BY CAST(product_id AS BIGINT)) AS product_key,
    CAST(product_id AS BIGINT) AS product_id,
    TRIM(sku) AS sku,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    TRIM(subcategory) AS subcategory,
    CAST(unit_cost AS DECIMAL(12, 2)) AS unit_cost,
    CAST(unit_price AS DECIMAL(12, 2)) AS unit_price,
    ROUND(((CAST(unit_price AS DECIMAL(12, 2)) - CAST(unit_cost AS DECIMAL(12, 2))) / CAST(unit_price AS DECIMAL(12, 2))) * 100.0, 2) AS profit_margin_pct,
    CASE 
        WHEN CAST(unit_price AS DECIMAL(12, 2)) < 500 THEN 'Budget'
        WHEN CAST(unit_price AS DECIMAL(12, 2)) BETWEEN 500 AND 3000 THEN 'Mid-Range'
        WHEN CAST(unit_price AS DECIMAL(12, 2)) BETWEEN 3001 AND 15000 THEN 'Premium'
        ELSE 'Luxury'
    END AS price_tier,
    CAST(COALESCE(reorder_level, '10') AS INTEGER) AS reorder_level,
    CASE WHEN LOWER(TRIM(is_discontinued)) IN ('true', '1', 't') THEN TRUE ELSE FALSE END AS is_discontinued,
    CURRENT_TIMESTAMP AS _loaded_at
FROM staging.stg_products
WHERE product_id IS NOT NULL 
  AND CAST(unit_price AS DECIMAL(12, 2)) > 0;


-- 3. Dim Store Transformation (Channel Categorization & Age Enrichment)
INSERT INTO warehouse.dim_store (
    store_key,
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
    _loaded_at
)
SELECT
    ROW_NUMBER() OVER (ORDER BY CAST(store_id AS BIGINT)) AS store_key,
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
    CURRENT_TIMESTAMP AS _loaded_at
FROM staging.stg_stores
WHERE store_id IS NOT NULL;
