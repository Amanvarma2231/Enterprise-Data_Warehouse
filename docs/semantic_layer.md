# RetailSphere Semantic Layer & Metric Definitions

The Semantic Layer provides centralized, governed metric logic across BI tools, SQL queries, and Python notebooks to eliminate metric divergence.

## Core Governed Metrics

| Metric Name | Business Definition | Mathematical Formula | SQL Representation |
| :--- | :--- | :--- | :--- |
| **Gross Revenue** | Total merchandise sales value before any promotional discounts | `Σ (quantity * unit_price)` | `SUM(gross_sales_amount)` |
| **Promotional Deductions** | Total customer savings and promotional deductions | `Σ (discount_amount)` | `SUM(discount_amount)` |
| **Net Revenue** | Realized sales revenue after deducting discounts | `Gross Revenue - Promotional Deductions` | `SUM(net_sales_amount)` |
| **Cost of Goods Sold (COGS)** | Total inventory procurement cost for items sold | `Σ (quantity * unit_cost)` | `SUM(cost_amount)` |
| **Gross Profit** | Gross monetary margin contribution | `Net Revenue - COGS` | `SUM(gross_profit_amount)` |
| **Gross Profit Margin %** | Percentage of net revenue retained as gross profit | `(Gross Profit / Net Revenue) * 100` | `ROUND((SUM(gross_profit_amount) / NULLIF(SUM(net_sales_amount), 0)) * 100.0, 2)` |
| **Total Order Count** | Total distinct orders placed | `Count(Distinct order_id)` | `COUNT(DISTINCT order_id)` |
| **Average Order Value (AOV)** | Average revenue generated per distinct order | `Net Revenue / Total Order Count` | `ROUND(SUM(net_sales_amount) / NULLIF(COUNT(DISTINCT order_id), 0), 2)` |
| **Units per Transaction (UPT)** | Average quantity of items purchased per order | `Total Units Sold / Total Order Count` | `ROUND(SUM(quantity) * 1.0 / NULLIF(COUNT(DISTINCT order_id), 0), 2)` |
| **Payment Success Rate %** | Percentage of attempted payments that succeeded | `(Successful Payments / Total Payments) * 100` | `ROUND((COUNT(CASE WHEN is_successful THEN 1 END) * 100.0) / COUNT(*), 2)` |
