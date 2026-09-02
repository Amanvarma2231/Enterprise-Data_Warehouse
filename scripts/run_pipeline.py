"""
Execute End-to-End RetailSphere ETL / ELT Pipeline
CLI Entrypoint for Ingestion, Validation, Transformation, and Governance
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Execute RetailSphere End-to-End Pipeline")
    parser.add_argument("--mode", choices=["all", "ingest", "dq", "transform", "governance", "profile"], default="all")
    parser.add_argument("--sample", action="store_true", help="Run with sample lightweight data")
    args = parser.parse_args()

    run_pipeline(mode=args.mode, use_sample=args.sample)


if __name__ == "__main__":
    main()
