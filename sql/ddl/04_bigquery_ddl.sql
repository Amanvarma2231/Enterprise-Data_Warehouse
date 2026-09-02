-- =============================================================================
-- Enterprise Sales & Customer Data Warehouse (RetailSphere)
-- Layer: Cloud Data Warehouse (Google Cloud BigQuery DDL)
-- Features: Partitioning, Clustering, Column Descriptions & Governance Metadata
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS `retailsphere_dw`
OPTIONS(
  location="us-central1",
  description="RetailSphere Governed Enterprise Analytics & Data Warehouse"
);

-- =============================================================================
-- 1. CLOUD DIMENSION TABLES
-- =============================================================================

CREATE OR REPLACE TABLE `retailsphere_dw.dim_date` (
    date_key            INT64 OPTIONS(description="Surrogate integer date key YYYYMMDD"),
    full_date           DATE OPTIONS(description="Standard ISO calendar date"),
    day_of_month        INT64 OPTIONS(description="Day number within month 1-31"),
    month_number        INT64 OPTIONS(description="Month number 1-12"),
    month_name          STRING OPTIONS(description="Full English month name"),
    month_short_name    STRING OPTIONS(description="3-letter month abbreviation"),
    quarter_number      INT64 OPTIONS(description="Calendar quarter 1-4"),
    quarter_name        STRING OPTIONS(description="Formatted quarter string Q1-Q4"),
    year_number         INT64 OPTIONS(description="4-digit calendar year"),
    year_month          STRING OPTIONS(description="Standard YYYY-MM period"),
    day_of_week         INT64 OPTIONS(description="ISO day of week: 1=Mon, 7=Sun"),
    day_name            STRING OPTIONS(description="Full day name"),
    week_of_year        INT64 OPTIONS(description="ISO calendar week number"),
    is_weekend          BOOL OPTIONS(description="True if Saturday or Sunday"),
    is_holiday          BOOL OPTIONS(description="True if standard public holiday"),
    fiscal_year         INT64 OPTIONS(description="Retail corporate fiscal year"),
    fiscal_quarter      STRING OPTIONS(description="Retail corporate fiscal quarter")
)
OPTIONS(
  description="Conformed Date Dimension table for calendar alignment across facts"
);

CREATE OR REPLACE TABLE `retailsphere_dw.dim_customer` (
    customer_key        INT64 OPTIONS(description="Surrogate customer key generated in warehouse"),
    customer_id         INT64 OPTIONS(description="Source system natural customer ID"),
    first_name          STRING OPTIONS(description="Customer given name"),
    last_name           STRING OPTIONS(description="Customer family name"),
    full_name           STRING OPTIONS(description="Concatenated full customer name"),
    email               STRING OPTIONS(description="Primary contact email [CONFIDENTIAL PII]"),
    phone               STRING OPTIONS(description="Primary contact telephone [CONFIDENTIAL PII]"),
    city                STRING OPTIONS(description="Customer billing city"),
    state               STRING OPTIONS(description="Customer billing state / province"),
    country             STRING OPTIONS(description="Customer country code/name"),
    postal_code         STRING OPTIONS(description="Postal / Zip code"),
    segment             STRING OPTIONS(description="Behavioral loyalty tier: Regular, Premium, VIP, Corporate"),
    registration_date   DATE OPTIONS(description="Initial profile onboarding date"),
    is_active           BOOL OPTIONS(description="Active customer status flag"),
    row_effective_date  DATE OPTIONS(description="SCD Type 2 record activation date"),
    row_expiration_date DATE OPTIONS(description="SCD Type 2 record expiry date"),
    is_current          BOOL OPTIONS(description="SCD Type 2 current record indicator"),
    _loaded_at          TIMESTAMP OPTIONS(description="ETL load timestamp")
)
CLUSTER BY customer_id, segment
OPTIONS(
  description="Customer master dimension with historical SCD audit metadata"
);

CREATE OR REPLACE TABLE `retailsphere_dw.dim_product` (
    product_key         INT64 OPTIONS(description="Surrogate product key"),
    product_id          INT64 OPTIONS(description="Source system natural product ID"),
    sku                 STRING OPTIONS(description="Stock Keeping Unit standard code"),
    product_name        STRING OPTIONS(description="Official catalog product title"),
    category            STRING OPTIONS(description="Top-level merchandising department"),
    subcategory         STRING OPTIONS(description="Detailed item subcategory"),
    unit_cost           NUMERIC OPTIONS(description="Standard product acquisition cost (INR)"),
    unit_price          NUMERIC OPTIONS(description="Standard retail catalog price (INR)"),
    profit_margin_pct   NUMERIC OPTIONS(description="Base profit margin percentage"),
    price_tier          STRING OPTIONS(description="Tier classification: Budget, Mid-Range, Premium, Luxury"),
    reorder_level       INT64 OPTIONS(description="Inventory safety reorder threshold"),
    is_discontinued     BOOL OPTIONS(description="Discontinued inventory lifecycle flag"),
    _loaded_at          TIMESTAMP OPTIONS(description="ETL load timestamp")
)
CLUSTER BY category, subcategory
OPTIONS(
  description="Product dimension catalog with pricing tiers and hierarchy"
);

