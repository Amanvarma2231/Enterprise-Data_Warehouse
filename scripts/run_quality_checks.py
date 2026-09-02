"""
Execute Standalone Data Quality & Statistical Profiling Engine
Generates Quality Audit Reports and Health Scorecards
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import duckdb
from src.config import DUCKDB_PATH
from src.validation.data_quality_engine import run_dq_pipeline
from src.governance.data_profiler import profile_warehouse_tables


def main():
    print(f"[*] Running standalone Data Quality & Profiling Suite on: {DUCKDB_PATH}")
    if not DUCKDB_PATH.exists():
        print(f"[ERROR] Database file not found at {DUCKDB_PATH}. Run scripts/run_pipeline.py first.")
        sys.exit(1)

    con = duckdb.connect(str(DUCKDB_PATH))
    print("\n--- 1. Running 10-Point Data Quality Audit ---")
    dq_results = run_dq_pipeline(con)

    print("\n--- 2. Running Column Statistical Health Profiler ---")
    profile_df = profile_warehouse_tables(con)

    con.close()
    print("\n[SUCCESS] Quality audit and statistical profiling completed successfully!")


if __name__ == "__main__":
    main()
