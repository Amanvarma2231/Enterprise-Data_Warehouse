import argparse
import sys
import time
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
from src.governance.metadata_manager import run_governance_generation
from src.ingestion.load_csv import load_raw_csvs_to_staging
from src.transformation.transformer import transform_and_build_warehouse
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


def run_pipeline(mode: str = "all", use_sample: bool = False):
    """Execute requested pipeline workflow stage."""
    start_time = time.time()
    print_banner()
    
    target_dir = SAMPLE_DATA_DIR if use_sample else RAW_DATA_DIR
    
    con = duckdb.connect(str(DUCKDB_PATH))
    
    if mode in ("generate", "all"):
        console.rule("[bold yellow]Phase 1: Synthetic Data Generation with Quality Anomalies[/bold yellow]")
        if use_sample:
            generate_all_data(n_customers=2000, n_products=300, n_stores=20, n_orders=10000, target_dir=target_dir)
        else:
            # Check if raw data already exists, if not generate
            if not (target_dir / "customers.csv").exists():
                generate_all_data(n_customers=10000, n_products=1000, n_stores=50, n_orders=50000, target_dir=target_dir)
            else:
                console.print(f"[green]✔ Existing raw datasets found in {target_dir.name}/. Proceeding...[/green]")

    if mode in ("ingest", "all"):
        console.rule("[bold yellow]Phase 2: High-Speed Staging Ingestion[/bold yellow]")
        load_raw_csvs_to_staging(source_dir=target_dir, db_path=DUCKDB_PATH)

    if mode in ("validate", "all"):
        console.rule("[bold yellow]Phase 3: 10-Point Data Quality Audit & Quarantine Routing[/bold yellow]")
        run_dq_pipeline(con)

    if mode in ("transform", "all"):
        console.rule("[bold yellow]Phase 4: Dimensional Star Schema Transformation[/bold yellow]")
        transform_and_build_warehouse(con)

    if mode in ("profile", "all"):
        console.rule("[bold yellow]Phase 5: Metadata Catalog & Lineage Generation[/bold yellow]")
        run_governance_generation()

    elapsed = time.time() - start_time
    con.close()
    
    console.rule("[bold green]Execution Successfully Completed[/bold green]")
    console.print(f"[bold green]✔ Pipeline execution finished in {elapsed:.2f} seconds![/bold green]")


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
