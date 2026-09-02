"""
Synthetic Retail Data Generator with Intentional Quality Anomalies
Enterprise Sales & Customer Data Warehouse (RetailSphere)
"""

import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from faker import Faker

from src.config import RAW_DATA_DIR, SAMPLE_DATA_DIR

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Audio & Headphones", "Smartwatches", "Cameras", "Accessories"],
    "Apparel": ["Men's Wear", "Women's Wear", "Kids' Fashion", "Footwear", "Sportswear", "Winter Wear"],
    "Home & Kitchen": ["Cookware", "Small Appliances", "Furniture", "Home Decor", "Bedding", "Kitchen Storage"],
    "Beauty & Personal Care": ["Skincare", "Haircare", "Fragrances", "Makeup", "Men's Grooming", "Oral Care"],
    "Sports & Fitness": ["Gym Equipment", "Yoga & Pilates", "Outdoor Recreation", "Cycling", "Team Sports", "Supplements"],
    "Grocery & Gourmet": ["Organic Foods", "Beverages", "Snacks & Confectionery", "Baking Supplies", "Dairy Alternatives", "Gourmet Oils"],
}

REGIONS = {
    "North": ["Delhi", "Jaipur", "Lucknow", "Chandigarh", "Noida", "Gurugram"],
    "South": ["Bengaluru", "Chennai", "Hyderabad", "Kochi", "Coimbatore", "Mysuru"],
    "West": ["Mumbai", "Pune", "Ahmedabad", "Surat", "Goa", "Nagpur"],
    "East": ["Kolkata", "Bhubaneswar", "Patna", "Guwahati", "Ranchi", "Siliguri"],
    "Central": ["Bhopal", "Indore", "Raipur", "Jabalpur", "Gwalior", "Ujjain"],
}

CUSTOMER_SEGMENTS = ["Regular", "Premium", "VIP", "Corporate", "Occasional"]
ORDER_STATUSES = ["Completed", "Shipped", "Processing", "Cancelled", "Returned"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "NetBanking", "PayPal", "Cash on Delivery"]
PAYMENT_STATUSES = ["Success", "Failed", "Refunded", "Pending"]
STORE_TYPES = ["Physical Flagship", "Physical Standard", "Outlet Mall", "Online Store", "Express Kiosk"]


def generate_customers(n_customers: int) -> pd.DataFrame:
    """Generate synthetic customer profiles with realistic demographics."""
    records = []
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2026, 6, 30)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days

    for cid in range(1001, 1001 + n_customers):
        region = random.choice(list(REGIONS.keys()))
        city = random.choice(REGIONS[region])
        reg_days = random.randint(0, days_between_dates)
        reg_date = start_date + timedelta(days=reg_days)
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 999)}@{fake.free_email_domain()}"

        records.append({
            "customer_id": cid,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": fake.phone_number()[:15],
            "city": city,
            "state": region + " Province",
            "country": "India",
            "postal_code": fake.postcode(),
            "segment": random.choices(CUSTOMER_SEGMENTS, weights=[0.45, 0.25, 0.10, 0.05, 0.15])[0],
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "is_active": random.choices([True, False], weights=[0.92, 0.08])[0],
        })
    return pd.DataFrame(records)


