"""
10-Point Data Quality Audit Engine
Executes Comprehensive Quality Checks on Staging and Warehouse Layers
"""

import duckdb
import pandas as pd
from src.utils.logger import logger
from src.validation.data_quality_engine import run_dq_pipeline


def execute_data_quality_checks(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Execute complete 10-point data quality audit."""
    logger.info("Executing 10-Point Data Quality suite...")
    return run_dq_pipeline(con)


if __name__ == "__main__":
    from src.config import DUCKDB_PATH
    con = duckdb.connect(str(DUCKDB_PATH))
    results = execute_data_quality_checks(con)
    print("Data Quality Results:", results)
    con.close()
