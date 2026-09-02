import sys
from pathlib import Path
import duckdb
import pandas as pd
from rich.console import Console

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.config import DUCKDB_PATH, SQL_DIR
from src.transformation.date_dimension_generator import generate_date_dimension_df

console = Console(soft_wrap=True)


def transform_and_build_warehouse(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Execute dimensional warehouse transformation logic."""
    console.print("[bold green][*] Transforming Staging Data into Dimensional Star Schema...[/bold green]")
    
    con.execute("CREATE SCHEMA IF NOT EXISTS warehouse;")
    
    # 1. Populate Date Dimension
    console.print("  [cyan]➜ Populating dim_date...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.dim_date;")
    df_date = generate_date_dimension_df()
    con.register("df_date_temp", df_date)
    con.execute("CREATE TABLE warehouse.dim_date AS SELECT * FROM df_date_temp;")
    con.unregister("df_date_temp")
    dim_date_count = con.execute("SELECT COUNT(*) FROM warehouse.dim_date").fetchone()[0]
    
    # 2. Populate Customer Dimension (Cleansed & Deduped)
    console.print("  [cyan]➜ Populating dim_customer...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.dim_customer;")
    con.execute("""
        CREATE TABLE warehouse.dim_customer AS
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
    """)
    dim_cust_count = con.execute("SELECT COUNT(*) FROM warehouse.dim_customer").fetchone()[0]

    # 3. Populate Product Dimension (Profit Margin & Price Tiers)
    console.print("  [cyan]➜ Populating dim_product...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.dim_product;")
    con.execute("""
        CREATE TABLE warehouse.dim_product AS
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
          AND TRY_CAST(unit_price AS DECIMAL(12, 2)) > 0;
    """)
    dim_prod_count = con.execute("SELECT COUNT(*) FROM warehouse.dim_product").fetchone()[0]

    # 4. Populate Store Dimension (Channel Grouping & Lifespan)
    console.print("  [cyan]➜ Populating dim_store...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.dim_store;")
    con.execute("""
        CREATE TABLE warehouse.dim_store AS
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
    """)
    dim_store_count = con.execute("SELECT COUNT(*) FROM warehouse.dim_store").fetchone()[0]

    # 5. Populate Fact Sales (Grain: Order Item Line)
    console.print("  [cyan]➜ Populating fact_sales...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.fact_sales;")
    con.execute("""
        CREATE TABLE warehouse.fact_sales AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY CAST(o.order_id AS BIGINT), CAST(oi.order_item_id AS BIGINT)) AS sales_key,
            CAST(o.order_id AS BIGINT) AS order_id,
            CAST(oi.order_item_id AS BIGINT) AS order_item_id,
            dc.customer_key,
            dp.product_key,
            ds.store_key,
            CAST(strftime(TRY_CAST(o.order_date AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
            TRY_CAST(o.order_date AS DATE) AS order_date,
            TRIM(o.order_status) AS order_status,
            CAST(oi.quantity AS INTEGER) AS quantity,
            CAST(oi.unit_price AS DECIMAL(12, 2)) AS unit_price,
            dp.unit_cost,
            CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2)) AS gross_sales_amount,
            CAST(oi.discount AS DECIMAL(14, 2)) AS discount_amount,
            (CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2)) AS net_sales_amount,
            CAST(oi.quantity AS INTEGER) * dp.unit_cost AS cost_amount,
            ((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2))) - (CAST(oi.quantity AS INTEGER) * dp.unit_cost) AS gross_profit_amount,
            ROUND(
                CASE 
                    WHEN ((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2))) > 0
                    THEN (
                        (((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2))) - (CAST(oi.quantity AS INTEGER) * dp.unit_cost)) /
                        ((CAST(oi.quantity AS INTEGER) * CAST(oi.unit_price AS DECIMAL(12, 2))) - CAST(oi.discount AS DECIMAL(14, 2)))
                    ) * 100.0
                    ELSE 0.0
                END, 2
            ) AS profit_margin_pct,
            CURRENT_TIMESTAMP AS _loaded_at
        FROM staging.stg_order_items oi
        INNER JOIN staging.stg_orders o 
            ON oi.order_id = o.order_id
        INNER JOIN warehouse.dim_customer dc 
            ON CAST(o.customer_id AS BIGINT) = dc.customer_id
        INNER JOIN warehouse.dim_product dp 
            ON CAST(oi.product_id AS BIGINT) = dp.product_id
        INNER JOIN warehouse.dim_store ds 
            ON CAST(o.store_id AS BIGINT) = ds.store_id
        WHERE TRY_CAST(oi.quantity AS INTEGER) > 0
          AND TRY_CAST(oi.unit_price AS DECIMAL(12, 2)) > 0
          AND TRY_CAST(o.order_date AS DATE) <= CURRENT_DATE;
    """)
    fact_sales_count = con.execute("SELECT COUNT(*) FROM warehouse.fact_sales").fetchone()[0]

    # 6. Populate Fact Payments
    console.print("  [cyan]➜ Populating fact_payments...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.fact_payments;")
    con.execute("""
        CREATE TABLE warehouse.fact_payments AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY CAST(p.payment_id AS BIGINT)) AS payment_key,
            CAST(p.payment_id AS BIGINT) AS payment_id,
            CAST(p.order_id AS BIGINT) AS order_id,
            COALESCE(dc.customer_key, 0) AS customer_key,
            CAST(strftime(TRY_CAST(p.payment_date AS TIMESTAMP), '%Y%m%d') AS INTEGER) AS date_key,
            TRIM(p.payment_method) AS payment_method,
            TRIM(p.payment_status) AS payment_status,
            CAST(p.payment_amount AS DECIMAL(14, 2)) AS payment_amount,
            TRY_CAST(p.payment_date AS TIMESTAMP) AS payment_timestamp,
            TRIM(p.transaction_ref) AS transaction_ref,
            CASE WHEN TRIM(p.payment_status) = 'Success' THEN TRUE ELSE FALSE END AS is_successful,
            CURRENT_TIMESTAMP AS _loaded_at
        FROM staging.stg_payments p
        LEFT JOIN staging.stg_orders o 
            ON p.order_id = o.order_id
        LEFT JOIN warehouse.dim_customer dc 
            ON CAST(o.customer_id AS BIGINT) = dc.customer_id
        WHERE p.payment_id IS NOT NULL;
    """)
    fact_pay_count = con.execute("SELECT COUNT(*) FROM warehouse.fact_payments").fetchone()[0]

    # 7. Populate Analytical Mart: Monthly Store Performance
    console.print("  [cyan]➜ Populating mart_monthly_store_performance...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.mart_monthly_store_performance;")
    con.execute("""
        CREATE TABLE warehouse.mart_monthly_store_performance AS
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
        FROM warehouse.fact_sales f
        JOIN warehouse.dim_date d ON f.date_key = d.date_key
        JOIN warehouse.dim_store ds ON f.store_key = ds.store_key
        GROUP BY d.year_month, d.year_number, d.month_number, ds.store_key, ds.store_name, ds.region, ds.channel_group;
    """)

    # 8. Populate Analytical Mart: Customer RFM Segmentation
    console.print("  [cyan]➜ Populating mart_customer_rfm...[/cyan]")
    con.execute("DROP TABLE IF EXISTS warehouse.mart_customer_rfm;")
    con.execute("""
        CREATE TABLE warehouse.mart_customer_rfm AS
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
            FROM warehouse.dim_customer dc
            INNER JOIN warehouse.fact_sales f ON dc.customer_key = f.customer_key
            GROUP BY dc.customer_key, dc.customer_id, dc.full_name, dc.segment, dc.city
        ),
        rfm_scores AS (
            SELECT
                *,
                NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,   -- Lower recency days = higher score
                NTILE(5) OVER (ORDER BY frequency_orders ASC) AS f_score, -- Higher frequency = higher score
                NTILE(5) OVER (ORDER BY monetary_spend ASC) AS m_score    -- Higher spend = higher score
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
        FROM rfm_scores;
    """)
    
    counts = {
        "dim_date": dim_date_count,
        "dim_customer": dim_cust_count,
        "dim_product": dim_prod_count,
        "dim_store": dim_store_count,
        "fact_sales": fact_sales_count,
        "fact_payments": fact_pay_count,
    }
    
    console.print(f"[bold green]✔ Star Schema dimensional model successfully loaded into DuckDB![/bold green]")
    for table, count in counts.items():
        console.print(f"  [bold white]{table:<15}[/bold white]: [green]{count:,} rows[/green]")
        
    return counts


if __name__ == "__main__":
    con = duckdb.connect(str(DUCKDB_PATH))
    transform_and_build_warehouse(con)
    con.close()
