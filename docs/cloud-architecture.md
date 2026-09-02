# ☁️ Cloud Architecture & BigQuery Deployment Guide

## 1. Cloud Architecture Overview
RetailSphere is engineered to be database-agnostic. While running locally on DuckDB and PostgreSQL for zero-cost developer testing, production DDLs are provided for Google Cloud BigQuery and Snowflake.

```
[Local PostgreSQL / CSV] ──(GCS Ingestion)──▶ [BigQuery Dataset: retailsphere_dw]
                                                      │
                                                      ├── Partitions: DATE(order_date)
                                                      └── Clustering: store_key, product_key
```

## 2. BigQuery Partitioning & Clustering Strategy
- **Partitioning:** `fact_sales` is partitioned by day on `order_date`. This prevents full-table scans during monthly and quarterly reporting, cutting query costs by up to 85%.
- **Clustering:** Clustered by `store_key` and `product_key` to colocate related transaction blocks on disk for rapid multi-dimensional aggregation.

## 3. Step-by-Step BigQuery Deployment
1. Set up GCP project and BigQuery dataset:
   ```bash
   bq mk --dataset --location=US retailsphere_dw
   ```
2. Execute the production partitioned DDL:
   ```bash
   bq query --use_legacy_sql=false < sql/ddl/04_bigquery_ddl.sql
   ```
3. Load data from Cloud Storage:
   ```bash
   bq load --source_format=CSV --skip_leading_rows=1 retailsphere_dw.dim_customer gs://retailsphere-bucket/customers.csv
   ```
