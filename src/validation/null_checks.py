"""
Data Quality Check: NULL / Missing Value Validations
"""

import duckdb
import pandas as pd


def check_null_counts(con: duckdb.DuckDBPyConnection, table_name: str, critical_columns: list[str]) -> list[dict]:
    """Check for null occurrences in designated critical attributes."""
    results = []
    total_rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    
    if total_rows == 0:
        return results
        
    for col in critical_columns:
        null_count = con.execute(f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE {col} IS NULL 
               OR TRIM(CAST({col} AS VARCHAR)) = '' 
               OR LOWER(TRIM(CAST({col} AS VARCHAR))) = 'nan'
        """).fetchone()[0]
        
        null_pct = round((null_count / total_rows) * 100.0, 3)
        status = "PASSED" if null_count == 0 else "FAILED"
        
        results.append({
            "check_category": "Null Check",
            "table_name": table_name,
            "column_name": col,
            "total_rows": total_rows,
            "failed_rows": null_count,
            "failure_rate_pct": null_pct,
            "status": status,
            "severity": "CRITICAL" if "id" in col or "key" in col else "WARNING",
            "rule_description": f"Column {col} must not contain NULL or empty string values",
        })
        
    return results
