# RetailSphere: Enterprise Sales & Customer Data Warehouse + Data Governance Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![DuckDB](https://img.shields.io/badge/duckdb-v1.1.0-orange.svg)](https://duckdb.org/)
[![dbt-Core](https://img.shields.io/badge/dbt-core-FF694B.svg)](https://www.getdbt.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20App-FF4B4B.svg)](https://enterprise-datawarehouse-amhwlzks6yuybmcbxtls2v.streamlit.app/)
[![SQL](https://img.shields.io/badge/SQL-MySQL%20|%20Postgres%20|%20Snowflake%20|%20BigQuery-4479A1.svg)](https://github.com/Amanvarma2231/Enterprise-Data_Warehouse)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Live Interactive BI Portal:** [https://enterprise-datawarehouse-amhwlzks6yuybmcbxtls2v.streamlit.app/](https://enterprise-datawarehouse-amhwlzks6yuybmcbxtls2v.streamlit.app/)  
> **Author & Lead Architect:** **Aman Varma** ([GitHub Profile](https://github.com/Amanvarma2231))

---

## 🌟 Executive Overview

**RetailSphere** is an end-to-end, production-grade **Enterprise Data Warehouse and Data Governance Platform** designed to solve complex analytical and governance challenges in high-velocity omnichannel retail operations. 

Moving beyond basic transactional databases, this platform ingests raw transactional streams from multiple sources (**MySQL, PostgreSQL, MongoDB, SQLite, and Flat CSV Feeds**), subjects them to an automated **10-Point Data Quality & Anomaly Quarantine Engine**, normalizes them into a **Kimball Dimensional Star Schema**, and serves high-impact executive dashboards and analytical data marts.

---

## ⚙️ How the Pipeline Works (End-to-End Data Flow)

The RetailSphere architecture follows a structured, multi-tier data pipeline designed for zero data loss, sub-second query performance, and strict data governance:

```
+----------------------------------------------------------------------------------------------------+
|                                    OPERATIONAL SOURCE SYSTEMS                                      |
|   +----------------+  +-------------------+  +------------------+  +----------------------------+  |
|   |  MySQL (OLTP)  |  | PostgreSQL (OLTP) |  | MongoDB (NoSQL)  |  | CSV / SFTP Batch Feeds     |  |
|   +-------+--------+  +---------+---------+  +--------+---------+  +-------------+--------------+  |
+-----------|---------------------|---------------------|--------------------------|-----------------+
            |                     |                     |                          |
            v                     v                     v                          v
+----------------------------------------------------------------------------------------------------+
| 1. INGESTION & STAGING LAYER (schema: staging)                                                     |
|    - Raw operational tables landed verbatim with ingestion timestamps & source provenance tags.    |
|    - stg_customers, stg_products, stg_stores, stg_orders, stg_order_items, stg_payments          |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| 2. 10-POINT DATA QUALITY & QUARANTINE ENGINE (schema: quarantine)                                  |
|    - Null Primary Key Checks, Duplicate Record Detection, Orphaned Foreign Key Validation          |
|    - Range Checks (Quantity > 0, Price > 0), Date Feasibility (Order Date <= CURRENT_DATE)        |
|    - Corrupted records isolated into quarantine tables with explicit reason codes                  |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   | [Clean Validated Streams]
                                                   v
+----------------------------------------------------------------------------------------------------+
| 3. KIMBALL DIMENSIONAL STAR SCHEMA (schema: warehouse)                                             |
|    - Conformed Dimensions: dim_customer (SCD Type 1/2), dim_product, dim_store, dim_date (2022-30)|
|    - Atomic Grain Facts:   fact_sales (Line-Item Atomic Grain), fact_payments (Reconciliation)     |
|    - Surrogate Keys, Referential Integrity, Financial Math & Realized Margin Calculation          |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| 4. ANALYTICS MARTS & dbt TRANSFORMATION (schema: analytics / marts)                                |
|    - mart_monthly_store_performance: Store-level MoM revenue, margin %, realized profitability    |
|    - mart_customer_rfm: Recency, Frequency, Monetary (RFM) behavioral scoring (NTILE 1-5)         |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
            +--------------------------------------+--------------------------------------+
            |                                                                             |
            v                                                                             v
+------------------------------------------+                 +--------------------------------------------+
| 5. GOVERNANCE & OBSERVABILITY            |                 | 6. REAL-TIME BI SERVING LAYER              |
|    - 60+ Documented Column Metadata      |                 |    - Executive Sales & Margin KPIs         |
|    - 4-Tier Security Classification      |                 |    - Regional & Category Revenue Trends    |
|    - Pipeline Execution Audit Ledger     |                 |    - Real-Time Data Quality Scorecard      |
|    - Column Statistical Health Profiler  |                 |    - On-Demand Pipeline Trigger Runner     |
+------------------------------------------+                 +--------------------------------------------+
```

---

## 🏛️ Key Platform Capabilities

### 1. Multi-Tier Data Modeling
- **Conceptual Model:** Business entity relationships and cardinality.
- **Logical Data Model (3NF):** Normalized operational staging layer.
- **Physical Star Schema:** Surrogate keys, conformed dimensions, atomic grain facts, and dimension role-playing.
- **Conformed Date Dimension:** 2022–2030 calendar with fiscal periods, quarter names, and holiday flags.

### 2. Multi-Database Ingestion Connectors (`src/ingestion/`)
- **MySQL / MariaDB:** Direct ingestion via `SQLAlchemy` and `PyMySQL`.
- **PostgreSQL:** High-throughput transactional table extraction via `psycopg2`.
- **MongoDB:** Extraction and automatic schema flattening of nested NoSQL JSON documents.
- **SQLite:** Embedded database ingestion for local and edge environments.
- **Portable SQL DDLs:** Dedicated DDL scripts for **MySQL 8.0**, **PostgreSQL 15**, **SQLite 3**, **Snowflake**, and **Google Cloud BigQuery**.

### 3. 10-Point Data Quality & Quarantine Framework
- **Primary Key Uniqueness & Nullability:** Enforces zero nulls on identifier columns.
- **Referential Integrity Constraints:** Catches orphaned foreign keys (`product_id`, `customer_id`, `store_id`).
- **Domain & Range Validations:** Prevents non-positive quantities and zero unit prices.
- **Business Logic Rules:** Mathematical reconciliation (`line_total = quantity * unit_price - discount`).
- **Quarantine Isolation:** Isolates anomalies into `quarantine.*` with explicit reason codes (`ERR_NULL_CUSTOMER_KEY`, `ERR_INVALID_QUANTITY`, `ERR_FUTURE_ORDER_DATE`).

### 4. Analytics Engineering with dbt
- Modular multi-layer transformations:
  - `models/staging/`: Source cleansing and data type casting.
  - `models/intermediate/`: Customer aggregation and order-item financial enrichment.
  - `models/marts/`: Business-ready dimensional tables and analytical marts.
- Automated dbt schema tests (`unique`, `not_null`, `relationships`, `accepted_values`).

### 5. Enterprise Governance, Profiling & Audit Logging
- **Data Dictionary:** Formatted Excel [`docs/data_dictionary.xlsx`](docs/data_dictionary.xlsx) and Markdown [`docs/data_dictionary.md`](docs/data_dictionary.md) documenting 60+ attributes.
- **4-Tier Data Classification:** `PUBLIC`, `INTERNAL`, `CONFIDENTIAL PII`, `RESTRICTED`.
- **Automated Column Profiler:** Generates comprehensive statistical quality scorecards [`docs/data_profiling_report.md`](docs/data_profiling_report.md).
- **Execution Audit Ledger:** Every pipeline execution is logged in `warehouse.dim_pipeline_execution_log` with row counts and duration.

---

## 📊 Interactive BI Dashboard (Streamlit Cloud)

The interactive dashboard is live deployed on Streamlit Community Cloud:
👉 **[https://enterprise-datawarehouse-amhwlzks6yuybmcbxtls2v.streamlit.app/](https://enterprise-datawarehouse-amhwlzks6yuybmcbxtls2v.streamlit.app/)**

### Dashboard Modules:
1. **Executive Analytics:** High-level KPI cards (Revenue, Gross Profit, Margin %, AOV), Monthly trends, Regional revenue split.
2. **Customer & RFM:** RFM behavioral clustering (Champions, Loyal, At Risk) with interactive spending distribution.
3. **Product Intelligence:** Best-selling SKUs, category margins, and unit sales velocity.
4. **Data Quality & Scorecard:** Quarantine reason breakdown, anomaly volume tracking, and column health scores.
5. **Pipeline Execution & Observability:** Live streaming application logs, execution run history ledger, and an interactive **"Run Pipeline On-Demand"** trigger.
6. **Data Dictionary & Catalog:** Live searchable metadata catalog with CSV export capability.

---

## 📁 Repository Structure

```
Enterprise-Data-Warehouse/
├── .github/workflows/ci.yml       # GitHub Actions Automated CI/CD Pipeline
├── .gitattributes                 # GitHub Linguist SQL Language Configuration
├── .gitignore                     # Git ignore rules for runtime files
├── README.md                      # Production Documentation & Architecture Guide
├── requirements.txt               # Complete Python & Database Driver Dependencies
├── pytest.ini                     # PyTest configuration
│
├── dashboard/
│   └── app.py                     # Streamlit Interactive BI & Observability App
│
├── data/
│   ├── sample/                    # Lightweight sample CSV datasets
│   └── quarantine/                # Isolated anomaly records with reason codes
│
├── dbt_retail_dw/                 # Complete dbt Project
│   ├── dbt_project.yml            # dbt configuration
│   ├── profiles.yml               # Connection profiles
│   ├── models/
│   │   ├── staging/               # Staging transformation models
│   │   ├── intermediate/          # Business logic enrichment models
│   │   └── marts/                 # Star schema facts, dimensions & marts
│   └── tests/                     # Singular schema validation tests
│
├── docs/                          # Architectural Assets & Governance
│   ├── architecture_decision_records.md # Production ADRs & design rationales
│   ├── data_dictionary.md         # Full Markdown Data Dictionary
│   ├── data_dictionary.xlsx       # Multi-tab Styled Excel Data Dictionary
│   ├── data_profiling_report.md   # Automated Column Health Scorecard
│   ├── data-lineage.md            # Column-level Data Lineage Map
│   ├── governance.md              # 4-Tier Security & PII Classification Policy
│   ├── modelling-standards.md     # Dimensional Modeling Naming Standards
│   ├── semantic_layer.md          # Standardized Business Metric Definitions
│   └── *.png                      # High-Resolution Architectural Diagrams
│
├── logs/
│   └── retailsphere_pipeline.log  # Structured Application & Execution Logs
│
├── metadata/
│   └── metadata.csv               # 60+ Attribute Governance Catalog
│
├── sql/
│   ├── ddl/                       # DDL Scripts for MySQL, Postgres, SQLite, Snowflake, BigQuery
│   ├── transformations/           # Production SQL ELT & Quarantine Scripts
│   └── analytics/                 # 20+ Production BI & Window Function Queries
│
├── src/
│   ├── config.py                  # Central Environment Paths & Constants
│   ├── data_generator.py          # Synthetic Data Generator with Injected Anomalies
│   ├── pipeline.py                # Master Pipeline Orchestrator & Audit Runner
│   ├── governance/
│   │   ├── data_profiler.py       # Column Statistical Profiling & Scorecard Engine
│   │   └── metadata_manager.py    # Governance & Data Dictionary Generator
│   ├── ingestion/
│   │   ├── load_csv.py            # High-Speed Staging CSV Loader
│   │   ├── mysql_connector.py     # MySQL Ingestion Connector
│   │   ├── postgres_connector.py  # PostgreSQL Ingestion Connector
│   │   ├── mongodb_connector.py   # MongoDB NoSQL Document Flattening Connector
│   │   └── sqlite_connector.py    # SQLite Embedded Database Connector
│   ├── transformation/
│   │   ├── transformer.py         # Star Schema Transformation Engine
│   │   └── date_dimension_generator.py # Conformed Date Dimension (2022-2030)
│   ├── utils/
│   │   └── logger.py              # Structured Enterprise Logging Utility
│   └── validation/
│       ├── data_quality_engine.py # 10-Point DQ Engine & Quarantine Dispatcher
│       ├── null_checks.py         # PK & Column Null Verification
│       ├── duplicate_checks.py    # Duplicate Record Detection
│       ├── integrity_checks.py    # Referential Integrity & Orphaned FK Checks
│       └── business_rules.py      # Range, Date, Email Regex & Math Validation
│
└── tests/
    ├── conftest.py                # Resilient PyTest Connection Fixtures
    ├── test_data_quality.py       # Data Quality & Quarantine Tests
    ├── test_data_models.py        # Dimensional Schema & Financial Math Tests
    └── test_pipeline.py           # End-to-End Pipeline Execution Tests
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Amanvarma2231/Enterprise-Data_Warehouse.git
cd Enterprise-Data_Warehouse
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the End-to-End Pipeline
```bash
# Execute full pipeline with sample data
python src/pipeline.py --mode all --sample

# Or generate full-scale 200k+ enterprise dataset
python src/pipeline.py --mode all
```

### 4. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 5. Launch Local BI Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 👨‍💻 Author & Contact Details

**Aman Varma**  
*Data Engineer & Analytics Modeler*  

- **GitHub:** [https://github.com/Amanvarma2231](https://github.com/Amanvarma2231)  
- **Live App:** [https://enterprise-datawarehouse-amhwlzks6yuybmcbxtls2v.streamlit.app/](https://enterprise-datawarehouse-amhwlzks6yuybmcbxtls2v.streamlit.app/)  
- **Project Repository:** [https://github.com/Amanvarma2231/Enterprise-Data_Warehouse](https://github.com/Amanvarma2231/Enterprise-Data_Warehouse)  
- **Contact:** Open for collaboration and opportunities in Data Engineering, Data Modeling, and Analytics Architecture.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
