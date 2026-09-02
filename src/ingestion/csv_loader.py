"""
CSV Ingestion Module
Loads Raw Omnichannel CSV Feeds into DuckDB/PostgreSQL Staging Tables
"""

import sys
from pathlib import Path
import duckdb
import pandas as pd

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import DUCKDB_PATH, RAW_DATA_DIR, SAMPLE_DATA_DIR
from src.ingestion.load_csv import load_raw_csvs_to_staging


def load_csv_files(source_dir: Path = RAW_DATA_DIR, db_path: Path = DUCKDB_PATH) -> dict[str, int]:
    """Load raw CSV data into staging tables."""
    return load_raw_csvs_to_staging(source_dir=source_dir, db_path=db_path)


if __name__ == "__main__":
    load_csv_files()
