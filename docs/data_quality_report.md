# RetailSphere Enterprise Data Quality Validation Report

**Execution Timestamp:** 2026-09-02 23:28:07

## 1. Quality Execution Summary

- **Total Checks Evaluated:** 33
- **Passed Checks:** 26
- **Failed / Quarantined Checks:** 7

## 2. Detailed Rule Validation Matrix

| check_category             | table_name              | column_name    |   total_rows |   failed_rows |   failure_rate_pct | status   | severity   | rule_description                                                                               |
|:---------------------------|:------------------------|:---------------|-------------:|--------------:|-------------------:|:---------|:-----------|:-----------------------------------------------------------------------------------------------|
| Null Check                 | staging.stg_customers   | customer_id    |        10000 |             0 |              0     | PASSED   | CRITICAL   | Column customer_id must not contain NULL or empty string values                                |
| Null Check                 | staging.stg_customers   | first_name     |        10000 |             0 |              0     | PASSED   | WARNING    | Column first_name must not contain NULL or empty string values                                 |
| Null Check                 | staging.stg_customers   | email          |        10000 |             0 |              0     | PASSED   | WARNING    | Column email must not contain NULL or empty string values                                      |
| Null Check                 | staging.stg_products    | product_id     |         1000 |             0 |              0     | PASSED   | CRITICAL   | Column product_id must not contain NULL or empty string values                                 |
| Null Check                 | staging.stg_products    | sku            |         1000 |             0 |              0     | PASSED   | WARNING    | Column sku must not contain NULL or empty string values                                        |
| Null Check                 | staging.stg_products    | unit_price     |         1000 |             0 |              0     | PASSED   | WARNING    | Column unit_price must not contain NULL or empty string values                                 |
| Null Check                 | staging.stg_stores      | store_id       |           50 |             0 |              0     | PASSED   | CRITICAL   | Column store_id must not contain NULL or empty string values                                   |
| Null Check                 | staging.stg_stores      | store_name     |           50 |             0 |              0     | PASSED   | WARNING    | Column store_name must not contain NULL or empty string values                                 |
| Null Check                 | staging.stg_stores      | region         |           50 |             0 |              0     | PASSED   | WARNING    | Column region must not contain NULL or empty string values                                     |
| Null Check                 | staging.stg_orders      | order_id       |        50200 |             0 |              0     | PASSED   | CRITICAL   | Column order_id must not contain NULL or empty string values                                   |
| Null Check                 | staging.stg_orders      | customer_id    |        50200 |           301 |              0.6   | FAILED   | CRITICAL   | Column customer_id must not contain NULL or empty string values                                |
| Null Check                 | staging.stg_orders      | order_date     |        50200 |             0 |              0     | PASSED   | WARNING    | Column order_date must not contain NULL or empty string values                                 |
| Null Check                 | staging.stg_order_items | order_item_id  |        93990 |             0 |              0     | PASSED   | CRITICAL   | Column order_item_id must not contain NULL or empty string values                              |
| Null Check                 | staging.stg_order_items | order_id       |        93990 |             0 |              0     | PASSED   | CRITICAL   | Column order_id must not contain NULL or empty string values                                   |
| Null Check                 | staging.stg_order_items | product_id     |        93990 |             0 |              0     | PASSED   | CRITICAL   | Column product_id must not contain NULL or empty string values                                 |
| Null Check                 | staging.stg_payments    | payment_id     |        50000 |             0 |              0     | PASSED   | CRITICAL   | Column payment_id must not contain NULL or empty string values                                 |
| Null Check                 | staging.stg_payments    | order_id       |        50000 |             0 |              0     | PASSED   | CRITICAL   | Column order_id must not contain NULL or empty string values                                   |
| Null Check                 | staging.stg_payments    | payment_amount |        50000 |             0 |              0     | PASSED   | WARNING    | Column payment_amount must not contain NULL or empty string values                             |
| Duplicate Check            | staging.stg_customers   | customer_id    |        10000 |             0 |              0     | PASSED   | CRITICAL   | Primary key (customer_id) must have zero duplicate occurrences                                 |
| Duplicate Check            | staging.stg_products    | product_id     |         1000 |             0 |              0     | PASSED   | CRITICAL   | Primary key (product_id) must have zero duplicate occurrences                                  |
| Duplicate Check            | staging.stg_stores      | store_id       |           50 |             0 |              0     | PASSED   | CRITICAL   | Primary key (store_id) must have zero duplicate occurrences                                    |
| Duplicate Check            | staging.stg_orders      | order_id       |        50200 |           200 |              0.398 | FAILED   | CRITICAL   | Primary key (order_id) must have zero duplicate occurrences                                    |
| Duplicate Check            | staging.stg_order_items | order_item_id  |        93990 |             0 |              0     | PASSED   | CRITICAL   | Primary key (order_item_id) must have zero duplicate occurrences                               |
| Duplicate Check            | staging.stg_payments    | payment_id     |        50000 |             0 |              0     | PASSED   | CRITICAL   | Primary key (payment_id) must have zero duplicate occurrences                                  |
| Referential Integrity      | staging.stg_orders      | customer_id    |        50200 |             0 |              0     | PASSED   | CRITICAL   | FK staging.stg_orders.customer_id must resolve to existing staging.stg_customers.customer_id   |
| Referential Integrity      | staging.stg_orders      | store_id       |        50200 |             0 |              0     | PASSED   | CRITICAL   | FK staging.stg_orders.store_id must resolve to existing staging.stg_stores.store_id            |
| Referential Integrity      | staging.stg_order_items | order_id       |        93990 |             0 |              0     | PASSED   | CRITICAL   | FK staging.stg_order_items.order_id must resolve to existing staging.stg_orders.order_id       |
| Referential Integrity      | staging.stg_order_items | product_id     |        93990 |           563 |              0.599 | FAILED   | CRITICAL   | FK staging.stg_order_items.product_id must resolve to existing staging.stg_products.product_id |
| Referential Integrity      | staging.stg_payments    | order_id       |        50000 |             0 |              0     | PASSED   | CRITICAL   | FK staging.stg_payments.order_id must resolve to existing staging.stg_orders.order_id          |
| Range Validation           | staging.stg_order_items | quantity       |        93990 |           751 |              0.799 | FAILED   | HIGH       | Quantity must be strictly positive (> 0)                                                       |
| Date Validation            | staging.stg_orders      | order_date     |        50200 |           100 |              0.199 | FAILED   | HIGH       | Order date must not be greater than current date (no future orders)                            |
| Format / Syntax Validation | staging.stg_customers   | email          |        10000 |           100 |              1     | FAILED   | MEDIUM     | Customer email must adhere to valid format pattern (contain @ and domain)                      |
| Business Logic             | staging.stg_order_items | line_total     |        93990 |           373 |              0.397 | FAILED   | HIGH       | Line total must reconcile with (quantity * unit_price) - discount                              |

## 3. Quarantine Routing Strategy

All records violating critical integrity rules (Null PKs, orphaned FKs, negative quantity) are automatically diverted to `data/quarantine/` and isolated from downstream Star Schema marts.
