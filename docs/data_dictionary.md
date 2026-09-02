# RetailSphere Enterprise Data Warehouse - Data Dictionary

This document provides business and technical definitions, source lineage, data types, security classifications, and quality validation rules for all warehouse entities.

## Table: `dim_customer`

| column_name       | data_type    | business_definition                                                    | sensitivity        | source_system   | quality_rule                                            |
|:------------------|:-------------|:-----------------------------------------------------------------------|:-------------------|:----------------|:--------------------------------------------------------|
| customer_key      | BIGINT       | System generated unique surrogate key for warehouse customer dimension | INTERNAL           | Internal DW     | PK / NOT NULL / UNIQUE                                  |
| customer_id       | BIGINT       | Primary customer identifier assigned by CRM / ERP transactional system | INTERNAL           | CRM / POS       | NOT NULL / > 0                                          |
| first_name        | VARCHAR(100) | Given name of the registered customer                                  | CONFIDENTIAL (PII) | CRM             | NOT NULL / TRIM                                         |
| last_name         | VARCHAR(100) | Family surname of the registered customer                              | CONFIDENTIAL (PII) | CRM             | NOT NULL / TRIM                                         |
| full_name         | VARCHAR(200) | Concatenated full name for reporting and customer communication        | CONFIDENTIAL (PII) | Internal DW     | NOT NULL                                                |
| email             | VARCHAR(255) | Primary contact electronic mail address                                | CONFIDENTIAL (PII) | CRM             | Regex Email Pattern: %@%.%                              |
| phone             | VARCHAR(50)  | Primary contact telephone / mobile number                              | CONFIDENTIAL (PII) | CRM             | Length <= 15                                            |
| city              | VARCHAR(100) | Municipal billing / residential city                                   | INTERNAL           | CRM             | NOT NULL                                                |
| state             | VARCHAR(100) | Administrative provincial territory                                    | INTERNAL           | CRM             | NOT NULL                                                |
| country           | VARCHAR(100) | Sovereign country name of registration                                 | PUBLIC             | CRM             | DEFAULT 'India'                                         |
| postal_code       | VARCHAR(30)  | Postal / ZIP geographical routing code                                 | INTERNAL           | CRM             | Standard Format                                         |
| segment           | VARCHAR(50)  | Loyalty tier classification: Regular, Premium, VIP, Corporate          | INTERNAL           | CRM / Marketing | IN ('Regular','Premium','VIP','Corporate','Occasional') |
| registration_date | DATE         | Date when customer account was created                                 | INTERNAL           | CRM             | <= CURRENT_DATE                                         |
| is_active         | BOOLEAN      | Active profile flag (True/False)                                       | INTERNAL           | CRM             | BOOLEAN                                                 |

---

## Table: `dim_product`

| column_name       | data_type     | business_definition                                              | sensitivity   | source_system   | quality_rule                                 |
|:------------------|:--------------|:-----------------------------------------------------------------|:--------------|:----------------|:---------------------------------------------|
| product_key       | BIGINT        | System generated unique surrogate key for product dimension      | INTERNAL      | Internal DW     | PK / NOT NULL / UNIQUE                       |
| product_id        | BIGINT        | Source system catalog product ID                                 | INTERNAL      | Catalog ERP     | NOT NULL / > 0                               |
| sku               | VARCHAR(100)  | Global unique merchandise identification code                    | INTERNAL      | Catalog ERP     | UNIQUE / NOT NULL                            |
| product_name      | VARCHAR(255)  | Official catalog merchandising title of the product              | PUBLIC        | Catalog ERP     | NOT NULL / LENGTH > 2                        |
| category          | VARCHAR(100)  | Top-level department classification (e.g., Electronics, Apparel) | PUBLIC        | Catalog ERP     | NOT NULL                                     |
| subcategory       | VARCHAR(100)  | Granular department subcategory (e.g., Laptops, Footwear)        | PUBLIC        | Catalog ERP     | NOT NULL                                     |
| unit_cost         | DECIMAL(12,2) | Procurement / manufacturing acquisition cost per unit (INR)      | RESTRICTED    | Procurement ERP | > 0.00                                       |
| unit_price        | DECIMAL(12,2) | Standard suggested retail selling price per unit (INR)           | PUBLIC        | Catalog ERP     | unit_price >= unit_cost                      |
| profit_margin_pct | DECIMAL(6,2)  | Base profit margin percentage ((price - cost) / price) * 100     | CONFIDENTIAL  | Internal DW     | BETWEEN 0 AND 100                            |
| price_tier        | VARCHAR(50)   | Pricing bracket: Budget, Mid-Range, Premium, Luxury              | INTERNAL      | Internal DW     | IN ('Budget','Mid-Range','Premium','Luxury') |
| reorder_level     | INTEGER       | Inventory minimum threshold before triggering reorder            | INTERNAL      | Inventory ERP   | >= 0                                         |
| is_discontinued   | BOOLEAN       | Lifecycle status indicating if item has been discontinued        | INTERNAL      | Catalog ERP     | BOOLEAN                                      |