CREATE OR REPLACE TABLE `retailsphere_dw.dim_store` (
    store_key           INT64 OPTIONS(description="Surrogate store key"),
    store_id            INT64 OPTIONS(description="Source system natural store identifier"),
    store_name          STRING OPTIONS(description="Retail branch trading name"),
    store_type          STRING OPTIONS(description="Store format: Flagship, Standard, Outlet, Online"),
    channel_group       STRING OPTIONS(description="Omnichannel grouping: Physical vs Digital"),
    region              STRING OPTIONS(description="Geographical retail sales territory"),
    city                STRING OPTIONS(description="Store municipal location"),
    state               STRING OPTIONS(description="Store state"),
    square_feet         INT64 OPTIONS(description="Retail floor space in square feet"),
    opened_date         DATE OPTIONS(description="Official store launch date"),
    store_age_years     INT64 OPTIONS(description="Store operating lifespan in years"),
    manager_name        STRING OPTIONS(description="Store general manager"),
    _loaded_at          TIMESTAMP OPTIONS(description="ETL load timestamp")
)
CLUSTER BY region, channel_group
OPTIONS(
  description="Store and channel dimension for retail location analytics"
);

-- =============================================================================
-- 2. CLOUD FACT TABLES (Partitioned & Clustered)
-- =============================================================================

CREATE OR REPLACE TABLE `retailsphere_dw.fact_sales` (
    sales_key           INT64 OPTIONS(description="Surrogate sales transaction line key"),
    order_id            INT64 OPTIONS(description="Degenerate order identifier"),
    order_item_id       INT64 OPTIONS(description="Degenerate order line item identifier"),
    customer_key        INT64 OPTIONS(description="Foreign key to dim_customer"),
    product_key         INT64 OPTIONS(description="Foreign key to dim_product"),
    store_key           INT64 OPTIONS(description="Foreign key to dim_store"),
    date_key            INT64 OPTIONS(description="Foreign key to dim_date YYYYMMDD"),
    order_date          DATE OPTIONS(description="Order placement date [Partition Key]"),
    order_status        STRING OPTIONS(description="Fulfillment status"),
    quantity            INT64 OPTIONS(description="Units ordered"),
    unit_price          NUMERIC OPTIONS(description="Unit retail price at time of sale"),
    unit_cost           NUMERIC OPTIONS(description="Unit cost at time of sale"),
    gross_sales_amount  NUMERIC OPTIONS(description="Gross revenue = quantity * unit_price"),
    discount_amount     NUMERIC OPTIONS(description="Promotional discount deduction"),
    net_sales_amount    NUMERIC OPTIONS(description="Net revenue = gross - discount"),
    cost_amount         NUMERIC OPTIONS(description="Cost of Goods Sold = quantity * unit_cost"),
    gross_profit_amount NUMERIC OPTIONS(description="Gross profit = net_sales - cost_amount"),
    profit_margin_pct   NUMERIC OPTIONS(description="Gross profit percentage on sale"),
    _loaded_at          TIMESTAMP OPTIONS(description="Warehouse loading timestamp")
)
PARTITION BY order_date
CLUSTER BY customer_key, product_key, store_key
OPTIONS(
  description="Partitioned and clustered sales fact table for enterprise analytical queries"
);

CREATE OR REPLACE TABLE `retailsphere_dw.fact_payments` (
    payment_key         INT64 OPTIONS(description="Surrogate payment key"),
    payment_id          INT64 OPTIONS(description="Source system payment ID"),
    order_id            INT64 OPTIONS(description="Related order identifier"),
    customer_key        INT64 OPTIONS(description="Foreign key to dim_customer"),
    date_key            INT64 OPTIONS(description="Foreign key to dim_date"),
    payment_method      STRING OPTIONS(description="Tender type: UPI, Credit Card, NetBanking, etc."),
    payment_status      STRING OPTIONS(description="Settlement status: Success, Failed, Refunded, Pending"),
    payment_amount      NUMERIC OPTIONS(description="Settled payment transaction amount"),
    payment_timestamp   TIMESTAMP OPTIONS(description="Payment gateway timestamp [Partition Key]"),
    transaction_ref     STRING OPTIONS(description="External banking reference hash"),
    is_successful       BOOL OPTIONS(description="Binary flag for successful transactions"),
    _loaded_at          TIMESTAMP OPTIONS(description="Warehouse loading timestamp")
)
PARTITION BY DATE(payment_timestamp)
CLUSTER BY payment_method, payment_status
OPTIONS(
  description="Partitioned payment ledger fact table for financial reconciliation"
);
