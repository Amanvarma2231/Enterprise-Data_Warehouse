# Capgemini Associate Data Modeller - Interview Preparation & Defense Guide

This guide is designed to help you speak with complete authority in technical interviews for **Associate Data Modeller / Analytics Engineer** positions.

---

## 🌟 1. Project Elevator Pitch (30-Second Introduction)

> **"In my recent project, RetailSphere, I architected an end-to-end Enterprise Sales & Customer Data Warehouse and Governance Platform.**  
> **I designed the conceptual, logical, and physical data models, developed a 10-point Data Quality & Quarantine Framework in Python and SQL, implemented a Kimball Dimensional Star Schema with surrogate keys and conformed dimensions, orchestrated staging-to-marts transformations using dbt and DuckDB, and documented enterprise metadata, lineage, and PII classification standards."**

---

## 🎯 2. Core Data Modelling Technical Questions & Answers

### Q1: What is the difference between Conceptual, Logical, and Physical Data Models?
- **Conceptual Data Model (Phase 3):** High-level business view identifying key business entities (`CUSTOMER`, `ORDER`, `PRODUCT`, `STORE`, `PAYMENT`) and their fundamental relationships (e.g., Customer places Order). No technical data types or primary keys are declared.
- **Logical Data Model (Phase 4):** Fully defined normalized relational schema specifying attributes, Primary Keys (PK), Foreign Keys (FK), cardinality (1:N, M:N), and business rules independent of database technology.
- **Physical Data Model (Phase 5):** Technology-specific implementation (PostgreSQL / DuckDB / BigQuery) with explicit data types, indexes, partitioning (`PARTITION BY order_date`), clustering (`CLUSTER BY customer_key`), constraints, and storage optimizations.

---

### Q2: Why did you choose a Dimensional Star Schema over a 3NF Relational Model for the Warehouse?
- **3NF (Third Normal Form):** Optimized for **OLTP (Online Transaction Processing)** to eliminate update anomalies and optimize single-record insert/update throughput. However, analytical reporting requires joining 8-12 normalized tables, which degrades query performance.
- **Star Schema (Kimball Dimensional Model):** Optimized for **OLAP (Online Analytical Processing)** and BI aggregation. By de-normalizing dimensions around a centralized transactional fact table (`fact_sales`), SQL joins are reduced to single-level equi-joins with predictable performance, intuitive business slicing, and fast aggregations.

---

### Q3: What is the Grain of your Fact Table and why is Grain declaration critical?
- **Grain of `fact_sales`:** **One row per line item in a completed sales order.**
- **Why it matters:** The grain defines the atomic level of detail represented in the fact table. Declaring the finest grain (individual order line) guarantees maximum analytical flexibility—allowing downstream users to slice by minute, individual SKU, store location, or customer loyalty tier without losing transaction context.

---

### Q4: Why use Surrogate Keys instead of Natural Business Keys in Dimensions?
1. **Upstream Decoupling:** Source systems may recycle IDs or change key formats during CRM/ERP migrations.
2. **SCD Type 2 Historization:** To track historical customer changes (e.g., city moves), a single natural customer ID must have multiple rows in the dimension table. Unique surrogate keys (`customer_key`) allow fact records to point to the exact historical profile active at the time of the sale.
3. **Join Performance:** Integer/BigInt surrogate keys join significantly faster than alphanumeric composite natural keys.

---

### Q5: How did you implement Data Quality & Quarantine Isolation?
- I engineered an automated **10-Point Data Quality Engine**:
  1. *Null PK Checks* (Zero tolerance on critical keys)
  2. *Primary Key Uniqueness Checks*
  3. *Referential Integrity Checks* (Orphaned product/customer keys)
  4. *Range Validation* (`quantity > 0`, `unit_price > 0`)
  5. *Business Logic Validation* (`line_total == qty * price - discount`)
  6. *Date Validation* (Rejection of future-dated transactions)
  7. *Syntax Validation* (Regex check on customer emails)
  8. *Duplicate Order Detection*
  9. *Payment Reconciliation*
  10. *Completeness Auditing*
- Anomalous rows are routed to `data/quarantine/` with explicit rejection reason codes (e.g., `ERR_NULL_CUSTOMER_KEY`, `ERR_INVALID_QUANTITY_NON_POSITIVE`) ensuring zero tainted data enters production marts.

---

### Q6: How does dbt fit into your Architecture?
- We utilize **dbt (data build tool)** to structure modular SQL transformations:
  - `staging/`: Cleanses raw CSV inputs, casts types, and trims whitespace.
  - `intermediate/`: Enriches line items with product procurement costs and aggregates order metrics.
  - `marts/`: Materializes final Star Schema dimension tables (`dim_customer`, `dim_product`, `dim_store`, `dim_date`) and fact tables (`fact_sales`, `fact_payments`).
  - Automated testing via dbt schema assertions (`unique`, `not_null`, `relationships`) and custom singular SQL tests.

---

### Q7: How would you scale this design to Google Cloud BigQuery?
- In BigQuery, `fact_sales` is partitioned by day (`PARTITION BY order_date`) to minimize query scan costs.
- High-frequency filtering attributes (`customer_key`, `product_key`, `store_key`) are clustered (`CLUSTER BY customer_key, product_key`) to co-locate related records in storage blocks.
- Column descriptions and PII policy tags are configured directly in BigQuery DDL for Dataplex governance integration.
