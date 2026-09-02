# 🛡️ 10-Point Data Quality & Quarantine Framework

## 1. Overview
RetailSphere incorporates an active **Quality Gatekeeper Engine** between Staging and the Star Schema. Rather than allowing corrupted records to pollute executive reports or crashing the pipeline, defective records are intercepted and routed to the `quarantine.*` schema with specific audit reason codes.

```
Staging Records ──▶ [10-Point Quality Gatekeeper]
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
    [Valid Records]            [Corrupted Records]
            │                           │
            ▼                           ▼
[Kimball Star Schema]       [Quarantine Layer + Reason Code]
                            • ERR_NULL_CUSTOMER_KEY
                            • ERR_INVALID_QUANTITY
                            • ERR_FUTURE_ORDER_DATE
                            • ERR_ORPHAN_PRODUCT_KEY
```

---

## 2. Implemented Quality Checks & Rules

| # | Quality Check Rule | Target Table | Validation Logic | Action on Violation |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Primary Key Not Null** | `stg_customers`, `stg_orders` | `customer_id IS NOT NULL AND order_id IS NOT NULL` | Route to `quarantine_orders` (`ERR_NULL_CUSTOMER_KEY`) |
| **2** | **Primary Key Uniqueness** | `stg_orders`, `stg_customers` | `COUNT(*) OVER (PARTITION BY pk) = 1` | Quarantine duplicate instances |
| **3** | **Referential Integrity (FK)** | `stg_order_items` ➜ `stg_products` | `oi.product_id IN (SELECT product_id FROM stg_products)` | Quarantine orphaned items (`ERR_ORPHAN_PRODUCT_KEY`) |
| **4** | **Positive Quantity Constraint**| `stg_order_items` | `TRY_CAST(quantity AS INT) > 0` | Quarantine negative/zero quantities (`ERR_INVALID_QUANTITY`) |
| **5** | **Positive Unit Price** | `stg_products`, `stg_order_items` | `TRY_CAST(unit_price AS DECIMAL) > 0.00` | Quarantine non-positive pricing |
| **6** | **Date Feasibility Rule** | `stg_orders` | `CAST(order_date AS DATE) <= CURRENT_DATE` | Quarantine future dated orders (`ERR_FUTURE_ORDER_DATE`) |
| **7** | **Email Format Regex** | `stg_customers` | `email LIKE '%@%.%'` | Standardize or route to customer quarantine |
| **8** | **Financial Reconciliation** | `stg_order_items` | `line_total = (quantity * unit_price) - discount` | Recompute line total during transformation |
| **9** | **Payment Range Sanity** | `stg_payments` | `TRY_CAST(payment_amount AS DECIMAL) >= 0.00` | Quarantine negative payments |
| **10**| **Column Statistical Profiler** | `warehouse.*` | Null %, Uniqueness %, Cardinality, Health Score | Logged to `warehouse.audit_column_profile` (100.0/100 A+) |
