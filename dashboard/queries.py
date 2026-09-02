"""
Pre-compiled Analytical SQL Queries for Streamlit BI Dashboard
Optimized for Sub-Second Execution on DuckDB Columnar Vectorized Engine
"""

TOTAL_SALES_KPIS = """
    SELECT
        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.customer_key) AS total_customers,
        SUM(f.quantity) AS total_units,
        SUM(f.net_sales_amount) AS net_revenue,
        SUM(f.gross_profit_amount) AS gross_profit,
        ROUND((SUM(f.gross_profit_amount)/NULLIF(SUM(f.net_sales_amount),0))*100.0, 2) AS margin_pct,
        ROUND(SUM(f.net_sales_amount)/NULLIF(COUNT(DISTINCT f.order_id),0), 2) AS aov
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_store s ON f.store_key = s.store_key
    JOIN warehouse.dim_product p ON f.product_key = p.product_key
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    WHERE {filter_clause};
"""

MONTHLY_TREND = """
    SELECT
        d.year_month,
        SUM(f.net_sales_amount) AS net_revenue,
        SUM(f.gross_profit_amount) AS gross_profit
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_store s ON f.store_key = s.store_key
    JOIN warehouse.dim_product p ON f.product_key = p.product_key
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    WHERE {filter_clause}
    GROUP BY d.year_month
    ORDER BY d.year_month ASC;
"""

REGIONAL_SPLIT = """
    SELECT
        s.region,
        SUM(f.net_sales_amount) AS region_revenue
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_store s ON f.store_key = s.store_key
    JOIN warehouse.dim_product p ON f.product_key = p.product_key
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    WHERE {filter_clause}
    GROUP BY s.region
    ORDER BY region_revenue DESC;
"""

TOP_PRODUCTS_QUERY = """
    SELECT
        p.sku,
        p.product_name,
        p.category,
        p.subcategory,
        SUM(f.quantity) AS units_sold,
        ROUND(SUM(f.net_sales_amount), 2) AS revenue,
        ROUND(SUM(f.gross_profit_amount), 2) AS gross_profit,
        ROUND((SUM(f.gross_profit_amount)/NULLIF(SUM(f.net_sales_amount),0))*100.0, 2) AS realized_margin_pct
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_product p ON f.product_key = p.product_key
    JOIN warehouse.dim_store s ON f.store_key = s.store_key
    WHERE {filter_clause}
    GROUP BY p.sku, p.product_name, p.category, p.subcategory
    ORDER BY revenue DESC
    LIMIT 15;
"""
