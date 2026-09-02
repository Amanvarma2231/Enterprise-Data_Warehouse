# 🔄 RetailSphere ETL / ELT Pipeline Design Document

## 1. ETL vs. ELT Architectural Strategy
RetailSphere employs a modern **Hybrid ELT (Extract-Load-Transform)** approach:
- **Extract & Load (EL):** Python ingestion connectors pull data verbatim from heterogeneous sources (MySQL, PostgreSQL, MongoDB, CSV) into a dedicated **Staging schema** (`staging.*`) without business mutations.
- **Transform (T):** High-speed SQL transformations executed within DuckDB / PostgreSQL / dbt handle deduplication, surrogate key assignment, dimensional modeling, and mart aggregations.

```
[Operational Feeds] ──(Python Load)──▶ [Staging Tables] ──(SQL Transform)──▶ [Star Schema Warehouse]
```

## 2. Pipeline Execution Modes
The pipeline orchestrator (`src/pipeline.py` / `scripts/run_pipeline.py`) supports flexible execution modes:
- `--mode all`: Full end-to-end extraction, quality validation, transformation, metadata cataloging, and profiling.
- `--mode ingest`: Ingests raw CSV and operational database feeds into staging.
- `--mode dq`: Executes 10-point data quality quarantine audit.
- `--mode transform`: Builds `dim_*` and `fact_*` tables.
- `--mode governance`: Generates data dictionary, lineage, and markdown catalogs.
- `--mode profile`: Calculates statistical column profiling scores.
