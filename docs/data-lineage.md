# RetailSphere Data Platform - End-to-End Data Lineage

## 1. High-Level Pipeline Lineage Architecture

```mermaid
flowchart TD
    subgraph S1 [Operational Data Sources]
        C[customers.csv]
        P[products.csv]
        S[stores.csv]
        O[orders.csv]
        OI[order_items.csv]
        PY[payments.csv]
    end

    subgraph S2 [Ingestion & Staging Layer]
        SC[staging.stg_customers]
        SP[staging.stg_products]
        SS[staging.stg_stores]
        SO[staging.stg_orders]
        SOI[staging.stg_order_items]
        SPY[staging.stg_payments]
    end

    subgraph S3 [Data Quality & Quarantine Layer]
        DQ{Data Quality Engine\n10 Rule Checks}
        Q1[quarantine_orders]
        Q2[quarantine_order_items]
        Q3[quarantine_customers]
    end

    subgraph S4 [Dimensional Star Schema Warehouse]
        DC[dim_customer]
        DP[dim_product]
        DS[dim_store]
        DD[dim_date]
        FS[fact_sales]
        FP[fact_payments]
    end

    subgraph S5 [Analytical Marts & Semantic Layer]
        M1[mart_monthly_store_performance]
        M2[mart_customer_rfm]
        BI[Executive BI Dashboard]
        BQ[Google BigQuery Cloud DW]
    end

    C --> SC
    P --> SP
    S --> SS
    O --> SO
    OI --> SOI
    PY --> SPY

    SC & SP & SS & SO & SOI & SPY --> DQ
    DQ -- "Invalid Records" --> Q1 & Q2 & Q3
    DQ -- "Valid Cleansed Records" --> DC & DP & DS & DD

    SC --> DC
    SP --> DP
    SS --> DS
    SO & SOI & DC & DP & DS & DD --> FS
    SPY & SO & DC & DD --> FP

    FS & DS & DD --> M1
    FS & DC --> M2
    M1 & M2 & FS --> BI
    FS & DC & DP & DS & DD --> BQ
```

## 2. Table-to-Table Dependency Matrix

| Target Table | Source Entity | Transformation Type | Business Logic & Surrogate Key Generation |
| :--- | :--- | :--- | :--- |
| `dim_customer` | `staging.stg_customers` | Cleansing, Deduplication, SCD Type 1/2 | Deduped on `customer_id` keeping newest registration; surrogate key `customer_key` generated via window ranking |
| `dim_product` | `staging.stg_products` | Enrichment, Pricing Tiering | Added `profit_margin_pct` and classified into `Budget`, `Mid-Range`, `Premium`, `Luxury` tiers |
| `dim_store` | `staging.stg_stores` | Channel Grouping, Age Calculation | Segmented into `Physical Retail` vs `Digital Channel`; computed `store_age_years` |
| `dim_date` | Date Generator Algorithm | Conformed Calendar Dimension | Generates full calendar, fiscal periods (Indian FY April-March), weekend and holiday flags |
| `fact_sales` | `stg_orders`, `stg_order_items`, Dimensions | Fact Grain Joins & Financial Metrics | Grain: 1 row per order item. Evaluates `net_sales_amount`, `cost_amount`, `gross_profit_amount`, `profit_margin_pct` |
| `fact_payments` | `stg_payments`, `stg_orders`, `dim_customer` | Financial Reconciliation | Maps payment transactions, validates against order values, evaluates success rates |
| `mart_monthly_store_performance` | `fact_sales`, `dim_date`, `dim_store` | Periodic Monthly Snapshot Aggregation | Computes MoM revenue, order counts, gross profit, margin percentage per store and territory |
| `mart_customer_rfm` | `fact_sales`, `dim_customer` | Behavioral Customer Segmentation | Calculates Recency (days), Frequency (order count), Monetary (total spend), and assigns RFM tiers |
