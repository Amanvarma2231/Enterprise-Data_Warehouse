# 🎙️ Data Modeler & Analytics Engineer Technical Q&A Guide

This technical guide prepares engineers to articulate the architectural decisions made throughout the **RetailSphere** data warehouse.

---

### Q1: What is conceptual data modelling?
**Answer:** High-level architectural modeling focusing on business entities (Customer, Store, Product, Order) and their real-world cardinalities without getting bogged down by physical keys or storage formats.

### Q2: What is logical data modelling?
**Answer:** Normalized (3NF) relational design defining Primary Keys, Foreign Keys, data types, nullability, and business constraints to model the operational transactional reality.

### Q3: What is physical data modelling?
**Answer:** Database-specific implementation scripts (PostgreSQL, BigQuery, Snowflake DDLs) incorporating indexes, storage parameters, clustering, and partitioning strategies.

### Q4: Why did you normalize the transactional model?
**Answer:** 3NF prevents write anomalies (insert/update/delete anomalies) and ensures data consistency across high-velocity operational POS and E-commerce transactions.

### Q5: Why did you use a star schema in the warehouse?
**Answer:** Star Schema simplifies BI reporting, minimizes the number of joins needed for analytics, and optimizes columnar vectorized scans across large fact tables.

### Q6: What is the grain of `fact_sales`?
**Answer:** **One row in `fact_sales` represents one product line item within one customer order.** This atomic grain provides maximum reporting flexibility.

### Q7: What is a surrogate key and why use it?
**Answer:** A system-generated, non-business integer (`customer_key`, `product_key`). It decouples warehouse dimensions from operational source system key changes and enables SCD Type 2 tracking.

### Q8: Business Key vs. Surrogate Key?
**Answer:** A business key (`customer_id`, `sku`) is the identifier from the source system. A surrogate key (`customer_key`, `product_key`) is warehouse-generated.

### Q9: Fact Table vs. Dimension Table?
**Answer:** Facts contain numerical business measures (`net_sales_amount`, `quantity`, `gross_profit`). Dimensions contain contextual attributes (`city`, `category`, `channel_group`) that filter and slice measures.

### Q10: What is dimensional modelling?
**Answer:** A Kimball-inspired data design technique focused on business user understandability and query performance, organizing data into Facts and Dimensions.

### Q11: What is data lineage?
**Answer:** Tracing data from its raw source through every intermediate transformation, quality filter, and dimension table to the final BI metric.

### Q12: What is a data dictionary?
**Answer:** A centralized catalog documenting table definitions, column descriptions, data types, nullability, primary/foreign keys, and PII sensitivity classifications.

### Q13: What is semantic modelling?
**Answer:** Defining standardized, business-friendly metrics (e.g. AOV = Net Revenue / Total Orders) in a single governed layer.

### Q14: What is ETL vs. ELT?
**Answer:** In ETL, data is transformed before loading. In modern ELT (used in RetailSphere), raw data is loaded into Staging, and powerful warehouse SQL engines execute transformations.

### Q15: Why dbt?
**Answer:** dbt enables analytics engineering best practices: modular SQL models (`staging` ➜ `intermediate` ➜ `marts`), automated testing, version control, and documentation generation.

### Q16: How did you perform data quality checks?
**Answer:** Built an automated 10-point quality gatekeeper that intercepts bad staging data and routes anomalies to a `quarantine` schema with explicit reason codes.

### Q17: How did you handle duplicate records?
**Answer:** Using SQL window functions (`ROW_NUMBER() OVER (PARTITION BY business_id ORDER BY ingested_at DESC)`) in staging transformation models.

### Q18: How did you handle invalid foreign keys?
**Answer:** Orphaned line items referencing non-existent products are isolated into `quarantine.quarantine_order_items` with code `ERR_ORPHAN_PRODUCT_KEY`.

### Q19: How did you optimize SQL performance?
**Answer:** Created indexes on Foreign Keys (`customer_key`, `product_key`, `date_key`), leveraged columnar DuckDB vectorized execution, and designed BigQuery date-partitioning.

### Q20: How would you handle Slowly Changing Dimensions (SCD Type 2)?
**Answer:** `dim_customer` contains `row_effective_date`, `row_expiration_date`, and `is_current` boolean flags to maintain historical customer profile snapshots over time.