def generate_products(n_products: int) -> pd.DataFrame:
    """Generate synthetic product catalog across realistic categories."""
    records = []
    sku_counter = 10001
    
    for pid in range(501, 501 + n_products):
        cat = random.choice(list(CATEGORIES.keys()))
        subcat = random.choice(CATEGORIES[cat])
        
        if cat == "Electronics":
            cost = round(random.uniform(500, 45000), 2)
            margin = random.uniform(1.15, 1.45)
        elif cat == "Apparel":
            cost = round(random.uniform(150, 3500), 2)
            margin = random.uniform(1.40, 2.20)
        elif cat == "Home & Kitchen":
            cost = round(random.uniform(250, 8000), 2)
            margin = random.uniform(1.30, 1.80)
        elif cat == "Beauty & Personal Care":
            cost = round(random.uniform(80, 2000), 2)
            margin = random.uniform(1.50, 2.50)
        elif cat == "Sports & Fitness":
            cost = round(random.uniform(300, 12000), 2)
            margin = random.uniform(1.25, 1.70)
        else:
            cost = round(random.uniform(40, 1200), 2)
            margin = random.uniform(1.15, 1.50)
            
        price = round(cost * margin, 2)
        sku = f"SKU-{cat[:3].upper()}-{sku_counter}"
        sku_counter += 1
        name = f"{subcat} - {fake.word().capitalize()} Model {random.randint(100, 999)}"

        records.append({
            "product_id": pid,
            "sku": sku,
            "product_name": name,
            "category": cat,
            "subcategory": subcat,
            "unit_cost": cost,
            "unit_price": price,
            "reorder_level": random.randint(10, 100),
            "is_discontinued": random.choices([False, True], weights=[0.95, 0.05])[0],
        })
    return pd.DataFrame(records)


def generate_stores(n_stores: int) -> pd.DataFrame:
    """Generate store metadata across physical and online channels."""
    records = []
    start_date = datetime(2018, 1, 1)
    
    # Store 1 is always the primary online digital storefront
    records.append({
        "store_id": 1,
        "store_name": "RetailSphere Online Portal",
        "store_type": "Online Store",
        "region": "National",
        "city": "Bengaluru",
        "state": "Digital HQ",
        "square_feet": 0,
        "opened_date": "2018-01-01",
        "manager_name": "E-Commerce Directorate",
    })
    
    for sid in range(2, 1 + n_stores):
        region = random.choice(list(REGIONS.keys()))
        city = random.choice(REGIONS[region])
        opened_days = random.randint(0, 2000)
        opened_date = start_date + timedelta(days=opened_days)
        stype = random.choices(STORE_TYPES[:-1], weights=[0.25, 0.45, 0.15, 0.15])[0]
        sqft = random.randint(1200, 15000) if "Kiosk" not in stype else random.randint(300, 800)

        records.append({
            "store_id": sid,
            "store_name": f"RetailSphere {city} {stype}",
            "store_type": stype,
            "region": region,
            "city": city,
            "state": region + " Province",
            "square_feet": sqft,
            "opened_date": opened_date.strftime("%Y-%m-%d"),
            "manager_name": fake.name(),
        })
    return pd.DataFrame(records)


