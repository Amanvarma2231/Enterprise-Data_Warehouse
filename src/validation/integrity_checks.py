"""
Data Quality Check: Foreign Key Referential Integrity & Range Validation
"""

import duckdb


def check_foreign_key_integrity(
    con: duckdb.DuckDBPyConnection,
    child_table: str,
    child_fk_col: str,
    parent_table: str,
    parent_pk_col: str
) -> dict:
    """Validate referential integrity between child and parent tables."""
    total_child_rows = con.execute(f"SELECT COUNT(*) FROM {child_table}").fetchone()[0]
    
    if total_child_rows == 0:
        return {
            "check_category": "Referential Integrity",
            "table_name": child_table,
            "column_name": child_fk_col,
            "total_rows": 0,
            "failed_rows": 0,
            "failure_rate_pct": 0.0,
            "status": "PASSED",
            "severity": "CRITICAL",
            "rule_description": f"FK {child_table}.{child_fk_col} must exist in {parent_table}.{parent_pk_col}",
        }
        
    orphan_query = f"""
        SELECT COUNT(*)
        FROM {child_table} c
        LEFT JOIN {parent_table} p 
            ON (TRY_CAST(c.{child_fk_col} AS BIGINT) = TRY_CAST(p.{parent_pk_col} AS BIGINT)
                OR TRIM(CAST(c.{child_fk_col} AS VARCHAR)) = TRIM(CAST(p.{parent_pk_col} AS VARCHAR)))
        WHERE c.{child_fk_col} IS NOT NULL 
          AND TRIM(CAST(c.{child_fk_col} AS VARCHAR)) != ''
          AND p.{parent_pk_col} IS NULL
    """
    orphan_count = con.execute(orphan_query).fetchone()[0]
    orphan_pct = round((orphan_count / total_child_rows) * 100.0, 3)
    status = "PASSED" if orphan_count == 0 else "FAILED"
    
    return {
        "check_category": "Referential Integrity",
        "table_name": child_table,
        "column_name": child_fk_col,
        "total_rows": total_child_rows,
        "failed_rows": orphan_count,
        "failure_rate_pct": orphan_pct,
        "status": status,
        "severity": "CRITICAL",
        "rule_description": f"FK {child_table}.{child_fk_col} must resolve to existing {parent_table}.{parent_pk_col}",
    }
