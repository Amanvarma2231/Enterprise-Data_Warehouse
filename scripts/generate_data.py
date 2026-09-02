"""
Generate Synthetic Enterprise Retail Datasets
CLI Wrapper for RetailSphere Data Generator
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import RAW_DATA_DIR, SAMPLE_DATA_DIR
from src.data_generator import generate_all_data


def main():
    parser = argparse.ArgumentParser(description="Generate RetailSphere Synthetic Datasets")
    parser.add_argument("--customers", type=int, default=10000, help="Number of customer records (default: 10,000)")
    parser.add_argument("--products", type=int, default=1000, help="Number of product records (default: 1,000)")
    parser.add_argument("--stores", type=int, default=50, help="Number of store records (default: 50)")
    parser.add_argument("--orders", type=int, default=50000, help="Number of order records (default: 50,000)")
    parser.add_argument("--sample", action="store_true", help="Generate lightweight dataset in data/sample")
    parser.add_argument("--no-anomalies", action="store_true", help="Do not inject intentional data quality anomalies")

    args = parser.parse_args()
    target = SAMPLE_DATA_DIR if args.sample else RAW_DATA_DIR

    print(f"[*] Generating synthetic retail data into: {target}")
    generate_all_data(
        n_customers=2000 if args.sample else args.customers,
        n_products=300 if args.sample else args.products,
        n_stores=20 if args.sample else args.stores,
        n_orders=10000 if args.sample else args.orders,
        target_dir=target,
        inject_anomalies=not args.no_anomalies,
    )
    print(f"[SUCCESS] Synthetic data generation complete!")


if __name__ == "__main__":
    main()