---

## Table: `dim_store`

| column_name   | data_type    | business_definition                                                       | sensitivity   | source_system   | quality_rule                              |
|:--------------|:-------------|:--------------------------------------------------------------------------|:--------------|:----------------|:------------------------------------------|
| store_key     | BIGINT       | System generated surrogate key for retail store dimension                 | INTERNAL      | Internal DW     | PK / NOT NULL / UNIQUE                    |
| store_id      | BIGINT       | Source store branch unique identifier                                     | INTERNAL      | Retail POS ERP  | NOT NULL / > 0                            |
| store_name    | VARCHAR(255) | Official retail outlet location display name                              | PUBLIC        | Retail POS ERP  | NOT NULL                                  |
| store_type    | VARCHAR(100) | Retail footprint format: Flagship, Standard, Outlet, Online               | INTERNAL      | Retail POS ERP  | NOT NULL                                  |
| channel_group | VARCHAR(50)  | Omnichannel division: Physical Retail vs Digital Channel                  | INTERNAL      | Internal DW     | IN ('Physical Retail', 'Digital Channel') |
| region        | VARCHAR(100) | Geographic retail operating territory (North, South, East, West, Central) | INTERNAL      | Retail POS ERP  | NOT NULL                                  |
| square_feet   | INTEGER      | Total commercial floor area in square feet                                | INTERNAL      | Facilities ERP  | >= 0                                      |
| opened_date   | DATE         | Grand opening commercial launch date                                      | INTERNAL      | Retail POS ERP  | <= CURRENT_DATE                           |

---

## Table: `dim_date`

| column_name    | data_type   | business_definition                                   | sensitivity   | source_system      | quality_rule              |
|:---------------|:------------|:------------------------------------------------------|:--------------|:-------------------|:--------------------------|
| date_key       | INTEGER     | Smart integer calendar key in YYYYMMDD format         | PUBLIC        | Conformed Calendar | PK / NOT NULL / 8 digits  |
| full_date      | DATE        | Standard calendar ISO date                            | PUBLIC        | Conformed Calendar | UNIQUE / NOT NULL         |
| year_month     | VARCHAR(7)  | Period identifier in YYYY-MM format                   | PUBLIC        | Conformed Calendar | Regex ^[0-9]{4}-[0-9]{2}$ |
| fiscal_quarter | VARCHAR(10) | Corporate financial reporting quarter (e.g., FY26-Q2) | PUBLIC        | Conformed Calendar | NOT NULL                  |

---

## Table: `fact_sales`

