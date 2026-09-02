-- =============================================================================
-- Analytics Query 1: Executive Revenue & Margin Analysis
-- Monthly MoM Revenue Growth, Gross Profit, and Realized Margin %
-- =============================================================================

SELECT
    d.calendar_year,
    d.year_month,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.gross_sales_amount), 2) AS gross_sales_inr,
    ROUND(SUM(f.discount_amount), 2) AS total_discounts_inr,
    ROUND(SUM(f.net_sales_amount), 2) AS net_revenue_inr,
    ROUND(SUM(f.gross_profit_amount), 2) AS gross_profit_inr,
    ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS realized_margin_pct,
    ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS average_order_value_inr,
    LAG(SUM(f.net_sales_amount)) OVER (ORDER BY d.year_month) AS prev_month_revenue,
    ROUND(((SUM(f.net_sales_amount) - LAG(SUM(f.net_sales_amount)) OVER (ORDER BY d.year_month)) / 
           NULLIF(LAG(SUM(f.net_sales_amount)) OVER (ORDER BY d.year_month), 0)) * 100.0, 2) AS mom_growth_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
GROUP BY d.calendar_year, d.year_month
ORDER BY d.year_month;
