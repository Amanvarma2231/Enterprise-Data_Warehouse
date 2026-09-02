"""
Diagram Image Generator
Renders high-resolution PNG architectural and data model diagrams for GitHub documentation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'


def draw_box(ax, x, y, w, h, title, lines, color="#1E3A8A", text_color="white", bg="#F8FAFC"):
    # Card Background
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", ec="#CBD5E1", fc=bg, lw=1.5)
    ax.add_patch(rect)
    
    # Header
    header_h = h * 0.25 if lines else h
    header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle="round,pad=0.02", ec=color, fc=color)
    ax.add_patch(header)
    
    ax.text(x + w/2, y + h - header_h/2, title, color=text_color, weight='bold', fontsize=10, ha='center', va='center')
    
    # Body lines
    if lines:
        curr_y = y + h - header_h - 0.05
        step = (h - header_h - 0.08) / max(1, len(lines))
        for line in lines:
            ax.text(x + 0.04, curr_y, line, color="#1E293B", fontsize=8.5, va='top')
            curr_y -= step


def generate_conceptual_png():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    fig.patch.set_facecolor('#FFFFFF')
    
    plt.title("RetailSphere - Conceptual Data Model (Phase 3)", fontsize=14, weight='bold', pad=15, color='#0F172A')
    
    # Entities
    draw_box(ax, 0.8, 4.0, 2.0, 1.2, "CUSTOMER", ["• Profile & Loyalty", "• Geographic Territory"], color="#0284C7")
    draw_box(ax, 4.0, 4.0, 2.0, 1.2, "ORDER", ["• Sales Header", "• Fulfillment Status"], color="#1E3A8A")
    draw_box(ax, 7.2, 4.0, 2.0, 1.2, "PAYMENT", ["• Gateway Tender", "• Settlement Amount"], color="#059669")
    
    draw_box(ax, 4.0, 1.5, 2.0, 1.2, "ORDER ITEM", ["• Quantity & Unit Price", "• Applied Discounts"], color="#4338CA")
    draw_box(ax, 7.2, 1.5, 2.0, 1.2, "PRODUCT", ["• SKU & Merchandising", "• Catalog Cost/Margin"], color="#D97706")
    draw_box(ax, 0.8, 1.5, 2.0, 1.2, "STORE", ["• Retail Channel", "• Location Territory"], color="#7C3AED")

    # Arrows
    arrow_props = dict(arrowstyle="->", color="#64748B", lw=2, mutation_scale=15)
    ax.annotate("", xy=(4.0, 4.6), xytext=(2.8, 4.6), arrowprops=arrow_props)
    ax.text(3.4, 4.75, "places (1:N)", fontsize=8, ha='center', color="#475569")
    
    ax.annotate("", xy=(7.2, 4.6), xytext=(6.0, 4.6), arrowprops=arrow_props)
    ax.text(6.6, 4.75, "settles (1:1)", fontsize=8, ha='center', color="#475569")

    ax.annotate("", xy=(5.0, 2.7), xytext=(5.0, 4.0), arrowprops=arrow_props)
    ax.text(5.5, 3.35, "contains (1:N)", fontsize=8, ha='center', color="#475569")

    ax.annotate("", xy=(6.0, 2.1), xytext=(7.2, 2.1), arrowprops=arrow_props)
    ax.text(6.6, 2.25, "ordered (N:1)", fontsize=8, ha='center', color="#475569")

    ax.annotate("", xy=(4.0, 4.2), xytext=(2.8, 2.5), arrowprops=arrow_props)
    ax.text(3.1, 3.3, "fulfills (1:N)", fontsize=8, ha='center', color="#475569")

    plt.tight_layout()
    plt.savefig(DOCS_DIR / "conceptual-model.png", bbox_inches='tight')
    plt.close()
    print("[+] Generated conceptual-model.png")


def generate_logical_png():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=200)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    
    plt.title("RetailSphere - Logical Data Model (Phase 4)", fontsize=14, weight='bold', pad=15, color='#0F172A')

    draw_box(ax, 0.5, 3.8, 2.6, 2.8, "CUSTOMER", [
        "customer_id (PK)", "first_name, last_name", "email, phone", "city, state, country", "segment, reg_date", "is_active"
    ], color="#0284C7")

    draw_box(ax, 4.7, 3.8, 2.6, 2.8, "ORDER", [
        "order_id (PK)", "customer_id (FK)", "store_id (FK)", "order_date", "order_status", "shipping_amount", "payment_status"
    ], color="#1E3A8A")

    draw_box(ax, 8.9, 3.8, 2.6, 2.8, "PAYMENT", [
        "payment_id (PK)", "order_id (FK)", "payment_method", "payment_status", "payment_amount", "payment_timestamp", "transaction_ref"
    ], color="#059669")

    draw_box(ax, 4.7, 0.4, 2.6, 2.8, "ORDER_ITEM", [
        "order_item_id (PK)", "order_id (FK)", "product_id (FK)", "quantity", "unit_price", "discount", "line_total"
    ], color="#4338CA")

    draw_box(ax, 8.9, 0.4, 2.6, 2.8, "PRODUCT", [
        "product_id (PK)", "sku (UK)", "product_name", "category, subcat", "unit_cost, unit_price", "profit_margin_pct", "is_discontinued"
    ], color="#D97706")

    draw_box(ax, 0.5, 0.4, 2.6, 2.8, "STORE", [
        "store_id (PK)", "store_name", "store_type", "channel_group", "region, city, state", "square_feet", "opened_date"
    ], color="#7C3AED")

    arrow_props = dict(arrowstyle="->", color="#64748B", lw=2, mutation_scale=12)
    ax.annotate("", xy=(4.7, 5.2), xytext=(3.1, 5.2), arrowprops=arrow_props)
    ax.annotate("", xy=(8.9, 5.2), xytext=(7.3, 5.2), arrowprops=arrow_props)
    ax.annotate("", xy=(6.0, 3.2), xytext=(6.0, 3.8), arrowprops=arrow_props)
    ax.annotate("", xy=(7.3, 1.8), xytext=(8.9, 1.8), arrowprops=arrow_props)
    ax.annotate("", xy=(4.7, 4.4), xytext=(3.1, 2.2), arrowprops=arrow_props)

    plt.tight_layout()
    plt.savefig(DOCS_DIR / "logical-model.png", bbox_inches='tight')
    plt.close()
    print("[+] Generated logical-model.png")


def generate_dimensional_png():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=200)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    
    plt.title("RetailSphere - Dimensional Star Schema Warehouse Model (Phase 6)", fontsize=15, weight='bold', pad=15, color='#0F172A')

    # Central Fact Table
    draw_box(ax, 4.8, 2.4, 3.4, 3.5, "fact_sales [FACT]", [
        "sales_key (PK)", "order_id, order_item_id (DD)", "customer_key (FK)", "product_key (FK)", "store_key (FK)", "date_key (FK)",
        "quantity", "unit_price, unit_cost", "gross_sales_amount", "discount_amount", "net_sales_amount", "cost_amount", "gross_profit_amount", "profit_margin_pct"
    ], color="#DC2626", bg="#FEF2F2")

    # Dimensions
    draw_box(ax, 0.5, 4.8, 3.2, 2.7, "dim_customer [DIM]", [
        "customer_key (PK / Surrogate)", "customer_id (Natural Key)", "full_name, email (PII)", "city, state, country", "segment, reg_date", "row_effective/expiry_date"
    ], color="#0284C7")

    draw_box(ax, 9.3, 4.8, 3.2, 2.7, "dim_store [DIM]", [
        "store_key (PK / Surrogate)", "store_id (Natural Key)", "store_name, store_type", "channel_group", "region, city, state", "square_feet, store_age"
    ], color="#7C3AED")

    draw_box(ax, 0.5, 0.5, 3.2, 2.7, "dim_product [DIM]", [
        "product_key (PK / Surrogate)", "product_id (Natural Key)", "sku, product_name", "category, subcategory", "unit_cost, unit_price", "profit_margin_pct, tier"
    ], color="#D97706")

    draw_box(ax, 9.3, 0.5, 3.2, 2.7, "dim_date [CONFORMED]", [
        "date_key (PK / YYYYMMDD)", "full_date (ISO Date)", "year_month, quarter_name", "day_name, month_name", "is_weekend, holiday_flag", "fiscal_year, fiscal_quarter"
    ], color="#059669")

    # Connectors
    arrow_props = dict(arrowstyle="<->", color="#1E3A8A", lw=2.2, mutation_scale=15)
    ax.annotate("", xy=(4.8, 4.6), xytext=(3.7, 5.5), arrowprops=arrow_props)
    ax.annotate("", xy=(8.2, 4.6), xytext=(9.3, 5.5), arrowprops=arrow_props)
    ax.annotate("", xy=(4.8, 3.6), xytext=(3.7, 2.2), arrowprops=arrow_props)
    ax.annotate("", xy=(8.2, 3.6), xytext=(9.3, 2.2), arrowprops=arrow_props)

    plt.tight_layout()
    plt.savefig(DOCS_DIR / "dimensional-model.png", bbox_inches='tight')
    plt.close()
    print("[+] Generated dimensional-model.png")


def generate_physical_png():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=200)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    
    plt.title("RetailSphere - Physical Ingestion & Staging Schema (Phase 5)", fontsize=14, weight='bold', pad=15, color='#0F172A')

    draw_box(ax, 0.6, 3.8, 2.8, 2.7, "staging.stg_customers", [
        "customer_id VARCHAR(50)", "first_name VARCHAR(100)", "email VARCHAR(255)", "city, state VARCHAR(100)", "_ingested_at TIMESTAMP", "_source_file VARCHAR"
    ], color="#334155")

    draw_box(ax, 4.1, 3.8, 2.8, 2.7, "staging.stg_orders", [
        "order_id VARCHAR(50)", "customer_id VARCHAR(50)", "store_id VARCHAR(50)", "order_date VARCHAR(50)", "order_status VARCHAR(50)", "_ingested_at TIMESTAMP"
    ], color="#334155")

    draw_box(ax, 7.6, 3.8, 2.8, 2.7, "staging.stg_payments", [
        "payment_id VARCHAR(50)", "order_id VARCHAR(50)", "payment_method VARCHAR", "payment_amount VARCHAR", "payment_date VARCHAR", "_ingested_at TIMESTAMP"
    ], color="#334155")

    draw_box(ax, 0.6, 0.5, 2.8, 2.7, "staging.stg_products", [
        "product_id VARCHAR(50)", "sku VARCHAR(100)", "product_name VARCHAR", "unit_cost, unit_price", "category, subcategory", "_ingested_at TIMESTAMP"
    ], color="#334155")

    draw_box(ax, 4.1, 0.5, 2.8, 2.7, "staging.stg_order_items", [
        "order_item_id VARCHAR(50)", "order_id VARCHAR(50)", "product_id VARCHAR(50)", "quantity VARCHAR(50)", "unit_price, discount", "_ingested_at TIMESTAMP"
    ], color="#334155")

    draw_box(ax, 7.6, 0.5, 2.8, 2.7, "staging.stg_stores", [
        "store_id VARCHAR(50)", "store_name VARCHAR", "store_type VARCHAR", "region, city, state", "square_feet, opened_date", "_ingested_at TIMESTAMP"
    ], color="#334155")

    plt.tight_layout()
    plt.savefig(DOCS_DIR / "physical-model.png", bbox_inches='tight')
    plt.close()
    print("[+] Generated physical-model.png")


if __name__ == "__main__":
    generate_conceptual_png()
    generate_logical_png()
    generate_physical_png()
    generate_dimensional_png()
    print("[SUCCESS] All 4 data model PNG diagrams successfully created in docs/")
