# RetailSphere Enterprise Data Modelling Standards & Conventions

## 1. Naming Conventions

- **Schema Names:** Lowercase snake_case (`staging`, `warehouse`, `quarantine`, `analytics`).
- **Dimension Tables:** Prefix `dim_` (e.g., `dim_customer`, `dim_product`, `dim_store`, `dim_date`).
- **Fact Tables:** Prefix `fact_` (e.g., `fact_sales`, `fact_payments`).
- **Analytical Marts:** Prefix `mart_` (e.g., `mart_monthly_store_performance`, `mart_customer_rfm`).
- **Surrogate Keys:** Named `<entity>_key` with `BIGINT` or `INTEGER` data type.
- **Natural / Business Keys:** Named `<entity>_id` matching source system keys.
- **Audit Columns:** Preceded with underscore (e.g., `_loaded_at`, `_source_file`).

---

## 2. Dimensional Modelling Rules (Kimball Methodology)

1. **Grain Declaration:** Every Fact table must have an explicitly documented atomic grain.
   - `fact_sales`: One row per line item in a completed retail sales order.
   - `fact_payments`: One row per financial settlement attempt.
2. **Conformed Dimensions:** Dimensions like `dim_date`, `dim_customer`, and `dim_store` must be shared across all business processes to ensure drill-across query consistency.
3. **Surrogate Keys:** Natural keys from upstream systems must never be used as primary keys in the dimensional model. Surrogate keys shield the warehouse from upstream key reuse and support SCD Type 2 tracking.
4. **Slowly Changing Dimensions (SCD):**
   - Customer dimension implements **SCD Type 1** for rapid operational attribute updates with `row_effective_date`, `row_expiration_date`, and `is_current` flags to support seamless evolution to **SCD Type 2**.
