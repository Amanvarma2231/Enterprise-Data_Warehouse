"""
Enterprise Data Warehouse Master Pipeline Orchestrator & Audit Runner
RetailSphere Analytics & Data Governance Platform
"""

import argparse
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import duckdb
from rich.console import Console
from rich.panel import Panel

from src.config import DUCKDB_PATH, RAW_DATA_DIR, SAMPLE_DATA_DIR
from src.data_generator import generate_all_data
from src.governance.data_profiler import profile_warehouse_tables
from src.governance.metadata_manager import run_governance_generation
from src.ingestion.load_csv import load_raw_csvs_to_staging
from src.transformation.transformer import transform_and_build_warehouse
from src.utils.logger import logger
from src.validation.data_quality_engine import run_dq_pipeline

console = Console(soft_wrap=True)


def print_banner():
    """Print visually striking enterprise pipeline banner."""
    banner_text = """
 =========================================================================
   RETAILSPHERE ENTERPRISE SALES & CUSTOMER DATA WAREHOUSE PLATFORM       
   Kimball Star Schema | 10-Point DQ Engine | Governance & Lineage        
 =========================================================================
"""
    console.print(Panel(banner_text.strip(), border_style="cyan"))


def record_pipeline_audit(
    con: duckdb.DuckDBPyConnection,
    run_id: str,
    start_time: datetime,
    end_time: datetime,
    mode: str,
    status: str,
    ingested_rows: int = 0,
    transformed_rows: int = 0,
    quarantined_rows: int = 0
):
    """Log pipeline execution metadata directly into the warehouse audit table."""
    con.execute("CREATE SCHEMA IF NOT EXISTS warehouse;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS warehouse.dim_pipeline_execution_log (
            run_id              VARCHAR(50) PRIMARY KEY,
            execution_mode      VARCHAR(50),
            started_at          TIMESTAMP,
            completed_at        TIMESTAMP,
            duration_seconds    DECIMAL(8, 2),
            records_ingested    BIGINT,
            records_transformed BIGINT,
            records_quarantined BIGINT,
            status              VARCHAR(20),
            executed_by         VARCHAR(100)
        );
    """)
    
    duration = (end_time - start_time).total_seconds()
    
    con.execute("""
        INSERT INTO warehouse.dim_pipeline_execution_log (
            run_id, execution_mode, started_at, completed_at, duration_seconds,
            records_ingested, records_transformed, records_quarantined, status, executed_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        run_id, mode, start_time, end_time, duration,
        ingested_rows, transformed_rows, quarantined_rows, status, "RetailSphere Orchestrator"
    ])
    logger.info(f"Audit log recorded for Run ID: {run_id} | Status: {status} | Duration: {duration:.2f}s")


def run_pipeline(mode: str = "all", use_sample: bool = False) -> dict:
    """Execute requested pipeline workflow stage with full auditing & logging."""
    run_id = f"RUN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    start_dt = datetime.now()
    start_time = time.time()
    
    print_banner()
    logger.info(f"Initiating Enterprise Warehouse Pipeline [Run ID: {run_id}] | Mode: {mode}")
    
    target_dir = SAMPLE_DATA_DIR if use_sample else RAW_DATA_DIR
    con = duckdb.connect(str(DUCKDB_PATH))
    
    ingested_count = 0
    transformed_count = 0
    quarantined_count = 0
    
    try:
        if mode in ("generate", "all"):
            console.rule("[bold yellow]Phase 1: Synthetic Data Generation with Quality Anomalies[/bold yellow]")
            logger.info("Generating operational retail datasets with deliberate anomalies...")
            if use_sample or not (target_dir / "customers.csv").exists():
                generate_all_data(n_customers=2000, n_products=300, n_stores=20, n_orders=10000, target_dir=target_dir)
            else:
                console.print(f"[green]✔ Existing raw datasets found in {target_dir.name}/. Proceeding...[/green]")

        if mode in ("ingest", "all"):
            console.rule("[bold yellow]Phase 2: High-Speed Staging Ingestion[/bold yellow]")
            logger.info("Ingesting operational CSV files into staging schema...")
            ingest_results = load_raw_csvs_to_staging(source_dir=target_dir, db_path=DUCKDB_PATH)
            ingested_count = sum(ingest_results.values())

        if mode in ("validate", "all"):
            console.rule("[bold yellow]Phase 3: 10-Point Data Quality Audit & Quarantine Routing[/bold yellow]")
            logger.info("Running 10-point data quality verification and routing anomalies...")
            run_dq_pipeline(con)
            q_orders = con.execute("SELECT COUNT(*) FROM quarantine.quarantine_orders").fetchone()[0]
            q_items = con.execute("SELECT COUNT(*) FROM quarantine.quarantine_order_items").fetchone()[0]
            q_cust = con.execute("SELECT COUNT(*) FROM quarantine.quarantine_customers").fetchone()[0]
            quarantined_count = q_orders + q_items + q_cust

        if mode in ("transform", "all"):
            console.rule("[bold yellow]Phase 4: Dimensional Star Schema Transformation[/bold yellow]")
            logger.info("Populating Kimball Star Schema dimensional tables and analytical marts...")
            transform_counts = transform_and_build_warehouse(con)
            transformed_count = sum(transform_counts.values())

        if mode in ("profile", "all"):
            console.rule("[bold yellow]Phase 5: Metadata Catalog & Governance Profiling[/bold yellow]")
            logger.info("Generating metadata catalog, Excel data dictionary, and column profiling...")
            run_governance_generation()
            profile_warehouse_tables(con)

        end_dt = datetime.now()
        record_pipeline_audit(
            con, run_id, start_dt, end_dt, mode, "SUCCESS",
            ingested_count, transformed_count, quarantined_count
        )
        status = "SUCCESS"

    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        end_dt = datetime.now()
        record_pipeline_audit(
            con, run_id, start_dt, end_dt, mode, "FAILED",
            ingested_count, transformed_count, quarantined_count
        )
        status = "FAILED"
        raise

    finally:
        con.close()

    elapsed = time.time() - start_time
    console.rule("[bold green]Execution Successfully Completed[/bold green]")
    console.print(f"[bold green]✔ Pipeline execution finished in {elapsed:.2f} seconds! (Audit logged in warehouse)[/bold green]")
    
    return {
        "run_id": run_id,
        "status": status,
        "duration_seconds": round(elapsed, 2),
        "ingested_count": ingested_count,
        "transformed_count": transformed_count,
        "quarantined_count": quarantined_count
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetailSphere Enterprise Data Warehouse Orchestrator")
    parser.add_argument(
        "--mode",
        choices=["generate", "ingest", "validate", "transform", "profile", "all"],
        default="all",
        help="Pipeline execution mode"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Run pipeline with lightweight sample dataset"
    )
    
    args = parser.parse_args()
    run_pipeline(mode=args.mode, use_sample=args.sample)
