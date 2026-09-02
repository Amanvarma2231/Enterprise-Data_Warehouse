"""
Multi-Source Ingestion Pipeline Coordinator
Orchestrates CSV, MySQL, PostgreSQL, and MongoDB Connectors into Unified Staging Layer
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import DUCKDB_PATH, RAW_DATA_DIR, SAMPLE_DATA_DIR
from src.ingestion.load_csv import load_raw_csvs_to_staging
from src.utils.logger import logger


class IngestionPipeline:
    def __init__(self, db_path: Path = DUCKDB_PATH, source_dir: Path = RAW_DATA_DIR):
        self.db_path = db_path
        self.source_dir = source_dir

    def run(self) -> dict[str, int]:
        logger.info(f"Starting Ingestion Pipeline from {self.source_dir} to {self.db_path}")
        counts = load_raw_csvs_to_staging(source_dir=self.source_dir, db_path=self.db_path)
        logger.info(f"Ingestion Pipeline Completed. Loaded {sum(counts.values()):,} total rows.")
        return counts


if __name__ == "__main__":
    pipeline = IngestionPipeline()
    pipeline.run()
