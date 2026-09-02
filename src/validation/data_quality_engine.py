import sys
from datetime import datetime
from pathlib import Path
import duckdb
import pandas as pd
from rich.console import Console
from rich.table import Table

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.config import DOCS_DIR, DUCKDB_PATH, QUARANTINE_DATA_DIR
from src.validation.business_rules import (
    check_email_syntax_validity,
    check_future_order_dates,
    check_line_total_calculation,
    check_positive_quantities,
)
from src.validation.duplicate_checks import check_primary_key_uniqueness
from src.validation.integrity_checks import check_foreign_key_integrity
from src.validation.null_checks import check_null_counts

console = Console(soft_wrap=True)


class DataQualityEngine:
    """Enterprise Data Quality Evaluation and Quarantine Orchestrator."""

    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con
        self.results: list[dict] = []

    def run_all_quality_checks(self) -> list[dict]:
        """Execute comprehensive 10-point data quality suite."""
        console.print("[bold yellow][*] Executing Enterprise Data Quality Validation Suite...[/bold yellow]")
        self.results = []
        
        # 1. Null Checks on Critical Keys
        self.results.extend(check_null_counts(self.con, "staging.stg_customers", ["customer_id", "first_name", "email"]))
        self.results.extend(check_null_counts(self.con, "staging.stg_products", ["product_id", "sku", "unit_price"]))
        self.results.extend(check_null_counts(self.con, "staging.stg_stores", ["store_id", "store_name", "region"]))
        self.results.extend(check_null_counts(self.con, "staging.stg_orders", ["order_id", "customer_id", "order_date"]))
        self.results.extend(check_null_counts(self.con, "staging.stg_order_items", ["order_item_id", "order_id", "product_id"]))
        self.results.extend(check_null_counts(self.con, "staging.stg_payments", ["payment_id", "order_id", "payment_amount"]))

        # 2. Duplicate / Primary Key Uniqueness Checks
        self.results.append(check_primary_key_uniqueness(self.con, "staging.stg_customers", ["customer_id"]))
        self.results.append(check_primary_key_uniqueness(self.con, "staging.stg_products", ["product_id"]))
        self.results.append(check_primary_key_uniqueness(self.con, "staging.stg_stores", ["store_id"]))
        self.results.append(check_primary_key_uniqueness(self.con, "staging.stg_orders", ["order_id"]))
        self.results.append(check_primary_key_uniqueness(self.con, "staging.stg_order_items", ["order_item_id"]))
        self.results.append(check_primary_key_uniqueness(self.con, "staging.stg_payments", ["payment_id"]))

        # 3. Foreign Key / Referential Integrity Checks
        self.results.append(check_foreign_key_integrity(
            self.con, "staging.stg_orders", "customer_id", "staging.stg_customers", "customer_id"
        ))
        self.results.append(check_foreign_key_integrity(
            self.con, "staging.stg_orders", "store_id", "staging.stg_stores", "store_id"
        ))
        self.results.append(check_foreign_key_integrity(
            self.con, "staging.stg_order_items", "order_id", "staging.stg_orders", "order_id"
        ))
        self.results.append(check_foreign_key_integrity(
            self.con, "staging.stg_order_items", "product_id", "staging.stg_products", "product_id"
        ))
        self.results.append(check_foreign_key_integrity(
            self.con, "staging.stg_payments", "order_id", "staging.stg_orders", "order_id"
        ))

        # 4. Business Logic, Range & Date Rules
        self.results.append(check_positive_quantities(self.con))
        self.results.append(check_future_order_dates(self.con))
        self.results.append(check_email_syntax_validity(self.con))
        self.results.append(check_line_total_calculation(self.con))

        return self.results

    def route_quarantine_records(self) -> dict[str, int]:
        """Isolate anomalous records and persist them into quarantine tables and CSVs."""
        console.print("[bold magenta][*] Routing anomalous records to Quarantine Storage...[/bold magenta]")
        QUARANTINE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        self.con.execute("CREATE SCHEMA IF NOT EXISTS quarantine;")
        
        # 1. Quarantine Orders
        self.con.execute("DROP TABLE IF EXISTS quarantine.quarantine_orders;")
        self.con.execute("""
            CREATE TABLE quarantine.quarantine_orders AS
            SELECT 
                o.*,
                CASE 
                    WHEN o.customer_id IS NULL OR TRIM(o.customer_id) = '' THEN 'ERR_NULL_CUSTOMER_KEY'
                    WHEN TRY_CAST(o.order_date AS DATE) > CURRENT_DATE THEN 'ERR_FUTURE_ORDER_DATE'
                    ELSE 'ERR_DUPLICATE_ORDER'
                END AS rejection_reason_code,
                CURRENT_TIMESTAMP AS quarantined_at
            FROM staging.stg_orders o
            WHERE o.customer_id IS NULL 
               OR TRIM(o.customer_id) = ''
               OR TRY_CAST(o.order_date AS DATE) > CURRENT_DATE
               OR o.order_id IN (
                   SELECT order_id FROM staging.stg_orders GROUP BY order_id HAVING COUNT(*) > 1
               );
        """)
        
        # 2. Quarantine Order Items
        self.con.execute("DROP TABLE IF EXISTS quarantine.quarantine_order_items;")
        self.con.execute("""
            CREATE TABLE quarantine.quarantine_order_items AS
            SELECT 
                oi.*,
                CASE 
                    WHEN TRY_CAST(oi.quantity AS INTEGER) <= 0 THEN 'ERR_INVALID_QUANTITY_NON_POSITIVE'
                    WHEN dp.product_id IS NULL THEN 'ERR_ORPHAN_PRODUCT_KEY'
                    WHEN TRY_CAST(oi.unit_price AS DECIMAL(12, 2)) <= 0 THEN 'ERR_INVALID_UNIT_PRICE'
                    ELSE 'ERR_MATH_MISMATCH'
                END AS rejection_reason_code,
                CURRENT_TIMESTAMP AS quarantined_at
            FROM staging.stg_order_items oi
            LEFT JOIN staging.stg_products dp 
                ON TRIM(oi.product_id) = TRIM(dp.product_id)
            WHERE TRY_CAST(oi.quantity AS INTEGER) <= 0
               OR dp.product_id IS NULL
               OR TRY_CAST(oi.unit_price AS DECIMAL(12, 2)) <= 0;
        """)

        # 3. Quarantine Customers
        self.con.execute("DROP TABLE IF EXISTS quarantine.quarantine_customers;")
        self.con.execute("""
            CREATE TABLE quarantine.quarantine_customers AS
            SELECT 
                c.*,
                'ERR_MALFORMED_EMAIL_SYNTAX' AS rejection_reason_code,
                CURRENT_TIMESTAMP AS quarantined_at
            FROM staging.stg_customers c
            WHERE c.email NOT LIKE '%@%.%' 
               OR c.email IS NULL;
        """)
        
        # Export quarantine tables to CSV for audit
        quarantine_counts = {}
        for qtable in ["quarantine_orders", "quarantine_order_items", "quarantine_customers"]:
            count = self.con.execute(f"SELECT COUNT(*) FROM quarantine.{qtable}").fetchone()[0]
            quarantine_counts[qtable] = count
            df_q = self.con.execute(f"SELECT * FROM quarantine.{qtable}").df()
            df_q.to_csv(QUARANTINE_DATA_DIR / f"{qtable}.csv", index=False)
            console.print(f"  [red]⚠ Quarantined {count:,} records[/red] -> [bold white]{qtable}.csv[/bold white]")
            
        return quarantine_counts

    def display_and_export_report(self) -> pd.DataFrame:
        """Display summary in terminal and write Markdown report."""
        df_results = pd.DataFrame(self.results)
        
        table = Table(title="Enterprise Data Quality Validation Summary", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan")
        table.add_column("Table", style="white")
        table.add_column("Target Column", style="magenta")
        table.add_column("Failures", justify="right")
        table.add_column("Failure Rate", justify="right")
        table.add_column("Severity", justify="center")
        table.add_column("Status", justify="center")

        for _, row in df_results.iterrows():
            status_style = "[bold green]PASSED[/bold green]" if row["status"] == "PASSED" else "[bold red]FAILED[/bold red]"
            sev_style = f"[bold red]{row['severity']}[/bold red]" if row["severity"] == "CRITICAL" else f"[yellow]{row['severity']}[/yellow]"
            table.add_row(
                row["check_category"],
                row["table_name"],
                row["column_name"],
                f"{row['failed_rows']:,}",
                f"{row['failure_rate_pct']:.2f}%",
                sev_style,
                status_style
            )

        console.print(table)
        
        # Export to Markdown Document
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = DOCS_DIR / "data_quality_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# RetailSphere Enterprise Data Quality Validation Report\n\n")
            f.write(f"**Execution Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 1. Quality Execution Summary\n\n")
            f.write(f"- **Total Checks Evaluated:** {len(df_results)}\n")
            f.write(f"- **Passed Checks:** {len(df_results[df_results['status'] == 'PASSED'])}\n")
            f.write(f"- **Failed / Quarantined Checks:** {len(df_results[df_results['status'] == 'FAILED'])}\n\n")
            f.write("## 2. Detailed Rule Validation Matrix\n\n")
            f.write(df_results.to_markdown(index=False))
            f.write("\n\n## 3. Quarantine Routing Strategy\n\n")
            f.write("All records violating critical integrity rules (Null PKs, orphaned FKs, negative quantity) ")
            f.write("are automatically diverted to `data/quarantine/` and isolated from downstream Star Schema marts.\n")
            
        console.print(f"[bold green]✔ Data Quality report saved to {report_path.name}[/bold green]")
        return df_results


def run_dq_pipeline(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Convenience runner for full Data Quality cycle."""
    engine = DataQualityEngine(con)
    engine.run_all_quality_checks()
    engine.route_quarantine_records()
    return engine.display_and_export_report()


if __name__ == "__main__":
    con = duckdb.connect(str(DUCKDB_PATH))
    run_dq_pipeline(con)
    con.close()
