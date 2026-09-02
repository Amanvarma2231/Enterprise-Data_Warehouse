# RetailSphere Enterprise Architecture Decision Records (ADRs)

This document outlines the core architectural principles, trade-off analyses, and design patterns implemented in the RetailSphere Enterprise Data Warehouse & Governance Platform.

---

## ADR-001: Hybrid Kimball Star Schema vs Inmon Corporate Information Factory (CIF)
- **Status:** Approved & Implemented
- **Context:** Omnichannel retail analytics require high-speed analytical query performance, sub-second aggregation, and self-serve business intelligence.
- **Decision:** Implemented a Kimball Star Schema with central atomic Fact tables (`fact_sales`, `fact_payments`) surrounded by conformed Dimensions (`dim_customer`, `dim_product`, `dim_store`, `dim_date`).
- **Rationale:** 
  1. Star schemas eliminate complex recursive joins typical in 3NF normalized systems.
  2. Conformed dimensions allow drill-across capabilities between sales and payments marts.
  3. Pre-aggregated data marts (`mart_monthly_store_performance`, `mart_customer_rfm`) satisfy low-latency BI dashboards.

---

## ADR-002: Active Quarantine Isolation vs Silent Ingestion Rejection
- **Status:** Approved & Implemented
- **Context:** Data corruption (Null PKs, negative values, future order timestamps) from POS terminals and web events can compromise downstream reporting.
- **Decision:** Engineered a 10-Point automated validation engine that intercepts raw staging data and isolates anomalies into a separate `quarantine` schema with explicit error reason codes (`ERR_NULL_CUSTOMER_KEY`, `ERR_INVALID_QUANTITY`, `ERR_FUTURE_ORDER_DATE`).
- **Rationale:** 
  1. Prevents pipeline failure (zero downtime ingestion).
  2. Guarantees 100% data integrity in production analytics marts.
  3. Enables operational data auditability and remediation workflows.

---

## ADR-003: Multi-Database Ingestion & Cloud Portability
- **Status:** Approved & Implemented
- **Context:** Modern enterprises operate hybrid database ecosystems (MySQL/PostgreSQL OLTP, MongoDB event streams, Snowflake/BigQuery cloud warehouses).
- **Decision:** Designed modular database connectors using SQLAlchemy, PyMySQL, psycopg2, and PyMongo, combined with portable SQL DDLs for MySQL, PostgreSQL, SQLite, Snowflake, and BigQuery.
- **Rationale:** Allows plug-and-play ingestion from any source system without modifying dimensional transformation logic.

---

## ADR-004: Data Governance & Four-Tier Classification Policy
- **Status:** Approved & Implemented
- **Context:** Regulatory compliance (GDPR, DPDP Act) requires stringent handling of customer PII.
- **Decision:** Implemented automated metadata cataloging with 4 security classifications:
  - `PUBLIC`: Catalog items and store details.
  - `INTERNAL`: Sales aggregates and metrics.
  - `CONFIDENTIAL PII`: Names, emails, and phone numbers (masked in non-production environments).
  - `RESTRICTED`: Financial transaction references and gross margin percentages.
