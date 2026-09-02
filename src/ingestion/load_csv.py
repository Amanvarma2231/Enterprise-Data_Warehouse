import sys
from pathlib import Path
import duckdb
import pandas as pd
from rich.console import Console

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.config import DUCKDB_PATH, RAW_DATA_DIR, RAW_FILES, SQL_DIR

console = Console(soft_wrap=True)


def get_db_connection(db_path: Path = DUCKDB_PATH) -> duckdb.DuckDBPyConnection:
    """Initialize and return DuckDB connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def initialize_schemas(con: duckdb.DuckDBPyConnection):
    """Execute DDL scripts to create staging and warehouse schemas."""
    con.execute("CREATE SCHEMA IF NOT EXISTS staging;")
    con.execute("CREATE SCHEMA IF NOT EXISTS warehouse;")
    con.execute("CREATE SCHEMA IF NOT EXISTS quarantine;")
    
    staging_ddl_path = SQL_DIR / "ddl" / "01_staging_schema.sql"
    if staging_ddl_path.exists():
        with open(staging_ddl_path, "r", encoding="utf-8") as f:
            con.execute(f.read())
            
    warehouse_ddl_path = SQL_DIR / "ddl" / "02_warehouse_schema.sql"
    if warehouse_ddl_path.exists():
        with open(warehouse_ddl_path, "r", encoding="utf-8") as f:
            con.execute(f.read())


def load_raw_csvs_to_staging(
    source_dir: Path = RAW_DATA_DIR,
    db_path: Path = DUCKDB_PATH
) -> dict[str, int]:
    """Ingest CSV files into staging tables."""
    console.print(f"[bold cyan][*] Ingesting CSV files from {source_dir.name}/ into Staging Schema...[/bold cyan]")
    con = get_db_connection(db_path)
    initialize_schemas(con)
    
    results = {}
    
    table_mappings = {
        "customers": "staging.stg_customers",
        "products": "staging.stg_products",
        "stores": "staging.stg_stores",
        "orders": "staging.stg_orders",
        "order_items": "staging.stg_order_items",
        "payments": "staging.stg_payments",
    }
    
    for entity, filename in RAW_FILES.items():
        file_path = source_dir / filename
        if not file_path.exists():
            console.print(f"[yellow][!] Warning: {filename} not found in {source_dir}. Skipping...[/yellow]")
            continue
            
        staging_table = table_mappings[entity]
        
        # Load CSV via DuckDB read_csv_auto for high speed
        con.execute(f"TRUNCATE TABLE {staging_table};")
        
        # Read with auto column matching
        df = pd.read_csv(file_path, dtype=str)
        df["_ingested_at"] = pd.Timestamp.now()
        df["_source_file"] = filename
        
        con.register("df_temp", df)
        con.execute(f"INSERT INTO {staging_table} SELECT * FROM df_temp;")
        con.unregister("df_temp")
        
        count = con.execute(f"SELECT COUNT(*) FROM {staging_table}").fetchone()[0]
        results[entity] = count
        console.print(f"  [green]✔ Loaded {entity:<12}[/green] -> [bold white]{staging_table}[/bold white] ({count:,} rows)")
        
    con.close()
    return results


if __name__ == "__main__":
    load_raw_csvs_to_staging()