def generate_orders_and_items(
    n_orders: int,
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    stores_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate correlated orders, order line items, and payment transactions."""
    orders = []
    order_items = []
    payments = []
    
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2026, 6, 30)
    total_days = (end_date - start_date).days
    
    customer_ids = customers_df["customer_id"].tolist()
    product_dict = products_df.set_index("product_id")[["unit_price", "unit_cost"]].to_dict("index")
    product_ids = list(product_dict.keys())
    store_ids = stores_df["store_id"].tolist()
    
    # Give digital store higher order volume
    store_weights = [0.35] + [0.65 / (len(store_ids) - 1)] * (len(store_ids) - 1)
    
    item_id_counter = 100001
    payment_id_counter = 200001
    
    for oid in range(50001, 50001 + n_orders):
        cid = random.choice(customer_ids)
        sid = random.choices(store_ids, weights=store_weights)[0]
        order_days = random.randint(0, total_days)
        odate = start_date + timedelta(days=order_days)
        ostatus = random.choices(ORDER_STATUSES, weights=[0.70, 0.12, 0.08, 0.05, 0.05])[0]
        
        # Generate 1 to 5 line items per order
        n_items = random.choices([1, 2, 3, 4, 5], weights=[0.50, 0.25, 0.15, 0.07, 0.03])[0]
        order_gross_total = 0.0
        order_discount_total = 0.0
        
        selected_products = random.sample(product_ids, min(n_items, len(product_ids)))
        
        for pid in selected_products:
            pinfo = product_dict[pid]
            qty = random.choices([1, 2, 3, 4, 5, 10], weights=[0.60, 0.22, 0.10, 0.04, 0.03, 0.01])[0]
            unit_price = pinfo["unit_price"]
            
            # Realistic discount logic (0%, 5%, 10%, 15%, 20%)
            discount_pct = random.choices([0.0, 0.05, 0.10, 0.15, 0.20], weights=[0.60, 0.15, 0.12, 0.08, 0.05])[0]
            discount_amt = round(qty * unit_price * discount_pct, 2)
            line_total = round((qty * unit_price) - discount_amt, 2)
            
            order_gross_total += qty * unit_price
            order_discount_total += discount_amt
            
            order_items.append({
                "order_item_id": item_id_counter,
                "order_id": oid,
                "product_id": pid,
                "quantity": qty,
                "unit_price": unit_price,
                "discount": discount_amt,
                "line_total": line_total,
            })
            item_id_counter += 1
            
        shipping_amt = 0.0 if order_gross_total > 1500 or sid != 1 else 99.0
        net_order_total = round(order_gross_total - order_discount_total + shipping_amt, 2)
        
        orders.append({
            "order_id": oid,
            "customer_id": cid,
            "store_id": sid,
            "order_date": odate.strftime("%Y-%m-%d"),
            "order_status": ostatus,
            "shipping_amount": shipping_amt,
            "discount_total": round(order_discount_total, 2),
            "payment_status": "Success" if ostatus in ["Completed", "Shipped", "Processing"] else "Cancelled" if ostatus == "Cancelled" else "Refunded",
        })
        
        # Correlated Payment Record
        pmethod = random.choice(PAYMENT_METHODS)
        pstatus = "Success" if ostatus in ["Completed", "Shipped", "Processing"] else ("Failed" if ostatus == "Cancelled" and random.random() < 0.5 else "Refunded")
        pay_date = odate + timedelta(minutes=random.randint(1, 120))
        
        payments.append({
            "payment_id": payment_id_counter,
            "order_id": oid,
            "payment_method": pmethod,
            "payment_status": pstatus,
            "payment_amount": net_order_total if pstatus != "Failed" else round(net_order_total * random.uniform(0.5, 1.0), 2),
            "payment_date": pay_date.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_ref": f"TXN-{fake.hexify(text='^^^^^^^^^^^^^^').upper()}",
        })
        payment_id_counter += 1
        
    return pd.DataFrame(orders), pd.DataFrame(order_items), pd.DataFrame(payments)


def inject_intentional_anomalies(
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
    payments_df: pd.DataFrame,
    anomaly_rate: float = 0.02
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Deliberately inject enterprise data quality anomalies into the raw data.
    This provides realistic test beds for DQ checks and quarantine routing.
    """
    print(f"[*] Injecting intentional data quality anomalies (rate: {anomaly_rate * 100:.1f}%)...")
    
    # 1. Null customer IDs in orders (Simulate guest checkout or ETL truncation)
    n_null_cust = max(5, int(len(orders_df) * anomaly_rate * 0.3))
    null_cust_indices = random.sample(range(len(orders_df)), n_null_cust)
    orders_df["customer_id"] = orders_df["customer_id"].astype("Int64")
    for idx in null_cust_indices:
        orders_df.iat[idx, orders_df.columns.get_loc("customer_id")] = pd.NA
        
    # 2. Duplicate order records (Simulate upstream message replay)
    n_dup_orders = max(3, int(len(orders_df) * anomaly_rate * 0.2))
    dup_orders = orders_df.iloc[:n_dup_orders].copy()
    orders_df = pd.concat([orders_df, dup_orders], ignore_index=True)
    
    # 3. Negative & Zero Quantities in Order Items (Simulate legacy return glitch)
    n_bad_qty = max(5, int(len(order_items_df) * anomaly_rate * 0.4))
    bad_qty_indices = random.sample(range(len(order_items_df)), n_bad_qty)
    for idx in bad_qty_indices:
        bad_val = random.choice([-1, -3, 0])
        order_items_df.iat[idx, order_items_df.columns.get_loc("quantity")] = bad_val
        
    # 4. Invalid Foreign Keys in Order Items (Referencing non-existent product IDs)
    n_bad_fk = max(5, int(len(order_items_df) * anomaly_rate * 0.3))
    bad_fk_indices = random.sample(range(len(order_items_df)), n_bad_fk)
    for idx in bad_fk_indices:
        order_items_df.iat[idx, order_items_df.columns.get_loc("product_id")] = 999999  # Orphan ID
        
    # 5. Invalid Email Formats in Customers (Missing domain or @ symbol)
    n_bad_email = max(5, int(len(customers_df) * anomaly_rate * 0.5))
    bad_email_indices = random.sample(range(len(customers_df)), n_bad_email)
    for idx in bad_email_indices:
        customers_df.iat[idx, customers_df.columns.get_loc("email")] = "invalid_user_at_domain_com"
        
    # 6. Future Order Dates (Simulate clock synchronization error)
    n_future_dates = max(3, int(len(orders_df) * anomaly_rate * 0.1))
    future_date_indices = random.sample(range(len(orders_df)), n_future_dates)
    for idx in future_date_indices:
        orders_df.iat[idx, orders_df.columns.get_loc("order_date")] = "2035-12-31"

    # 7. Math Mismatch in Line Totals
    n_math_err = max(5, int(len(order_items_df) * anomaly_rate * 0.2))
    math_err_indices = random.sample(range(len(order_items_df)), n_math_err)
    for idx in math_err_indices:
        order_items_df.iat[idx, order_items_df.columns.get_loc("line_total")] = 0.01  # Incorrect calculation
        
    print("[+] Anomalies successfully injected into raw datasets.")
    return customers_df, products_df, orders_df, order_items_df, payments_df


def generate_all_data(
    n_customers: int = 10000,
    n_products: int = 1000,
    n_stores: int = 50,
    n_orders: int = 50000,
    target_dir: Path = RAW_DATA_DIR,
    inject_anomalies: bool = True
) -> dict[str, pd.DataFrame]:
    """Execute end-to-end dataset generation and persist to CSV."""
    print(f"[*] Starting synthetic data generation...")
    print(f"    Customers: {n_customers:,} | Products: {n_products:,} | Stores: {n_stores:,} | Orders: {n_orders:,}")
    
    customers_df = generate_customers(n_customers)
    products_df = generate_products(n_products)
    stores_df = generate_stores(n_stores)
    orders_df, order_items_df, payments_df = generate_orders_and_items(
        n_orders, customers_df, products_df, stores_df
    )
    
    if inject_anomalies:
        customers_df, products_df, orders_df, order_items_df, payments_df = inject_intentional_anomalies(
            customers_df, products_df, orders_df, order_items_df, payments_df
        )
        
    target_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = {
        "customers": customers_df,
        "products": products_df,
        "stores": stores_df,
        "orders": orders_df,
        "order_items": order_items_df,
        "payments": payments_df,
    }
    
    for name, df in datasets.items():
        csv_path = target_dir / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        print(f"    [+] Saved {name}.csv -> {len(df):,} rows -> {csv_path.name}")
        
    print(f"[SUCCESS] All synthetic datasets successfully generated in {target_dir}")
    return datasets


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Enterprise Retail Synthetic Datasets")
    parser.add_argument("--customers", type=int, default=10000, help="Number of customer records")
    parser.add_argument("--products", type=int, default=1000, help="Number of product records")
    parser.add_argument("--stores", type=int, default=50, help="Number of store records")
    parser.add_argument("--orders", type=int, default=50000, help="Number of order records")
    parser.add_argument("--sample", action="store_true", help="Generate lightweight sample dataset")
    parser.add_argument("--no-anomalies", action="store_true", help="Do not inject intentional anomalies")
    
    args = parser.parse_args()
    
    if args.sample:
        generate_all_data(
            n_customers=2000,
            n_products=300,
            n_stores=20,
            n_orders=10000,
            target_dir=SAMPLE_DATA_DIR,
            inject_anomalies=not args.no_anomalies
        )
    else:
        generate_all_data(
            n_customers=args.customers,
            n_products=args.products,
            n_stores=args.stores,
            n_orders=args.orders,
            target_dir=RAW_DATA_DIR,
            inject_anomalies=not args.no_anomalies
        )
