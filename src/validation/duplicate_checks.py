"""
Data Quality Check: Primary Key & Record Duplication Validations
"""

import duckdb


def check_primary_key_uniqueness(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    primary_key_cols: list[str]
) -> dict:
    """Validate that specified primary key columns are strictly unique."""
    pk_str = ", ".join(primary_key_cols)
    total_rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    
    if total_rows == 0:
        return {
            "check_category": "Duplicate Check",
            "table_name": table_name,
            "column_name": pk_str,
            "total_rows": 0,
            "failed_rows": 0,
            "failure_rate_pct": 0.0,
            "status": "PASSED",
            "severity": "CRITICAL",
            "rule_description": f"Primary key ({pk_str}) must be unique",
        }
        
    dup_query = f"""
        SELECT SUM(cnt - 1) FROM (
            SELECT {pk_str}, COUNT(*) as cnt
            FROM {table_name}
            WHERE {primary_key_cols[0]} IS NOT NULL
            GROUP BY {pk_str}
            HAVING COUNT(*) > 1
        ) sub
    """
    dup_res = con.execute(dup_query).fetchone()[0]
    dup_count = dup_res if dup_res is not None else 0
    dup_pct = round((dup_count / total_rows) * 100.0, 3)
    status = "PASSED" if dup_count == 0 else "FAILED"
    
    return {
        "check_category": "Duplicate Check",
        "table_name": table_name,
        "column_name": pk_str,
        "total_rows": total_rows,
        "failed_rows": dup_count,
        "failure_rate_pct": dup_pct,
        "status": status,
        "severity": "CRITICAL",
        "rule_description": f"Primary key ({pk_str}) must have zero duplicate occurrences",
    }
