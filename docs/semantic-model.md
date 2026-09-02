# 📐 RetailSphere Enterprise Semantic Layer & Metric Catalog

This document defines standardized business metrics and semantic dimensions across the RetailSphere platform, ensuring a unified Single Source of Truth across executive BI dashboards and SQL reporting.

---

## 1. Conformed Semantic Dimensions

| Dimension | Key Attributes | Source Table | Business Role |
| :--- | :--- | :--- | :--- |
| **Customer** | `customer_id`, `full_name`, `email`, `city`, `segment`, `rfm_tier` | `warehouse.dim_customer` | Customer profiling, cohort retention, and RFM behavioral clustering. |
| **Product** | `sku`, `product_name`, `category`, `subcategory`, `price_tier` | `warehouse.dim_product` | Merchandising analysis, price tier profitability, and category margins. |
| **Store** | `store_name`, `store_type`, `channel_group`, `region`, `square_feet` | `warehouse.dim_store` | Physical vs digital channel performance and store productivity ($/sqft). |
| **Date** | `date_key`, `full_date`, `year_month`, `calendar_year`, `is_weekend` | `warehouse.dim_date` | Time-series trend analysis, MoM / YoY growth, and seasonality tracking. |

---

## 2. Core Business Measures & Formulas

| Metric Name | Business Definition | Mathematical Formula | Grain / Source |
| :--- | :--- | :--- | :--- |
| **Gross Sales Amount** | Total list price revenue before any promotional discounts. | `SUM(quantity * unit_price)` | Line-Item Grain (`fact_sales`) |
| **Net Sales Revenue** | Realized transactional revenue after discounts deducted. | `SUM((quantity * unit_price) - discount_amount)` | Line-Item Grain (`fact_sales`) |
| **Cost of Goods Sold (COGS)** | Direct inventory acquisition and production cost. | `SUM(quantity * unit_cost)` | Line-Item Grain (`fact_sales`) |
| **Gross Profit Amount** | Gross earnings retained after subtracting COGS from Net Revenue. | `SUM(net_sales_amount - cost_amount)` | Line-Item Grain (`fact_sales`) |
| **Gross Profit Margin %** | Percentage of revenue converted into gross profit. | `(SUM(gross_profit) / NULLIF(SUM(net_sales), 0)) * 100.0` | Line-Item Grain (`fact_sales`) |
| **Average Order Value (AOV)** | Average monetary spend realized per order transaction. | `SUM(net_sales_amount) / NULLIF(COUNT(DISTINCT order_id), 0)` | Order-Level Grain (`fact_sales`) |
| **Payment Success Rate %** | Percentage of payment transactions successfully cleared. | `(COUNT(CASE WHEN status='Success') / COUNT(*)) * 100.0` | Transaction Grain (`fact_payments`) |