| column_name         | data_type     | business_definition                                                | sensitivity   | source_system    | quality_rule                    |
|:--------------------|:--------------|:-------------------------------------------------------------------|:--------------|:-----------------|:--------------------------------|
| sales_key           | BIGINT        | Surrogate primary key for individual order line item in fact table | INTERNAL      | Internal DW      | PK / NOT NULL / UNIQUE          |
| order_id            | BIGINT        | Transaction order identifier from POS (Degenerate Dimension)       | INTERNAL      | POS / E-Commerce | NOT NULL / > 0                  |
| order_item_id       | BIGINT        | Line item identifier from order manifest                           | INTERNAL      | POS / E-Commerce | NOT NULL / > 0                  |
| customer_key        | BIGINT        | Referential surrogate key connecting to dim_customer               | INTERNAL      | Internal DW      | FK -> dim_customer.customer_key |
| product_key         | BIGINT        | Referential surrogate key connecting to dim_product                | INTERNAL      | Internal DW      | FK -> dim_product.product_key   |
| store_key           | BIGINT        | Referential surrogate key connecting to dim_store                  | INTERNAL      | Internal DW      | FK -> dim_store.store_key       |
| date_key            | INTEGER       | Referential smart key connecting to dim_date                       | INTERNAL      | Internal DW      | FK -> dim_date.date_key         |
| quantity            | INTEGER       | Units of product sold in transaction line                          | INTERNAL      | POS / E-Commerce | quantity > 0                    |
| unit_price          | DECIMAL(12,2) | Actual selling price per unit at time of sale                      | INTERNAL      | POS / E-Commerce | unit_price > 0.00               |
| gross_sales_amount  | DECIMAL(14,2) | Gross monetary line total = quantity * unit_price                  | INTERNAL      | Internal DW      | gross_sales_amount > 0.00       |
| discount_amount     | DECIMAL(14,2) | Total discount deduction applied to line item                      | INTERNAL      | POS / Promotions | discount_amount >= 0.00         |
| net_sales_amount    | DECIMAL(14,2) | Net revenue earned after promotional discount = gross - discount   | INTERNAL      | Internal DW      | net_sales_amount >= 0.00        |
| cost_amount         | DECIMAL(14,2) | Total procurement cost = quantity * unit_cost                      | RESTRICTED    | Internal DW      | cost_amount >= 0.00             |
| gross_profit_amount | DECIMAL(14,2) | Gross margin contribution = net_sales_amount - cost_amount         | CONFIDENTIAL  | Internal DW      | Numeric                         |
| profit_margin_pct   | DECIMAL(6,2)  | Realized gross profit margin percentage on transaction line        | CONFIDENTIAL  | Internal DW      | Numeric Percentage              |

---

## Table: `fact_payments`

| column_name     | data_type     | business_definition                                                | sensitivity   | source_system   | quality_rule                                                                   |
|:----------------|:--------------|:-------------------------------------------------------------------|:--------------|:----------------|:-------------------------------------------------------------------------------|
| payment_key     | BIGINT        | Surrogate primary key for payment transaction in warehouse         | INTERNAL      | Internal DW     | PK / NOT NULL / UNIQUE                                                         |
| payment_id      | BIGINT        | Payment gateway transactional settlement ID                        | INTERNAL      | Payment Gateway | NOT NULL / > 0                                                                 |
| payment_method  | VARCHAR(50)   | Payment instrument: UPI, Credit Card, Debit Card, NetBanking, Cash | INTERNAL      | Payment Gateway | IN ('UPI','Credit Card','Debit Card','NetBanking','PayPal','Cash on Delivery') |
| payment_status  | VARCHAR(50)   | Settlement outcome: Success, Failed, Refunded, Pending             | INTERNAL      | Payment Gateway | IN ('Success','Failed','Refunded','Pending')                                   |
| payment_amount  | DECIMAL(14,2) | Actual transacted currency amount settled through gateway          | INTERNAL      | Payment Gateway | payment_amount > 0.00                                                          |
| transaction_ref | VARCHAR(100)  | External banking authorization reference code                      | CONFIDENTIAL  | Payment Gateway | NOT NULL / Standard Prefix                                                     |

---

