# 🏗️ RetailSphere End-to-End Enterprise Data Warehouse Architecture

## 1. Executive Summary
**RetailSphere** is an omnichannel retail data platform designed to process transactional data from physical stores and digital channels. It consolidates disparate data sources (MySQL, PostgreSQL, MongoDB NoSQL, CSV feeds) into a single, high-performance, Kimball Star Schema data warehouse with sub-second analytical querying.

```
[Operational Sources]
├── MySQL (POS Systems)
├── PostgreSQL (E-Commerce)
├── MongoDB (Event Logs)
└── CSV Bulk Feeds
        │
        ▼ (Python Ingestion)
[Staging Layer: staging.*]
        │
        ▼ (10-Point Data Quality & Profiler)
   ┌────┴─────────────────────────────┐
   ▼                                  ▼
[Quarantine Layer: quarantine.*]   [Kimball Star Schema: warehouse.*]
• Error Reason Codes               • Conformed Dimensions (Date, Customer, Product, Store)
• Root-Cause Ledger                • Line-Item Atomic Fact Sales & Fact Payments
                                      │
                                      ▼ (dbt Transformations)
                                   [Analytical Marts: marts.*]
                                   • mart_customer_rfm
                                   • mart_monthly_store_performance
                                      │
                                      ▼ (Serving & AI Layer)
                                   [Streamlit BI Dashboard & AI Copilot]
```

## 2. Core Architectural Pillars
1. **Multi-Source Ingestion:** Automated loaders with metadata provenance stamping (`_ingested_at`, `_source_system`).
2. **10-Point Quality Gatekeeper:** Null Primary Key detection, referential integrity check, duplicate order prevention, and date sanity tests.
3. **Kimball Star Schema:** Conformed dimensions with SCD Type 1/2 fields and line-item atomic fact tables with surrogate keys.
4. **Analytics Engineering:** Modular dbt DAG executing automated schema tests and business transformations.
5. **Data Governance & PII Protection:** 4-Tier classification (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL PII`, `RESTRICTED`) and automated metadata cataloging.
6. **Observability & Observability:** Structured log streaming (`logs/retailsphere_pipeline.log`) and execution audit ledger table (`dim_pipeline_execution_log`).
