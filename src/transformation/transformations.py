"""
Warehouse Transformation Orchestrator
Builds Conformed Dimensions, Line-Item Fact Sales, and Analytical Marts
"""

import duckdb
from src.transformation.transformer import transform_and_build_warehouse
from src.utils.logger import logger


def run_all_transformations(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Execute complete dimensional transformation logic."""
    logger.info("Executing full warehouse transformation pipeline...")
    return transform_and_build_warehouse(con)


if __name__ == "__main__":
    from src.config import DUCKDB_PATH
    con = duckdb.connect(str(DUCKDB_PATH))
    results = run_all_transformations(con)
    print("Transformation Row Counts:", results)
    con.close()
